## Why

The current exporter uses Total Cost notation `{{ total_amount CURR }}` for security purchases. While mathematically correct for Beancount, it is confusing for users because the total amount (e.g., $1502.15) appears where they expect to see the unit price (e.g., $300.43). This leads to the impression that the stock was purchased at an impossibly high price.

Switching to Unit Cost notation `{ unit_price CURR }` makes the ledger more readable and easier to verify against historical market data.

## What Changes

- **Update Security Buys**: Change from `{{ total_amount CURRENCY }}` to `{ unit_price CURRENCY }` in `src/beancount_exporter.py`.
- **Calculate Unit Price**: Divide the total received amount by the number of shares during export.
- **Maintain Precision**: Ensure the calculated unit price has sufficient precision (e.g., matching the currency's decimal or a fixed high precision).

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `beancount-export`: Update the security purchase requirement to use unit cost notation.

## Impact

- `src/beancount_exporter.py`: Modify the cost basis generation logic for security buys.
- `tests/test_export.py`: Update existing tests to assert unit cost notation.
