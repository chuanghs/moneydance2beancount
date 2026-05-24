import json
from uuid import UUID
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from .models import (
    Currency, Account, Transaction, Split, Status,
    BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo, SecurityInfo,
    PriceSnapshot, BudgetItem
)

class MoneydanceError(Exception):
    pass

class Database:
    def __init__(self):
        self.accounts: Dict[UUID, Account] = {}
        self.currencies: Dict[UUID, Currency] = {}
        self.transactions: List[Transaction] = []
        self.price_snapshots: List[PriceSnapshot] = []
        self.budget_items: List[BudgetItem] = []
        self.base_currency_code: str = "USD" # Default

    @classmethod
    def load(cls, data_str: str) -> 'Database':
        raw_data = json.loads(data_str)
        db = cls()
        
        accounts_raw, currencies_raw, transactions_raw, csnaps_raw, budgets_raw = db._sort_exported_data(raw_data['all_items'])

        # First pass: map MD ID to raw code
        md_id_to_raw_code = {}
        for curr_raw in currencies_raw:
            code = curr_raw.get('currid', "")
            if not code:
                code = curr_raw.get('ticker', "")
            if not code:
                code = curr_raw.get('name', "")
            if not code:
                code = "UNKNOWN"
            md_id_to_raw_code[curr_raw['id']] = code

        for curr_raw in currencies_raw:
            id_val = UUID(curr_raw['id'])
            code = curr_raw['currid']
            
            # Resolve parent_code
            parent_id_raw = curr_raw.get('relative_to_currid') or curr_raw.get('rel_curr_id')
            parent_code = None
            if parent_id_raw:
                # Moneydance sometimes uses MD ID (UUID-like) and sometimes uses the raw code string (e.g. 'USD')
                if parent_id_raw in md_id_to_raw_code:
                    parent_code = md_id_to_raw_code[parent_id_raw]
                else:
                    parent_code = parent_id_raw
            
            # If parent is the same as this currency, it's not a real hierarchy (self-referential base)
            if parent_code == md_id_to_raw_code[curr_raw['id']]:
                parent_code = None

            db.currencies[id_val] = Currency(
                code=code,
                decimal=int(curr_raw['dec']),
                rate=float(curr_raw['rate']),
                ticker=curr_raw.get('ticker', ""),
                name=curr_raw.get('name', ""),
                md_id=curr_raw['id'],
                parent_code=parent_code
            )
            if curr_raw.get('isbase') == 'y':
                db.base_currency_code = md_id_to_raw_code[curr_raw['id']]

        # Accounts might be hierarchical, use the same logic as Rust
        remaining_accounts = {UUID(a['id']): a for a in accounts_raw}
        while remaining_accounts:
            id_val = next(iter(remaining_accounts))
            db._add_accounts(remaining_accounts, id_val)

        for txn_raw in transactions_raw:
            db._import_splits(txn_raw)
            
        for snap_raw in csnaps_raw:
            db._import_snapshot(snap_raw)
            
        for budget_raw in budgets_raw:
            db._import_budget(budget_raw)

        return db

    def _sort_exported_data(self, all_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        accounts = []
        currencies = []
        transactions = []
        csnaps = []
        budgets = []

        for item in all_items:
            obj_type = item.get('obj_type')
            if obj_type == 'acct':
                accounts.append(item)
            elif obj_type == 'curr':
                currencies.append(item)
            elif obj_type == 'txn':
                transactions.append(item)
            elif obj_type == 'csnap':
                csnaps.append(item)
            elif obj_type == 'bdgtitem':
                budgets.append(item)
        
        return accounts, currencies, transactions, csnaps, budgets

    def _add_accounts(self, parent_set: Dict[UUID, Dict[str, Any]], id_val: UUID) -> Account:
        if id_val in self.accounts:
            return self.accounts[id_val]

        acct_raw = parent_set.pop(id_val, None)
        if acct_raw is None:
            raise MoneydanceError(f"Account {id_val} does not exist")

        acct_type = acct_raw.get('type')
        
        if acct_type == 'r':
            result = self._new_root_account(acct_raw)
        else:
            parent_id = UUID(acct_raw['parentid'])
            parent = self._add_accounts(parent_set, parent_id)
            result = self._new_account(acct_raw, parent)

        self.accounts[id_val] = result
        return result

    def _import_splits(self, orig: Dict[str, Any]) -> None:
        acctid_str = orig.get('acctid')
        if not acctid_str:
            raise MoneydanceError("invalid_acctid field")
        acctid = UUID(acctid_str)

        stat_str = orig.get('stat')
        if stat_str == 'X':
            stat = Status.RECONCILED
        else:
            stat = Status.NONE

        desc = orig.get('desc')
        if desc is None:
            raise MoneydanceError("invalid desc field in transaction")

        dt_str = orig.get('dt')
        if not dt_str:
            raise MoneydanceError("invalid dt field in transaction")
        date = datetime.strptime(dt_str, "%Y%m%d")

        splits_data: Dict[int, Dict[str, Any]] = {}
        for k, v in orig.items():
            parts = k.split('.')
            if len(parts) == 2:
                try:
                    index = int(parts[0])
                    remain = parts[1]
                    if index not in splits_data:
                        splits_data[index] = {}
                    
                    if remain == "acctid":
                        splits_data[index]["acctid"] = UUID(v)
                    elif remain == "pamt":
                        splits_data[index]["pamt"] = int(v)
                    elif remain == "samt":
                        splits_data[index]["samt"] = int(v)
                    elif remain == "tags":
                        splits_data[index]["tags"] = v
                    elif remain == "desc":
                        splits_data[index]["desc"] = v
                except ValueError:
                    continue

        txn_splits = []
        # Sort indices to match Rust's resize behavior
        for i in sorted(splits_data.keys()):
            data = splits_data[i]
            # In Rust, it resizes and defaults if some indices are missing.
            # Here we just iterate over found indices. If there are gaps, 
            # we should probably handle them if we want exact compatibility.
            # Rust code: `splits.resize(index+1, rawjson::Txn::default());`
            # This means gaps are filled with default values.
            # Let's fill gaps.
        
        max_index = max(splits_data.keys()) if splits_data else -1
        full_splits = []
        for i in range(max_index + 1):
            if i in splits_data:
                data = splits_data[i]
                full_splits.append(Split(
                    receiver=self.get_account(data["acctid"]),
                    received_amount=data.get("pamt", 0),
                    given_amount=data.get("samt", 0),
                    tags=data.get("tags", ""),
                    description=data.get("desc", "")
                ))
            else:
                # Default Split? Rust uses `rawjson::Txn::default()`
                # which has nil uuid and empty strings.
                # get_account will fail for nil uuid though.
                # Actually, looking at Rust code:
                # `splits[index].acctid = Uuid::parse_str(&v)?;`
                # If a split exists, it MUST have an acctid.
                # If we have a gap, what happens? 
                # `self.get_account(t.acctid)?` will be called on a default Txn (nil uuid).
                # That will likely fail.
                pass

        giver = self.get_account(acctid)

        self.transactions.append(Transaction(
            giver=giver,
            date=date,
            status=stat,
            description=desc,
            splits=full_splits
        ))

    def _import_snapshot(self, snap_raw: Dict[str, Any]) -> None:
        currid = UUID(snap_raw['curr'])
        if currid not in self.currencies:
            return # Skip if currency not known
        
        curr = self.currencies[currid]
        dt_str = snap_raw.get('dt')
        if not dt_str:
            return
        date = datetime.strptime(dt_str, "%Y%m%d")
        
        # User Rate (urt) is price relative to base currency
        # In MD urt is how many base units per 1 unit of this currency.
        # Wait, usually urt is 1/rate.
        # Let's check sample data again.
        # TWD (base) has rate 1.0.
        # USD has rate 0.033... (TWD per 1 USD?) No, that would be 30.
        # Usually rate is how many units per 1 base unit.
        # NT$ 1.0 = USD 0.033. So 1 Base = 0.033 USD.
        # urt = User Rate. 
        # In MD sample:
        # USD id: 87970f73-aeef-4693-9a9f-e56e1c45884f
        # csnap for USD has urt: 0.03220249138616486
        # This means 1 Base (TWD) = 0.0322 USD.
        # So price of TWD in USD is 0.0322.
        # Price of USD in TWD is 1 / 0.0322 = 31.05.
        
        # Fava price directive: DATE price CURRENCY AMOUNT TARGET_CURRENCY
        # 2026-02-13 price USD 31.42 TWD
        
        # If we want price of USD in TWD:
        # urt_base = 1.0
        # urt_usd = 0.0322
        # Price = urt_base / urt_usd = 31.05
        
        # For simplicity, let's just store the urt as the 'price' and handle it in exporter.
        urt = float(snap_raw.get('urt', 0))
        if urt == 0:
            return
            
        self.price_snapshots.append(PriceSnapshot(
            currency=curr,
            date=date,
            price=urt
        ))

    def _import_budget(self, budget_raw: Dict[str, Any]) -> None:
        catid = UUID(budget_raw['catid'])
        if catid not in self.accounts:
            return
            
        acct = self.accounts[catid]
        dt_str = budget_raw.get('intstart')
        if not dt_str:
            return
        date = datetime.strptime(dt_str, "%Y%m%d")
        
        amt = int(budget_raw.get('amt', 0))
        interval = int(budget_raw.get('interval', 0))
        
        self.budget_items.append(BudgetItem(
            account=acct,
            date=date,
            amount=amt,
            interval=interval
        ))

    def get_currency(self, id_val: UUID) -> Currency:
        curr = self.currencies.get(id_val)
        if not curr:
            raise MoneydanceError("currency not exist")
        return curr

    def get_account(self, id_val: UUID) -> Account:
        acct = self.accounts.get(id_val)
        if not acct:
            raise MoneydanceError("account not exist")
        return acct

    def _new_root_account(self, acct_raw: Dict[str, Any]) -> Account:
        currid = UUID(acct_raw['currid'])
        curr = self.get_currency(currid)
        return Account(
            name=acct_raw['name'],
            currency=curr,
            initial=0,
            comment="",
            info=None
        )

    def _new_account(self, acct_raw: Dict[str, Any], parent: Account) -> Account:
        acct_type = acct_raw.get('type')
        currid = UUID(acct_raw['currid'])
        currency = self.get_currency(currid)
        name = acct_raw['name']
        comment = acct_raw.get('comment', "")
        initial = int(acct_raw.get('sbal', 0))

        if acct_type == 'b':
            info = BankInfo(
                parent=parent,
                bank_name=acct_raw.get('bank_name', ""),
                account_number=acct_raw.get('bank_account_number', "")
            )
        elif acct_type == 'c':
            info = CreditCardInfo(
                parent=parent,
                bank_name=acct_raw.get('bank_name', "")
            )
        elif acct_type == 'v':
            info = InvestmentInfo(
                parent=parent,
                account_number=acct_raw.get('invst_account_number', "")
            )
        elif acct_type == 'a':
            info = AssetInfo(parent=parent)
        elif acct_type == 'l':
            info = LiabilityInfo(parent=parent)
        elif acct_type == 'o':
            init_p = int(acct_raw.get('init_principal', 0))
            info = LoanInfo(parent=parent, init_principal=init_p)
        elif acct_type == 'i':
            info = IncomeInfo(parent=parent)
        elif acct_type == 'e':
            info = ExpenseInfo(parent=parent)
        elif acct_type == 's':
            info = SecurityInfo(
                parent=parent,
                sec_type=acct_raw.get('sec_type', ""),
                broker=acct_raw.get('broker', "")
            )
        else:
            raise MoneydanceError(f"Unknown account type: {acct_type}")

        return Account(
            name=name,
            currency=currency,
            initial=initial,
            comment=comment,
            info=info
        )
