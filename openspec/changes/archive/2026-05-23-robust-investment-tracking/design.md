## Context

The previous `security-cost-notation` change was incomplete because it only handled "Buy" transactions. This left "Sell" transactions and "Initial Balances" with no-cost lots, causing Beancount to fail validation.

## Goals / Non-Goals

**Goals:**
- Eliminate `bean-check` "No position matches" errors.
- Ensure all security holdings have cost basis from the start.
- Automate lot matching for sales using FIFO.

**Non-Goals:**
- Precise historical cost calculation for initial balances (out of scope for now, using zero as placeholder).
- Supporting complex booking policies (FIFO is the default for all).

## Decisions

### 1. Unified Security Notation
All postings to accounts containing securities will use costed inventory:
- `shares {{ total_cost CURR }}` for Buys.
- `shares {} @@ total_price CURR` for Sells.
- `shares {{ 0 CURR }}` for Initial Balances.

### 2. Automatic FIFO on Investment Accounts
The `export_accounts` logic will detect if a path contains any `SecurityInfo` records. If it does, it will append `"FIFO"` to the `open` directive.
- **Example**: `2026-01-01 open Assets:Investment:Brokerage USD,TWD "FIFO"`

### 3. Price Context for Sells
For sales, we use `@@` (Total Price) to reflect the cash received, while `{}` tells Beancount to pick an existing lot to reduce.

### 4. Automatic Balancing via Equity
Beancount requires transactions to balance at **cost**. Since security sales often result in capital gains/losses, and we don't have a specific gains account, we will add an empty `Equity:OpeningBalances` posting to any transaction that includes a security sale. Beancount will automatically fill this posting with the difference, ensuring the transaction balances.

## Risks / Trade-offs

- **[Risk]** Zero-cost initial balances hide performance history → **[Mitigation]** It's better than failing validation; users can manually update their ledger if they have the historical cost.
- **[Trade-off]** All securities use FIFO → **[Mitigation]** FIFO is the most common default and much safer than STRICT without manual lot matching.
