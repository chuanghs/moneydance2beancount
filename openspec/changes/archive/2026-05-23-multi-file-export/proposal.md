## Why

As the financial ledger grows, a single large Beancount file becomes difficult to maintain and navigate. Splitting the ledger into category-specific files improves organization, allows for better version control diffs, and can improve performance in tools like Fava. 

Specifically, users want to separate stable data (commodities, prices) from frequent transactions, and further categorize transactions by account type (Assets, Investments, Liabilities) while isolating "daily" cash spending.

## What Changes

- **Export Directory**: Introduce an `export/` directory to house all generated Beancount files.
- **File Partitioning**:
    - `main.beancount`: Entry point with options, includes, and Income/Expense definitions/transactions.
    - `commodity.beancount`: All `commodity` directives.
    - `prices.beancount`: Historical price snapshots.
    - `assets.beancount`: Non-investment Asset accounts and transactions.
    - `investment.beancount`: Investment/Security accounts and transactions.
    - `liability.beancount`: Liability/Loan/CreditCard accounts and transactions.
    - `daily.beancount`: High-priority file for any transaction involving "Cash" or "現金" accounts.
- **Routing Logic**: Implement a priority-based routing system for transactions to determine their target file.
- **Equity:OpeningBalances**: The account definition will live in `main.beancount`, but opening balance transactions will be co-located with the accounts they initialize.

## Capabilities

### New Capabilities
- `multi-file-export`: Support for generating a split-file Beancount ledger.

### Modified Capabilities
- `beancount-export`: Update to support either single-file or multi-file output.

## Impact

- `src/beancount_exporter.py`: Extensive refactoring of the export engine to support multiple output streams and routing logic.
- `src/database.py`: No changes expected.
- `tests/test_export.py`: Add tests for file partitioning and transaction routing.
