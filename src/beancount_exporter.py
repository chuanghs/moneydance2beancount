import os
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

# 1. Load legacy globals and initialize mapper defaults via ExportConfig
config = ExportConfig.load_from_yaml()
COMMODITY_MAP: Dict[str, str] = config.commodity_map
GLOBAL_SETTINGS: Dict[str, any] = config.global_settings
DEFAULT_OPERATING_CURRENCIES = ["TWD", "USD", "EUR"]

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

def full_export(db: Database, operating_currencies: Optional[List[str]] = None, ignore_future: Optional[bool] = None, cutoff_date: Optional[str] = None) -> str:
    if operating_currencies is None:
        operating_currencies = []
    cfg = ExportConfig.load_from_yaml()
    if operating_currencies:
        cfg.operating_currencies = operating_currencies
    if ignore_future is not None:
        cfg.ignore_future = ignore_future
    if cutoff_date is not None:
        cfg.cutoff_date = cutoff_date
    exporter = BeancountExporter(db, cfg)
    return exporter.export()

def full_multi_export(db: Database, operating_currencies: List[str], output_dir: str, ignore_future: Optional[bool] = None, cutoff_date: Optional[str] = None) -> None:
    cfg = ExportConfig.load_from_yaml()
    if operating_currencies:
        cfg.operating_currencies = operating_currencies
    if ignore_future is not None:
        cfg.ignore_future = ignore_future
    if cutoff_date is not None:
        cfg.cutoff_date = cutoff_date
    exporter = BeancountExporter(db, cfg)
    exporter.export_multi(output_dir)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Moneydance to Beancount Exporter")
    parser.add_argument("moneydance_json", help="Path to Moneydance exported JSON file")
    
    # Legacy positional parameters for compatibility
    parser.add_argument("legacy_base_currencies", nargs="?", default=None, help="Legacy base currencies list")
    parser.add_argument("legacy_output_dir", nargs="?", default=None, help="Legacy output directory")
    
    # Optional parameters
    parser.add_argument("-c", "--base-currencies", help="Comma-separated list of operating currencies")
    parser.add_argument("-o", "--output-dir", help="Output directory for multi-file export")
    parser.add_argument("-i", "--ignore-future", action="store_true", default=None, help="Ignore future records")
    parser.add_argument("-d", "--cutoff-date", help="Ignore records after this date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # 1. Load config from YAML
    cfg = ExportConfig.load_from_yaml()
    
    # 2. Apply CLI overrides
    # Resolve base currencies
    base_currencies_str = args.base_currencies or args.legacy_base_currencies
    if base_currencies_str:
        cfg.operating_currencies = [c.strip() for c in base_currencies_str.split(",") if c.strip()]
        
    # Resolve output directory
    output_dir = args.output_dir or args.legacy_output_dir
    
    # Resolve ignore_future flag
    if args.ignore_future is not None:
        cfg.ignore_future = args.ignore_future
        
    # Resolve cutoff_date option
    if args.cutoff_date is not None:
        cfg.cutoff_date = args.cutoff_date
        
    # Load database
    with open(args.moneydance_json, "r") as f:
        data = f.read()
        
    loaded_db = Database.load(data)
    
    # Perform export
    exporter = BeancountExporter(loaded_db, cfg)
    if output_dir:
        exporter.export_multi(output_dir)
        print(f";; Multi-file export complete. Files generated in: {output_dir}")
    else:
        print(exporter.export())
