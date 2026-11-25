# Customer pilot acceptance

The candidate operator receives recurring files from one reseller and has a distributor-approved mapping for countable items. A meaningful trial needs stable order and line identifiers. The software accepts the documented CSV layout and emits a JSON preview. The operator continues using their existing order system throughout the trial.

## Entry conditions

1. Obtain the file owner's permission and a representative anonymized order file. Keep all lines of each order together. Record the export format, unit of measure and catalog revision privately.
2. Have the catalog owner confirm item mappings. Have the operator independently identify the intended orders, lines, internal item codes, quantities and expected holds before seeing the program's output.
3. Run the two supplied examples on the trial workstation. Prefer the offline CLI for the first comparison. Establish who may see the files, where they are kept and when copies are removed.

## Decision record

For each trial file, record expected and observed ready/held order IDs, missing or unexpected lines, differing codes or quantities, and each disputed issue. Identify whether the difference arose in the source, the mapping, the agreed contract or the validator. Stop using the result if any order is incorrectly released.

Time the same work in the incumbent workflow and with the preview, including file preparation, correction and review. Report individual measurements. The original proposal suggested three representative runs, zero false-ready orders and a 30% reduction in median active time. The buyer can revise those targets before a trial. A few files establish feasibility only for the tested feed.

A WooCommerce importer already offers order CSV import, product lookup and a dry run. Compare the candidate buyer's current workflow on their own file before promising savings. The public ERPNext example concerns a customer-creation prerequisite, a separate problem from SKU mapping. [WooCommerce importer](https://woocommerce.com/document/customer-order-csv-import-suite/) · [ERPNext operator report](https://discuss.frappe.io/t/importing-bulk-sales-order-using-data-import/119143)

## Release decision

Synthetic examples and local technical tests support a demonstration now. A supervised read-only comparison can proceed after the entry conditions are met. Production entry, destination export, stock and price checks, cross-file replay protection and shared network service require separately agreed scope and verification. Customer demand, willingness to pay and time savings remain unmeasured.
