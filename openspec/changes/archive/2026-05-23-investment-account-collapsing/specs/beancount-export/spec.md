## MODIFIED Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. **The system SHALL collapse security accounts (SecurityInfo) into their parent Investment accounts, mapping them to the same Beancount path.** The system SHALL map accounts to hierarchical Beancount categories based on their type:
- `BankInfo` -> `Assets:Bank`
- `InvestmentInfo` -> `Assets:Investment`
- `AssetInfo` -> `Assets:Cash`
- `CreditCardInfo` -> `Liabilities:Card`
- `LiabilityInfo` and `LoanInfo` -> `Liabilities`
- `IncomeInfo` -> `Income`
- `ExpenseInfo` -> `Expenses`

#### Scenario: Collapsing security into investment account
- **WHEN** a security "VCSH" exists under Investment account "Schwab"
- **THEN** both the Schwab account and the VCSH security account SHALL map to `Assets:Investment:Schwab`

### Requirement: Commodity Identity and Export
The system SHALL extract and export all currencies and securities as Beancount `commodity` directives. **The system SHALL select the most descriptive code for each commodity using the following priority:**
1. Official `ticker` (if present)
2. `currid` (if not an internal GUID)
3. Normalized `name` (slugified)

The system SHALL generate a `commodity` directive for each, including `name` and `md_id` metadata.

#### Scenario: Commodity code selection (Ticker present)
- **WHEN** a security has ticker `VT` and name `Vanguard Total World`
- **THEN** the Beancount commodity code SHALL be `VT`

#### Scenario: Commodity code selection (GUID fallback)
- **WHEN** a security has ticker `""`, currid `5c02d8d8-...`, and name `My Fund`
- **THEN** the Beancount commodity code SHALL be `MyFund`

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. **Postings involving securities SHALL use the parent Investment account path while specifying the security's commodity code.**

#### Scenario: Security purchase
- **WHEN** 10 shares of "VT" are bought in account "Schwab"
- **THEN** the posting SHALL be to `Assets:Investment:Schwab` with commodity `VT`
