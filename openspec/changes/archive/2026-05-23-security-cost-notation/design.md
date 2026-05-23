## Context

Moneydance stores multi-currency transactions using `pamt` (Parent Amount) and `samt` (Split Amount). Our current Beancount exporter uses the `@@` (Total Price) syntax for all multi-currency splits. While this is sufficient for currency conversion, it is insufficient for security tracking in Beancount, which expects a cost basis (`{}`) to correctly manage investment lots.

## Goals / Non-Goals

**Goals:**
- Use Beancount cost notation (`{}` or `{{}}`) for security purchases.
- Preserve exact precision from Moneydance.
- Maintain account collapsing logic (Securities under Investments).
- Improve readability by minimizing trailing zeros.

**Non-Goals:**
- Automated lot matching for "Sell" transactions (will continue to use `@@` or a simple reduction for now).
- Handling "Short" positions.

## Decisions

### 1. Use `{{ }}` (Total Cost) for Security Purchases
Instead of calculating the unit cost manually (which might result in repeating decimals like 33.333333), we will use Beancount's double-brace syntax for total cost.
- **Example**: `1000 YUANTA_TW50 {{ 96400.00 TWD }}`
- **Rationale**: This is perfectly exact as it uses the `pamt` value directly from Moneydance. Beancount will automatically calculate the unit cost of `96.4`.

### 2. Detection of Security Splits
We will check if the receiving account of a split has `SecurityInfo`. If it does, and the quantity is positive (a "Buy"), we apply the cost notation.

### 3. Smart Formatting for Amounts
We will update `format_amount` to optionally strip trailing zeros if they follow a decimal point.
- **Example**: `1000.0000` -> `1000`, `123.4500` -> `123.45`.

## Risks / Trade-offs

- **[Risk]** Imbalance in Beancount if signs are wrong → **[Mitigation]** The `{{}}` notation is syntactically balanced against the cash side of the transaction in the same way `@@` is.
- **[Trade-off]** Sell transactions remain using `@@` → **[Mitigation]** Without explicit lot information from Moneydance, `@@` is the safest way to let Beancount resolve the reduction.
