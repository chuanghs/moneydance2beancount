## Why

The current Beancount exporter uses a flat category structure for general assets and liabilities. To provide better organization and match standard accounting practices, we want to group "Cash" accounts (represented by Moneydance `AssetInfo`) under `Assets:Cash` and "Credit Card" accounts (represented by `CreditCardInfo`) under `Liabilities:Card`. This improves the readability and navigability of the exported ledger.

## What Changes

- **Account Mapping**: Update `get_beancount_path` to map `AssetInfo` to `Assets:Cash` and `CreditCardInfo` to `Liabilities:Card`.
- **Parentheses Normalization**: Update `normalize_name` to convert names like 'A(B)' into hierarchical paths 'A:B'.
- **Constraint Enforcement**: Ensure other liability types (e.g., `LoanInfo`) remain at the top-level `Liabilities` category.
- **Redundancy Handling**: Leverage the existing redundancy check to prevent stuttering like `Assets:Cash:Cash`.
- **Requirement Update**: Update the `beancount-export` specification to reflect these new organizational rules.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update the account path generation requirements to include sub-categories for cash and credit cards.

## Impact

- `src/beancount_exporter.py`: `get_beancount_path` will be refactored.
- `tests/test_export.py` and `tests/test_normalization.py`: Account path expectations in tests will need to be updated.
