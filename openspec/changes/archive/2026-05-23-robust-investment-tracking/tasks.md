## 1. Setup and Failure

- [x] 1.1 Update `tests/test_export.py` with a "Sell" transaction test case and verify it fails or produces incorrect notation.
- [x] 1.2 Verify that `export_accounts` currently doesn't add `"FIFO"`.

## 2. Core Implementation

- [x] 2.1 Update `export_accounts` in `src/beancount_exporter.py` to add `"FIFO"` and costed initial balances for securities.
- [x] 2.2 Update `export_transactions` in `src/beancount_exporter.py` to use `{}` for security reductions and add an empty `Equity:OpeningBalances` posting to absorb gains/losses.


## 3. Validation

- [x] 3.1 Run `bean-check finance.beancount` on the sample data and verify that "No position matches" errors are significantly reduced or eliminated.
- [x] 3.2 Verify all unit tests pass.
