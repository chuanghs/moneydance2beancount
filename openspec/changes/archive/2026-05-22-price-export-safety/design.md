## Context

The Beancount exporter iterates through `PriceSnapshot` objects and generates `price` directives. The current logic assumes that `snap.currency.code` and the `base_currency` parameter are always present and valid.

## Goals / Non-Goals

**Goals:**
- Prevent generation of malformed `price` directives.
- Ensure the export process is resilient to missing currency identification.

**Non-Goals:**
- Repairing missing data (we will simply skip).
- Validating the price *amount* beyond its presence (it's already a float in the model).

## Decisions

### 1. Early Return for Missing Base Currency
If `base_currency` is empty or `None`, `export_prices` will return an empty string immediately.
- **Rationale**: A price directive without a target currency is invalid in Beancount.

### 2. Pre-filter snapshots
We will filter the `snapshots` list to remove any records where `snap.currency` or `snap.currency.code` is missing.
- **Rationale**: This prevents `AttributeError` or `KeyError` during sorting and ensure we only process "Capital" identifying records.

## Risks / Trade-offs

- **[Risk]** → Users might not realize that some price data is missing from their export.
  - **Mitigation** → We could add a warning log, but for now, the priority is generating a valid Beancount file.
