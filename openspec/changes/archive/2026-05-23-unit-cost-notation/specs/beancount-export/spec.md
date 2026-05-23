## MODIFIED Requirements

### Requirement: Exchange Rate Handling
The system SHALL use appropriate Beancount syntax for transactions involving multiple currencies or commodities.
- For **Security Purchases** (quantity increases), the system SHALL use the `{ }` (Unit Cost) syntax. The unit cost SHALL be calculated as `Total Cost / Quantity`.

#### Scenario: Security purchase with unit cost
- **WHEN** 5 shares of "CDNS" are purchased for a total of 1500.00 USD
- **THEN** the posting SHALL be `Assets:Investment:ETrade 5 CDNS { 300.00 USD }`
