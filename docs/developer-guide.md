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

The workflow runs dependency checks, pytest and the live smoke test on Windows Server 2022 and Ubuntu 24.04. A separate job initializes PostgreSQL 18, installs the schema and runs its constraints twice. All three jobs passed for `fc5c18d`. [Hosted verification](verification.md#github-actions)

## Preparing a release

Choose the commit to distribute. Confirm the version in `ordercheck/__init__.py`, the OpenAPI snapshot and the changelog. Check the workflow result for that exact commit before tagging it. Read the source files, license, notices and wheel inventory from the commit. Add only the wheels whose names and SHA-256 digests match that inventory. Extract the finished ZIP into a fresh directory, compare its source files to the Git blobs, install with the Windows hash lock and run the tests and smoke check there. Include the full commit ID in the release notes and the ZIP digest in `SHA256SUMS`.
