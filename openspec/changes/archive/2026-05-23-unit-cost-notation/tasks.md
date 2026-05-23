## 1. Phase 1: Red (Failing Tests)

- [x] 1.1 Update `tests/test_export.py`: Find security purchase assertions and change them to expect single-brace `{ }` with unit prices instead of double-brace `{{ }}` with totals.
- [x] 1.2 Verify tests fail.

## 2. Phase 2: Green (Implementation)

- [x] 2.1 Update `src/beancount_exporter.py`: In `export_transactions`, calculate the unit price by dividing `abs(split.received_amount)` by `abs(split.given_amount)`, adjusting for their respective currency decimals.
- [x] 2.2 Update `src/beancount_exporter.py`: Change the formatting string for security buys from `{{ {amt_parent_str} {giver_currency} }}` to `{ {unit_price_str} {giver_currency} }`.
- [x] 2.3 Ensure `unit_price_str` uses sufficient precision (e.g., `.6f`).

## 3. Phase 3: Verification

- [x] 3.1 Run tests and verify they pass.
- [x] 3.2 Manually check the exported `finance.beancount` to ensure CDNS RSU vests show unit prices (e.g., `300.43 USD`) instead of totals.
