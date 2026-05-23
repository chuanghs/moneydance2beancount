## ADDED Requirements

### Requirement: String Data Safety
The system SHALL ensure that all free-text strings (descriptions, metadata, comments) are properly escaped when wrapped in double quotes in the Beancount file. Specifically, it SHALL escape backslashes (`\`) as `\\` and double quotes (`"`) as `\"`.

#### Scenario: Escaping quotes in transaction description
- **WHEN** a transaction has description `Bought "Lunch"`
- **THEN** the output line SHALL be `YYYY-MM-DD * "Bought \"Lunch\""`

#### Scenario: Escaping backslashes in account comment
- **WHEN** an account has comment `Path: C:\Users`
- **THEN** the metadata line SHALL be `comment: "Path: C:\\Users"`

## MODIFIED Requirements

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. It SHALL use the raw Moneydance `pamt` and `samt` signs directly to ensure correct accounting polarity. It SHALL shift decimal points based on the currency's decimal precision. It SHALL map Moneydance status flags to Beancount status characters. The system SHALL escape the transaction description to ensure valid Beancount syntax.

#### Scenario: Standard transaction export
- **WHEN** a transaction for "Lunch" with amount 2500 (2 decimals) is exported from "Checking" to "Dining"
- **THEN** the output SHALL include a balanced Beancount transaction with Assets:Checking at -25.00 and Expenses:Dining at 25.00
