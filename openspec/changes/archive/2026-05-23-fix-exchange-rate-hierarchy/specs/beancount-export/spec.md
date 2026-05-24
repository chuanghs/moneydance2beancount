## MODIFIED Requirements

### Requirement: Hierarchical Price History Export
The system SHALL export historical exchange rates as Beancount `price` directives. It SHALL respect the currency hierarchy defined in Moneydance by targeting the specific parent currency for each commodity.

- If a commodity is relative to a specific currency (e.g., CDNS relative to USD), the `price` directive SHALL target that specific currency.
- If no specific parent is defined, or it is the base currency, the `price` directive SHALL target the Moneydance base currency.

#### Scenario: Hierarchical price export
- **GIVEN** a base currency of TWD
- **GIVEN** a stock "CDNS" defined as relative to "USD"
- **GIVEN** a price snapshot for "CDNS" of 0.00285 USD (meaning 1 USD = 0.00285 CDNS)
- **WHEN** prices are exported
- **THEN** the system SHALL produce a `price` directive: `DATE price CDNS 350.87719298 USD`
