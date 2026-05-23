## 1. Red Phase: Failing Tests

- [x] 1.1 Add failing test cases for Unicode characters (CJK, accents, mixed) in `tests/test_normalization.py`
- [x] 1.2 Update existing tests in `tests/test_normalization.py` to fail on 'A' prefix for leading digits (v3 expectation)

## 2. Green Phase: Implementation

- [x] 2.1 Refactor `normalize_name` in `src/beancount_exporter.py` using Unicode-aware regex to pass new tests
- [x] 2.2 Remove legacy 'A' prefix and 'U' fallback logic until all normalization tests pass

## 3. Refactor & Validate

- [x] 3.1 Clean up `normalize_name` implementation for readability
- [x] 3.2 Run full suite in `tests/test_normalization.py` to ensure zero regressions
- [x] 3.3 Validate end-to-end export with sample data
