## NEW Requirements

### Requirement: Multi-file Export Support
The system SHALL support exporting the ledger into multiple categorized files within an `export/` directory.

#### Scenario: File structure generation
- **GIVEN** a database with accounts and transactions
- **WHEN** multi-file export is triggered
- **THEN** the system SHALL create the following files in the `export/` directory:
    - `main.beancount`
    - `commodity.beancount`
    - `prices.beancount`
    - `assets.beancount`
    - `investment.beancount`
    - `liability.beancount`
    - `daily.beancount`

#### Scenario: Transaction routing priority
The system SHALL route transactions to files based on the following priority:
1. **DAILY**: Any transaction touching an account with "Cash" or "現金" in its name SHALL be routed to `daily.beancount`.
2. **INVESTMENT**: Any remaining transaction touching an Investment or Security account SHALL be routed to `investment.beancount`.
3. **LIABILITY**: Any remaining transaction touching a Liability, Loan, or Credit Card account SHALL be routed to `liability.beancount`.
4. **ASSETS**: Any remaining transaction touching a Bank or non-investment Asset account SHALL be routed to `assets.beancount`.
5. **MAIN**: All other transactions (e.g., Income/Expenses only) SHALL be routed to `main.beancount`.

#### Scenario: Account definition routing
Accounts SHALL be defined (`open` directive) in the file corresponding to their category:
- `assets.beancount`: BankInfo, AssetInfo
- `investment.beancount`: InvestmentInfo, SecurityInfo
- `liability.beancount`: LiabilityInfo, LoanInfo, CreditCardInfo
- `main.beancount`: IncomeInfo, ExpenseInfo, Equity:OpeningBalances

#### Scenario: Opening balance routing
The initial balance transaction for an account SHALL be placed in the same file where that account is defined.
