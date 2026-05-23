# beancount-export

## Requirements

### Requirement: Account Normalization
The system SHALL normalize Moneydance account names into Beancount-compliant CamelCase components. It SHALL preserve the account hierarchy while excluding the root account. **The system SHALL collapse security accounts (SecurityInfo) into their parent Investment accounts, mapping them to the same Beancount path.** The system SHALL map accounts to hierarchical Beancount categories based on their type:
- `BankInfo` -> `Assets:Bank`
- `InvestmentInfo` -> `Assets:Investment`
- `AssetInfo` -> `Assets:Cash`
- `CreditCardInfo` -> `Liabilities:Card`
- `LiabilityInfo` and `LoanInfo` -> `Liabilities`
- `IncomeInfo` -> `Income`
- `ExpenseInfo` -> `Expenses`

The system SHALL support Unicode letters and numbers in account names, following Beancount v3 naming rules. The system SHALL convert account names containing parentheses (e.g., "A(B)") into hierarchical Beancount components (e.g., "A:B"). The system SHALL prevent redundant components if an account's name or its parent's name matches the sub-category (e.g., preventing `Assets:Cash:Cash`).

#### Scenario: Successful normalization of cash account
- **WHEN** an account name is "現金" and has AssetInfo
- **THEN** the resulting Beancount account SHALL be "Assets:Cash:現金"

#### Scenario: Collapsing security into investment account
- **WHEN** a security "VCSH" exists under Investment account "Schwab"
- **THEN** both the Schwab account and the VCSH security account SHALL map to `Assets:Investment:Schwab`

#### Scenario: Normalization of credit card
- **WHEN** an account name is "HSBC Card" and has CreditCardInfo
- **THEN** the resulting Beancount account SHALL be "Liabilities:Card:HSBCCard"

#### Scenario: Prevention of redundancy in cash path
- **WHEN** an account name is "Cash" and has AssetInfo
- **THEN** the resulting Beancount account SHALL be "Assets:Cash"

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

### Requirement: Mandatory Account Definitions
The system SHALL ensure that all accounts referenced in the exported file are explicitly opened with an `open` directive. This specifically includes virtual accounts like `Equity:OpeningBalances` which are used for initial balance adjustments.

#### Scenario: Opening balance account definition
- **WHEN** the accounts section is generated
- **THEN** an `open Equity:OpeningBalances` directive SHALL be included at the beginning of the section

### Requirement: Transaction Transformation
The system SHALL transform Moneydance Transactions and their Splits into zero-sum Beancount transactions. It SHALL use the raw Moneydance `pamt` and `samt` signs directly to ensure correct accounting polarity. It SHALL shift decimal points based on the currency's decimal precision. It SHALL map Moneydance status flags to Beancount status characters. The system SHALL escape the transaction description to ensure valid Beancount syntax. **Postings involving securities SHALL use the parent Investment account path while specifying the security's commodity code.**

#### Scenario: Standard transaction export
- **WHEN** a transaction for "Lunch" with amount 2500 (2 decimals) is exported from "Checking" to "Dining"
- **THEN** the output SHALL include a balanced Beancount transaction with Assets:Checking at -25.00 and Expenses:Dining at 25.00

#### Scenario: Security purchase
- **WHEN** 10 shares of "VT" are bought in account "Schwab"
- **THEN** the posting SHALL be to `Assets:Investment:Schwab` with commodity `VT`

### Requirement: Exchange Rate Handling
The system SHALL use the Beancount `@@` (Total Price) syntax for transactions involving multiple currencies. It SHALL use the raw `pamt` and `samt` values directly to ensure precision and correct balancing without intermediate floating-point math or artificial negation.

#### Scenario: Multi-currency transfer
- **WHEN** 100.00 USD is transferred from HSBC USD to HSBC TWD resulting in 3000.00 TWD
- **THEN** the Beancount transaction SHALL include a posting for HSBC USD at -100.00 USD and a posting for HSBC TWD at "3000.00 TWD @@ 100.00 USD"

### Requirement: Price History Extraction
The system SHALL extract all historical price points from Moneydance `csnap` objects and generate corresponding Beancount `price` directives. The system SHALL validate each price record before export, ensuring both the capital (source currency/security) and the target currency (base currency) are identified by non-empty codes. Any record failing this validation SHALL be skipped.

#### Scenario: Price point generation
- **WHEN** a `csnap` object exists for "AAPL" on 2026-05-21 with a calculated price of 150.00 USD
- **THEN** a directive "2026-05-21 price AAPL 150.00 USD" SHALL be generated

#### Scenario: Skipping incomplete price record (Missing Capital)
- **WHEN** a `csnap` object exists with a missing or empty currency code
- **THEN** the record SHALL be skipped and no Beancount directive generated

#### Scenario: Skipping incomplete price record (Missing Target Currency)
- **WHEN** the export is performed without providing a valid base currency
- **THEN** all price records referencing that base currency SHALL be skipped

### Requirement: String Data Safety
The system SHALL ensure that all free-text strings (descriptions, metadata, comments) are properly escaped when wrapped in double quotes in the Beancount file. Specifically, it SHALL escape backslashes (`\`) as `\\` and double quotes (`"`) as `\"`.

#### Scenario: Escaping quotes in transaction description
- **WHEN** a transaction has description `Bought "Lunch"`
- **THEN** the output line SHALL be `YYYY-MM-DD * "Bought \"Lunch\""`

#### Scenario: Escaping backslashes in account comment
- **WHEN** an account has comment `Path: C:\Users`
- **THEN** the metadata line SHALL be `comment: "Path: C:\\Users"`

### Requirement: Budget Export
The system SHALL export Moneydance budget items using the Fava-compatible `custom "budget"` syntax. It SHALL map Moneydance intervals to the appropriate frequency strings.

#### Scenario: Budget item export
- **WHEN** a monthly budget item for "Groceries" exists with amount 500.00
- **THEN** a directive `2026-01-01 custom "budget" Expenses:Groceries "monthly" 500.00 USD` SHALL be generated
