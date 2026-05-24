## ADDED Requirements

### Requirement: Ignore Future Records
The system SHALL support an option to ignore/exclude all Transactions, Price Snapshots, and Budget Items that are dated in the future.

#### Scenario: Enabled via CLI
- **WHEN** the exporter is run with the `--ignore-future` or `-i` flag
- **THEN** all transactions, prices, and budgets dated after today's calendar date SHALL be excluded from the export output, and a summary warning of ignored records SHALL be printed to standard error.

#### Scenario: Cutoff date CLI override
- **WHEN** the exporter is run with `--cutoff-date YYYY-MM-DD` or `-d YYYY-MM-DD`
- **THEN** all records dated strictly after that cutoff date SHALL be filtered out of the export.
