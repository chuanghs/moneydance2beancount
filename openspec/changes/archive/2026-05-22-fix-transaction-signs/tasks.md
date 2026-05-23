## 1. Red Phase: Failing Tests

- [x] 1.1 Add failing test case to `tests/test_export.py` for same-currency transaction with correct signs (Expense > 0, Asset < 0)
- [x] 1.2 Add failing test case to `tests/test_export.py` for multi-currency transaction with correct signs and balancing

## 2. Green Phase: Core Fix

- [x] 2.1 Update `export_transactions` in `src/beancount_exporter.py` to remove negation from giver amount
- [x] 2.2 Update `export_transactions` in `src/beancount_exporter.py` to consistently use `given_amount` for split postings
- [x] 2.3 Verify all tests in `tests/test_export.py` and `tests/test_normalization.py` pass

## 3. Validation

- [x] 3.1 Validate end-to-end export using `export-beancount.sh` and verify signs in `finance.beancount`
- [x] 3.2 Perform manual check on HSBC USD/TWD transactions to ensure they match the requirement
