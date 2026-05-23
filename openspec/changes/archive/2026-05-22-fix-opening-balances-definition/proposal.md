## Why

Beancount requires all accounts to be explicitly opened with an `open` directive before they can be used in transactions. Currently, the exporter references `Equity:OpeningBalances` for initial balance adjustments but never generates an `open` directive for it. This results in validation errors when the exported file is processed by Beancount tools.

## What Changes

- **Account Opening**: Explicitly add an `open Equity:OpeningBalances` directive to the exported accounts section.
- **Consistency**: Ensure the opening balance account is always available regardless of whether any specific account has an initial balance.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update the account path generation requirements to include the mandatory `Equity:OpeningBalances` definition.

## Impact

- `src/beancount_exporter.py`: `export_accounts` will be updated to include the additional `open` directive.
- `tests/test_export.py`: The test expectations will be updated to verify the presence of the `Equity:OpeningBalances` definition.
