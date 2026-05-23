## 1. Red Phase: Failing Tests

- [x] 1.1 Add test case to `tests/test_export.py` with quotes and backslashes in transaction descriptions
- [x] 1.2 Add test case to `tests/test_export.py` with quotes and backslashes in account comments and names

## 2. Green Phase: Implementation

- [x] 2.1 Implement `escape_beancount_string` in `src/beancount_exporter.py`
- [x] 2.2 Apply `escape_beancount_string` to all quoted fields in `src/beancount_exporter.py`
- [x] 2.3 Verify all tests pass

## 3. Validation

- [x] 3.1 Run end-to-end export and manually verify that quotes in `finance.beancount.tmp` are escaped (e.g., `\"`)
