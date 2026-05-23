## 1. Red Phase: Failing Tests

- [x] 1.1 Add test case to `tests/test_export.py` for `export_prices` with missing capital (empty currency code)
- [x] 1.2 Add test case to `tests/test_export.py` for `export_prices` with missing target currency (empty base currency)

## 2. Green Phase: Implementation

- [x] 2.1 Update `export_prices` in `src/beancount_exporter.py` to pre-filter snapshots and validate base currency
- [x] 2.2 Verify all price export tests pass

## 3. Validation

- [x] 3.1 Run end-to-end export to ensure no crashes on potentially incomplete price data
