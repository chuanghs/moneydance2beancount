# Proposal: Exporter Modularization and Ignore Future Records

## Goal
Decouple database parsing from Beancount syntax, modularize the export process, upgrade command line argument handling, and support ignoring future-dated records.

## Changes
- **Database Decoupling**: Make database parsing independent of Beancount-specific token constraints.
- **Config Management**: Introduce a configuration context that handles translation maps and defaults.
- **Modular Exporter Package**: Partition exporter formatting, routing, and mapping into separate modules under `src/exporter/`.
- **Ignore Future Records**: Filter out future-dated transactions, price snapshots, and budget items based on a date-only cutoff limit.
- **CLI parser upgrade**: Replace positional indexing of CLI arguments with Python's native `argparse` module.
