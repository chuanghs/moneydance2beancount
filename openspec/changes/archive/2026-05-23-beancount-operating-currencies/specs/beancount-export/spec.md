## MODIFIED Requirements

### Requirement: Price History Extraction
The system SHALL extract all historical price points from Moneydance `csnap` objects and generate corresponding Beancount `price` directives. The system SHALL validate each price record before export, ensuring both the capital (source currency/security) and the target currency (base currency) are identified by non-empty codes. Any record failing this validation SHALL be skipped. **If multiple operating currencies are defined, the system SHALL use the first currency in the list as the default target for price directives, unless a specific mapping exists.**

#### Scenario: Price point generation
- **WHEN** a `csnap` object exists for "AAPL" on 2026-05-21 with a calculated price of 150.00 USD
- **THEN** a directive "2026-05-21 price AAPL 150.00 USD" SHALL be generated

#### Scenario: Skipping incomplete price record (Missing Capital)
- **WHEN** a `csnap` object exists with a missing or empty currency code
- **THEN** the record SHALL be skipped and no Beancount directive generated

#### Scenario: Skipping incomplete price record (Missing Target Currency)
- **WHEN** the export is performed without providing a valid base currency
- **THEN** all price records referencing that base currency SHALL be skipped
