## Why

Currently, the `commodity_map.yaml` file is a manual requirement that users might not be aware of. Automatically generating a default configuration file on startup improves discoverability, surfaces default settings (like operating currencies), and provides a template for manual translations.

## What Changes

- **Automatic File Generation**: On startup, the exporter will check for the existence of `commodity_map.yaml` in the current working directory.
- **Default Scaffolding**: If missing, it will create the file with default `settings` (TWD, USD, EUR) and an empty `translations` block.
- **Improved UX**: Users get immediate visual confirmation and a path to customization without reading documentation.

## Capabilities

### New Capabilities
- `auto-config`: Handles the detection and generation of default project configuration files.

### Modified Capabilities
- `beancount-export`: Update initialization logic to ensure configuration is present before the export begins.

## Impact

- `src/beancount_exporter.py`: Update module-level initialization logic.
- Project root: A new `commodity_map.yaml` will be created if not present.
