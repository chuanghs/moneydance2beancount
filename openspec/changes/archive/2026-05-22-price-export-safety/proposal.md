## Why

The Beancount exporter currently lacks safety checks when generating price directives. If a price snapshot is missing its currency code (the "Capital") or if the target base currency is not provided, it can generate invalid Beancount directives or cause the export process to crash. This change ensures that only complete price records are exported.

## What Changes

- **Price Validation**: Update `export_prices` to validate each snapshot's currency code and the target base currency.
- **Record Skipping**: Skip any price records that are missing essential identification data.
- **Requirement Update**: Formalize the validation rules in the `beancount-export` specification.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update price extraction requirements to include mandatory validation and skipping of incomplete records.

## Impact

- `src/beancount_exporter.py`: `export_prices` will be refactored to include validation logic.
- `tests/test_export.py`: New test cases will be added to verify skipping of incomplete records.
