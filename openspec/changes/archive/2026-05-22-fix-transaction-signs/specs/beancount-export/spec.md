## MODIFIED Requirements

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. It SHALL use the raw Moneydance `pamt` and `samt` signs directly to ensure correct accounting polarity. It SHALL shift decimal points based on the currency's decimal precision. It SHALL map Moneydance status flags to Beancount status characters.

#### Scenario: Standard transaction export
- **WHEN** a transaction for "Lunch" with amount 2500 (2 decimals) is exported from "Checking" to "Dining"
- **THEN** the output SHALL include a balanced Beancount transaction with Assets:Checking at -25.00 and Expenses:Dining at 25.00

### Requirement: Exchange Rate Handling
The system SHALL use the Beancount `@@` (Total Price) syntax for transactions involving multiple currencies. It SHALL use the raw `pamt` and `samt` values directly to ensure precision and correct balancing without intermediate floating-point math or artificial negation.

#### Scenario: Multi-currency transfer
- **WHEN** 100.00 USD is transferred from HSBC USD to HSBC TWD resulting in 3000.00 TWD
- **THEN** the Beancount transaction SHALL include a posting for HSBC USD at -100.00 USD and a posting for HSBC TWD at "3000.00 TWD @@ 100.00 USD"
