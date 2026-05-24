import unittest
from datetime import datetime
from src.models import Account, Currency, BankInfo, ExpenseInfo, Transaction, Split, Status, PriceSnapshot, BudgetItem, AssetInfo, CreditCardInfo, InvestmentInfo, SecurityInfo
from src.beancount_exporter import (
    export_accounts, export_transactions, export_prices, export_budgets, 
    AccountRegistry, get_beancount_path, export_options
)

class TestExport(unittest.TestCase):
    def setUp(self):
        self.usd = Currency(code="USD", rate=1.0, decimal=2)
        self.root = Account(name="Personal Finances", currency=self.usd, initial=0, info=None)

    def test_export_options(self):
        # Test default options
        output_default = export_options(self.root, [])
        self.assertIn('option "title" "Personal Finances"', output_default)
        # Note: These may depend on local commodity_map.yaml if not mocked
        self.assertIn('option "operating_currency"', output_default)

        # Test specific currencies
        output_custom = export_options(self.root, ["USD", "JPY"])
        self.assertIn('option "operating_currency" "USD"', output_custom)
        self.assertIn('option "operating_currency" "JPY"', output_custom)

    def test_export_accounts(self):
        checking = Account(
            name="Chase Checking",
            currency=self.usd,
            initial=100000, # $1000.00
            comment="Main account",
            info=BankInfo(parent=self.root)
        )
        cash = Account(
            name="現金",
            currency=self.usd,
            initial=5000,
            info=AssetInfo(parent=self.root)
        )
        card = Account(
            name="Visa",
            currency=self.usd,
            initial=0,
            info=CreditCardInfo(parent=self.root)
        )
        
        account_paths = {}
        for a in [checking, cash, card]:
            account_paths[id(a)] = get_beancount_path(a)
            
        output = export_accounts([checking, cash, card], account_paths, start_date="2026-01-01")
        
        self.assertIn('2026-01-01 open Equity:OpeningBalances', output)
        self.assertIn('2026-01-01 open Assets:Bank:ChaseChecking USD', output)
        self.assertIn('2026-01-01 open Assets:Cash:現金 USD', output)
        self.assertIn('2026-01-01 open Liabilities:Card:Visa USD', output)
        self.assertIn('md_name: "Chase Checking"', output)
        self.assertIn('comment: "Main account"', output)
        
        # Opening balance transaction
        self.assertIn('2026-01-01 * "Opening Balance"', output)
        self.assertIn('Assets:Bank:ChaseChecking  1000 USD', output)
        self.assertIn('Equity:OpeningBalances', output)

    def test_export_transactions(self):
        checking = Account(name="Checking", currency=self.usd, initial=0, info=BankInfo(parent=self.root))
        dining = Account(name="Dining", currency=self.usd, initial=0, info=ExpenseInfo(parent=self.root))
        
        # Simple transaction (Spending money)
        # MD reality: pamt is negative, samt is positive
        txn = Transaction(
            giver=checking,
            description="Lunch",
            date=datetime(2026, 5, 21),
            status=Status.CLEARED,
            splits=[
                Split(
                    receiver=dining,
                    given_amount=2500,  # samt: +25.00 to Expenses
                    received_amount=-2500, # pamt: -25.00 from Assets
                    description="Lunch"
                )
            ]
        )
        # We need the paths to be consistent
        account_paths = {
            id(checking): "Assets:Bank:Checking",
            id(dining): "Expenses:Dining"
        }

        output = export_transactions([txn], account_paths)

        self.assertIn('2026-05-21 * "Lunch"', output)
        self.assertIn('Assets:Bank:Checking  -25.00 USD', output)
        self.assertIn('Expenses:Dining   25 USD', output)

    def test_export_multi_currency(self):
        twd = Currency(code="TWD", rate=30.0, decimal=2)
        usd_account = Account(name="USD Checking", currency=self.usd, initial=0, info=BankInfo(parent=self.root))
        twd_account = Account(name="TWD Savings", currency=twd, initial=0, info=BankInfo(parent=self.root))
        
        # Transfer $100 USD to TWD and get $3000 TWD
        # MD reality: pamt (giver) is -100.00 USD, samt (receiver) is +3000.00 TWD
        txn = Transaction(
            giver=usd_account,
            description="Transfer to TWD",
            date=datetime(2026, 5, 21),
            status=Status.CLEARED,
            splits=[
                Split(
                    receiver=twd_account,
                    given_amount=300000, # samt: +3000.00 TWD
                    received_amount=-10000, # pamt: -100.00 USD
                    description="Transfer"
                )
            ]
        )
        
        account_paths = {
            id(usd_account): "Assets:Bank:USDChecking",
            id(twd_account): "Assets:Bank:TWDSavings"
        }
        
        output = export_transactions([txn], account_paths)
        
        self.assertIn('2026-05-21 * "Transfer to TWD"', output)
        self.assertIn('Assets:Bank:USDChecking  -100.00 USD', output)
        self.assertIn('Assets:Bank:TWDSavings   3000 TWD @@ 100.00 USD', output)

    def test_export_prices(self):
        usd = Currency(code="USD", rate=1.0, decimal=2)
        # urt is 0.03333333 (meaning 1 TWD = 0.03333333 USD)
        # Beancount price should be 1 / 0.03333333 = 30.0 TWD
        usd_snapshot = PriceSnapshot(
            currency=usd,
            date=datetime(2026, 5, 21),
            price=0.03333333
        )
        
        # Snapshot for commodity with empty code but valid ticker (common in Taiwan stocks)
        tw_stock = Currency(code="", rate=1.0, decimal=4, ticker="0050.TW", name="元大台灣50")
        tw_snapshot = PriceSnapshot(
            currency=tw_stock,
            date=datetime(2026, 5, 22),
            price=0.010 # 1 TWD = 0.010 YUANTA_TW50 -> 1 YUANTA_TW50 = 100 TWD
        )
        
        # Should now accept base_currency_code instead of operating_currencies list
        output = export_prices([usd_snapshot, tw_snapshot], base_currency_code="TWD")
        self.assertIn('2026-05-21 price USD  30.00000300 TWD', output)
        self.assertIn('2026-05-22 price YUANTA_TW50  100.00000000 TWD', output)

    def test_export_budgets(self):
        dining = Account(name="Dining", currency=self.usd, initial=0, info=ExpenseInfo(parent=self.root))
        budget = BudgetItem(
            account=dining,
            date=datetime(2026, 1, 1),
            amount=50000, # $500.00
            interval=6 # Monthly
        )
        
        account_paths = {id(dining): "Expenses:Dining"}
        output = export_budgets([budget], account_paths)
        
        self.assertIn('2026-01-01 custom "budget" Expenses:Dining "monthly" 500.00 USD', output)

    def test_database_base_currency_detection(self):
        # Verify that Database.load identifies the currency with isbase: "y"
        db_data = {
            "all_items": [
                {"obj_type": "curr", "id": "00000000-0000-0000-0000-000000000001", "currid": "TWD", "dec": "0", "rate": "1.0", "isbase": "y"},
                {"obj_type": "curr", "id": "00000000-0000-0000-0000-000000000002", "currid": "USD", "dec": "2", "rate": "0.033", "isbase": "n"},
                {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000003", "name": "Root", "type": "r", "currid": "00000000-0000-0000-0000-000000000001"}
            ]
        }
        import json
        from src.database import Database
        db = Database.load(json.dumps(db_data))
        
        self.assertEqual(db.base_currency_code, "TWD")

    def test_multi_file_export(self):
        import tempfile
        import shutil
        import os
        from src.beancount_exporter import full_multi_export
        from src.database import Database
        import json

        # Create a temp directory
        out_dir = tempfile.mkdtemp()
        try:
            # Setup mock database data
            db_data = {
                "all_items": [
                    {"obj_type": "curr", "id": "00000000-0000-0000-0000-000000000001", "currid": "TWD", "dec": "0", "rate": "1.0", "isbase": "y"},
                    {"obj_type": "curr", "id": "00000000-0000-0000-0000-000000000002", "currid": "AAPL", "dec": "4", "rate": "0.003", "ticker": "AAPL"},
                    # Root
                    {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000003", "name": "Root", "type": "r", "currid": "00000000-0000-0000-0000-000000000001"},
                    # Cash (Daily)
                    {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000004", "name": "現金", "type": "b", "currid": "00000000-0000-0000-0000-000000000001", "parentid": "00000000-0000-0000-0000-000000000003"},
                    # Investment
                    {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000005", "name": "ETrade", "type": "v", "currid": "00000000-0000-0000-0000-000000000001", "parentid": "00000000-0000-0000-0000-000000000003"},
                    {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000006", "name": "AAPL", "type": "s", "currid": "00000000-0000-0000-0000-000000000002", "parentid": "00000000-0000-0000-0000-000000000005"},
                    # Expense
                    {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000007", "name": "Food", "type": "e", "currid": "00000000-0000-0000-0000-000000000001", "parentid": "00000000-0000-0000-0000-000000000003"},
                    # Transactions
                    {
                        "obj_type": "txn", "id": "t1", "dt": "20260523", "desc": "Lunch", "acctid": "00000000-0000-0000-0000-000000000004",
                        "0.acctid": "00000000-0000-0000-0000-000000000007", "0.pamt": "-100", "0.samt": "100"
                    }
                ]
            }
            db = Database.load(json.dumps(db_data))
            full_multi_export(db, ["TWD"], out_dir)

            # 1. Check if files exist
            for f in ["main.beancount", "commodity.beancount", "daily.beancount", "investment.beancount"]:
                self.assertTrue(os.path.exists(os.path.join(out_dir, f)))

            # 2. Verify daily.beancount contains the "Lunch" transaction (because of "現金")
            with open(os.path.join(out_dir, "daily.beancount"), "r") as f:
                content = f.read()
                self.assertIn('"Lunch"', content)
                self.assertIn('open Assets:Bank:現金 TWD', content) 

            # 3. Verify investment.beancount contains AAPL definition
            with open(os.path.join(out_dir, "investment.beancount"), "r") as f:
                content = f.read()
                self.assertIn('open Assets:Investment:ETrade AAPL,TWD "FIFO"', content)

            # 4. Verify main.beancount contains includes and opening balance definition
            with open(os.path.join(out_dir, "main.beancount"), "r") as f:
                content = f.read()
                self.assertIn('include "commodity.beancount"', content)
                self.assertIn('open Equity:OpeningBalances', content)

        finally:
            shutil.rmtree(out_dir)

    def test_export_escaping(self):
        # 1. Transaction Description Escaping
        checking = Account(name="Checking", currency=self.usd, initial=0, info=BankInfo(parent=self.root))
        dining = Account(name="Dining", currency=self.usd, initial=0, info=ExpenseInfo(parent=self.root))
        
        txn = Transaction(
            giver=checking,
            description='Lunch at "The Mall"',
            date=datetime(2026, 5, 21),
            status=Status.CLEARED,
            splits=[
                Split(
                    receiver=dining,
                    given_amount=2500,
                    received_amount=-2500,
                    description='Lunch at "The Mall"'
                )
            ]
        )
        account_paths = {
            id(checking): "Assets:Bank:Checking",
            id(dining): "Expenses:Dining"
        }
        output_txn = export_transactions([txn], account_paths)
        self.assertIn('2026-05-21 * "Lunch at \\"The Mall\\""', output_txn)

        # 2. Account Metadata Escaping
        slashed_account = Account(
            name='C:\\Users',
            currency=self.usd,
            initial=0,
            comment='Comment with "quotes" and \\slashes',
            info=BankInfo(parent=self.root)
        )
        account_paths = {
            id(slashed_account): get_beancount_path(slashed_account)
        }
        output_acct = export_accounts([slashed_account], account_paths)
        self.assertIn('open Assets:Bank:CUsers USD', output_acct) # C:\Users -> CUsers after normalization
        self.assertIn('md_name: "C:\\\\Users"', output_acct)
        self.assertIn('comment: "Comment with \\"quotes\\" and \\\\slashes"', output_acct)

    def test_export_investment_collapsing(self):
        investment_acct = Account(
            name="Schwab",
            currency=self.usd,
            initial=100000, # $1000.00 cash
            info=InvestmentInfo(parent=self.root)
        )
        vt_curr = Currency(code="VT", rate=1.0, decimal=4, ticker="VT", name="Vanguard Total World")
        vt_security = Account(
            name="Vanguard Total World",
            currency=vt_curr,
            initial=1000000, # 100.0000 shares
            info=SecurityInfo(parent=investment_acct)
        )
        
        # Test get_beancount_path collapsing
        self.assertEqual(get_beancount_path(investment_acct), "Assets:Investment:Schwab")
        self.assertEqual(get_beancount_path(vt_security), "Assets:Investment:Schwab")
        
        # Test export_accounts aggregation
        account_paths = {
            id(investment_acct): get_beancount_path(investment_acct),
            id(vt_security): get_beancount_path(vt_security)
        }
        output = export_accounts([investment_acct, vt_security], account_paths)
        
        # Should only have one open directive for the path
        self.assertIn('open Assets:Investment:Schwab USD,VT', output)
        self.assertEqual(output.count('open Assets:Investment:Schwab'), 1)
        
        # Should have two opening balance transactions
        self.assertIn('Assets:Investment:Schwab  1000 USD', output)
        self.assertIn('Assets:Investment:Schwab  100 VT', output)

    def test_export_security_initial_balance_cost(self):
        investment_acct = Account(name="Schwab", currency=self.usd, initial=0, info=InvestmentInfo(parent=self.root))
        vt_curr = Currency(code="VT", rate=1.0, decimal=4, ticker="VT")
        vt_security = Account(name="VT", currency=vt_curr, initial=1000000, info=SecurityInfo(parent=investment_acct))
        
        account_paths = {
            id(investment_acct): "Assets:Investment:Schwab",
            id(vt_security): "Assets:Investment:Schwab"
        }
        
        output = export_accounts([investment_acct, vt_security], account_paths)
        
        # Should include FIFO booking policy
        self.assertIn('open Assets:Investment:Schwab USD,VT "FIFO"', output)
        
        # Should have costed initial balance for security
        self.assertIn('Assets:Investment:Schwab  100 VT {{ 0 USD }}', output)

    def test_full_export(self):
        # Verify that full_export generates all sections including OPTIONS
        db_data = {
            "all_items": [
                {"obj_type": "acct", "id": "00000000-0000-0000-0000-000000000001", "name": "My Ledger", "type": "r", "currid": "00000000-0000-0000-0000-000000000002"},
                {"obj_type": "curr", "id": "00000000-0000-0000-0000-000000000002", "currid": "USD", "dec": "2", "rate": "1.0"}
            ]
        }
        from src.database import Database
        import json
        db = Database.load(json.dumps(db_data))
        
        from src.beancount_exporter import full_export
        output = full_export(db, ["USD", "TWD"])
        
        self.assertIn(';; === OPTIONS ===', output)
        self.assertIn('option "title" "My Ledger"', output)
        self.assertIn('option "operating_currency" "USD"', output)
        self.assertIn('option "operating_currency" "TWD"', output)
        self.assertIn(';; === COMMODITIES ===', output)
        self.assertIn(';; === ACCOUNTS ===', output)
        self.assertIn(';; === TRANSACTIONS ===', output)

    def test_export_integration(self):
        import os
        from src.database import Database
        
        json_path = os.path.join(os.path.dirname(__file__), "..", "src", "test_account_import.json")
        with open(json_path, "r") as f:
            json_data = f.read()
        
        db = Database.load(json_data)
        
        # Collect paths
        registry = AccountRegistry()
        account_paths = {}
        for acct in db.accounts.values():
            raw_path = get_beancount_path(acct)
            unique_path = registry.get_unique_path(raw_path)
            account_paths[id(acct)] = unique_path
            
        # Export everything
        out_accounts = export_accounts(list(db.accounts.values()), account_paths)
        out_transactions = export_transactions(db.transactions, account_paths)
        
        self.assertIn('open Assets:Bank:Checking USD', out_accounts)
        self.assertIn('open Expenses:Automotive USD', out_accounts)
        self.assertIn('2018-02-06 ! "Transfer From Loan"', out_transactions)
        self.assertIn('Assets:Bank:Checking  200000.00 USD', out_transactions)

    def test_commodity_translation_integration(self):
        # Verify that digit tickers and Chinese names are translated/sanitized in the accounts output
        cht_curr = Currency(code="CHT_ID", ticker="2412", name="中華電信", rate=1.0, decimal=2)
        invest_acct = Account(name="Invest", currency=self.usd, initial=0, info=InvestmentInfo(parent=self.root))
        cht_security = Account(name="中華電信", currency=cht_curr, initial=1000, info=SecurityInfo(parent=invest_acct))
        
        account_paths = {
            id(invest_acct): "Assets:Investment:Invest",
            id(cht_security): "Assets:Investment:Invest"
        }
        
        output = export_accounts([invest_acct, cht_security], account_paths)
        
        # Should use the manual translation CH_TELECOM from commodity_map.yaml
        self.assertIn('open Assets:Investment:Invest CH_TELECOM,USD', output)
        self.assertIn('Assets:Investment:Invest  10 CH_TELECOM', output)

    def test_security_purchase_cost_notation(self):
        # Setup: Brokerage account (TWD) and Security (YUANTA_TW50)
        twd = Currency(code="TWD", rate=1.0, decimal=0)
        tw50_curr = Currency(code="TW50_ID", ticker="0050", name="YUANTA_TW50", rate=1.0, decimal=4)
        
        brokerage = Account(name="Brokerage", currency=twd, initial=0, info=InvestmentInfo(parent=self.root))
        tw50_sec = Account(name="YUANTA_TW50", currency=tw50_curr, initial=0, info=SecurityInfo(parent=brokerage))
        
        account_paths = {
            id(brokerage): "Assets:Investment:Brokerage",
            id(tw50_sec): "Assets:Investment:Brokerage"
        }
        
        # Transaction: Buy 1000 shares for 96400 TWD
        # pamt is -96400 (spent), samt is 10000000 (received 1000.0000 shares)
        txn = Transaction(
            giver=brokerage,
            description="Buy TW50",
            splits=[
                Split(receiver=tw50_sec, given_amount=10000000, received_amount=-96400)
            ],
            date=datetime(2026, 5, 23),
            status=Status.NONE
        )
        
        output = export_transactions([txn], account_paths)
        
        # Should use { } for security purchase (unit cost) and strip trailing zeros
        # 96400 TWD / 1000 shares = 96.4 TWD
        self.assertIn('  Assets:Investment:Brokerage   1000 SYM_0050 { 96.400000 TWD }', output)

    def test_security_sell_lot_matching(self):
        # Setup: Brokerage account (USD) and Security (VT)
        usd = Currency(code="USD", rate=1.0, decimal=2)
        vt_curr = Currency(code="VT_ID", ticker="VT", name="VT", rate=1.0, decimal=4)
        
        brokerage = Account(name="Brokerage", currency=usd, initial=0, info=InvestmentInfo(parent=self.root))
        vt_sec = Account(name="VT", currency=vt_curr, initial=0, info=SecurityInfo(parent=brokerage))
        
        account_paths = {
            id(brokerage): "Assets:Investment:Brokerage",
            id(vt_sec): "Assets:Investment:Brokerage"
        }
        
        # Transaction: Sell 5 shares for 600 USD
        # samt is -50000 (sold 5.0000 shares), pamt is 60000 (received 600.00 USD)
        txn = Transaction(
            giver=brokerage,
            description="Sell VT",
            splits=[
                Split(receiver=vt_sec, given_amount=-50000, received_amount=60000)
            ],
            date=datetime(2026, 5, 23),
            status=Status.NONE
        )
        
        output = export_transactions([txn], account_paths)
        
        # Should use {} @@ for security sell and add balancing posting
        self.assertIn('  Assets:Investment:Brokerage   -5 VT {} @@ 600.00 USD', output)
        self.assertIn('  Equity:OpeningBalances USD', output)

if __name__ == "__main__":
    unittest.main()
