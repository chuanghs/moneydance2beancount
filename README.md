# m2b: Moneydance to Beancount Exporter

`m2b` is a Python tool designed to parse exported Moneydance JSON data and generate clean, structured Beancount double-entry ledger files. It supports multi-currency transfers, automated price snapshots conversion, budget directives, investment lot matching, and multi-file outputs.

---

## Installation & Setup

1. **Prerequisites**: Python 3.10+
2. **Setup Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Usage

Run the exporter from the command line:

```bash
# General Syntax
python3 -m src.beancount_exporter <moneydance_json_path> [options]
```

### Command Line Flags

| Flag | Long Option | Description |
| :--- | :--- | :--- |
| `-c` | `--base-currencies` | Comma-separated list of operating currencies (e.g., `USD,TWD`). |
| `-o` | `--output-dir` | Directory to output a multi-file include structure. |
| `-i` | `--ignore-future` | Exclude all transactions, price snapshots, and budgets dated in the future. |
| `-d` | `--cutoff-date` | Filter out all records dated strictly after `YYYY-MM-DD`. |

#### Examples:
* **Single Unified Output**:
  ```bash
  python3 -m src.beancount_exporter sample/moneydance.json -c TWD,USD > ledger.beancount
  ```
* **Multi-File Output** (splits daily, assets, investment, liability, and commodities into separate files):
  ```bash
  python3 -m src.beancount_exporter sample/moneydance.json -o my_beancount_ledger/
  ```
* **Ignore Future Transactions**:
  ```bash
  python3 -m src.beancount_exporter sample/moneydance.json --ignore-future
  ```

---

## Configuration (`commodity_map.yaml`)

On startup, `m2b` checks for `commodity_map.yaml` in the current working directory. If it is missing, a default configuration file will be automatically scaffolded for you.

### Structure:
```yaml
settings:
  # Base currencies declared as operating currencies in Beancount
  operating_currencies: ["TWD", "USD", "EUR"]
  
  # Exclude records dated in the future
  ignore_future: false

translations:
  # Map Moneydance commodity names/tickers to compliant Beancount ASCII symbols
  "中華電信": "CH_TELECOM"
  "元大台灣50": "YUANTA_TW50"
```

* **Precedence Rule**: CLI argument overrides (e.g., `--ignore-future` or `--base-currencies`) take precedence over configurations defined in `commodity_map.yaml`.

---

## Architecture Design

The project separates parsing concerns from ledger formatting:

* **[src/database.py](file:///Users/zombie/Projects/m2b/src/database.py)**: Parses raw exported Moneydance ledger JSON files and builds format-neutral models.
* **[src/config.py](file:///Users/zombie/Projects/m2b/src/config.py)**: Manages configuration settings loading, YAML mapping, and default config file creation.
* **[src/exporter/beancount/](file:///Users/zombie/Projects/m2b/src/exporter/beancount/)**: Houses Beancount-specific formatting, path routing, and commodity mapping logic.
* **[src/beancount_exporter.py](file:///Users/zombie/Projects/m2b/src/beancount_exporter.py)**: Serves as the CLI parser facade and command entrypoint.

---

## Development Hints

### Running Tests
Always run the test suites to verify code modifications do not introduce regressions:
```bash
# Run all unit tests
.venv/bin/python -m unittest discover -s tests -p "test_*.py"

# Run database import integration tests
.venv/bin/python -m unittest src/tests.py
```

### Adding a New Target Exporter (e.g. Ledger or hledger)
To support exporting to another ledger format:
1. Inherit from the abstract class `BaseExporter` defined in [src/exporter/base.py](file:///Users/zombie/Projects/m2b/src/exporter/base.py).
2. Implement the required `export` (single-file string) and `export_multi` (multi-file writer) methods.
3. Call it from a customized CLI flag inside the main facade.

### Development Stance (OpenSpec Workflow)
We follow the **OpenSpec agentic workflow** to trace design and implementation:
1. **Explore**: Use `/opsx-explore` to map codebase points and tradeoffs. Do not edit source files during explore mode.
2. **Propose**: Generate requirement specifications under `openspec/specs/` and tasks in `tasks.md` using `/opsx-propose`.
3. **Build**: Code sequentially and check off task checkboxes.
4. **Archive**: Use `/opsx-archive` to move specs and proposals into `openspec/changes/archive/` upon completion.
