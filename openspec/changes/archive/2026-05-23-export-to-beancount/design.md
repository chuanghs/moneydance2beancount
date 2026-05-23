## Context

The current project parses Moneydance JSON exports into an internal Python object model. Users need to export this data into Beancount, a plain-text accounting format. This design addresses the transformation logic required to map Moneydance's hierarchical, multi-currency, and snapshot-heavy data model into the flat but strict double-entry format of Beancount.

## Goals / Non-Goals

**Goals:**
- Provide a high-fidelity export of accounts, transactions, and price history.
- Implement robust CamelCase normalization for account names.
- Ensure all exported transactions are zero-sum and correctly formatted for Beancount.
- Export all available historical price snapshots (`csnap`).
- Support Fava-compatible budget directives.

**Non-Goals:**
- Support for other plain-text formats (e.g., Ledger or GnuCash) in this specific implementation.
- Exporting of file attachments or budget items not related to `bdgtitem`.
- Real-time synchronization or two-way sync between Moneydance and Beancount.

## Decisions

### 1. New Module: `src/beancount_exporter.py`
To maintain a clean separation of concerns, all Beancount-specific formatting and logic will reside in a new dedicated module. This module will take a `Database` instance as input and produce a string output.

### 2. Account Path Generation
The `Account` model will be extended with a helper method (or a utility function in the exporter) that recursively climbs the parent tree to build the full Beancount path. 
- **Rationale**: This centralizes normalization and ensures consistency between transactions and account openings.
- **Alternatives**: Pre-calculating all paths into a dictionary was considered, but recursive lookup is simpler given the relatively small number of accounts.

### 3. Normalization Registry
To prevent collisions during CamelCase normalization (e.g., "Food & Drink" and "Food Drink" both becoming "FoodDrink"), the exporter will maintain a registry of used paths.
- **Decision**: If a collision occurs, a numeric suffix will be appended (e.g., `FoodDrink_2`).

### 4. Decimal Formatting
All amounts will be formatted using the `decimal` property from the account's `Currency`.
- **Rationale**: Beancount is sensitive to decimal places. Using the internal precision ensures the output matches the original ledger's granularity.

### 5. Multi-Currency Transfers
We will use the `@@` (Total Price) syntax for all cross-currency transfers.
- **Rationale**: This avoids rounding errors that occur when calculating unit prices (`@`). It allows Beancount to see the exact amounts exchanged as recorded in Moneydance's `pamt` and `samt` fields.

## Risks / Trade-offs

- **[Risk]**: Normalization creates confusing account names. 
  - **Mitigation**: Original Moneydance names will be preserved as metadata on the `open` directives for easier reference.
- **[Risk]**: Massive price history (45k+ entries) makes the Beancount file slow to load.
  - **Mitigation**: This is a standard characteristic of Beancount; however, we will ensure prices are sorted by date to optimize processing.
- **[Risk]**: Missing `pamt` or `samt` in some older Moneydance transactions.
  - **Mitigation**: The exporter will fallback to balancing the transaction using a single posting without an amount if exactly one amount is missing, allowing Beancount to infer it.
