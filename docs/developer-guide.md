# Development and verification

Run from the project root. The base interpreter can run the core suite. For the other Python checks, use the environment from the [Windows setup](deployment.md).

| Check | PowerShell command |
|---|---|
| Core and CLI | `py -3.14 -m unittest discover -s tests -p test_intake.py` |
| Dependency consistency | `.\.venv\Scripts\python.exe -m pip check` |
| All Python tests | `.\.venv\Scripts\python.exe -m pytest -q` |
| Live Uvicorn and CLI agreement | `.\.venv\Scripts\python.exe -m scripts.smoke` |
| Validation-only benchmark | `.\.venv\Scripts\python.exe -m scripts.benchmark` |
| Regenerate the API contract | `.\.venv\Scripts\python.exe -m scripts.export_spec` |

If Windows denies access to pytest's user temp directory, create a writable temporary directory and set `TEMP` and `TMP` to its absolute path in the test terminal. Pytest creates its own numbered directories underneath it. The smoke check starts a short-lived loopback server with a random credential and runs the actual CLI against both fixtures. The full test suite compares the runtime OpenAPI to the checked-in JSON.

## PostgreSQL 18

Use a new disposable database with PostgreSQL 18 and `psql` on PATH. Set the standard libpq connection variables for the test instance, including `PGDATABASE`. The first command creates five tables. Run it once per database. The next two commands intentionally repeat the rollback-only checks against the same tables.

```powershell
psql -X -v ON_ERROR_STOP=1 -f docs/schema.sql
psql -X -v ON_ERROR_STOP=1 -f tests/schema_checks.sql
psql -X -v ON_ERROR_STOP=1 -f tests/schema_checks.sql
```

Each command should exit 0. A check that unexpectedly succeeds raises an SQL error. Rolled-back tests still advance identity sequences. Additional two-session and recovery observations are in the [verification record](verification.md).

## CI

The workflow defines Windows and Ubuntu test jobs and a disposable PostgreSQL 18 service. GitHub Actions results become available after an owner-authorized run. The workflow does not deploy the application.
