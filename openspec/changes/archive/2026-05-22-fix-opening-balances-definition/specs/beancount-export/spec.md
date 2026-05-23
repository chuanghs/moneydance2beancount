## ADDED Requirements

### Requirement: Mandatory Account Definitions
The system SHALL ensure that all accounts referenced in the exported file are explicitly opened with an `open` directive. This specifically includes virtual accounts like `Equity:OpeningBalances` which are used for initial balance adjustments.

#### Scenario: Opening balance account definition
- **WHEN** the accounts section is generated
- **THEN** an `open Equity:OpeningBalances` directive SHALL be included at the beginning of the section
