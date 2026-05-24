# Design: Exporter Modularization and Ignore Future Records

## Components

### 1. Format-Neutral Parsing
* **database.py**: Stores raw currency names and parent IDs exactly as they appear in the Moneydance source ledger. Removes all imports of Beancount formatting functions.

### 2. Config & Scaffolding Context
* **config.py**: Introduces `ExportConfig` that reads Settings from `commodity_map.yaml`. If the YAML file is missing, it auto-scaffolds a default configuration template containing comments and defaulting `ignore_future: false`.

### 3. Exporter Packages
* **exporter/base.py**: Defines abstract `BaseExporter` interface.
* **exporter/beancount/mapper.py**: Translates account names and resolves commodity symbols using the configuration map.
* **exporter/beancount/router.py**: Houses multi-file file split destination routing rules.
* **exporter/beancount/formatter.py**: Implements pure formatting string generators.
* **exporter/beancount/exporter.py**: Coordinates formatting and applies cutoff date boundaries for future records.

### 4. argparse CLI Facade
* **beancount_exporter.py**: CLI parser entrypoint using `argparse`. Sets config precedence: CLI Arguments > YAML File Settings > Defaults. Offers facade functions for backward compatibility.
