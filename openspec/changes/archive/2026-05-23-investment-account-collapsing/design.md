## Context

Moneydance uses a strict account-based model for securities, while Beancount uses a commodity-based model. Collapsing security accounts into their parents makes the ledger more readable and aligns with Beancount best practices.

## Decisions

### 1. Recursive Path Resolution
Modify `get_beancount_path` to handle `SecurityInfo`.
- **Logic**: `if isinstance(account.info, SecurityInfo): return get_beancount_path(account.info.parent)`
- **Rationale**: This ensures that every security "belongs" to its brokerage account in the Beancount hierarchy.

### 2. Commodity "Best Code" Selection
Introduce a helper function `get_commodity_code(currency: Currency, account_name: str)`.
- **Logic**:
  1. If `currency.ticker` is not empty, use it.
  2. Else if `currency.code` is not a GUID, use it.
  3. Else, use `normalize_name(account_name)`.
- **GUID Detection**: A regex or length-check to identify standard UUID/GUID formats.

### 3. Dedicated `export_commodities` Function
Iterate over all unique `Currency` objects in the database.
- **Output**:
  ```beancount
  commodity VT
    name: "Vanguard Total World Stock"
    md_id: "..."
  ```
- **Note**: Standard currencies (USD, TWD) will also get `commodity` directives.

### 4. Account Opening Logic
In `export_accounts`, ensure that `open` directives are only generated for unique paths.
- **Problem**: Multiple security accounts now map to the same path.
- **Fix**: Use a `set` to track paths that have already been "opened".

## Risks / Trade-offs

- **[Risk]** → Collisions in slugified security names.
  - **Mitigation** → Use the `AccountRegistry` to ensure commodity codes are unique if needed, though tickers are globally unique by nature.
- **[Risk]** → Loss of security-specific metadata on the account.
  - **Mitigation** → Transfer this metadata (like `sec_type`) to the `commodity` directive as Beancount metadata.
