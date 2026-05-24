import os
from src.database import Database
from src.config import ExportConfig
from src.exporter.base import BaseExporter
from src.exporter.beancount.mapper import AccountRegistry, get_beancount_path
from src.exporter.beancount.formatter import (
    export_options, export_commodities, export_accounts,
    export_prices, export_budgets, export_transactions
)

class BeancountExporter(BaseExporter):
    def export(self) -> str:
        registry = AccountRegistry()
        account_paths = {}
        raw_to_unique = {}
        
        for acct in self.db.accounts.values():
            raw_path = get_beancount_path(acct)
            if raw_path not in raw_to_unique:
                raw_to_unique[raw_path] = registry.get_unique_path(raw_path)
            account_paths[id(acct)] = raw_to_unique[raw_path]
            
        sections = []
        
        # Options
        root_account = next((a for a in self.db.accounts.values() if a.info is None), None)
        sections.append(";; === OPTIONS ===")
        sections.append(export_options(root_account, self.config.operating_currencies, self.config.global_settings))
        sections.append("")
        
        # Commodities
        sections.append(";; === COMMODITIES ===")
        sections.append(export_commodities(list(self.db.currencies.values()), self.config.start_date, self.config.commodity_map))
        sections.append("")
        
        # Accounts
        sections.append(";; === ACCOUNTS ===")
        sections.append(export_accounts(list(self.db.accounts.values()), account_paths, self.config.start_date, commodity_map=self.config.commodity_map))
        sections.append("")
        
        # Prices
        if self.db.price_snapshots:
            sections.append(";; === PRICES ===")
            sections.append(export_prices(self.db.price_snapshots, self.db.base_currency_code, self.config.commodity_map))
            sections.append("")
            
        # Budgets
        if self.db.budget_items:
            sections.append(";; === BUDGETS ===")
            sections.append(export_budgets(self.db.budget_items, account_paths, self.config.commodity_map))
            sections.append("")
            
        # Transactions
        sections.append(";; === TRANSACTIONS ===")
        sections.append(export_transactions(self.db.transactions, account_paths, commodity_map=self.config.commodity_map))
        
        return "\n".join(sections)

    def export_multi(self, output_dir: str) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        registry = AccountRegistry()
        account_paths = {}
        raw_to_unique = {}
        
        for acct in self.db.accounts.values():
            raw_path = get_beancount_path(acct)
            if raw_path not in raw_to_unique:
                raw_to_unique[raw_path] = registry.get_unique_path(raw_path)
            account_paths[id(acct)] = raw_to_unique[raw_path]

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
            f.write(export_commodities(list(self.db.currencies.values()), self.config.start_date, self.config.commodity_map))
            
        # prices.beancount
        with open(os.path.join(output_dir, "prices.beancount"), "w", encoding="utf-8") as f:
            f.write(";; === PRICES ===\n\n")
            if self.db.price_snapshots:
                f.write(export_prices(self.db.price_snapshots, self.db.base_currency_code, self.config.commodity_map))
                
        # Category files (Accounts + Transactions)
        for cat_file in ["assets.beancount", "investment.beancount", "liability.beancount", "daily.beancount"]:
            with open(os.path.join(output_dir, cat_file), "w", encoding="utf-8") as f:
                f.write(f";; === {cat_file.upper().replace('.BEANCOUNT', '')} ===\n\n")
                f.write(export_accounts(list(self.db.accounts.values()), account_paths, self.config.start_date, target_file=cat_file, commodity_map=self.config.commodity_map))
                f.write("\n\n")
                f.write(export_transactions(self.db.transactions, account_paths, target_file=cat_file, commodity_map=self.config.commodity_map))
                
        # main.beancount
        with open(os.path.join(output_dir, "main.beancount"), "w", encoding="utf-8") as f:
            root_account = next((a for a in self.db.accounts.values() if a.info is None), None)
            f.write(";; === OPTIONS ===\n")
            f.write(export_options(root_account, self.config.operating_currencies, self.config.global_settings))
            f.write("\n\n")
            
            for cat in categories:
                f.write(f'include "{cat}"\n')
            f.write("\n")
            
            f.write(";; === MAIN ACCOUNTS (Income/Expenses) ===\n\n")
            f.write(export_accounts(list(self.db.accounts.values()), account_paths, self.config.start_date, target_file="main.beancount", commodity_map=self.config.commodity_map))
            f.write("\n\n")
            f.write(";; === MAIN TRANSACTIONS ===\n\n")
            f.write(export_transactions(self.db.transactions, account_paths, target_file="main.beancount", commodity_map=self.config.commodity_map))
