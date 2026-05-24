## Context

The system needs to accurately represent the relationship between assets and currencies to allow Beancount to perform correct valuations.

## Decisions

### 1. Model Extension
We will add an optional `parent_code` field to the `Currency` model. This field will store the Beancount commodity code of the currency this asset is relative to.

### 2. Database Mapping
During the import of currencies in `src/database.py`, we will:
1. Store a mapping of MD `id` to the final Beancount code.
2. For each currency, check the `relative_to_currid` or `rel_curr_id` fields.
3. Resolve these IDs to their corresponding Beancount codes and store them in the `Currency` object.

### 3. Exporter Logic
In `src/beancount_exporter.py`, the `export_prices` function will be updated:
- Instead of using a single `base_currency_code` for every line, it will check if `snap.currency.parent_code` exists.
- If it exists, it uses `parent_code` as the target currency.
- If it doesn't (meaning it's relative to the base or has no parent), it falls back to the `base_currency_code`.

## Data Flow

```
MD JSON (curr) ──▶ relative_to_currid ──▶ Resolve to Code (e.g. USD)
                                                  │
                                                  ▼
                                         Currency.parent_code = "USD"
                                                  │
                                                  ▼
Price Snapshot ────────────────────────▶ price STOCK 350 USD
```
