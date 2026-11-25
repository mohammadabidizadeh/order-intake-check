# Operator guide

## Prepare the inputs

Use comma-delimited UTF-8 CSV, optionally with a BOM and CRLF. Standard CSV quoting is accepted. Header order can change. Every named column must occur once and extra columns are rejected. A file may contain up to 5,000 data records and 524,288 bytes. Do not include customer names, addresses, prices or payment information. This template has no columns for those values.

| File | Fields | Owner |
|---|---|---|
| Product mapping | source_sku, item_code | Distributor confirms the internal code for each reseller SKU. Each source SKU appears once. Multiple source SKUs can map to one internal code. |
| Reseller orders | order_id, line_id, source_sku, quantity | Reseller supplies stable order and line references. Keep leading zeroes when exporting from spreadsheet software. |

Identifiers are 1–64 characters, case-sensitive, with an alphanumeric first character. Subsequent characters can also be period, underscore, hyphen or slash. Unicode letters and alphanumeric digits are preserved exactly. Whitespace is invalid. Quantities accept 1–6 ASCII, Arabic-Indic or Persian digits, with numeric value from 1 through 999999. The service never turns a product code into a number. Keep the original spreadsheet under the operator's local retention policy.

## Read and correct the result

A preview of a well-formed file gives `records`, `ready_orders`, `held_orders` and the orders themselves. A ready line includes its internal item code and integer quantity. A held order has empty lines and a list of issues. Record numbers count logical CSV records including the header. Repeating a SKU on different line IDs is allowed.

| Issue | Operator action |
|---|---|
| unknown_sku | Verify the reseller code. Correct the source or arrange for the owner to approve a catalog entry. Restart the local API after a catalog update. |
| duplicate_line | Reconcile the two entries with the source. The report identifies the later occurrence. Keep both only if the source confirms distinct legitimate line IDs. |
| invalid_quantity | Confirm the actual count and unit. Fractional, negative and zero quantities require a different workflow. |
| invalid_sku / invalid_line_id | Review the field against the identifier contract. Preserve meaningful zeroes. |
| invalid_order_id, invalid_header, invalid_width, invalid_csv, empty_file, invalid_encoding | Fix the file and submit it again. The service could not safely group or read it. |
| file_too_large / too_many_records | Use an approved smaller file. Keep all lines of an order in one submission. Cross-file duplicate detection is outside this release. |
| duplicate_mapping / invalid_catalog_id | Catalog owner resolves the mapping before the service can start. |

The CLI writes a complete preview to stdout and exits 0 when all orders are ready, or 2 when at least one is held. An input or file-access failure exits 1 with a JSON problem on stderr and empty stdout. For `unreadable_file`, check both paths and their read permissions. Incorrect command syntax also exits 2, with usage on stderr and no preview.

| HTTP result | Operator action |
|---|---|
| 200 | Inspect the ready and held counts. |
| 400 | Use the configured loopback host. Retry an interrupted upload with the complete file. |
| 401 | Supply one valid bearer credential. |
| 408 | Send the complete body within 30 seconds. |
| 413 | Check the file size and keep orders intact if splitting the file. |
| 415 | Use uncompressed UTF-8 `text/csv` with a header. Explicit charset and header parameters must agree. |
| 422 | Use the issue code and logical record to correct the file. |
| 503 from Uvicorn | The configured concurrency limit was reached. Retry the read-only preview after outstanding requests finish. |

Inspect the result before acting. No preview creates an ERP order. A ready order may still lack stock, a customer, tax information or a valid price in the destination.
