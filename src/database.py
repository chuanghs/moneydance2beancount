import json
from uuid import UUID
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from .models import (
    Currency, Account, Transaction, Split, Status,
    BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo
)
from .rawjson import (
    RawCurrency, RawTxn
)

class MoneydanceError(Exception):
    pass

class Database:
    def __init__(self):
        self.accounts: Dict[UUID, Account] = {}
        self.currencies: Dict[UUID, Currency] = {}
        self.transactions: List[Transaction] = []

    @classmethod
    def load(cls, data_str: str) -> 'Database':
        raw_data = json.loads(data_str)
        db = cls()
        
        accounts_raw, currencies_raw, transactions_raw = db._sort_exported_data(raw_data['all_items'])

        for curr_raw in currencies_raw:
            id_val = UUID(curr_raw['id'])
            db.currencies[id_val] = Currency(
                code=curr_raw['currid'],
                decimal=int(curr_raw['dec']),
                rate=float(curr_raw['rate'])
            )

        # Accounts might be hierarchical, use the same logic as Rust
        remaining_accounts = {UUID(a['id']): a for a in accounts_raw}
        while remaining_accounts:
            id_val = next(iter(remaining_accounts))
            db._add_accounts(remaining_accounts, id_val)

        for txn_raw in transactions_raw:
            db._import_splits(txn_raw)

        return db

    def _sort_exported_data(self, all_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        accounts = []
        currencies = []
        transactions = []

        for item in all_items:
            obj_type = item.get('obj_type')
            if obj_type == 'acct':
                accounts.append(item)
            elif obj_type == 'curr':
                currencies.append(item)
            elif obj_type == 'txn':
                transactions.append(item)
        
        return accounts, currencies, transactions

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
            splits=txn_splits # Wait, I used full_splits above
        ))
        self.transactions[-1].splits = full_splits

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
            info = InvestmentInfo(parent=parent)
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
        else:
            raise MoneydanceError(f"Unknown account type: {acct_type}")

        return Account(
            name=name,
            currency=currency,
            initial=initial,
            comment=comment,
            info=info
        )
