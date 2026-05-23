## Context

Splitting a Beancount ledger requires careful routing of both definitions (`commodity`, `open`) and transactions to ensure the final output is logically sound and avoids duplication.

## Goals

- Support categorized multi-file export.
- Implement priority-based transaction routing.
- Maintain compatibility with single-file export (stdout).

## Decisions

### 1. Mapping Account Types to Files
We will implement a helper function `get_file_for_account(account: Account) -> str`:
- `InvestmentInfo`, `SecurityInfo` -> `investment.beancount`
- `LiabilityInfo`, `LoanInfo`, `CreditCardInfo` -> `liability.beancount`
- `BankInfo`, `AssetInfo` -> `assets.beancount`
- `IncomeInfo`, `ExpenseInfo`, `None` (Root) -> `main.beancount`

### 2. Transaction Routing Priority
A transaction can involve multiple accounts from different categories. We will use the following priority:
```python
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
```

### 3. File Headers and Includes
`main.beancount` will serve as the root. It will contain:
- `option` directives.
- `include "commodity.beancount"`
- `include "prices.beancount"`
- `include "assets.beancount"`
- `include "investment.beancount"`
- `include "liability.beancount"`
- `include "daily.beancount"`
- `open Equity:OpeningBalances`
- Income/Expense definitions and transactions.

### 4. CLI Interface
The `__main__` block will be updated to check for a `--multi` flag or a directory argument. If present, it will use `full_multi_export(db, operating_currencies, output_dir)`.

## Risks / Trade-offs

- **[Risk]** Duplication of opening balances if an account path is shared across files. -> **[Mitigation]** The `AccountRegistry` already ensures unique paths. We must ensure that each `path` is assigned to exactly one file based on its "primary" account.
- **[Trade-off]** Complexity of cross-file references. -> **[Mitigation]** Beancount doesn't care about the file boundary as long as all files are included in the same run.
