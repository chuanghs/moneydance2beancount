from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union
from datetime import datetime

class Status(Enum):
    NONE = "none"
    CLEARED = "cleared"
    RECONCILED = "reconciled"

@dataclass(frozen=True)
class Currency:
    code: str
    rate: float
    decimal: int
    ticker: str = ""
    name: str = ""
    md_id: str = ""
    parent_code: Optional[str] = None

@dataclass
class BankInfo:
    parent: 'Account'
    bank_name: str = ""
    account_number: str = ""

@dataclass
class CreditCardInfo:
    parent: 'Account'
    bank_name: str = ""

@dataclass
class InvestmentInfo:
    parent: 'Account'
    account_number: str = ""

@dataclass
class AssetInfo:
    parent: 'Account'

@dataclass
class LiabilityInfo:
    parent: 'Account'

@dataclass
class LoanInfo:
    parent: 'Account'
    init_principal: int

@dataclass
class IncomeInfo:
    parent: 'Account'

@dataclass
class ExpenseInfo:
    parent: 'Account'

@dataclass
class SecurityInfo:
    parent: 'Account'
    sec_type: str = ""
    broker: str = ""

AccountInfo = Union[
    BankInfo,
    CreditCardInfo,
    InvestmentInfo,
    AssetInfo,
    LiabilityInfo,
    LoanInfo,
    IncomeInfo,
    ExpenseInfo,
    SecurityInfo,
    None  # For Root
]

@dataclass
class Account:
    name: str
    currency: Currency
    initial: int
    comment: str = ""
    info: AccountInfo = None

@dataclass
class Split:
    receiver: Account
    given_amount: int
    received_amount: int
    tags: str = ""
    description: str = ""

@dataclass
class Transaction:
    giver: Account
    description: str
    splits: List[Split]
    date: datetime
    status: Status

@dataclass
class PriceSnapshot:
    currency: Currency
    date: datetime
    price: float # Relative to base currency

@dataclass
class BudgetItem:
    account: Account
    date: datetime
    amount: int
    interval: int # MD interval code (e.g., 6 for monthly)
