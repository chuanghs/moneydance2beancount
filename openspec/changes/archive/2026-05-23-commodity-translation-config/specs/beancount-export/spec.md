## MODIFIED Requirements

### Requirement: Commodity Identity and Export
The system SHALL extract and export all currencies and securities as Beancount `commodity` directives. **The system SHALL select the most descriptive code for each commodity using the following priority:**
1. Manual translation from `commodity_map.yaml` (if configured)
2. Official `ticker` (if present)
3. `currid` (if not an internal GUID)
4. Normalized `name` (slugified)

The system SHALL generate a `commodity` directive for each, including `name` and `md_id` metadata. All generated codes SHALL be sanitized to comply with Beancount's strict uppercase ASCII requirements.

#### Scenario: Commodity code selection (Ticker present)
- **WHEN** a security has ticker `VT` and name `Vanguard Total World`
- **THEN** the Beancount commodity code SHALL be `VT`

#### Scenario: Commodity code selection (GUID fallback)
- **WHEN** a security has ticker `""`, currid `5c02d8d8-...`, and name `My Fund`
- **THEN** the Beancount commodity code SHALL be `MyFund`

#### Scenario: Commodity code selection (Manual Translation)
- **WHEN** a security has name "中華電信" and ticker "2412", and the map contains `"中華電信": "CH_TELECOM"`
- **THEN** the Beancount commodity code SHALL be `CH_TELECOM`
