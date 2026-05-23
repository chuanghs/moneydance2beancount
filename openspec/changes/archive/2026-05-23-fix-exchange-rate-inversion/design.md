## Context

Moneydance's `urt` (User Rate) is stored as `Units per 1 Base Currency`. 
Example: `1 TWD = 0.033 USD`.
Beancount's `price` directive requires `Target Units per 1 Source Unit`.
Example: `1 USD = 30 TWD`.

Our current implementation exports `urt` directly as the Beancount price, which results in the inverse rate being used.

## Goals / Non-Goals

**Goals:**
- Fix the price inversion bug.
- Use the correct target currency (MD Base) for all prices.
- Ensure high precision for accurate reporting.

## Decisions

### 1. Inversion in `export_prices`
We will apply the formula `beancount_price = 1.0 / md_urt`. This ensures that Beancount reports match the expected values in the base currency.

### 2. Base Currency Detection
We will modify `Database.load` to find the currency object with `isbase: "y"` and store its `currid` (code) in a `base_currency_code` attribute.

### 3. Precision
We will use `.8f` formatting for prices to minimize cumulative rounding errors when Beancount converts large balances.

## Risks / Trade-offs

- **[Risk]** Division by zero if `urt` is 0 → **[Mitigation]** The loader already filters out `urt == 0`.
- **[Trade-off]** All prices target the MD base → **[Mitigation]** This is the most robust approach as it matches the source data. Beancount can handle multi-hop conversions automatically if needed.
