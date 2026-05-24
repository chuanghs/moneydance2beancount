import re
import hashlib
from typing import Optional, Dict, List
from src.models import (
    Account, Currency, BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo, SecurityInfo,
    Transaction, Split, Status, PriceSnapshot, BudgetItem
)
from src.exporter.beancount.mapper import get_commodity_code, normalize_commodity
from src.exporter.beancount.router import get_file_for_account, get_file_for_transaction

DEFAULT_OPERATING_CURRENCIES = ["TWD", "USD", "EUR"]

def escape_beancount_string(s: str) -> str:
    """Escapes backslashes and double quotes for Beancount strings."""
    if not s:
        return ""
    # IMPORTANT: Backslash must be replaced FIRST
    return s.replace('\\', '\\\\').replace('"', '\\"')

def format_amount(amount: int, decimal_places: int, strip_zeros: bool = False) -> str:
    s = str(abs(amount))
    if decimal_places <= 0:
        res = s
    elif len(s) <= decimal_places:
        res = "0." + s.zfill(decimal_places)
    else:
        res = s[:-decimal_places] + "." + s[-decimal_places:]

    if strip_zeros and "." in res:
        res = res.rstrip('0').rstrip('.')

    if amount < 0:
        return "-" + res
    return res

def export_options(root_account: Account, operating_currencies: List[str], global_settings: Optional[Dict] = None) -> str:
    """Generates the OPTIONS section of the Beancount file."""
    if global_settings is None:
        global_settings = {}
    lines = []
    
    # 1. Title
    title = root_account.name if root_account else "Moneydance Export"
    lines.append(f'option "title" "{escape_beancount_string(title)}"')
    
    # 2. Operating Currencies
    currencies = operating_currencies
    if not currencies:
        currencies = global_settings.get("operating_currencies", DEFAULT_OPERATING_CURRENCIES)
        
    for curr in currencies:
        lines.append(f'option "operating_currency" "{curr}"')
        
    return "\n".join(lines)

def export_commodities(currencies: List[Currency], start_date: str = "1970-01-01", commodity_map: Optional[Dict] = None) -> str:
    lines = []
    seen_codes = set()
    
    for curr in sorted(currencies, key=lambda x: get_commodity_code(x, commodity_map)):
        code = get_commodity_code(curr, commodity_map)
        if code in seen_codes:
            continue
        seen_codes.add(code)
        
        lines.append(f'{start_date} commodity {code}')
        if curr.name:
            lines.append(f'  name: "{escape_beancount_string(curr.name)}"')
        if curr.md_id:
            lines.append(f'  md_id: "{curr.md_id}"')
        lines.append("")
        
    return "\n".join(lines)

def export_budgets(budgets: List[BudgetItem], account_paths: Dict[int, str], commodity_map: Optional[Dict] = None) -> str:
    lines = []
    interval_map = {
        6: "monthly",
        5: "weekly",
        8: "yearly"
    }
    
    for item in sorted(budgets, key=lambda x: x.date):
        date_str = item.date.strftime("%Y-%m-%d")
        freq = interval_map.get(item.interval, "monthly")
        path = account_paths[id(item.account)]
        amount_str = format_amount(item.amount, item.account.currency.decimal)
        currency = get_commodity_code(item.account.currency, commodity_map)
        
        lines.append(f'{date_str} custom "budget" {path} "{freq}" {amount_str} {currency}')
        
    return "\n".join(lines)

def export_prices(snapshots: List[PriceSnapshot], base_currency_code: str, commodity_map: Optional[Dict] = None) -> str:
    if not base_currency_code:
        return ""
        
    lines = []
    valid_snapshots = [s for s in snapshots if s.currency and get_commodity_code(s.currency, commodity_map) != "UNKNOWN"]
    
    # Sort by date and derived commodity code
    for snap in sorted(valid_snapshots, key=lambda x: (x.date, get_commodity_code(x.currency, commodity_map))):
        code = get_commodity_code(snap.currency, commodity_map)
        
        # Determine the target currency for this price
        target_currency = normalize_commodity(snap.currency.parent_code) if snap.currency.parent_code else base_currency_code
        
        if code == target_currency:
            continue
            
        date_str = snap.date.strftime("%Y-%m-%d")
        price = 1.0 / snap.price
        
        lines.append(f'{date_str} price {code}  {price:.8f} {target_currency}')
        
    return "\n".join(lines)

