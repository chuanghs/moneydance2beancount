## Context

The current `normalize_name` implementation in `src/beancount_exporter.py` uses a simple ASCII-only regex (`[^a-zA-Z0-9]+`) to split account names. This causes all non-ASCII characters to be stripped, often resulting in empty strings that trigger a hash-based fallback. Beancount v3 has expanded support for Unicode in account names, which we intend to leverage.

## Goals / Non-Goals

**Goals:**
- Enable high-fidelity account names for international users.
- Support Beancount v3 naming rules (Unicode letters/numbers, digits at start).
- Maintain the CamelCase formatting style for consistency.

**Non-Goals:**
- Support for Beancount v2 strict ASCII-only environments (without hashes).
- Support for spaces or underscores in account names (still prohibited in Beancount).

## Decisions

### 1. Unicode-Aware Regex
We will use a regex that splits on characters that are NOT Unicode letters or numbers.
- **Decision**: Use `re.split(r'[^\w]+', name, flags=re.UNICODE)` or a similar pattern that includes Unicode categories. However, since Python's `\w` includes underscores, we will be explicit: `r'[^\w]+'` but then filtering out underscores if necessary, or better: `r'[^\p{L}\p{N}]+'` (if using the `regex` module) or `r'[^a-zA-Z0-9\u00C0-\u00FF\u0100-\u017F\u0400-\u04FF\u4E00-\u9FFF]+'` for common blocks.
- **Refined Decision**: Since we want to support ALL Unicode letters, we will use `re.findall(r'[\w]+', name)` and then filter/process. Actually, `re.split(r'[^\w]+', name)` is good if we handle the underscore.
- **Final Decision**: We will use `re.findall(r'[^\W_]+', name, re.UNICODE)` to extract parts consisting of any Unicode letter or digit, excluding underscores.

### 2. CamelCase Processing
We will preserve the existing CamelCase logic: capitalize the first letter of each part and join them.
- **Rationale**: This keeps the account names looking like identifiers while ensuring they don't contain spaces.

### 3. Removal of Prefixes
We will remove the logic that adds an 'A' prefix for leading digits and the 'U' fallback for empty results.
- **Rationale**: Beancount v3 allows digits at the start of components. With Unicode support, the "empty name" fallback is much less likely to be triggered unless the name is pure punctuation.

## Risks / Trade-offs

- **[Risk]**: Some characters categorized as `\w` might still be illegal in some Beancount versions.
  - **Mitigation**: We will stick to the core v3 rule: Letters and Numbers. `[^\W_]` is a safe approximation for Unicode letters and numbers.
- **[Risk]**: Compatibility with Beancount v2 tools.
  - **Mitigation**: The proposal explicitly targets v3. Users on v2 may need to adjust their ledgers or use a newer parser.
