## 1. Phase 1: Red (Failing Tests)

- [x] 1.1 Add `tests/test_routing.py`: Create tests for `get_file_for_account` and `get_file_for_transaction` based on the design priority.
- [x] 1.2 Verify tests fail (module not found or function not found).

## 2. Phase 2: Green (Routing Logic)

- [x] 2.1 Implement `get_file_for_account` in `src/beancount_exporter.py`.
- [x] 2.2 Implement `get_file_for_transaction` in `src/beancount_exporter.py`.
- [x] 2.3 Verify routing tests pass.

## 3. Phase 3: Green (Multi-file Export)

- [x] 3.1 Refactor `export_accounts` to support filtering by target file.
- [x] 3.2 Refactor `export_transactions` to support filtering by target file.
- [x] 3.3 Implement `full_multi_export` that orchestrates writing to the `export/` directory.
- [x] 3.4 Update CLI in `src/beancount_exporter.py` to trigger multi-file export if a directory is provided as a third argument.

## 4. Phase 4: Verification

- [x] 4.1 Add integration test in `tests/test_export.py` that verifies the content of multiple files after a `full_multi_export`.
- [x] 4.2 Manually run the exporter on `sample/finance.json` with the `export/` directory and verify the result with `bean-check`.
