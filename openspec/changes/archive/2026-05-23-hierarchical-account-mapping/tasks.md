## 1. Red Phase: Failing Tests

- [x] 1.1 Update `tests/test_export.py` with failing expectations for `Assets:Bank` hierarchy
- [x] 1.2 Update `tests/test_normalization.py` with failing expectations for redundancy handling (Bank parent)

## 2. Green Phase: Implementation

- [x] 2.1 Update `get_beancount_path` in `src/beancount_exporter.py` with hierarchical category mapping
- [x] 2.2 Refactor redundancy check in `get_beancount_path` to match against category sub-parts
- [x] 2.3 Verify all export and normalization tests pass

## 3. Validation

- [x] 3.1 Run end-to-end export and manually verify hierarchy in `finance.beancount.tmp`
