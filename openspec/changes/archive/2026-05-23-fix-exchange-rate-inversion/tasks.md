## 1. Phase 1: Red (Failing Tests)

- [x] 1.1 Update `tests/test_export.py`: Modify `test_export_prices` to assert that the price is inverted (`1 / urt`). For example, if `urt` is 0.033333, the expected price string should be `30.00000000`.
- [x] 1.2 Update `tests/test_export.py`: Add a test case for `Database.load` that asserts `db.base_currency_code` is correctly set to the currency marked with `isbase: "y"`.
- [x] 1.3 Verify both tests fail.

## 2. Phase 2: Green (Implementation)

- [x] 2.1 Update `src/database.py`: In `Database.load`, iterate through currencies to find the one with `isbase == "y"` and store its `currid` in `self.base_currency_code`.
- [x] 2.2 Update `src/beancount_exporter.py`: Modify `export_prices` signature to accept `base_currency_code`.
- [x] 2.3 Update `src/beancount_exporter.py`: Implement the `1.0 / snap.price` inversion and use the passed `base_currency_code` as the target currency.
- [x] 2.4 Update `src/beancount_exporter.py`: In `full_export`, pass `db.base_currency_code` to `export_prices`.

## 3. Phase 3: Refactor and Verify

- [x] 3.1 Run all tests and verify they pass.
- [x] 3.2 Manually run the exporter on `sample/finance.json` and confirm the `price` directives in `finance.beancount` use the correct direction and target.
