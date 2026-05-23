## Context

Building on the hierarchical organization introduced for banks and investments, we want to further categorize "Cash" and "Credit Card" accounts. Moneydance uses the `a` type (AssetInfo) for general assets which often represent physical cash, and the `c` type (CreditCardInfo) for credit cards.

## Goals / Non-Goals

**Goals:**
- Group general assets under `Assets:Cash`.
- Group credit cards under `Liabilities:Card`.
- Ensure other liability types (Loans) remain distinct.
- Leverage existing redundancy logic to keep paths clean.

**Non-Goals:**
- Creating new types in the Python model.

## Decisions

### 1. Updated `AssetInfo` Mapping
Update the `isinstance` check in `get_beancount_path` to map `AssetInfo` to `Assets:Cash`.
- **Rationale**: This separates physical cash/general assets from bank-managed accounts (`BankInfo`).

### 2. Updated `CreditCardInfo` Mapping
Update the `isinstance` check to map `CreditCardInfo` to `Liabilities:Card`.
- **Rationale**: This provides a clear sub-category for cards while leaving room for other liabilities (like Loans) at the top level.

### 3. Parentheses to Hierarchy
We will update `normalize_name` to split the input string by parentheses before performing word extraction and capitalization.
- **Implementation**:
  1. `raw_parts = re.split(r'[()]', name)`
  2. Normalize each part using the existing `findall` and join logic.
  3. Filter out empty parts.
  4. Join the normalized parts with `:`.
- **Result**: `"富邦(宇萱)"` $\rightarrow$ `["富邦", "宇萱"]` $\rightarrow$ `"富邦:宇萱"`.

### 4. Redundancy Handling (Existing)
No changes needed here. The existing logic that checks `cat_parts[-1]` against `path_parts[-1]` will automatically handle `Assets:Cash:Cash` $\rightarrow$ `Assets:Cash`.

## Risks / Trade-offs

- **[Risk]** → Non-cash assets (like a "Car" or "House" if stored as type `a`) will now be mapped to `Assets:Cash`.
  - **Mitigation** → Given the user's specific request for "現金" (Cash) mapping, this is the intended behavior for their current database. If they add non-cash physical assets later, they can use a more specific type or we can add a name-based override.
