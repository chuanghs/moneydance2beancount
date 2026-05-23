## Why

Moneydance represents security holdings as individual sub-accounts under an "Investment Account". In Beancount, it is more idiomatic to treat the Investment Account as a single "bucket" that holds multiple commodities (cash and securities). The current exporter preserves the Moneydance sub-account structure, leading to deeply nested, repetitive paths like `Assets:Investment:Schwab:VanguardTotalWorldStock`.

This change refactors the export logic to "collapse" security accounts into their parent investment accounts, while using the security's ticker/symbol as the primary identity for the commodity itself.

## What Changes

- **Path Collapsing**: Update `get_beancount_path` to map all `SecurityInfo` accounts directly to their parent account's Beancount path.
- **Commodity Identity**: Introduce a "best-code" logic to select the most readable ticker/symbol for Beancount, falling back to a normalized name if a ticker is missing or is a GUID.
- **Commodity Export**: Add a new export phase that generates Beancount `commodity` directives to preserve full security names and metadata.
- **GUID Filtering**: Implement a utility to detect and skip Moneydance internal GUID strings when selecting commodity codes.

## Capabilities

### Modified Capabilities
- `beancount-export`: Update account mapping and transaction transformation requirements to reflect the collapsed hierarchy and commodity-based identity.

## Impact

- `src/beancount_exporter.py`: Major updates to `get_beancount_path`, `export_accounts`, and addition of `export_commodities`.
- `src/database.py`: Potential updates to how `Currency` objects are populated from Moneydance data to capture tickers and full names.
- `tests/test_export.py`: Updated test cases to verify that securities resolve to parent paths and use clean tickers.
