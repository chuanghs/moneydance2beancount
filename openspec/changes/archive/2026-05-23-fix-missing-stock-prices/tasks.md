## 1. Phase 1: Red (Failing Tests)

- [x] 1.1 Update `tests/test_export.py`: Modify `test_export_prices` to include a snapshot where `currency.code` is an empty string, but `ticker` is set.
- [x] 1.2 Verify tests fail (assertion error or missing price line).

## 2. Phase 2: Green (Implementation)

- [x] 2.1 Update `src/beancount_exporter.py`: Relax the filter in `export_prices` to check for `get_commodity_code(s.currency) != \"UNKNOWN\"`.
- [x] 2.2 Update `src/beancount_exporter.py`: Update the sorting key in `export_prices` to use `get_commodity_code(snap.currency)`.
- [x] 2.3 Verify tests pass.

## 3. Phase 3: Verification

- [x] 3.1 Manually run the exporter on `sample/finance.json`.
- [x] 3.2 Verify that `export/prices.beancount` now contains price entries for `YUANTA_TW50`, `PROMOS`, and `CH_TELECOM`.

