## Why

The current Beancount exporter has a "sign inversion" bug that causes multi-currency transactions to fail to balance and single-currency transactions to have inverted (backwards) signs. This is because the exporter logic incorrectly negates the Moneydance `pamt` (Parent Amount) values and uses the wrong fields for split amounts. Fixing this ensures accurate financial reporting and compatibility with Beancount validation tools.

## What Changes

- **Sign Correction**: Use raw Moneydance `pamt` and `samt` signs directly without artificial negation.
- **Field Alignment**: Consistently use `samt` (given_amount in models) for split postings to correctly reflect the impact on the receiving account.
- **Requirement Update**: Update the `beancount-export` specification to reflect the correct accounting signs.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Correct the requirements for transaction sign handling and multi-currency balancing.

## Impact

- `src/beancount_exporter.py`: Correct the math in `export_transactions`.
- `tests/test_export.py`: Update or add test cases to verify correct signs for both same-currency and multi-currency transactions.
