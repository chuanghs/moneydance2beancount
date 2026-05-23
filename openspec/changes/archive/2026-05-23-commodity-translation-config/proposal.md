## Why

The Beancount export fails because many commodity names (tickers) in Moneydance do not comply with Beancount's strict syntax rules (e.g., they start with digits or contain non-ASCII characters). This leads to syntax errors that cause Beancount to silently drop `open` directives, resulting in "Invalid reference to unknown account" errors.

## What Changes

- **Commodity Translation Map**: Introduce an external configuration file (`commodity_map.yaml`) to allow users to manually map Chinese or non-compliant commodity names to valid Beancount IDs.
- **Automatic Digit Prefixing**: Automatically prepend `SYM_` to any ticker or currency code that starts with a digit.
- **Strict Commodity Validation**: Implement a robust sanitization process to ensure all exported commodity IDs strictly follow the Beancount character set rules (Uppercase ASCII, starts with a letter).
- **Configuration Loading**: Add logic to load and merge the translation map during the export process.

## Capabilities

### New Capabilities
- `commodity-translation`: Manages the translation and sanitization of commodity identifiers based on user configuration and strict syntax rules.

### Modified Capabilities
- `beancount-export`: Update the account and transaction export requirements to use sanitized commodity IDs and integrate with the new translation capability.

## Impact

- `src/beancount_exporter.py`: Update `get_commodity_code` and add configuration loading logic.
- `openspec/config.yaml` or a new `commodity_map.yaml`: New user-editable configuration for translations.
- `tests/test_export.py`: New test cases for digit-prefixing and translation mapping.
