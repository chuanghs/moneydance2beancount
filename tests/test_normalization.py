import unittest
from src.beancount_exporter import normalize_name, get_beancount_path, AccountRegistry, get_commodity_code, normalize_commodity
from src.models import Account, Currency, BankInfo, ExpenseInfo, IncomeInfo, InvestmentInfo, SecurityInfo, AssetInfo, CreditCardInfo

class TestNormalization(unittest.TestCase):
    def setUp(self):
        self.usd = Currency(code="USD", rate=1.0, decimal=2)

    def test_commodity_normalization(self):
        # Digit prefixing
        self.assertEqual(normalize_commodity("2412"), "SYM_2412")
        self.assertEqual(normalize_commodity("0050TW"), "SYM_0050TW")
        
        # Valid starts
        self.assertEqual(normalize_commodity("AAPL"), "AAPL")
        self.assertEqual(normalize_commodity("VT"), "VT")
        
        # Sanitization
        self.assertEqual(normalize_commodity("AAPL$"), "AAPL")
        self.assertEqual(normalize_commodity("my-ticker"), "MY-TICKER")

    def test_get_commodity_code_with_map(self):
        # With map (CH_TELECOM is mapped from "中華電信" in commodity_map.yaml)
        cht = Currency(code="CH_TELECOM_ID", ticker="2412", name="中華電信", rate=1.0, decimal=2)
        self.assertEqual(get_commodity_code(cht), "CH_TELECOM")

        # Without mapped name, falls back to ticker (digit prefixed)
        unmapped = Currency(code="OTHER", ticker="5387", name="Other", rate=1.0, decimal=2)
        self.assertEqual(get_commodity_code(unmapped), "SYM_5387")

    def test_camel_case(self):
        self.assertEqual(normalize_name("Food & Drink"), "FoodDrink")
        self.assertEqual(normalize_name("Chase Checking 123"), "ChaseChecking123")
        self.assertEqual(normalize_name("Amazon.com"), "AmazonCom")
        self.assertEqual(normalize_name("富邦(宇萱)"), "富邦:宇萱")

    def test_leading_digits(self):
        # Beancount v3 allows digits at the start
        self.assertEqual(normalize_name("2024 Taxes"), "2024Taxes")

    def test_unicode_names(self):
        self.assertEqual(normalize_name("Dining 餐饮"), "Dining餐饮")
        self.assertEqual(normalize_name("账户"), "账户")
        self.assertEqual(normalize_name("Café"), "Café")

    def test_symbols_and_spaces(self):
        self.assertEqual(normalize_name("Rent & Utilities (2026)"), "RentUtilities:2026")

    def test_account_registry(self):
        registry = AccountRegistry()
        
        # Normal case
        self.assertEqual(registry.get_unique_path("Assets:Bank:Checking"), "Assets:Bank:Checking")
        
        # Collision
        self.assertEqual(registry.get_unique_path("Assets:Bank:Checking"), "Assets:Bank:Checking_2")
        self.assertEqual(registry.get_unique_path("Assets:Bank:Checking"), "Assets:Bank:Checking_3")
        
        # Different path, no collision
        self.assertEqual(registry.get_unique_path("Assets:Savings:Checking"), "Assets:Savings:Checking")

    def test_beancount_path(self):
        root = Account(name="Personal Finances", currency=self.usd, initial=0, info=None)
        
        # Root -> Expenses (ExpenseInfo) -> Food (ExpenseInfo) -> Dining (ExpenseInfo)
        expenses = Account(name="Expenses", currency=self.usd, initial=0, info=ExpenseInfo(parent=root))
        food = Account(name="Food", currency=self.usd, initial=0, info=ExpenseInfo(parent=expenses))
        dining = Account(name="Dining Out", currency=self.usd, initial=0, info=ExpenseInfo(parent=food))
        
        # Beancount categories: Assets, Liabilities, Income, Expenses, Equity
        # ExpenseInfo should map to "Expenses"
        self.assertEqual(get_beancount_path(dining), "Expenses:Food:DiningOut")

        # Root -> Bank (BankInfo) -> Checking (BankInfo)
        # BankInfo should map to "Assets:Bank"
        bank = Account(name="Bank", currency=self.usd, initial=0, info=BankInfo(parent=root))
        checking = Account(name="Chase Checking", currency=self.usd, initial=0, info=BankInfo(parent=bank))
        
        # Expectation: Assets:Bank:ChaseChecking (NOT Assets:Bank:Bank:ChaseChecking)
        self.assertEqual(get_beancount_path(checking), "Assets:Bank:ChaseChecking")
        
        # Test InvestmentInfo - Securities are collapsed into parent
        etrade = Account(name="ETrade", currency=self.usd, initial=0, info=InvestmentInfo(parent=root))
        aapl = Account(name="AAPL", currency=self.usd, initial=0, info=SecurityInfo(parent=etrade))
        self.assertEqual(get_beancount_path(aapl), "Assets:Investment:ETrade")

        # Test Redundancy for Cash
        cash_parent = Account(name="Cash", currency=self.usd, initial=0, info=AssetInfo(parent=root))
        wallet = Account(name="Wallet", currency=self.usd, initial=0, info=AssetInfo(parent=cash_parent))
        self.assertEqual(get_beancount_path(cash_parent), "Assets:Cash")
        self.assertEqual(get_beancount_path(wallet), "Assets:Cash:Wallet")

if __name__ == "__main__":
    unittest.main()
