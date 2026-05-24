## Why

Moneydance allows commodities to be defined relative to currencies other than the base currency (e.g., a US stock is priced in USD, while the base currency is TWD). Our current exporter ignores this hierarchy and forces all price directives to target the base currency.

This results in incorrect valuation in Beancount/Fava. For example, if a stock is worth 350 USD and 1 USD = 31 TWD, our exporter currently produces `price STOCK 350 TWD`, causing Fava to think the stock is worth only 350 TWD instead of ~10,850 TWD.

## What Changes

- **Preserve Hierarchy**: Update the data model to track which currency each commodity is relative to.
- **Hierarchical Export**: Modify the price export logic to target the specific parent currency instead of the global base currency.
- **Enable Chaining**: By exporting `STOCK -> USD` and `USD -> TWD`, Beancount can automatically calculate the correct `STOCK -> TWD` valuation.

## Capabilities

### Modified Capabilities
- `beancount-export`: Support multi-level price chaining by respecting currency relationships.

## Impact

- `src/models.py`: Add `relative_to_code` to `Currency` (or a way to resolve the parent).
- `src/database.py`: Extract `relative_to_currid` and map it to Beancount commodity codes.
- `src/beancount_exporter.py`: Update `export_prices` to use the derived parent code as the price target.
- `tests/test_export.py`: Add a test case for hierarchical pricing.
