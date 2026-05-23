## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. It SHALL preserve the account hierarchy while excluding the root account. The system SHALL map accounts to hierarchical Beancount categories based on their type:
- `BankInfo` -> `Assets:Bank`
- `InvestmentInfo` and `SecurityInfo` -> `Assets:Investment`
- `AssetInfo` -> `Assets:Cash`
- `CreditCardInfo` -> `Liabilities:Card`
- `LiabilityInfo` and `LoanInfo` -> `Liabilities`
- `IncomeInfo` -> `Income`
- `ExpenseInfo` -> `Expenses`

The system SHALL support Unicode letters and numbers in account names, following Beancount v3 naming rules. The system SHALL convert account names containing parentheses (e.g., "A(B)") into hierarchical Beancount components (e.g., "A:B"). The system SHALL prevent redundant components if an account's name or its parent's name matches the sub-category (e.g., preventing `Assets:Cash:Cash`).

#### Scenario: Successful normalization of cash account
- **WHEN** an account name is "現金" and has AssetInfo
- **THEN** the resulting Beancount account SHALL be "Assets:Cash:現金"

#### Scenario: Normalization of account with parentheses
- **WHEN** an account name is "富邦(宇萱)"
- **THEN** the resulting Beancount path SHALL include "富邦:宇萱"

#### Scenario: Normalization of credit card
- **WHEN** an account name is "HSBC Card" and has CreditCardInfo
- **THEN** the resulting Beancount account SHALL be "Liabilities:Card:HSBCCard"

#### Scenario: Prevention of redundancy in cash path
- **WHEN** an account name is "Cash" and has AssetInfo
- **THEN** the resulting Beancount account SHALL be "Assets:Cash"
