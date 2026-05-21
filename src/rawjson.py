from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import UUID

@dataclass
class RawBankAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    comment: Optional[str] = None

@dataclass
class RawCreditCardAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None
    bank_name: Optional[str] = None

@dataclass
class RawInvestmentAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None

@dataclass
class RawAssetAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None

@dataclass
class RawLiabilityAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None

@dataclass
class RawLoanAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    init_principal: str
    comment: Optional[str] = None

@dataclass
class RawExpenseAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None

@dataclass
class RawIncomeAccount:
    id: UUID
    name: str
    parentid: UUID
    currid: UUID
    sbal: str
    comment: Optional[str] = None

@dataclass
class RawRootAccount:
    id: UUID
    name: str
    currid: UUID

@dataclass
class RawCurrency:
    id: UUID
    currid: str
    rate: str
    dec: str

@dataclass
class RawTxn:
    acctid: UUID
    pamt: str
    samt: str
    tags: str
    desc: str

    @classmethod
    def default(cls):
        return cls(
            acctid=UUID('00000000-0000-0000-0000-000000000000'),
            pamt="",
            samt="",
            tags="",
            desc=""
        )

@dataclass
class ExportedData:
    all_items: List[Dict[str, Any]]
