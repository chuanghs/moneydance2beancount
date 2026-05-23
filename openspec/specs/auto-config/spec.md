## ADDED Requirements

### Requirement: Automatic Config Scaffolding
The system SHALL detect if `commodity_map.yaml` exists in the current working directory. If it is missing, the system SHALL automatically create a default file with a predefined template.

#### Scenario: Missing config on startup
- **WHEN** the exporter is run and `commodity_map.yaml` does not exist
- **THEN** a new `commodity_map.yaml` file SHALL be created with default settings and empty translations

### Requirement: Default Settings Template
The automatically generated configuration file SHALL include a `settings` block with `operating_currencies` defaulted to `["TWD", "USD", "EUR"]`. It SHALL also include a `translations` block with at least one commented-out sample entry (e.g., `"中華電信": "CH_TELECOM"`) to guide the user.

#### Scenario: Correct template content with samples
- **WHEN** the default config is generated
- **THEN** the file SHALL contain the `settings` key, the `translations` key, and a commented-out sample mapping
