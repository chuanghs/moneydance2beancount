import os
import yaml
from typing import Optional, List, Dict
from src.database import Database
from src.config import ExportConfig
from src.models import (
    Account, Currency, BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LiabilityInfo, LoanInfo, IncomeInfo, ExpenseInfo, SecurityInfo,
    Transaction, Split, Status, PriceSnapshot, BudgetItem
)
from src.exporter.beancount.mapper import (
    normalize_commodity as _normalize_commodity,
    get_commodity_code as _get_commodity_code,
    normalize_name as _normalize_name,
    get_beancount_path as _get_beancount_path,
    AccountRegistry as _AccountRegistry,
    DEFAULT_COMMODITY_MAP as _DEFAULT_COMMODITY_MAP
)
from src.exporter.beancount.router import (
    get_file_for_account as _get_file_for_account,
    get_file_for_transaction as _get_file_for_transaction
)
from src.exporter.beancount import formatter
from src.exporter.beancount.exporter import BeancountExporter

# 1. Load legacy globals and initialize mapper defaults
COMMODITY_MAP: Dict[str, str] = {}
GLOBAL_SETTINGS: Dict[str, any] = {}
DEFAULT_OPERATING_CURRENCIES = ["TWD", "USD", "EUR"]

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

_DEFAULT_COMMODITY_MAP.update(COMMODITY_MAP)

# 2. Expose the exact same functions and classes for backwards compatibility
escape_beancount_string = formatter.escape_beancount_string
format_amount = formatter.format_amount
normalize_commodity = _normalize_commodity
normalize_name = _normalize_name
AccountRegistry = _AccountRegistry
get_file_for_account = _get_file_for_account
get_file_for_transaction = _get_file_for_transaction
get_beancount_path = _get_beancount_path

def get_commodity_code(currency: Currency) -> str:
    return _get_commodity_code(currency, COMMODITY_MAP)

def export_options(root_account: Account, operating_currencies: List[str]) -> str:
    return formatter.export_options(root_account, operating_currencies, GLOBAL_SETTINGS)

def export_commodities(currencies: List[Currency], start_date: str = "1970-01-01") -> str:
    return formatter.export_commodities(currencies, start_date, COMMODITY_MAP)

def export_budgets(budgets: List[BudgetItem], account_paths: Dict[int, str]) -> str:
    return formatter.export_budgets(budgets, account_paths, COMMODITY_MAP)

def export_prices(snapshots: List[PriceSnapshot], base_currency_code: str) -> str:
    return formatter.export_prices(snapshots, base_currency_code, COMMODITY_MAP)

def export_accounts(accounts: List[Account], account_paths: Dict[int, str], start_date: str = "1970-01-01", target_file: Optional[str] = None) -> str:
    return formatter.export_accounts(accounts, account_paths, start_date, target_file, COMMODITY_MAP)

def export_transactions(transactions: List[Transaction], account_paths: Dict[int, str], target_file: Optional[str] = None) -> str:
    return formatter.export_transactions(transactions, account_paths, target_file, COMMODITY_MAP)

def full_export(db: Database, operating_currencies: Optional[List[str]] = None) -> str:
    if operating_currencies is None:
        operating_currencies = []
    config = ExportConfig(
        operating_currencies=operating_currencies,
        commodity_map=COMMODITY_MAP,
        global_settings=GLOBAL_SETTINGS
    )
    exporter = BeancountExporter(db, config)
    return exporter.export()

def full_multi_export(db: Database, operating_currencies: List[str], output_dir: str) -> None:
    config = ExportConfig(
        operating_currencies=operating_currencies,
        commodity_map=COMMODITY_MAP,
        global_settings=GLOBAL_SETTINGS
    )
    exporter = BeancountExporter(db, config)
    exporter.export_multi(output_dir)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.beancount_exporter <moneydance_json> [base_currencies_comma_separated] [output_dir]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    base_curr_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    operating_currencies_arg = [c.strip() for c in base_curr_arg.split(",")] if base_curr_arg else []
    
    output_dir_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    with open(json_path, "r") as f:
        data = f.read()
        
    loaded_db = Database.load(data)
    
    if output_dir_arg:
        full_multi_export(loaded_db, operating_currencies_arg, output_dir_arg)
        print(f";; Multi-file export complete. Files generated in: {output_dir_arg}")
    else:
        print(full_export(loaded_db, operating_currencies_arg))
