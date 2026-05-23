## Why

Moneydance distinguishes between bank accounts and investment accounts, but the current Beancount exporter maps both to a flat `Assets` category. This makes the exported ledger harder to navigate and organize. By introducing hierarchical sub-categories (`Assets:Bank` and `Assets:Investment`), we can provide a better-organized ledger that matches Moneydance's internal organization.

## What Changes

- **Account Mapping**: Update `get_beancount_path` to map `BankInfo` to `Assets:Bank` and `InvestmentInfo`/`SecurityInfo` to `Assets:Investment`.
- **Redundancy Handling**: Improve the redundancy check in `get_beancount_path` to handle multi-part categories correctly, preventing duplicate components like `Assets:Bank:Bank:Checking`.
- **Requirement Update**: Update the `beancount-export` specification to reflect the new hierarchical structure.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update the account path generation requirements to include hierarchical sub-categories for assets and potentially liabilities.

## Impact

- `src/beancount_exporter.py`: `get_beancount_path` will be refactored.
- `tests/test_export.py` and `tests/test_normalization.py`: Account path expectations in tests will need to be updated.
