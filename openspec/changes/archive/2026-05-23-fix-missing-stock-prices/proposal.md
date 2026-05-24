## Why

Currently, many stocks (especially Taiwan stocks) in the Moneydance data have an empty `currid`. While our exporter correctly translates these into Beancount commodity codes (e.g., `YUANTA_TW50`), the `export_prices` function contains a strict filter that excludes any price snapshot where the currency's internal `code` is empty.

This results in a ledger missing all historical exchange rates for these commodities, preventing tools like Fava from converting their balances into the operating currency (TWD).

## What Changes

- **Update `export_prices` filter**: Relax the condition to allow snapshots where the currency code is empty, as long as a valid Beancount commodity can be derived from the name or ticker.
- **Update sorting logic**: Change the sorting key in `export_prices` to use the derived Beancount commodity code instead of the raw currency code for stability.

## Capabilities

### Modified Capabilities
- `beancount-export`: Update the price export engine to be more inclusive of stocks with incomplete metadata.

## Impact

- `src/beancount_exporter.py`: Modify `export_prices` to include more snapshots and improve sorting consistency.
- `tests/test_export.py`: Add a test case specifically for a currency with an empty code but valid price history.
