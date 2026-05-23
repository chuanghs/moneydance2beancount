## Why

The recent implementation of security cost notation (`{{ }}`) caused numerous `bean-check` errors because it created mixed cost/no-cost inventories. Specifically:
1. Security "Sell" transactions still used `@@` (no cost), resulting in separate no-cost lots that couldn't reconcile with "Buy" lots.
2. Initial balances for securities didn't have cost notation, making them unreachable for costed reductions.
3. Lack of explicit booking policies (`FIFO`) made lot matching difficult for Beancount.

## What Changes

- **Consistent Cost Notation**: Use `{}` (empty braces) for all security reduction (Sell) transactions to ensure they match existing costed lots.
- **Initial Balance Costing**: Add a dummy zero cost `{{ 0 BASE_CURR }}` to initial balances of securities to ensure they are part of the costed inventory from the start.
- **Automatic Booking Policy**: Add `"FIFO"` to the `open` directive of any account path that contains security holdings, enabling automatic lot matching.
- **Balancing Posting for Sells**: Add an empty `Equity:OpeningBalances` posting to any transaction involving a security sale to absorb capital gains/losses and ensure Beancount validation passes.
- **Total Price for Sells**: Ensure "Sell" transactions use `{} @@ TOTAL_PRICE` to let Beancount resolve the gain/loss.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `beancount-export`: Improve the robustness of investment account exports and lot tracking.

## Impact

- `src/beancount_exporter.py`: Update `export_accounts` and `export_transactions`.
- `tests/test_export.py`: Update tests to reflect the more robust notation.
