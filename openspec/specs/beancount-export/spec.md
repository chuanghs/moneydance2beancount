## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. **The system SHALL collapse security accounts (SecurityInfo) into their parent Investment accounts, mapping them to the same Beancount path.** It SHALL add a `"FIFO"` booking policy to any Beancount account that contains security holdings to facilitate automatic lot matching.

#### Scenario: Account with FIFO booking
- **WHEN** an account path contains a `SecurityInfo` account
- **THEN** the resulting `open` directive SHALL include `"FIFO"` (e.g., `open Assets:Investment:Schwab USD "FIFO"`)

### Requirement: Exchange Rate Handling
The system SHALL use appropriate Beancount syntax for transactions involving multiple currencies or commodities.
- For **Currency Exchanges** (Asset/Expense accounts), the system SHALL use the `@@` (Total Price) syntax.
- For **Security Purchases** (quantity increases), the system SHALL use the `{ }` (Unit Cost) syntax. The unit cost SHALL be calculated as `Total Cost / Quantity`.
- For **Security Sales** (quantity decreases), the system SHALL use the `{}` (Lot Matcher) syntax combined with `@@` (Total Price).
- **Initial balances** for securities SHALL also use cost notation `{{ 0 BASE_CURR }}`.

#### Scenario: Security purchase with unit cost
- **WHEN** 5 shares of "CDNS" are purchased for a total of 1500.00 USD
- **THEN** the posting SHALL be `Assets:Investment:ETrade 5 CDNS { 300.00 USD }`

#### Scenario: Security sale with lot matching
- **WHEN** 5 shares of "VT" are sold for 600.00 USD
- **THEN** the posting SHALL be to `Assets:Investment:Schwab -5 VT {} @@ 600.00 USD`

#### Scenario: Security initial balance with cost
- **WHEN** an account starts with 10 shares of "VT" and the investment base currency is USD
- **THEN** the opening balance posting SHALL be `Assets:Investment:Schwab 10 VT {{ 0 USD }}`

### Requirement: Hierarchical Price History Export
The system SHALL export historical exchange rates as Beancount `price` directives. It SHALL respect the currency hierarchy defined in Moneydance by targeting the specific parent currency for each commodity.

- If a commodity is relative to a specific currency (e.g., CDNS relative to USD), the `price` directive SHALL target that specific currency.
- If no specific parent is defined, or it is the base currency, the `price` directive SHALL target the Moneydance base currency.

It SHALL invert the Moneydance `urt` value (`1 / urt`) to ensure the price represents the cost of 1 unit of the commodity in the target currency. It SHALL use high precision (at least 8 decimal places) for price values.

**The system SHALL include price snapshots for commodities even if their raw currency code (currid) is empty, provided a valid Beancount commodity symbol can be derived from their name or ticker.**

#### Scenario: Hierarchical price export
- **GIVEN** a base currency of TWD
- **GIVEN** a stock "CDNS" defined as relative to "USD"
- **GIVEN** a price snapshot for "CDNS" of 0.00285 USD (meaning 1 USD = 0.00285 CDNS)
- **WHEN** prices are exported
- **THEN** the system SHALL produce a `price` directive: `DATE price CDNS 350.87719298 USD`

#### Scenario: Price export with empty currency code
- **GIVEN** a commodity named "YUANTA_TW50" with an empty `currid` and a price snapshot of 0.010 TWD
- **WHEN** prices are exported
- **THEN** the system SHALL produce a `price` directive: `DATE price YUANTA_TW50 100.00000000 TWD`
