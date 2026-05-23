## 1. Red Phase: Failing Tests

- [x] 1.1 Update `tests/test_export.py` to expect `Assets:Cash` for `AssetInfo` and `Liabilities:Card` for `CreditCardInfo`
- [x] 1.2 Update `tests/test_normalization.py` to assert redundancy handling for `Assets:Cash:Cash`
- [x] 1.3 Update `tests/test_normalization.py` to assert that `A(B)` is converted to `A:B`

## 2. Green Phase: Implementation

- [x] 2.1 Update `get_beancount_path` in `src/beancount_exporter.py` with the updated mapping for `AssetInfo` and `CreditCardInfo`
- [x] 2.2 Verify all tests in `tests/test_export.py` and `tests/test_normalization.py` pass

## 3. Validation

- [x] 3.1 Run end-to-end export and manually verify hierarchy in `finance.beancount.tmp`
