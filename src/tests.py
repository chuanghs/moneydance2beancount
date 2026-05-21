import unittest
import os
from .database import Database
from .models import (
    BankInfo, CreditCardInfo, InvestmentInfo, AssetInfo,
    LoanInfo, LiabilityInfo, ExpenseInfo, IncomeInfo, SecurityInfo
)

class TestDatabase(unittest.TestCase):
    def test_account_import(self):
        json_path = os.path.join(os.path.dirname(__file__), "test_account_import.json")
        with open(json_path, "r") as f:
            json_data = f.read()
        
        db = Database.load(json_data)

        income_num = 0
        expense_num = 0

        for acct in db.accounts.values():
            info = acct.info
            if isinstance(info, BankInfo):
                self.assertEqual(acct.name, "Checking")
            elif isinstance(info, CreditCardInfo):
                self.assertEqual(acct.name, "My Credit Card")
            elif isinstance(info, InvestmentInfo):
                self.assertEqual(acct.name, "My Fund")
                self.assertEqual(info.account_number, "INV-123")
            elif isinstance(info, AssetInfo):
                self.assertEqual(acct.name, "My Asset")
            elif isinstance(info, LoanInfo):
                self.assertEqual(acct.name, "House Loan")
            elif isinstance(info, LiabilityInfo):
                self.assertEqual(acct.name, "Some Liability")
            elif isinstance(info, SecurityInfo):
                self.assertEqual(acct.name, "My Security")
                self.assertEqual(info.sec_type, "3")
                self.assertEqual(info.broker, "My Broker")
            elif info is None: # Root
                self.assertEqual(acct.name, "Personal Finances")
            elif isinstance(info, ExpenseInfo):
                expense_num += 1
            elif isinstance(info, IncomeInfo):
                income_num += 1

        self.assertEqual(expense_num, 9)
        self.assertEqual(income_num, 12)

        # Check transactions
        self.assertEqual(len(db.transactions), 1)
        txn = db.transactions[0]
        self.assertEqual(txn.description, "Transfer From Loan")
        self.assertEqual(len(txn.splits), 1)
        self.assertEqual(txn.splits[0].description, "Transfer From Loan")
        self.assertEqual(txn.splits[0].received_amount, 20000000)
        self.assertEqual(txn.splits[0].given_amount, -20000000)

if __name__ == "__main__":
    unittest.main()
