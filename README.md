# Order Intake Check

Order Intake Check validates a reseller's order CSV against a distributor-approved SKU mapping. One bad line holds the entire order, even when another order's lines appear between its records. The operator gets a JSON preview with the records that need attention.

**Version 0.1.1.** The CLI runs offline with the Python standard library. An optional authenticated HTTP endpoint uses the same rules. The workflow ends at operator review. ERP entry, stock availability, pricing and order acceptance are separate steps.

## Try the example

Clone the repository or extract the source archive. Open a terminal in the folder containing this README. On Windows with Python 3.14, run the following commands in PowerShell. On Ubuntu, use `python3.14` in place of `py -3.14` and `echo $?` to inspect the exit code.

```powershell
py -3.14 -m ordercheck examples/orders.csv --catalog examples/catalog.csv
$LASTEXITCODE
```

| Order | Result | What the operator sees |
|---|---|---|
| PO-100 | Ready | Lines 01 and 02 map to BOX-01 and PART-127. |
| PO-101 | Held | Record 5 has an unknown SKU. The order has zero releasable lines. |

The first command exits with code 2. After the source confirms the correction, run the second fixture.

```powershell
py -3.14 -m ordercheck examples/orders-corrected.csv --catalog examples/catalog.csv
```

Both orders are ready and the exit code is 0. The examples contain invented identifiers. [راهنمای فارسی](docs/start-fa.md)

## Use and verification

| For | Read |
|---|---|
| Preparing files and correcting errors | [Operator guide](docs/operator-guide.md) |
| Installing the API from a checkout or a Windows offline kit | [Windows setup](docs/deployment.md) and [OpenAPI contract](docs/openapi.json) |
| Reviewing the code and repeating the tests | [Architecture](docs/architecture.md), [developer commands](docs/developer-guide.md) and [verification results](docs/verification.md) |
| Assessing a customer trial | [Pilot acceptance](docs/product.md) and [security boundary](SECURITY.md) |
| Reviewing the project as a portfolio sample | [Engineering case study](docs/case-study.md) and [changelog](CHANGELOG.md) |

GitHub Actions verified the CLI and API on Windows Server 2022 and Ubuntu 24.04 at commit `fc5c18d`. A separate job verified the proposed PostgreSQL schema. The preview runs without a database. [CI run and job results](https://github.com/mohammadabidizadeh/order-intake-check/actions/runs/45570396805)

The optional Windows offline kit targets standard 64-bit CPython 3.14. GitHub's automatic source archives contain the pinned requirements and hash lock. The wheel binaries and their original notices are part of the separate kit. [Dependency inventory](docs/dependencies.md)

## Use in a business

A ready order means that the lines supplied in this file passed the checks against the selected mapping. An omitted line, an outdated mapping or an order already entered through another file can still pass. For a trial, have the operator reconcile complete orders, item codes and quantities against an independent answer before using the result. Customer accuracy, time savings and paid adoption have yet to be measured. [Pilot acceptance](docs/product.md)

## License

The original Order Intake Check code, tests, scripts, workflow, documentation and synthetic examples are offered under the Apache License, Version 2.0, to the extent the project holds the rights or is authorized to grant them. The license permits commercial use under its terms. Third-party software, notices and referenced materials retain their respective licenses. Customer files and mappings remain subject to their owners' permissions. [Project license](LICENSE) · [Third-party licenses and notices](docs/dependencies.md)
