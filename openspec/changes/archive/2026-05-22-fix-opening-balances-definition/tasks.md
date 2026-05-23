## 1. Red Phase: Establishing Failure

- [x] 1.1 Add a test case to `tests/test_export.py` that specifically asserts the presence of `open Equity:OpeningBalances` in the output of `export_accounts`.
- [x] 1.2 Run the test to verify it fails.

## 2. Green Phase: Implementation

- [x] 2.1 Update `export_accounts` in `src/beancount_exporter.py` to prepend the `open Equity:OpeningBalances` directive.
- [x] 2.2 Verify that all tests in `tests/test_export.py` pass.

## 3. Validation

- [x] 3.1 Run a full end-to-end export using `export-beancount.sh` and verify that the `finance.beancount` file now contains the account definition.
