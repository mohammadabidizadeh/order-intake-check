# Engineering case study

A reseller's order file can contain valid lines alongside a product code the distributor cannot map. The synthetic example has two interleaved orders. Record 5 belongs to PO-101 and contains the unknown code. Releasing the other line of PO-101 would make an incomplete order appear valid.

The validator keeps records grouped by the exact source order ID and tracks line IDs within that order. A line-level error clears its releasable lines. Later records can still add diagnostic details. PO-100 remains available, including the line whose source SKU begins with zeroes. Correcting record 5 makes both complete orders available.

The CLI and HTTP service use the same validation module. The HTTP service adds an approved startup catalog, a bearer credential, bounded input and a deadline. A loopback check exercises the external CLI and HTTP entry points and compares the complete JSON. A separate database experiment verifies source-scoped uniqueness under two concurrent transactions and verifies a backup restore.

The most important design limit is the unit of work. A successful preview says the lines in this file satisfy the active mapping and validation rules. It cannot detect a missing line that was never supplied, a stale but valid mapping, or an order already entered by another operator. These cases need independent reconciliation before a customer can rely on the result.

This is a local engineering project using synthetic data. The measured behavior, environment and limitations are in the [verification record](verification.md). Any portfolio description should attribute the contributor's actual work and separately identify assisted development.
