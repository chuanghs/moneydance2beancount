## 1. Research and Preparation

- [x] 1.1 Add a reproduction test case in `tests/test_export.py` that simulates a security purchase and asserts the use of `{{ }}` notation.
- [x] 1.2 Verify the test fails.

## 2. Core Implementation

- [x] 2.1 Update `format_amount` in `src/beancount_exporter.py` to support stripping trailing zeros.
- [x] 2.2 Update `export_transactions` in `src/beancount_exporter.py` to use `{{ }}` notation for `SecurityInfo` buy transactions.

## 3. Verification

- [x] 3.1 Run tests and verify the new security notation is correctly exported.
- [x] 3.2 Verify that currency-to-currency transactions still use `@@`.
- [x] 3.3 Verify that trailing zeros are removed as expected.
