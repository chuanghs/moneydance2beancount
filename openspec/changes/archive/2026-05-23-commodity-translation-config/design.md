## Context

Beancount has strict naming conventions for commodities: they must start with an uppercase letter and consist only of uppercase letters, numbers, and a few specific punctuation marks (`.`, `_`, `-`, `'`). Moneydance allows free-form names and tickers, which frequently violate these rules (e.g., Taiwanese stock tickers like `2412` or Chinese names like `中華電信`).

## Goals / Non-Goals

**Goals:**
- Provide a mechanism to translate non-compliant commodity names to valid Beancount IDs via configuration.
- Automatically handle common digit-based ticker violations.
- Ensure 100% compliance with Beancount commodity syntax to prevent "unknown account" errors.

**Non-Goals:**
- Automated translation via external APIs (e.g., Google Translate).
- Support for complex commodity metadata beyond `name` and `md_id`.

## Decisions

### 1. Manual Translation Map (`commodity_map.yaml`)
We will use a YAML file to store manual mappings. YAML is chosen over JSON for its readability and support for comments, which is useful for maintaining a list of financial commodities.
- **Rationale**: Gives the user full control over the "canonical" name of their assets in the ledger.
- **Alternatives**: Environment variables (too verbose for long lists), hardcoding in Python (not user-editable).

### 2. Auto-prefixing `SYM_` for Digits
Any ticker or identifier that begins with a digit will be prefixed with `SYM_`.
- **Rationale**: Simple, deterministic, and avoids collisions with standard letter-starting tickers. It is a common convention in Beancount conversions.

### 3. Centralized `normalize_commodity` function
A new utility function will encapsulate all sanitation rules (capitalization, character filtering, prefixing).
- **Rationale**: Ensures consistency across accounts, commodities, and price exports.

## Risks / Trade-offs

- **[Risk]** Collisions in translated names → **[Mitigation]** The validation phase will ensure uniqueness (though collisions are unlikely if the user provides descriptive names).
- **[Trade-off]** Complexity in `get_commodity_code` → **[Mitigation]** The logic is strictly layered (Map -> Selection -> Prefix -> Sanitize) to maintain testability.
