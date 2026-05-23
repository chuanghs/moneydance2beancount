## Context

Moneydance stores transaction amounts in a "giver/receiver" model where `pamt` is the impact on the parent (giver) and `samt` is the impact on the split (receiver). The current implementation in `src/beancount_exporter.py` incorrectly negates the parent amount and sometimes uses the wrong field for splits, leading to unbalanced or inverted Beancount entries.

## Goals / Non-Goals

**Goals:**
- Ensure all exported Beancount transactions balance to zero.
- Ensure Asset accounts are negative when spending and positive when receiving.
- Ensure Expense accounts are positive when spending.
- Maintain precision by using raw integer amounts from the model.

**Non-Goals:**
- Supporting Beancount's automatic balancing (we will explicitly provide all posting amounts).

## Decisions

### 1. Directly Use `pamt` for Giver Posting
Instead of negating the total split amount, we will sum the `received_amount` (pamt) from each split and use it directly for the giver's posting.
- **Rationale**: Moneydance already provides the correct signed value for the impact on the parent account.

### 2.Consistently Use `given_amount` (samt) for Split Postings
In the split posting loop, we will always use `split.given_amount` (which maps to Moneydance's `samt`) regardless of whether the currencies match.
- **Rationale**: `samt` is the correct amount to be posted to the account receiving the funds in its own currency.

### 3. Update Multi-Currency Logic
For multi-currency transactions using `@@`, we will use `format_amount(split.given_amount, ...)` for the primary amount and `format_amount(abs(split.received_amount), ...)` for the total price.
- **Rationale**: This correctly reflects "Amount in Receiver Currency @@ Total Price in Giver Currency".

## Risks / Trade-offs

- **[Risk]** → Existing "accidentally correct" same-currency entries (which balanced but had flipped signs) will change.
  - **Mitigation** → This is intentional and brings the ledger into alignment with standard accounting practices and the user's HSBC example.
