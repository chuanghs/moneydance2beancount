## MODIFIED Requirements

### Requirement: Price History Export
The system SHALL export historical exchange rates as Beancount `price` directives. **It SHALL use the Moneydance base currency as the target currency for all prices.** It SHALL invert the Moneydance `urt` value (`1 / urt`) to ensure the price represents the cost of 1 unit of the commodity in the base currency. It SHALL use high precision (at least 8 decimal places) for price values.

#### Scenario: Correct price direction
- **WHEN** Moneydance has a base currency of TWD and a USD snapshot with `urt` 0.033333
- **THEN** the exporter SHALL produce `DATE price USD 30.00000000 TWD`

#### Scenario: Security price export
- **WHEN** a stock has `urt` 0.0004 (Units per TWD)
- **THEN** the exporter SHALL produce `DATE price STOCK 2500.00000000 TWD`
