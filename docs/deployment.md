# Run the local preview on Windows

Use standard 64-bit CPython 3.14 and open PowerShell in the folder containing the README. The CLI needs only Python. For HTTP and tests, create a project-local environment.

```powershell
py -3.14 -c "import platform,sys; print(sys.version, platform.machine())"
py -3.14 -m venv .venv
```

**From a Git checkout or GitHub source ZIP**, install the pinned Windows packages from your approved Python package index.

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --require-hashes -r offline/windows-cp314-x64.lock
```

**From the Windows offline kit**, install using the wheels included in the extracted folder.

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --only-binary=:all: --require-hashes --find-links offline/windows-cp314-x64 -r offline/windows-cp314-x64.lock
```

Verify either installation.

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.smoke
```

The smoke command generates a temporary credential, starts a loopback server, checks both fixtures and shuts down the server. If the Python launcher is unavailable, substitute the path of a verified 64-bit CPython 3.14 interpreter for `py -3.14`.

## Serve one approved mapping

For an interactive session, generate a random token of at least 32 ASCII letters and digits in your password manager. Use it at both masked prompts below. Start in one PowerShell terminal in the project root. The process runs in the foreground. A configuration or port error appears here.

```powershell
$credential = [System.Net.NetworkCredential]::new('', (Read-Host 'Local preview token' -AsSecureString))
$env:ORDERCHECK_TOKEN = $credential.Password
$env:ORDERCHECK_CATALOG = (Resolve-Path examples/catalog.csv).Path
try {
    .\.venv\Scripts\python.exe -m uvicorn ordercheck.api:create_app --factory --host 127.0.0.1 --port 8000 --limit-concurrency 8 --no-access-log --no-proxy-headers
} finally {
    Remove-Item Env:ORDERCHECK_TOKEN, Env:ORDERCHECK_CATALOG
    Remove-Variable credential
}
```

When Uvicorn reports it is listening, open another PowerShell terminal in the same folder. Send bytes with `-InFile` so PowerShell preserves the CSV encoding.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
$credential = [System.Net.NetworkCredential]::new('', (Read-Host 'Local preview token' -AsSecureString))
$headers = @{ Authorization = "Bearer $($credential.Password)" }
try {
    Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/order-previews -Headers $headers -ContentType 'text/csv' -InFile examples/orders.csv | ConvertTo-Json -Depth 8
} finally {
    Remove-Variable headers, credential
}
```

Press Ctrl+C in the server terminal to stop. If port 8000 is occupied, use another free loopback port in the launch command and both URLs. Restart to replace the mapping or rotate the token. The CLI reads the selected mapping on each invocation.

Keep the approved mapping and a known-good fixture in private storage. To recover the preview, reinstall the release, load that mapping, issue a fresh token and compare the fixture's full result with the operator's saved answer.
