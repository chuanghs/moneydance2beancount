## Context

Free-text fields from Moneydance are currently wrapped in double quotes in the Beancount output without escaping. This leads to invalid files if the text contains `"` or `\`.

## Goals / Non-Goals

**Goals:**
- Ensure all double-quoted strings in the Beancount file are properly escaped.
- Handle both double quotes and backslashes.

**Non-Goals:**
- Exporting split descriptions (remains ignored as per user request).
- Handling other escape sequences like newlines (unless they appear in Moneydance data).

## Decisions

### 1. Centralized Escaping Utility
Create a function `escape_beancount_string(s: str) -> str` in `src/beancount_exporter.py`.
- **Logic**:
  1. Replace `\` with `\\`.
  2. Replace `"` with `\"`.
- **Rationale**: Escaping the backslash first is critical to avoid double-escaping the backslash introduced for the quote.

### 2. Mandatory Application
All f-strings that wrap variables in double quotes must call `escape_beancount_string`.

## Risks / Trade-offs

- **[Risk]** → Performance overhead for large ledgers.
  - **Mitigation** → String replacement is extremely fast in Python; this is negligible compared to other transformations.
