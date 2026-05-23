## Why

Currently, all multi-currency transactions are exported using the Beancount `@@` (Total Price) syntax. While this works for simple currency exchanges, it is incorrect for securities (stocks, mutual funds) because Beancount needs explicit cost basis notation (`{}`) to track lots, calculate capital gains, and manage investment portfolios correctly.

Additionally, the user noted that stocks should be treated as commodities within an account rather than unique accounts themselves. Our existing logic handles account collapsing, but the notation needs to reflect this commodity-centric approach.

## What Changes

- **Cost Notation for Securities**: Transactions involving security accounts (`SecurityInfo`) will now use the Beancount `{}` (Unit Cost) syntax instead of `@@` (Total Price) for "Buy" transactions (where quantity increases).
- **Exact Total Cost**: To avoid rounding errors during unit cost calculation, we will prefer the double-brace `{{ }}` (Total Cost) syntax which maps directly to Moneydance's `pamt` field.
- **Improved Readability**: We will strip trailing zeros from amounts and prices to make the ledger cleaner (e.g., `100` instead of `100.0000` if the precision allows).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `beancount-export`: Update the transaction transformation requirements to distinguish between currency exchange and security cost basis.

## Impact

- `src/beancount_exporter.py`: Modify `export_transactions` and `format_amount` logic.
- `tests/test_export.py`: Add test cases for security purchases with cost notation.
