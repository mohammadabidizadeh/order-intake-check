# Order Intake Check

Order Intake Check validates a reseller's order CSV against a distributor-approved SKU mapping. One bad line holds the entire order, even when another order's lines appear between its records. The operator gets a JSON preview with the records that need attention.

**0.1.1 · Windows x64 · CPython 3.14.** The command line runs offline with the standard library. An optional authenticated HTTP endpoint uses the same rules. The workflow ends at operator review. ERP entry, stock availability, pricing and order acceptance are separate steps.

## Try the example

Extract the ZIP and open PowerShell in the folder containing this README.

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
| Installing the offline kit and running the local API | [Windows setup](docs/deployment.md) and [OpenAPI contract](docs/openapi.json) |
| Reviewing the code and repeating the tests | [Architecture](docs/architecture.md), [developer commands](docs/developer-guide.md) and [verification results](docs/verification.md) |
| Assessing a customer trial | [Pilot acceptance](docs/product.md) and [security boundary](SECURITY.md) |
| Reviewing the project as a portfolio sample | [Engineering case study](docs/case-study.md) and [changelog](CHANGELOG.md) |

The SQL files are a separately tested design for future persistence. The preview runs without PostgreSQL. The Windows archive includes the original dependency wheels and their notices. Source publication and licensing require the owner's decision. [Dependency inventory](docs/dependencies.md)
