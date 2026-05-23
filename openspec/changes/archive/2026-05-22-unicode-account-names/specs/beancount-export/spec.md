## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. It SHALL preserve the account hierarchy while excluding the root account. The system SHALL support Unicode letters and numbers in account names, following Beancount v3 naming rules (allowing components to start with digits and containing any Unicode letter).

#### Scenario: Successful normalization of nested account
- **WHEN** an account path is "Personal Finances" > "Bank" > "Chase Checking 123"
- **THEN** the resulting Beancount account SHALL be "Assets:Bank:ChaseChecking123"

#### Scenario: Normalization of account starting with a digit
- **WHEN** an account name is "2024 Taxes"
- **THEN** the resulting Beancount component SHALL be "2024Taxes"

#### Scenario: Normalization of Unicode account name
- **WHEN** an account name is "Dining 餐饮"
- **THEN** the resulting Beancount component SHALL be "Dining餐饮"

#### Scenario: Normalization of CJK-only account name
- **WHEN** an account name is "账户"
- **THEN** the resulting Beancount component SHALL be "账户"
