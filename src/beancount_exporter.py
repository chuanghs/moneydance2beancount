import re
import hashlib
import os
import yaml
from typing import Optional

from src.models import (
    Account, Currency, BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo, SecurityInfo,
    Transaction, Split, Status, PriceSnapshot, BudgetItem
)

# Load commodity translation map if it exists
COMMODITY_MAP = {}
GLOBAL_SETTINGS = {}
map_path = "commodity_map.yaml"
if os.path.exists(map_path):
    try:
        with open(map_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config:
                if "translations" in config:
                    COMMODITY_MAP = config["translations"]
                if "settings" in config:
                    GLOBAL_SETTINGS = config["settings"]
    except Exception as e:
        print(f";; Warning: Failed to load {map_path}: {e}")

DEFAULT_OPERATING_CURRENCIES = ["TWD", "USD", "EUR"]

def escape_beancount_string(s: str) -> str:
    """Escapes backslashes and double quotes for Beancount strings."""
    if not s:
        return ""
    # IMPORTANT: Backslash must be replaced FIRST
    return s.replace('\\', '\\\\').replace('"', '\\"')

def export_options(root_account: Account, operating_currencies: list[str]) -> str:
    """Generates the OPTIONS section of the Beancount file."""
    lines = []
    
    # 1. Title
    title = root_account.name if root_account else "Moneydance Export"
    lines.append(f'option "title" "{escape_beancount_string(title)}"')
    
    # 2. Operating Currencies
    # Priority: 1. CLI Arg (if not empty) 2. Config Setting 3. Default List
    currencies = operating_currencies
    if not currencies:
        currencies = GLOBAL_SETTINGS.get("operating_currencies", DEFAULT_OPERATING_CURRENCIES)
        
    for curr in currencies:
        lines.append(f'option "operating_currency" "{curr}"')
        
    return "\n".join(lines)

def normalize_commodity(code: str) -> str:
    """Sanitizes a commodity code to strictly follow Beancount v3 syntax."""
    if not code:
        return "UNKNOWN"
    
    # 1. Convert to uppercase and replace common separators with underscores
    res = code.upper().replace(' ', '_').replace('&', '_')
    
    # 2. Keep only allowed characters: A-Z, 0-9, '.', '_', '-', "'"
    res = "".join(c for c in res if c.isalnum() or c in "._-'")
    
    # 3. Ensure it starts with a letter. If not, prepend SYM_
    if res and res[0].isdigit():
        res = "SYM_" + res
    
    # 4. Final check: if it's empty or still doesn't start with a letter, fallback
    if not res or not res[0].isalpha():
        res = "C_" + (res if res else hashlib.md5(code.encode()).hexdigest()[:8].upper())
        
    # 5. Limit length (Beancount limit is 24)
    return res[:24]

def get_commodity_code(currency: Currency) -> str:
    """Selects the best Beancount commodity code for a given currency/security."""
    # 1. Check manual translation map first (priority)
    if currency.name in COMMODITY_MAP:
        return normalize_commodity(COMMODITY_MAP[currency.name])
    if currency.ticker in COMMODITY_MAP:
        return normalize_commodity(COMMODITY_MAP[currency.ticker])
    if currency.code in COMMODITY_MAP:
        return normalize_commodity(COMMODITY_MAP[currency.code])

    # 2. Prefer ticker if present
    if currency.ticker:
        return normalize_commodity(currency.ticker)
    
    # 3. Prefer code if it's not a GUID
    code = currency.code
    is_guid = len(code) == 36 and code.count('-') == 4
    if code and not is_guid:
        return normalize_commodity(code)
    
    # 4. Fallback to name
    if currency.name:
        return normalize_commodity(currency.name)
    
    return normalize_commodity(code) if code else "UNKNOWN"

def export_commodities(currencies: list[Currency], start_date: str = "1970-01-01") -> str:
    lines = []
    seen_codes = set()
    
    for curr in sorted(currencies, key=lambda x: get_commodity_code(x)):
        code = get_commodity_code(curr)
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

def export_budgets(budgets: list[BudgetItem], account_paths: dict[int, str]) -> str:
    lines = []
    # Interval mapping: 6 -> monthly. 
    # Let's assume others for now, but focus on 6 as it was seen in sample.
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
        currency = get_commodity_code(item.account.currency)
        
        lines.append(f'{date_str} custom "budget" {path} "{freq}" {amount_str} {currency}')
        
    return "\n".join(lines)

def export_prices(snapshots: list[PriceSnapshot], base_currency_code: str) -> str:
    if not base_currency_code:
        return ""
        
    lines = []
    # Filter out snapshots missing currency info or where we can't derive a valid symbol
    valid_snapshots = [s for s in snapshots if s.currency and get_commodity_code(s.currency) != "UNKNOWN"]
    
    # Sort by date and derived commodity code
    for snap in sorted(valid_snapshots, key=lambda x: (x.date, get_commodity_code(x.currency))):
        code = get_commodity_code(snap.currency)
        
        # Determine the target currency for this price
        target_currency = snap.currency.parent_code if snap.currency.parent_code else base_currency_code
        
        if code == target_currency:
            continue
            
        date_str = snap.date.strftime("%Y-%m-%d")
        # Beancount price = 1 / MD urt
        price = 1.0 / snap.price
        
        # Use high precision for prices (8 decimal places)
        lines.append(f'{date_str} price {code}  {price:.8f} {target_currency}')
        
    return "\n".join(lines)

def normalize_name(name: str) -> str:
    # 1. Split by parentheses for hierarchical conversion (e.g. A(B) -> A:B)
    raw_parts = re.split(r'[()]', name)
    
    normalized_parts = []
    for part in raw_parts:
        # 2. Extract alphanumeric components (Unicode-aware, excluding underscore)
        components = re.findall(r'[^\W_]+', part, re.UNICODE)
        
        # 3. Capitalize each component for CamelCase
        normalized_components = [c[0].upper() + c[1:] if c else "" for c in components]
        
        # 4. Join components
        res = "".join(normalized_components)
        if res:
            normalized_parts.append(res)
    
    # 5. Join hierarchical parts with ':'
    result = ":".join(normalized_parts)
    
    # 6. Fallback for completely non-alphanumeric names (rare)
    if not result and name:
        h = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
        result = "U" + h
        
    return result

class AccountRegistry:
    def __init__(self):
        self.used_paths = set()

    def get_unique_path(self, path: str) -> str:
        if path not in self.used_paths:
            self.used_paths.add(path)
            return path
        
        counter = 2
        while True:
            new_path = f"{path}_{counter}"
            if new_path not in self.used_paths:
                self.used_paths.add(new_path)
                return new_path
            counter += 1

def get_file_for_account(account: Account) -> str:
    if re.search(r'Cash|現金', account.name):
        return "daily.beancount"
    if isinstance(account.info, (InvestmentInfo, SecurityInfo)):
        return "investment.beancount"
    elif isinstance(account.info, (LiabilityInfo, LoanInfo, CreditCardInfo)):
        return "liability.beancount"
    elif isinstance(account.info, (BankInfo, AssetInfo)):
        return "assets.beancount"
    # IncomeInfo, ExpenseInfo, and None (Root) go to main
    return "main.beancount"

def get_file_for_transaction(txn: Transaction) -> str:
    all_accounts = [txn.giver] + [s.receiver for s in txn.splits]
    
    # 1. Daily (Cash/現金)
    if any(re.search(r'Cash|現金', acc.name) for acc in all_accounts):
        return "daily.beancount"
    
    # 2. Investment
    if any(isinstance(acc.info, (InvestmentInfo, SecurityInfo)) for acc in all_accounts):
        return "investment.beancount"
        
    # 3. Liability
    if any(isinstance(acc.info, (LiabilityInfo, LoanInfo, CreditCardInfo)) for acc in all_accounts):
        return "liability.beancount"
        
    # 4. Assets
    if any(isinstance(acc.info, (BankInfo, AssetInfo)) for acc in all_accounts):
        return "assets.beancount"
        
    # 5. Fallback
    return "main.beancount"

def get_beancount_path(account: Account) -> str:
    # If it's a security, collapse it into its parent (the Investment account)
    if isinstance(account.info, SecurityInfo):
        return get_beancount_path(account.info.parent)

    current = account
    path_parts = []
    
    # Climb up and collect names
    while current and current.info is not None:
        name = normalize_name(current.name)
        path_parts.append(name)
        current = current.info.parent
        
    # Determine the category from the account's info
    info = account.info
    if info is None:
        return "Equity:Root"
    
    if isinstance(info, BankInfo):
        category = "Assets:Bank"
    elif isinstance(info, (InvestmentInfo, SecurityInfo)):
        category = "Assets:Investment"
    elif isinstance(info, AssetInfo):
        category = "Assets:Cash"
    elif isinstance(info, CreditCardInfo):
        category = "Liabilities:Card"
    elif isinstance(info, (LiabilityInfo, LoanInfo)):
        category = "Liabilities"
    elif isinstance(info, IncomeInfo):
        category = "Income"
    elif isinstance(info, ExpenseInfo):
        category = "Expenses"
    else:
        category = "Equity"
        
    # If the top-most account name matches the category, skip it to avoid redundant prefix
    # We check the last part of the category (e.g. "Bank" in "Assets:Bank")
    cat_parts = category.split(":")
    if path_parts and path_parts[-1].lower() == cat_parts[-1].lower():
        path_parts.pop()
        
    path_parts.append(category)
    return ":".join(reversed(path_parts))

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
def export_accounts(accounts: list[Account], account_paths: dict[int, str], start_date: str = "1970-01-01", target_file: Optional[str] = None) -> str:
    lines = []
    
    # Opening balance account definition - ONLY in main.beancount
    if target_file is None or target_file == "main.beancount":
        lines.append(f'{start_date} open Equity:OpeningBalances')
        lines.append("")
    
    # Group accounts by their unique path
    path_to_accounts = {} # unique_path -> list of MD accounts
    for acct in accounts:
        # If filtering, check if this account belongs to the target file
        if target_file and get_file_for_account(acct) != target_file:
            continue
            
        upath = account_paths[id(acct)]
        if upath not in path_to_accounts:
            path_to_accounts[upath] = []
        path_to_accounts[upath].append(acct)

    # Generate open directives
    for path in sorted(path_to_accounts.keys()):
        accts_in_path = path_to_accounts[path]
        
        # Collect all unique currencies for this path.
        currencies = sorted(list(set(get_commodity_code(a.currency) for a in accts_in_path)))
        curr_str = " " + ",".join(currencies) if currencies else ""
        
        # Pick the "best" MD account for metadata (usually the one that isn't a security)
        primary_acct = next((a for a in accts_in_path if not isinstance(a.info, SecurityInfo)), accts_in_path[0])
        
        # If any account in this path is a security, add FIFO booking policy
        has_security = any(isinstance(a.info, SecurityInfo) for a in accts_in_path)
        booking_policy = ' "FIFO"' if has_security else ""
        
        lines.append(f'{start_date} open {path}{curr_str}{booking_policy}')
        lines.append(f'  md_name: "{escape_beancount_string(primary_acct.name)}"')
        if primary_acct.comment:
            lines.append(f'  comment: "{escape_beancount_string(primary_acct.comment)}"')

        # Handle initial balances for all accounts in this path
        for acct in accts_in_path:
            if acct.initial != 0:
                lines.append("")
                lines.append(f'{start_date} * "{escape_beancount_string("Opening Balance")}"')
                amount_str = format_amount(acct.initial, acct.currency.decimal, strip_zeros=True)
                
                # If it's a security, add {{ 0 BASE_CURR }}
                cost_str = ""
                if isinstance(acct.info, SecurityInfo):
                    base_curr = get_commodity_code(acct.info.parent.currency)
                    cost_str = f" {{{{ 0 {base_curr} }}}}"
                
                lines.append(f'  Equity:OpeningBalances')
                lines.append(f'  {path}  {amount_str} {get_commodity_code(acct.currency)}{cost_str}')
                lines.append("")

    return "\n".join(lines)

def export_transactions(transactions: list[Transaction], account_paths: dict[int, str], target_file: Optional[str] = None) -> str:
    lines = []
    
    for txn in sorted(transactions, key=lambda x: x.date):
        # If filtering, check if this transaction belongs to the target file
        if target_file and get_file_for_transaction(txn) != target_file:
            continue
            
        # Status mapping
        flag = "*" if txn.status in (Status.CLEARED, Status.RECONCILED) else "!"
        
        date_str = txn.date.strftime("%Y-%m-%d")
        lines.append(f'{date_str} {flag} "{escape_beancount_string(txn.description)}"')
        
        # Calculate total pamt (giver amount in giver currency)
        total_pamt = 0
        for split in txn.splits:
            total_pamt += split.received_amount
            
        # Giver posting
        giver_path = account_paths[id(txn.giver)]
        giver_currency = get_commodity_code(txn.giver.currency)
        # Giver gives the total_pamt (MD pamt is already negative for spending)
        giver_amount_str = format_amount(total_pamt, txn.giver.currency.decimal)
        lines.append(f'  {giver_path}  {giver_amount_str} {giver_currency}')
        
        # Split postings
        has_security_sell = False
        for split in txn.splits:
            recv_path = account_paths[id(split.receiver)]
            recv_currency = get_commodity_code(split.receiver.currency)
            
            # Use given_amount (samt) for the receiving account's posting
            if split.receiver.currency.code == txn.giver.currency.code:
                amount_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                lines.append(f'  {recv_path}   {amount_str} {recv_currency}')
            else:
                # Multi-currency logic
                # For Security transactions (receiver is SecurityInfo and quantity non-zero), use cost basis notation
                if isinstance(split.receiver.info, SecurityInfo) and split.given_amount != 0:
                    amt_recv_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                    
                    if split.given_amount > 0:
                        # Buy: Establish cost basis (Unit Cost notation { })
                        # Calculate unit price: abs(total_cost) / abs(quantity)
                        # Convert from MD integer amounts to floats first
                        total_cost_val = abs(split.received_amount) / (10 ** txn.giver.currency.decimal)
                        quantity_val = abs(split.given_amount) / (10 ** split.receiver.currency.decimal)
                        unit_price = total_cost_val / quantity_val
                        
                        lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} {{ {unit_price:.6f} {giver_currency} }}')
                    else:
                        # Sell: Use lot matcher {} and specify total price @@
                        has_security_sell = True
                        amt_parent_str = format_amount(abs(split.received_amount), txn.giver.currency.decimal)
                        lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} {{}} @@ {amt_parent_str} {giver_currency}')
                else:
                    # Currency exchange logic: use @@ (Total Price)
                    amt_recv_str = format_amount(split.given_amount, split.receiver.currency.decimal, strip_zeros=True)
                    amt_parent_str = format_amount(abs(split.received_amount), txn.giver.currency.decimal)
                    lines.append(f'  {recv_path}   {amt_recv_str} {recv_currency} @@ {amt_parent_str} {giver_currency}')
        
        # If we had a security sell, add an empty Equity:OpeningBalances posting with explicit currency
        # to absorb gain/loss and avoid ambiguity in multi-currency transactions.
        if has_security_sell:
            lines.append(f'  Equity:OpeningBalances {giver_currency}')
            
        lines.append("")

    return "\n".join(lines)

