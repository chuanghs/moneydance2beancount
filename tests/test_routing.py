import unittest
from datetime import datetime
from src.models import (
    Account, Currency, BankInfo, InvestmentInfo, SecurityInfo,
    LiabilityInfo, CreditCardInfo, IncomeInfo, ExpenseInfo,
    Transaction, Split, Status
)
from src.beancount_exporter import get_file_for_account, get_file_for_transaction

class TestRouting(unittest.TestCase):
    def setUp(self):
        self.usd = Currency(code="USD", rate=1.0, decimal=2)
        self.twd = Currency(code="TWD", rate=30.0, decimal=0)

    def test_get_file_for_account(self):
        # Assets:Bank -> assets.beancount
        bank_acct = Account(name="Checking", currency=self.usd, initial=0, info=BankInfo(parent=None))
        self.assertEqual(get_file_for_account(bank_acct), "assets.beancount")

        # Assets:Investment -> investment.beancount
        inv_acct = Account(name="ETrade", currency=self.usd, initial=0, info=InvestmentInfo(parent=None))
        self.assertEqual(get_file_for_account(inv_acct), "investment.beancount")
        
        sec_acct = Account(name="AAPL", currency=self.usd, initial=0, info=SecurityInfo(parent=inv_acct))
        self.assertEqual(get_file_for_account(sec_acct), "investment.beancount")

        # Liabilities -> liability.beancount
        cc_acct = Account(name="Visa", currency=self.usd, initial=0, info=CreditCardInfo(parent=None))
        self.assertEqual(get_file_for_account(cc_acct), "liability.beancount")
        
        loan_acct = Account(name="Mortgage", currency=self.usd, initial=0, info=LiabilityInfo(parent=None))
        self.assertEqual(get_file_for_account(loan_acct), "liability.beancount")

        # Income/Expenses -> main.beancount
        inc_acct = Account(name="Salary", currency=self.usd, initial=0, info=IncomeInfo(parent=None))
        self.assertEqual(get_file_for_account(inc_acct), "main.beancount")
        
        exp_acct = Account(name="Rent", currency=self.usd, initial=0, info=ExpenseInfo(parent=None))
        self.assertEqual(get_file_for_account(exp_acct), "main.beancount")

    def test_get_file_for_transaction_priority(self):
        # Setup accounts
        cash_acct = Account(name="現金", currency=self.twd, initial=0, info=BankInfo(parent=None))
        bank_acct = Account(name="Checking", currency=self.usd, initial=0, info=BankInfo(parent=None))
        inv_acct = Account(name="ETrade", currency=self.usd, initial=0, info=InvestmentInfo(parent=None))
        cc_acct = Account(name="Visa", currency=self.usd, initial=0, info=CreditCardInfo(parent=None))
        exp_acct = Account(name="Food", currency=self.usd, initial=0, info=ExpenseInfo(parent=None))

        # 1. Daily Priority (Touches Cash)
        txn_daily = Transaction(
            giver=cash_acct,
            description="Buy bread",
            date=datetime(2026, 5, 23),
            status=Status.NONE,
            splits=[Split(receiver=exp_acct, given_amount=100, received_amount=-100)]
        )
        self.assertEqual(get_file_for_transaction(txn_daily), "daily.beancount")

        # 2. Investment Priority
        txn_inv = Transaction(
            giver=bank_acct,
            description="Transfer to ETrade",
            date=datetime(2026, 5, 23),
            status=Status.NONE,
            splits=[Split(receiver=inv_acct, given_amount=1000, received_amount=-1000)]
        )
        self.assertEqual(get_file_for_transaction(txn_inv), "investment.beancount")

        # 3. Liability Priority
        txn_lia = Transaction(
            giver=cc_acct,
            description="Pay Visa from Checking",
            date=datetime(2026, 5, 23),
            status=Status.NONE,
            splits=[Split(receiver=bank_acct, given_amount=500, received_amount=-500)]
        )
        self.assertEqual(get_file_for_transaction(txn_lia), "liability.beancount")

        # 4. Assets Priority
        txn_asset = Transaction(
            giver=bank_acct,
            description="Internal transfer",
            date=datetime(2026, 5, 23),
            status=Status.NONE,
            splits=[Split(receiver=Account(name="Savings", currency=self.usd, initial=0, info=BankInfo(parent=None)), given_amount=100, received_amount=-100)]
        )
        self.assertEqual(get_file_for_transaction(txn_asset), "assets.beancount")

        # 5. Main Fallback
        txn_main = Transaction(
            giver=Account(name="Salary", currency=self.usd, initial=0, info=IncomeInfo(parent=None)),
            description="Interest",
            date=datetime(2026, 5, 23),
            status=Status.NONE,
            splits=[Split(receiver=exp_acct, given_amount=10, received_amount=-10)]
        )
        self.assertEqual(get_file_for_transaction(txn_main), "main.beancount")

if __name__ == '__main__':
    unittest.main()
