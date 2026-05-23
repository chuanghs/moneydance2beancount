## Why

Moneydance users often seek a more flexible and long-lived format for their financial data. Beancount provides a robust plain-text accounting environment. This change introduces a high-fidelity exporter that transforms the existing internal data model into a valid Beancount ledger, preserving account hierarchies, full transaction history, multi-currency data, and price snapshots.

## What Changes

- **New Capability**: Comprehensive Beancount export functionality.
- **Account Normalization**: Implements CamelCase naming, hierarchy mapping (excluding root), and Beancount-compliant component validation.
- **Transaction Export**: Converts Moneydance's Giver/Split model into zero-sum Beancount postings with proper decimal handling.
- **Multi-currency Support**: Employs `@@` syntax for precise exchange rate transfers.
- **Price History**: Automatically extracts and generates historical price directives from `csnap` objects.
- **Budget Export**: Maps Moneydance budgets to Fava-compatible `custom "budget"` directives.

## Capabilities

### New Capabilities
- `beancount-export`: Transforms the internal database state into a Beancount-compliant plain-text ledger, including metadata and historical rates.

### Modified Capabilities
- None

## Impact

- **New Module**: `src/export.py` will be created to house the export logic.
- **Data Models**: `src/models.py` and `src/database.py` may receive minor helper methods to facilitate path normalization and decimal formatting.
- **Dependencies**: No new external dependencies are required.
