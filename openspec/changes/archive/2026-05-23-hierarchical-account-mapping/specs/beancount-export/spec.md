## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. It SHALL preserve the account hierarchy while excluding the root account. The system SHALL map accounts to hierarchical Beancount categories based on their type:
- `BankInfo` -> `Assets:Bank`
- `InvestmentInfo` and `SecurityInfo` -> `Assets:Investment`
- `AssetInfo` -> `Assets`
- `CreditCardInfo`, `LiabilityInfo`, and `LoanInfo` -> `Liabilities`
- `IncomeInfo` -> `Income`
- `ExpenseInfo` -> `Expenses`

The system SHALL support Unicode letters and numbers in account names, following Beancount v3 naming rules (allowing components to start with digits and containing any Unicode letter). The system SHALL prevent redundant components if an account's name or its parent's name matches the sub-category (e.g., preventing `Assets:Bank:Bank:Checking`).

#### Scenario: Successful normalization of nested account
- **WHEN** an account path is "Personal Finances" > "Bank" > "Chase Checking 123"
- **THEN** the resulting Beancount account SHALL be "Assets:Bank:ChaseChecking123"

#### Scenario: Normalization of bank account without parent
- **WHEN** an account name is "HSBC Checking" and has BankInfo (parent is Root)
- **THEN** the resulting Beancount account SHALL be "Assets:Bank:HSBCChecking"

#### Scenario: Normalization of investment security
- **WHEN** a security "AAPL" is held in "ETrade" (InvestmentInfo)
- **THEN** the resulting Beancount account SHALL be "Assets:Investment:ETrade:AAPL"
