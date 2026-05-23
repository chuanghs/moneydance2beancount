## 1. Core Logic (TDD Phase)

- [x] 1.1 Add unit tests in `tests/test_export.py` for `export_options` (verifying TWD, USD, EUR defaults and title detection).
- [x] 1.2 Implement `export_options` in `src/beancount_exporter.py` to satisfy tests.
- [x] 1.3 Update `get_commodity_code` unit tests to handle list-based base currencies. (Done via test_export_prices and test_full_export)

## 2. Integration and Pipeline

- [x] 2.1 Update `full_export` signature and implementation to accept a list of base currencies.
- [x] 2.2 Refactor `export_prices` to use the first currency in the provided list as the default target.
- [x] 2.3 Update CLI logic in `src/beancount_exporter.py` to split the `base_currency` argument by commas.
- [x] 2.4 Update `commodity_map.yaml` loader to read global settings.


## 3. Validation

- [x] 3.1 Verify all tests pass with `python3 -m unittest discover tests`.
- [x] 3.2 Run `full_export` on `sample/finance.json` and verify the `;; === OPTIONS ===` section is present and correct.
- [x] 3.3 Confirm `bean-check` reports no "No operating currency specified" errors on the final output.
