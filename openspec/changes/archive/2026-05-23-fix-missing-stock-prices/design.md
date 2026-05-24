## Context

The `export_prices` function uses a filter that is too restrictive for Taiwan stocks and other commodities that lack a formal `currid` in Moneydance.

## Decisions

### 1. Relaxing the Filter
We will update the list comprehension that defines `valid_snapshots`. Instead of checking `s.currency.code` (which is often `""`), we will check `get_commodity_code(s.currency) != "UNKNOWN"`. Since `get_commodity_code` has robust fallbacks to name and ticker, this will include almost all relevant snapshots.

### 2. Consistent Sorting
Currently, snapshots are sorted by `(date, currency.code)`. Since `code` can be empty, we will change this to `(date, get_commodity_code(snap.currency))` to ensure deterministic output ordering.

## Implementation Details

```python
# Updated export_prices logic
def export_prices(snapshots: list[PriceSnapshot], base_currency_code: str) -> str:
    ...
    # NEW: Relaxed filter
    valid_snapshots = [s for s in snapshots if s.currency and get_commodity_code(s.currency) != "UNKNOWN"]
    
    # NEW: Sorting by derived code
    for snap in sorted(valid_snapshots, key=lambda x: (x.date, get_commodity_code(x.currency))):
        ...
```
