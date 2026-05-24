## 1. Cycle 1: Data Model (Currency.parent_code)

- [x] 1.1 **RED**: Update `tests/test_export.py` or a new test to verify `Currency` objects can be initialized with a `parent_code` field. (This will fail to compile/run initially).
- [x] 1.2 **GREEN**: Add `parent_code: Optional[str] = None` to the `Currency` dataclass in `src/models.py`.
- [x] 1.3 **REFACTOR**: Ensure all `Currency` instantiations in tests/code remain valid.

## 2. Cycle 2: Database Loader (Hierarchy Resolution)

- [x] 2.1 **RED**: Add a test in `tests/test_export.py` (or a dedicated database test) that loads a MD JSON snippet where `Currency A` is relative to `Currency B`, and verify `A.parent_code` is correctly set to `B`'s Beancount code.
- [x] 2.2 **GREEN**: Update `src/database.py` to perform a two-pass import for currencies to resolve hierarchy links and populate `parent_code`.
- [x] 2.3 **REFACTOR**: Simplify currency import logic if it becomes too complex.

## 3. Cycle 3: Exporter (Hierarchical Price Export)

- [x] 3.1 **RED**: Add a test case to `test_export_prices` where a snapshot's currency has a `parent_code`. Verify that the output `price` directive targets the `parent_code` instead of the base currency.
- [x] 3.2 **GREEN**: Update `src/beancount_exporter.py`'s `export_prices` to respect `snap.currency.parent_code`.
- [x] 3.3 **REFACTOR**: Clean up the `export_prices` function.

## 4. Phase 4: System Verification

- [x] 4.1 Run full export on `sample/finance.json`.
- [x] 4.2 Verify `export/prices.beancount` contains hierarchical targets (e.g., `price CDNS ... USD`).
- [x] 4.3 Confirm that Fava now correctly aggregates the TWD totals through the price chain.
