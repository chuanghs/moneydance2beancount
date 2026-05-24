import re
from src.models import Account, Transaction, InvestmentInfo, SecurityInfo, LiabilityInfo, LoanInfo, CreditCardInfo, BankInfo, AssetInfo

def get_file_for_account(account: Account) -> str:
    if re.search(r'Cash|現金', account.name):
        return "daily.beancount"
    if isinstance(account.info, (InvestmentInfo, SecurityInfo)):
        return "investment.beancount"
    elif isinstance(account.info, (LiabilityInfo, LoanInfo, CreditCardInfo)):
        return "liability.beancount"
    elif isinstance(account.info, (BankInfo, AssetInfo)):
        return "assets.beancount"
    # IncomeInfo, ExpenseInfo, and None (Root) go to main
    return "main.beancount"

def get_file_for_transaction(txn: Transaction) -> str:
    all_accounts = [txn.giver] + [s.receiver for s in txn.splits]
    
    # 1. Daily (Cash/現金)
    if any(re.search(r'Cash|現金', acc.name) for acc in all_accounts):
        return "daily.beancount"
    
    # 2. Investment
    if any(isinstance(acc.info, (InvestmentInfo, SecurityInfo)) for acc in all_accounts):
        return "investment.beancount"
        
    # 3. Liability
    if any(isinstance(acc.info, (LiabilityInfo, LoanInfo, CreditCardInfo)) for acc in all_accounts):
        return "liability.beancount"
        
    # 4. Assets
    if any(isinstance(acc.info, (BankInfo, AssetInfo)) for acc in all_accounts):
        return "assets.beancount"
        
    # 5. Fallback
    return "main.beancount"
