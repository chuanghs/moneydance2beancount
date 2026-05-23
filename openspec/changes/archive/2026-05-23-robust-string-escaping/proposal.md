## Why

The Beancount exporter currently injects free-text fields (transaction descriptions, account names, and comments) directly into double-quoted strings in the exported file. If these fields contain double quotes (`"`) or backslashes (`\`), the resulting Beancount file becomes syntactically invalid, causing the Beancount parser or Fava to fail. This change introduces proper escaping for these characters to ensure the exported ledger is always valid.

## What Changes

- **String Escaping Utility**: Introduce a `escape_beancount_string` helper to escape `"` and `\` characters.
- **Universal Application**: Apply this escaping to all free-text fields exported as Beancount strings (transaction descriptions, account metadata, and comments).
- **Requirement Update**: Update the `beancount-export` specification to include string escaping as a core requirement.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update transaction and account export requirements to include mandatory string escaping.

## Impact

- `src/beancount_exporter.py`: Implementation of the escaping utility and its application in `export_accounts` and `export_transactions`.
- `tests/test_export.py`: Updated test cases with quotes and backslashes in descriptions.