def full_multi_export(db: 'Database', operating_currencies: list[str], output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    registry = AccountRegistry()
    account_paths = {} # id(acct) -> unique_path
    raw_to_unique = {} # raw_path -> unique_path
    
    for acct in db.accounts.values():
        raw_path = get_beancount_path(acct)
        if raw_path not in raw_to_unique:
            raw_to_unique[raw_path] = registry.get_unique_path(raw_path)
        account_paths[id(acct)] = raw_to_unique[raw_path]

    # File definitions
    categories = [
        "commodity.beancount",
        "prices.beancount",
        "assets.beancount",
        "investment.beancount",
        "liability.beancount",
        "daily.beancount"
    ]
    
    # 1. Export Category Files
    
    # commodity.beancount
    with open(os.path.join(output_dir, "commodity.beancount"), "w", encoding="utf-8") as f:
        f.write(";; === COMMODITIES ===\n\n")
        f.write(export_commodities(list(db.currencies.values())))
        
    # prices.beancount
    with open(os.path.join(output_dir, "prices.beancount"), "w", encoding="utf-8") as f:
        f.write(";; === PRICES ===\n\n")
        if db.price_snapshots:
            f.write(export_prices(db.price_snapshots, db.base_currency_code))
            
    # Category files (Accounts + Transactions)
    for cat_file in ["assets.beancount", "investment.beancount", "liability.beancount", "daily.beancount"]:
        with open(os.path.join(output_dir, cat_file), "w", encoding="utf-8") as f:
            f.write(f";; === {cat_file.upper().replace('.BEANCOUNT', '')} ===\n\n")
            f.write(export_accounts(list(db.accounts.values()), account_paths, target_file=cat_file))
            f.write("\n\n")
            f.write(export_transactions(db.transactions, account_paths, target_file=cat_file))
            
    # main.beancount
    with open(os.path.join(output_dir, "main.beancount"), "w", encoding="utf-8") as f:
        root_account = next((a for a in db.accounts.values() if a.info is None), None)
        f.write(";; === OPTIONS ===\n")
        f.write(export_options(root_account, operating_currencies))
        f.write("\n\n")
        
        for cat in categories:
            f.write(f'include "{cat}"\n')
        f.write("\n")
        
        f.write(";; === MAIN ACCOUNTS (Income/Expenses) ===\n\n")
        f.write(export_accounts(list(db.accounts.values()), account_paths, target_file="main.beancount"))
        f.write("\n\n")
        f.write(";; === MAIN TRANSACTIONS ===\n\n")
        f.write(export_transactions(db.transactions, account_paths, target_file="main.beancount"))

def full_export(db: 'Database', operating_currencies: list[str] = None) -> str:
    if operating_currencies is None:
        operating_currencies = []
        
    registry = AccountRegistry()
    account_paths = {} # id(acct) -> unique_path
    raw_to_unique = {} # raw_path -> unique_path
    
    for acct in db.accounts.values():
        raw_path = get_beancount_path(acct)
        if raw_path not in raw_to_unique:
            raw_to_unique[raw_path] = registry.get_unique_path(raw_path)
        account_paths[id(acct)] = raw_to_unique[raw_path]
        
    sections = []
    
    # -1. Options
    # Try to find the root account to get the title
    root_account = next((a for a in db.accounts.values() if a.info is None), None)
    sections.append(";; === OPTIONS ===")
    sections.append(export_options(root_account, operating_currencies))
    sections.append("")
    
    # Resolve actual operating currencies used (for price export)
    # This logic matches export_options' priority
    actual_currencies = operating_currencies
    if not actual_currencies:
        actual_currencies = GLOBAL_SETTINGS.get("operating_currencies", DEFAULT_OPERATING_CURRENCIES)

    # 0. Commodities
    sections.append(";; === COMMODITIES ===")
    sections.append(export_commodities(list(db.currencies.values())))
    sections.append("")
    
    # 1. Accounts
    sections.append(";; === ACCOUNTS ===")
    sections.append(export_accounts(list(db.accounts.values()), account_paths))
    sections.append("")
    
    # 2. Prices
    if db.price_snapshots:
        sections.append(";; === PRICES ===")
        sections.append(export_prices(db.price_snapshots, db.base_currency_code))
        sections.append("")
        
    # 3. Budgets
    if db.budget_items:
        sections.append(";; === BUDGETS ===")
        sections.append(export_budgets(db.budget_items, account_paths))
        sections.append("")
        
    # 4. Transactions
    sections.append(";; === TRANSACTIONS ===")
    sections.append(export_transactions(db.transactions, account_paths))
    
    return "\n".join(sections)

if __name__ == "__main__":
    import sys
    from src.database import Database
    
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.beancount_exporter <moneydance_json> [base_currencies_comma_separated] [output_dir]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    # base_curr can be a comma-separated list like "TWD,USD,EUR"
    base_curr_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    operating_currencies = [c.strip() for c in base_curr_arg.split(",")] if base_curr_arg else []
    
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(json_path, "r") as f:
        data = f.read()
        
    db = Database.load(data)
    
    if output_dir:
        full_multi_export(db, operating_currencies, output_dir)
        print(f";; Multi-file export complete. Files generated in: {output_dir}")
    else:
        print(full_export(db, operating_currencies))
