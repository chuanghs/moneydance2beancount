## 1. Research & Model Updates

- [x] 1.1 Update `Currency` model in `src/models.py` to include `ticker`, `name`, and `md_id`
- [x] 1.2 Update `Database._sort_exported_data` and `Database.load` in `src/database.py` to extract ticker and name from `curr` objects

## 2. Path Collapsing

- [x] 2.1 Implement recursion in `get_beancount_path` for `SecurityInfo` in `src/beancount_exporter.py`
- [x] 2.2 Update `export_accounts` to skip duplicate `open` directives and aggregate initial balances for collapsed paths
- [x] 2.3 Verify with new test cases in `tests/test_export.py`

## 3. Commodity Identity

- [x] 3.1 Implement `get_commodity_code` with GUID detection in `src/beancount_exporter.py`
- [x] 3.2 Implement `export_commodities` and integrate it into the main export flow
- [x] 3.3 Ensure transactions use the new commodity codes

## 4. Validation

- [x] 4.1 Run end-to-end export and verify `Assets:Investment` accounts no longer have security sub-accounts
- [x] 4.2 Verify commodity directives exist with full names
