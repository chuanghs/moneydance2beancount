# Capability: Ignore Future Records

## Requirements

### Requirement: Ignore Future Records
The exporter system SHALL support filtering and excluding future-dated ledger records to avoid exporting pending/unconfirmed future transactions, price snapshots, or budgets.

### Requirement: cutoff-date and ignore-future parameters
The exporter system SHALL accept `--ignore-future` or `--cutoff-date YYYY-MM-DD` parameters in CLI or `ignore_future: true` / `cutoff_date: "YYYY-MM-DD"` in the `settings` block of `commodity_map.yaml`.
* CLI parameters take precedence over YAML configuration settings.
* Dates are checked via date-only (calendar) comparisons.
* Skips/filtering counts are logged to `sys.stderr`.
