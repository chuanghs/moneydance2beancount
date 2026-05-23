## Context

Beancount supports two ways to specify cost basis for a purchase:
1. `{{ total_cost CURR }}`: Total amount paid for all units.
2. `{ unit_price CURR }`: Amount paid per single unit.

Our current implementation uses the double-brace total cost, which is confusing when the total amount looks like a unit price for other stocks.

## Goals

- Improve readability of security purchase transactions.
- Clarify the cost basis for users.

## Decisions

### 1. Calculation Logic
In `export_transactions`, when a security buy is detected:
```python
unit_price = abs(split.received_amount) / abs(split.given_amount)
```
Wait, `split.received_amount` is an integer (e.g. 150215 for $1502.15).
`split.given_amount` is an integer (e.g. 500000 for 5.00000 shares).

We need to convert them to float values using their respective currency decimals before division.

### 2. Formatting
The unit price will be formatted with high precision (e.g., 6 or 8 decimal places) to ensure Beancount can accurately reconstruct the total amount.

### 3. Syntax Change
The exporter will produce `{ unit_price CURR }` instead of `{{ total_cost CURR }}`.

## Risks

- **[Risk]** Floating point precision issues during division → **[Mitigation]** Use enough decimal places in the output. Beancount v3 is quite good at inferring the exact total if the unit price is reasonably precise.
