## 1. Normalization Utilities (TDD)

- [x] 1.1 Create `tests/test_normalization.py` with failing tests for `normalize_name` (CamelCase, symbols, leading digits)
- [x] 1.2 Implement `normalize_name` in `src/beancount_exporter.py` until tests pass
- [x] 1.3 Add failing tests for `get_beancount_path` (hierarchy, root exclusion)
- [x] 1.4 Implement `get_beancount_path` until tests pass
- [x] 1.5 Add failing tests for `AccountRegistry` (collision detection, numeric suffixing)
- [x] 1.6 Implement `AccountRegistry` until tests pass

## 2. Directive Generation (TDD)

- [x] 2.1 Add failing tests for account opening directives (metadata, initial balances)
- [x] 2.2 Implement `export_accounts` logic until tests pass
- [x] 2.3 Add failing tests for simple transactions (zero-sum, decimal shifting)
- [x] 2.4 Implement `export_transactions` for single-currency items until tests pass
- [x] 2.5 Add failing tests for multi-currency transactions (`@@` syntax, precision)
- [x] 2.6 Implement `@@` support in `export_transactions` until tests pass

## 3. Metadata & Budgeting (TDD)

- [x] 3.1 Add failing tests for price extraction from `csnap` objects
- [x] 3.2 Implement `export_prices` until tests pass
- [x] 3.3 Add failing tests for budget extraction (Fava syntax, interval mapping)
- [x] 3.4 Implement `export_budgets` until tests pass

## 4. Database Integration & Pipeline

- [x] 4.1 Update `src/database.py` to support loading `csnap` and `bdgtitem` objects from raw JSON
- [x] 4.2 Implement end-to-end integration test using `test_account_import.json`
- [x] 4.3 Create CLI entry point in `src/beancount_exporter.py`
- [x] 4.4 Final validation of exported sample ledger using `bean-check`
- [x] 4.5 Create `export-beancount.sh` runner script with venv auto-activation

