## MODIFIED Requirements

### Requirement: Price History Export
The system SHALL export historical exchange rates as Beancount `price` directives. It SHALL use the Moneydance base currency as the target currency for all prices. It SHALL invert the Moneydance `urt` value (`1 / urt`) to ensure the price represents the cost of 1 unit of the commodity in the base currency. It SHALL use high precision (at least 8 decimal places) for price values.

**The system SHALL include price snapshots for commodities even if their raw currency code (currid) is empty, provided a valid Beancount commodity symbol can be derived from their name or ticker.**

#### Scenario: Price export with empty currency code
- **GIVEN** a commodity named "YUANTA_TW50" with an empty `currid` and a price snapshot of 0.010 TWD
- **WHEN** prices are exported
- **THEN** the system SHALL produce a `price` directive: `DATE price YUANTA_TW50 100.00000000 TWD`
