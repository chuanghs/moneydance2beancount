## 1. Setup and Failure Definition (Red Phase)

- [x] 1.1 Create `commodity_map.yaml` with initial translations for known Chinese commodities (e.g., `"中華電信": "CH_TELECOM"`).
- [x] 1.2 Add unit tests in `tests/test_normalization.py` that define the required behavior for digit-starting tickers (`2412` -> `SYM_2412`) and manual translations.
- [x] 1.3 Verify that these new tests FAIL as expected (since logic is not yet implemented).

## 2. Core Implementation (Green Phase)

- [x] 2.1 Implement configuration loading logic in `src/beancount_exporter.py` to read `commodity_map.yaml`.
- [x] 2.2 Refactor `get_commodity_code` in `src/beancount_exporter.py` to prioritize manual translations and implement auto-prefixing for digits.
- [x] 2.3 Implement `normalize_commodity` utility to enforce strict Beancount ASCII rules.
- [x] 2.4 Verify that unit tests now PASS.

## 3. Integration and Validation (Refactor Phase)

- [x] 3.1 Update `export_commodities`, `export_prices`, and `export_budgets` to use the new sanitized commodity codes.
- [x] 3.2 Add integration tests in `tests/test_export.py` verifying that the translation map is correctly applied to the full export output.
- [x] 3.3 Run `full_export` on `sample/finance.json` and verify the output with `bean-check` (via `.venv/bin/python`) to ensure zero syntax errors.
