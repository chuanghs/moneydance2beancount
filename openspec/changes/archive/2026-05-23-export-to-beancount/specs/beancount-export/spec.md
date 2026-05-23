## ADDED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. It SHALL preserve the account hierarchy while excluding the root account. If an account component starts with a digit, the system SHALL prefix it with an 'A'.

#### Scenario: Successful normalization of nested account
- **WHEN** an account path is "Personal Finances" > "Bank" > "Chase Checking 123"
- **THEN** the resulting Beancount account SHALL be "Assets:Bank:ChaseChecking123"

#### Scenario: Normalization of account starting with a digit
- **WHEN** an account name is "2024 Taxes"
- **THEN** the resulting Beancount component SHALL be "A2024Taxes"

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. It SHALL shift decimal points based on the currency's decimal precision. It SHALL map Moneydance status flags to Beancount status characters.

#### Scenario: Standard transaction export
- **WHEN** a transaction for "Lunch" with amount 2500 (2 decimals) is exported from "Checking" to "Dining"
- **THEN** the output SHALL include a balanced Beancount transaction with amounts -25.00 and 25.00

### Requirement: Exchange Rate Handling
The system SHALL use the Beancount `@@` (Total Price) syntax for transactions involving multiple currencies. It SHALL use the raw `pamt` and `samt` values to ensure precision without intermediate floating-point math.

#### Scenario: Multi-currency transfer
- **WHEN** 100.00 USD is transferred to a TWD account resulting in 3000.00 TWD
- **THEN** the Beancount posting for the TWD account SHALL be "3000.00 TWD @@ 100.00 USD"

### Requirement: Price History Extraction
The system SHALL extract all historical price points from Moneydance `csnap` objects and generate corresponding Beancount `price` directives.

#### Scenario: Price point generation
- **WHEN** a `csnap` object exists for "AAPL" on 2026-05-21 with a calculated price of 150.00 USD
- **THEN** a directive "2026-05-21 price AAPL 150.00 USD" SHALL be generated

### Requirement: Budget Export
The system SHALL export Moneydance budget items using the Fava-compatible `custom "budget"` syntax. It SHALL map Moneydance intervals to the appropriate frequency strings.

#### Scenario: Budget item export
- **WHEN** a monthly budget item for "Groceries" exists with amount 500.00
- **THEN** a directive `2026-01-01 custom "budget" Expenses:Groceries "monthly" 500.00 USD` SHALL be generated
