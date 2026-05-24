import unittest
import os
import tempfile
import datetime as dt_mod
from src.config import ExportConfig
from src.database import Database
from src.models import (
    Currency, Account, Transaction, Split, Status, PriceSnapshot, BudgetItem, BankInfo
)
from src.exporter.beancount.exporter import BeancountExporter

class TestConfigAndFiltering(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.usd = Currency(code="USD", rate=1.0, decimal=2)
        self.root = Account(name="Root", currency=self.usd, initial=0, info=None)
        self.checking = Account(name="Checking", currency=self.usd, initial=0, info=BankInfo(parent=self.root))

    def tearDown(self):
        # Clean up files in temp_dir
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_auto_scaffolding_creation(self):
        config_path = os.path.join(self.temp_dir, "test_scaffold.yaml")
        self.assertFalse(os.path.exists(config_path))
        
        # Load from nonexistent file triggers scaffolding
        config = ExportConfig.load_from_yaml(config_path)
        
        self.assertTrue(os.path.exists(config_path))
        self.assertFalse(config.ignore_future)
        self.assertEqual(config.operating_currencies, ["TWD", "USD", "EUR"])
        
        # Verify content template contains comments and translations block
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("ignore_future: false", content)
            self.assertIn("translations:", content)

    def test_load_yaml_values(self):
        config_path = os.path.join(self.temp_dir, "test_load.yaml")
        yaml_content = """
settings:
  operating_currencies: ["JPY", "USD"]
  ignore_future: true
  cutoff_date: "2026-05-25"
translations:
  "中華電信": "CH_TELECOM"
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
            
        config = ExportConfig.load_from_yaml(config_path)
        self.assertEqual(config.operating_currencies, ["JPY", "USD"])
        self.assertTrue(config.ignore_future)
        self.assertEqual(config.cutoff_date, "2026-05-25")
        self.assertEqual(config.commodity_map.get("中華電信"), "CH_TELECOM")

    def test_date_filtering_logic(self):
        # Create a database with past, today, and future transactions
        db = Database()
        db.base_currency_code = "USD"
        db.accounts = {id(self.root): self.root, id(self.checking): self.checking}
        
        today = dt_mod.datetime.now()
        yesterday = today - dt_mod.timedelta(days=1)
        tomorrow = today + dt_mod.timedelta(days=1)
        
        t_past = Transaction(giver=self.checking, description="Past", splits=[], date=yesterday, status=Status.NONE)
        t_today = Transaction(giver=self.checking, description="Today", splits=[], date=today, status=Status.NONE)
        t_future = Transaction(giver=self.checking, description="Future", splits=[], date=tomorrow, status=Status.NONE)
        db.transactions = [t_past, t_today, t_future]
        
        p_past = PriceSnapshot(currency=self.usd, date=yesterday, price=1.0)
        p_today = PriceSnapshot(currency=self.usd, date=today, price=1.0)
        p_future = PriceSnapshot(currency=self.usd, date=tomorrow, price=1.0)
        db.price_snapshots = [p_past, p_today, p_future]
        
        b_past = BudgetItem(account=self.checking, date=yesterday, amount=100, interval=6)
        b_today = BudgetItem(account=self.checking, date=today, amount=100, interval=6)
        b_future = BudgetItem(account=self.checking, date=tomorrow, amount=100, interval=6)
        db.budget_items = [b_past, b_today, b_future]
        
        # Test 1: No filtering
        config_none = ExportConfig(ignore_future=False)
        exporter_none = BeancountExporter(db, config_none)
        txns, prices, budgets = exporter_none._get_filtered_records()
        self.assertEqual(len(txns), 3)
        self.assertEqual(len(prices), 3)
        self.assertEqual(len(budgets), 3)
        
        # Test 2: Filter future (ignore_future=True)
        config_future = ExportConfig(ignore_future=True)
        exporter_future = BeancountExporter(db, config_future)
        txns, prices, budgets = exporter_future._get_filtered_records()
        # Today and yesterday should be kept (date-only comparison allows today), future filtered
        self.assertEqual(len(txns), 2)
        self.assertNotIn(t_future, txns)
        self.assertEqual(len(prices), 2)
        self.assertNotIn(p_future, prices)
        self.assertEqual(len(budgets), 2)
        self.assertNotIn(b_future, budgets)
        
        # Test 3: Specific cutoff date filtering (yesterday)
        config_cutoff = ExportConfig(cutoff_date=yesterday.strftime("%Y-%m-%d"))
        exporter_cutoff = BeancountExporter(db, config_cutoff)
        txns, prices, budgets = exporter_cutoff._get_filtered_records()
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0].description, "Past")

if __name__ == "__main__":
    unittest.main()
