## Why

The current Beancount exporter is restricted to ASCII-only account names, replacing any Unicode characters with a stable hash. This significantly reduces the readability of the exported ledger for users who use non-ASCII characters (e.g., CJK, accents) in their financial records. By targeting Beancount v3's more relaxed Unicode rules, we can provide a high-fidelity export that preserves the original account names.

## What Changes

- **Account Normalization**: Refactor `normalize_name` to support Unicode letters and numbers.
- **V3 Ruleset**: Adopt Beancount v3 naming rules, allowing components to start with digits and containing any Unicode letter.
- **Prefix Removal**: Remove the mandatory 'A' prefix for components starting with digits and the 'U' fallback for non-ASCII names.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `beancount-export`: Update the account normalization requirements to allow Unicode characters and follow Beancount v3 naming conventions.

## Impact

- `src/beancount_exporter.py`: `normalize_name` will be refactored.
- `tests/test_normalization.py`: New test cases for Unicode account names will be added.
