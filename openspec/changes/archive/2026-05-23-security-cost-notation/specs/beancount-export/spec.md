## MODIFIED Requirements

### Requirement: Exchange Rate Handling
The system SHALL use appropriate Beancount syntax for transactions involving multiple currencies or commodities.
- For **Currency Exchanges** (Asset/Expense accounts), the system SHALL use the `@@` (Total Price) syntax.
- For **Security Purchases** (where the receiver is a `SecurityInfo` account and quantity is positive), the system SHALL use the `{{ }}` (Total Cost) syntax to establish a cost basis for lot tracking.
- The system SHALL use raw `pamt` and `samt` values directly to ensure precision and correct balancing.

#### Scenario: Multi-currency transfer
- **WHEN** 100.00 USD is transferred from HSBC USD to HSBC TWD resulting in 3000.00 TWD
- **THEN** the Beancount transaction SHALL include a posting for HSBC USD at -100.00 USD and a posting for HSBC TWD at `3000.00 TWD @@ 100.00 USD`

#### Scenario: Security purchase with cost basis
- **WHEN** 10 shares of "VT" are bought for 1000.00 USD in account "Schwab"
- **THEN** the posting SHALL be to `Assets:Investment:Schwab 10 VT {{ 1000.00 USD }}`

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. It SHALL use the raw Moneydance `pamt` and `samt` signs directly to ensure correct accounting polarity. It SHALL shift decimal points based on the currency's decimal precision. It SHALL map Moneydance status flags to Beancount status characters. The system SHALL escape the transaction description to ensure valid Beancount syntax. **Postings involving securities SHALL use the parent Investment account path while specifying the security's commodity code.**

#### Scenario: Standard transaction export
- **WHEN** a transaction for "Lunch" with amount 2500 (2 decimals) is exported from "Checking" to "Dining"
- **THEN** the output SHALL include a balanced Beancount transaction with Assets:Checking at -25.00 and Expenses:Dining at 25.00

#### Scenario: Security purchase
- **WHEN** 10 shares of "VT" are bought in account "Schwab"
- **THEN** the posting SHALL be to `Assets:Investment:Schwab` with commodity `VT` and appropriate cost notation.
