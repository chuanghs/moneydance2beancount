## Context

The current account mapping in `src/beancount_exporter.py` uses a flat category structure for Assets and Liabilities. Users with many accounts find this difficult to manage in Beancount. Moneydance provides specific info types for bank, investment, credit card, and loan accounts, which we can use to generate a more useful hierarchy.

## Goals / Non-Goals

**Goals:**
- Automatically organize bank and investment accounts into sub-categories.
- Prevent redundant path components (e.g., `Assets:Bank:Bank:Checking`).
- Maintain backward compatibility for accounts that don't fit these specific types.

**Non-Goals:**
- Changing the names of Moneydance accounts (we only change the Beancount mapping).

## Decisions

### 1. Type-to-Category Mapping
We will update the `category` determination logic in `get_beancount_path` to return hierarchical strings:
- `BankInfo` -> `Assets:Bank`
- `InvestmentInfo` and `SecurityInfo` -> `Assets:Investment`
- `CreditCardInfo`, `LiabilityInfo`, and `LoanInfo` -> `Liabilities`

### 2. Refined Redundancy Check
Instead of matching the entire `category` string against the top-most `path_parts`, we will match only the *last* component of the category.
- **Rationale**: If `category` is `Assets:Bank` and `path_parts` ends with `Bank`, the result should be `Assets:Bank:...` not `Assets:Bank:Bank:...`.
- **Implementation**: `cat_parts = category.split(":")` and compare `path_parts[-1].lower() == cat_parts[-1].lower()`.

## Risks / Trade-offs

- **[Risk]** → Users with highly customized Moneydance hierarchies might find the automatic sub-categories redundant or misplaced.
  - **Mitigation** → The redundancy check handles the most common case ("Bank" parent). Other cases can be adjusted by the user in Moneydance or via post-export scripts.
