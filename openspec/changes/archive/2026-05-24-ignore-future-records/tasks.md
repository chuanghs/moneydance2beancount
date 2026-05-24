# Tasks: Exporter Modularization and Ignore Future Records

## Refactoring
- [x] Create config context and settings loader
- [x] Decouple database parser from Beancount syntax
- [x] Clean up unused rawjson models
- [x] Partition exporter logic into mapping, routing, formatting, and exporter classes
- [x] Integrate facade inside old exporter wrapper

## Feature Implementation
- [x] Implement date-only record filtering in exporter class
- [x] Print skipped summary counts to standard error
- [x] Upgrade CLI parameters checking to argparse
- [x] Write template scaffolding template on missing configuration

## Verification
- [x] Add config and filtering unit tests in tests
- [x] Confirm all 31 tests pass successfully
- [x] Verify CLI argument execution manually
