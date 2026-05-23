## 1. Setup and Failure (TDD Phase)

- [x] 1.1 Add unit tests in `tests/test_normalization.py` or a new test file that mock `os.path.exists` and `open` to verify that `commodity_map.yaml` is generated when missing.
- [x] 1.2 Verify tests fail.

## 2. Implementation

- [x] 2.1 Define the default YAML template string in `src/beancount_exporter.py`.
- [x] 2.2 Implement the auto-generation logic in the module initialization block of `src/beancount_exporter.py`.
- [x] 2.3 Verify unit tests pass.

## 3. Validation

- [x] 3.1 Manually delete `commodity_map.yaml` and run the exporter.
- [x] 3.2 Verify the file is correctly recreated with default content.
- [x] 3.3 Verify that running the exporter again does not overwrite a modified file.
