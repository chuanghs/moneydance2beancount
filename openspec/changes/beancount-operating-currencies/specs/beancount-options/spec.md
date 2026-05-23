## ADDED Requirements

### Requirement: Default Operating Currencies
The system SHALL set the default operating currencies to `TWD`, `USD`, and `EUR` if no currencies are provided via command-line arguments or configuration.

#### Scenario: No currency provided
- **WHEN** the export is run without any currency arguments
- **THEN** the Beancount file SHALL include `option "operating_currency" "TWD"`, `option "operating_currency" "USD"`, and `option "operating_currency" "EUR"`

### Requirement: Multi-Currency Configuration
The system SHALL support specifying multiple operating currencies via a comma-separated list in the CLI or a list in the `commodity_map.yaml` file.

#### Scenario: Multiple currencies in CLI
- **WHEN** the user provides `USD,JPY` as the base currency argument
- **THEN** the Beancount file SHALL include both `USD` and `JPY` as operating currencies

### Requirement: Auto-Detection of Ledger Title
The system SHALL attempt to detect the Moneydance root account name (e.g., "My Finances") and use it as the Beancount `title` option.

#### Scenario: Root account detection
- **WHEN** the root account name in Moneydance is "Personal Ledger"
- **THEN** the Beancount file SHALL include `option "title" "Personal Ledger"`
