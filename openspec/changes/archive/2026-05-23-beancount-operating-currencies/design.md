## Context

Beancount uses `option` directives to define global ledger settings. The most critical are `operating_currency` and `title`. Currently, the exporter does not generate any options, leading to validation errors in tools like `bean-check`.

## Goals / Non-Goals

**Goals:**
- Eliminate the "No operating currency specified" error by providing sensible defaults (**TWD, USD, EUR**).
- Support multiple operating currencies via CLI and config.
- Automatically title the ledger based on the Moneydance root account name.

**Non-Goals:**
- Supporting every Beancount option (focusing only on `title` and `operating_currency`).
- Complex currency conversion math (keeping it simple with list-based defaults).

## Decisions

### 1. New `export_options` Function
A dedicated function will be added to generate the `;; === OPTIONS ===` section at the very top of the output file.
- **Rationale**: Keeps the header logic clean and isolated from account/transaction generation.

### 2. Default List: `["TWD", "USD", "EUR"]`
If no input is provided, the system will use this static list.
- **Rationale**: Covers the primary currencies identified in the user's data (Moneydance sample).

### 3. CLI Argument Splitting
The existing `base_currency` CLI argument (which currently takes a single string) will be updated to split by commas and return a list.
- **Rationale**: Minimal friction for the user while enabling multi-currency support.

### 4. Configuration Schema Expansion
The `commodity_map.yaml` will be expanded to support a `settings` block:
```yaml
settings:
  operating_currencies: ["TWD", "USD", "EUR"]
```
- **Rationale**: Allows users to override defaults permanently without using CLI flags every time.

## Risks / Trade-offs

- **[Risk]** Missing root account name → **[Mitigation]** Fallback to "Moneydance Export" if no root account info is found.
- **[Trade-off]** CLI argument naming → **[Mitigation]** We'll keep the name `base_currency` for now to avoid breaking existing scripts, but treat it as a list internally.