def export_accounts(accounts: List[Account], account_paths: Dict[int, str], start_date: str = "1970-01-01", target_file: Optional[str] = None, commodity_map: Optional[Dict] = None) -> str:
    lines = []
    
    if target_file is None or target_file == "main.beancount":
        lines.append(f'{start_date} open Equity:OpeningBalances')
        lines.append("")
    
    path_to_accounts = {}
    for acct in accounts:
        if target_file and get_file_for_account(acct) != target_file:
            continue
            
        upath = account_paths[id(acct)]
        if upath not in path_to_accounts:
            path_to_accounts[upath] = []
        path_to_accounts[upath].append(acct)

    for path in sorted(path_to_accounts.keys()):
        accts_in_path = path_to_accounts[path]
        
        currencies = sorted(list(set(get_commodity_code(a.currency, commodity_map) for a in accts_in_path)))
        curr_str = " " + ",".join(currencies) if currencies else ""
        
        primary_acct = next((a for a in accts_in_path if not isinstance(a.info, SecurityInfo)), accts_in_path[0])
        
        has_security = any(isinstance(a.info, SecurityInfo) for a in accts_in_path)
        booking_policy = ' "FIFO"' if has_security else ""
        
        lines.append(f'{start_date} open {path}{curr_str}{booking_policy}')
        lines.append(f'  md_name: "{escape_beancount_string(primary_acct.name)}"')
        if primary_acct.comment:
            lines.append(f'  comment: "{escape_beancount_string(primary_acct.comment)}"')

        for acct in accts_in_path:
            if acct.initial != 0:
                lines.append("")
                lines.append(f'{start_date} * "{escape_beancount_string("Opening Balance")}"')
                amount_str = format_amount(acct.initial, acct.currency.decimal, strip_zeros=True)
                
                cost_str = ""
                if isinstance(acct.info, SecurityInfo):
                    base_curr = get_commodity_code(acct.info.parent.currency, commodity_map)
                    cost_str = f" {{{{ 0 {base_curr} }}}}"
                
                lines.append(f'  Equity:OpeningBalances')
                lines.append(f'  {path}  {amount_str} {get_commodity_code(acct.currency, commodity_map)}{cost_str}')
                lines.append("")

    return "\n".join(lines)

def export_transactions(transactions: List[Transaction], account_paths: Dict[int, str], target_file: Optional[str] = None, commodity_map: Optional[Dict] = None) -> str:
    lines = []
    
    for txn in sorted(transactions, key=lambda x: x.date):
        if target_file and get_file_for_transaction(txn) != target_file:
            continue
            
        flag = "*" if txn.status in (Status.CLEARED, Status.RECONCILED) else "!"
        
        date_str = txn.date.strftime("%Y-%m-%d")
        lines.append(f'{date_str} {flag} "{escape_beancount_string(txn.description)}"')
        
        total_pamt = 0
        for split in txn.splits:
            total_pamt += split.received_amount
            
        giver_path = account_paths[id(txn.giver)]
        giver_currency = get_commodity_code(txn.giver.currency, commodity_map)
        giver_amount_str = format_amount(total_pamt, txn.giver.currency.decimal)
        lines.append(f'  {giver_path}  {giver_amount_str} {giver_currency}')
        
        has_security_sell = False
        for split in txn.splits:
            recv_path = account_paths[id(split.receiver)]
            recv_currency = get_commodity_code(split.receiver.currency, commodity_map)
            
            if split.receiver.currency.code == txn.giver.currency.code:
                amount_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                lines.append(f'  {recv_path}   {amount_str} {recv_currency}')
            else:
                if isinstance(split.receiver.info, SecurityInfo) and split.given_amount != 0:
                    amt_recv_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                    
                    if split.given_amount > 0:
                        total_cost_val = abs(split.received_amount) / (10 ** txn.giver.currency.decimal)
                        quantity_val = abs(split.given_amount) / (10 ** split.receiver.currency.decimal)
                        unit_price = total_cost_val / quantity_val
                        
                        lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} {{ {unit_price:.6f} {giver_currency} }}')
                    else:
                        has_security_sell = True
                        amt_parent_str = format_amount(abs(split.received_amount), txn.giver.currency.decimal)
                        lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} {{}} @@ {amt_parent_str} {giver_currency}')
                else:
                    amt_recv_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                    amt_parent_str = format_amount(abs(split.received_amount), txn.giver.currency.decimal)
                    lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} @@ {amt_parent_str} {giver_currency}')
        
        if has_security_sell:
            lines.append(f'  Equity:OpeningBalances {giver_currency}')
            
        lines.append("")

    return "\n".join(lines)
