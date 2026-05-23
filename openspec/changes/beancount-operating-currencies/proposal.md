## Why

Beancount reports (like Fava) and validation tools (like `bean-check`) expect one or more `operating_currency` options to be defined. Without these, Beancount fails with "No operating currency specified," and reports are not correctly grouped by primary currencies.

## What Changes

- **Options Export Phase**: Add a new phase to the export process that generates the `;; === OPTIONS ===` section at the top of the file.
- **Default Operating Currencies**: Set the default operating currencies to `TWD`, `USD`, and `EUR` if the user does not provide any.
- **Multiple Currency Support**: Update the CLI and configuration to support a list of multiple operating currencies.
- **Configuration Integration**: Allow users to persist their preferred operating currencies in the `commodity_map.yaml` file under a `settings` block.
- **Auto-Title Detection**: Automatically detect the Moneydance "Root Account" name and set it as the Beancount `title` option.

## Capabilities

### New Capabilities
- `beancount-options`: Manages the generation of global Beancount options and ledger-wide settings.

### Modified Capabilities
- `beancount-export`: Update the main export pipeline to include the options section and propagate operating currency settings to other phases (like price export).

## Impact

- `src/beancount_exporter.py`: New `export_options` function, updated `full_export`, and CLI logic changes.
- `commodity_map.yaml`: New `settings` section for user-defined defaults.
- `tests/test_export.py`: New tests for multi-currency options and title detection.
