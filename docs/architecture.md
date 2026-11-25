# Architecture

The CLI and the local HTTP service call the same two operations. `load_catalog` validates an approved reseller-to-item mapping. `preview` validates a file against that mapping and returns a dataclass result. Neither operation opens a network connection or writes orders.

| Boundary | Responsibility |
|---|---|
| `ordercheck/intake.py` | Read bounded bytes, decode UTF-8, check CSV shape, validate identifiers and quantities, group records and report issues. |
| `ordercheck/__main__.py` | Read the two paths, write the preview to stdout, and return the documented process status. |
| `ordercheck/api.py` | Load one catalog at startup, verify the host and bearer token, check the representation, bound the streamed body, and translate domain failures to HTTP. |
| `docs/schema.sql` | Model accepted orders in a separate PostgreSQL experiment. No application code connects to these tables. |

## Whole-order validation

A file can interleave lines from several orders. Each group tracks the line IDs it has seen, its valid lines and its issues. On the first issue, the validator releases the buffered lines from memory. It continues checking later records for that order so the operator gets all discoverable errors. First occurrence determines order position, and input order determines line and issue position. An unusable order ID or broken file structure aborts the whole preview.

Identifiers retain their exact Unicode spelling, case and leading zeroes. Quantities use a separate grammar and become integers only after passing validation. Changing a SKU spelling rule can merge distinct products, so a new feed requires an approved mapping and fixtures.

Expected time and memory both grow linearly with bounded input. The API reads the body asynchronously, dispatches validation to a worker thread and uses FastAPI's response model for JSON. This keeps the event loop available while a worker runs. Python workers still share CPU time. [Measured workload](verification.md)

## Persistence design

A source owns batches and external order identities. A composite foreign key ties an order to a batch from the same source. A per-source replay key and a per-source external order ID address different duplicate conditions. A batch stores the file and catalog digests. Orders own lines and batches own events. Identifiers use deterministic C collation for exact identity.

The SQL enforces keys, foreign keys, digest format, event types, quantity range and identifier lengths. A future writer must validate the full Unicode identifier grammar, require a nonempty complete order, bind the approved catalog and write batch, orders, lines and event in one transaction. A unique-key violation alone cannot decide whether a retry is equivalent. That decision needs a comparison of the saved payload and catalog digests and a defined response to the caller.

The schema tests exercise database constraints directly. A persistence API, migrations from deployed data, per-actor permissions and downstream acknowledgement would each require separate acceptance tests.
