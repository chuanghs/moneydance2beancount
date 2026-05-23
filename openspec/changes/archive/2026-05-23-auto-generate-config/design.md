## Context

The `commodity_map.yaml` is the central place for user-specific settings and manual commodity translations. Currently, the code assumes this file exists but doesn't provide a way to create it. If it's missing, users have to manually create it with the correct schema, which is error-prone and discoverable only through documentation or error messages.

## Goals / Non-Goals

**Goals:**
- Auto-generate a valid `commodity_map.yaml` template on the first run.
- Surface default operating currencies to the user.
- Provide a template for commodity translations.

**Non-Goals:**
- Supporting multiple configuration file locations (keeping it strictly in CWD for now).
- Intelligent merging (if the file exists but is empty, we don't overwrite).

## Decisions

### 1. Hardcoded Template String
We will use a hardcoded YAML string within `src/beancount_exporter.py`. This string will include helpful comments and a commented-out sample mapping for clarity:
```yaml
settings:
  operating_currencies: ["TWD", "USD", "EUR"]

translations:
  # Map Moneydance commodity names to Beancount-compatible ASCII symbols.
  # "中華電信": "CH_TELECOM"
```

### 2. Startup Hook
The generation logic will reside in the module-level initialization phase of `src/beancount_exporter.py`, specifically before the `COMMODITY_MAP` and `GLOBAL_SETTINGS` are loaded.
- **Rationale**: Ensures the file is available for the subsequent load operation in the same execution.

## Risks / Trade-offs

- **[Risk]** Overwriting user data → **[Mitigation]** Strictly check `os.path.exists()` before writing. Never overwrite.
- **[Trade-off]** Cluttering the root directory → **[Mitigation]** The file is essential for the tool's operation, so its presence is justified.
