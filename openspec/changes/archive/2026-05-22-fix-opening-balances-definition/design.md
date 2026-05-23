## Context

The Beancount exporter uses `Equity:OpeningBalances` to balance initial account positions. However, Beancount requires every account used in a transaction to be explicitly defined with an `open` directive. Currently, only accounts present in the Moneydance database are opened.

## Goals / Non-Goals

**Goals:**
- Comply with Beancount validation rules by ensuring `Equity:OpeningBalances` is opened.
- Ensure the account is opened once at the start of the accounts section.

**Non-Goals:**
- Creating a physical account in the internal `Database` model for `Equity:OpeningBalances`.

## Decisions

### 1. Hardcoded Open Directive in `export_accounts`
We will prepend `f'{start_date} open Equity:OpeningBalances'` to the `lines` list at the beginning of the `export_accounts` function in `src/beancount_exporter.py`.
- **Rationale**: This is a mandatory system account for the export process. Adding it directly to the export function is the simplest and most reliable way to ensure it's always present.

## Risks / Trade-offs

- **[Risk]** → If a user already has an account named `Equity:OpeningBalances` in Moneydance, we might generate a duplicate `open` directive.
  - **Mitigation** → Given the current `get_beancount_path` logic and typical user naming, this is unlikely. However, if it happens, the redundancy check in `AccountRegistry` or the existing path generation might handle it, or Beancount will just report a double-definition error which the user can then resolve. For now, the benefit of a guaranteed definition outweighs this minor risk.
