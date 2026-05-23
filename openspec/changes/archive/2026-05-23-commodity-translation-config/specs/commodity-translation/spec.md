## ADDED Requirements

### Requirement: Configuration-Based Translation
The system SHALL support an external configuration file (defaulting to `commodity_map.yaml`) that defines manual translations for commodity identifiers. If a commodity's name or ticker exists in this map, the system SHALL use the mapped value as the primary identifier.

#### Scenario: Manual translation of Chinese commodity
- **WHEN** the translation map contains `"中華電信": "CH_TELECOM"`
- **THEN** a security with name "中華電信" SHALL use `CH_TELECOM` as its Beancount commodity code

### Requirement: Automatic Digit Prefixing
The system SHALL automatically prepend `SYM_` to any commodity identifier (ticker, code, or name) that starts with a decimal digit (0-9). This rule SHALL be applied AFTER the manual translation check but BEFORE final validation.

#### Scenario: Ticker starting with digit
- **WHEN** a security has ticker `2412` and no manual translation exists
- **THEN** the Beancount commodity code SHALL be `SYM_2412`

#### Scenario: Ticker starting with digit and letters
- **WHEN** a security has ticker `0050TW`
- **THEN** the Beancount commodity code SHALL be `SYM_0050TW`

### Requirement: Strict Beancount Commodity Validation
The system SHALL ensure that all generated commodity identifiers comply with strict Beancount v3 syntax:
1. MUST start with an uppercase ASCII letter (A-Z).
2. MUST only contain uppercase ASCII letters, decimal digits, and a limited set of symbols (`.`, `_`, `-`, `'`).
3. MUST NOT exceed 24 characters.
The system SHALL automatically capitalize and sanitize identifiers to meet these rules.

#### Scenario: Sanitization of lowercase ticker
- **WHEN** a security has ticker `vt`
- **THEN** the Beancount commodity code SHALL be `VT`

#### Scenario: Stripping invalid characters
- **WHEN** a ticker is `AAPL$`
- **THEN** the Beancount commodity code SHALL be `AAPL`
