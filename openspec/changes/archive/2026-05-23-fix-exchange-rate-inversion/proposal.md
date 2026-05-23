## Why

The current currency conversion logic in the exporter is producing inverted exchange rates. Beancount `price` directives expect the price of 1 unit of a commodity expressed in a target currency (e.g., `1 USD = 30 TWD`). The current code is exporting `urt` directly, which represents `1 TWD = 0.033 USD`. This causes Fava and Beancount to show incorrect values for net worth and unrealized gains.

Additionally, the code incorrectly assumes the target for prices is always the first currency in the `operating_currencies` list, which may not match the base currency the rates were calculated against in Moneydance.

## What Changes

- **Detect Base Currency**: Identify the Moneydance base currency (where `isbase` is "y") during database load.
- **Invert Exchange Rates**: Change the price calculation to `1 / urt` to match Beancount's required direction.
- **Dynamic Price Target**: Use the detected Moneydance base currency as the target for all `price` directives.
- **High Precision**: Increase decimal precision for exchange rates to 8 decimal places.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `beancount-export`: Update the price export requirement to use correct inversion and target currency.

## Impact

- `src/database.py`: Store the base currency code in the `Database` object.
- `src/beancount_exporter.py`: Update `export_prices` to use the correct math and target.
- `tests/test_export.py`: Add/update tests to verify correct exchange rate direction.
