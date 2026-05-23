## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. **The system SHALL collapse security accounts (SecurityInfo) into their parent Investment accounts, mapping them to the same Beancount path.** It SHALL add a `"FIFO"` booking policy to any Beancount account that contains security holdings to facilitate automatic lot matching.

#### Scenario: Account with FIFO booking
- **WHEN** an account path contains a `SecurityInfo` account
- **THEN** the resulting `open` directive SHALL include `"FIFO"` (e.g., `open Assets:Investment:Schwab USD "FIFO"`)

### Requirement: Exchange Rate Handling
The system SHALL use appropriate Beancount syntax for transactions involving multiple currencies or commodities.
- For **Currency Exchanges** (Asset/Expense accounts), the system SHALL use the `@@` (Total Price) syntax.
- For **Security Purchases** (quantity increases), the system SHALL use the `{{ }}` (Total Cost) syntax.
- For **Security Sales** (quantity decreases), the system SHALL use the `{}` (Lot Matcher) syntax combined with `@@` (Total Price).
- **Initial balances** for securities SHALL also use cost notation `{{ 0 BASE_CURR }}`.

#### Scenario: Security sale with lot matching
- **WHEN** 5 shares of "VT" are sold for 600.00 USD
- **THEN** the posting SHALL be to `Assets:Investment:Schwab -5 VT {} @@ 600.00 USD`

#### Scenario: Security initial balance with cost
- **WHEN** an account starts with 10 shares of "VT" and the investment base currency is USD
- **THEN** the opening balance posting SHALL be `Assets:Investment:Schwab 10 VT {{ 0 USD }}`
