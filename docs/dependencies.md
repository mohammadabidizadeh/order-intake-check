# Dependency provenance

The CLI uses the Python standard library. Runtime and development pins live in `requirements.txt` and `requirements-dev.txt`. The optional offline kit includes 23 original wheels for standard 64-bit CPython 3.14 on Windows. The platform-specific lock adds SHA-256 checks during installation and includes the development requirements so incompatible pin changes fail resolution. [Windows setup](deployment.md)

On 24 November 2026, every wheel in the previous kit matched the filename, SHA-256 and download URL of a non-yanked file on its version-specific PyPI release. The review read each wheel as a ZIP, verified the entries and hashed records in its RECORD, matched distribution name and version, and checked its listed notice paths. The machine-readable inventory links to each upstream release and lists its notices. [Wheel inventory](../offline/wheels.json)

On 25 November 2026, the 23 wheel digests in the current kit matched the inventory and the non-yanked files on PyPI. Version-specific PyPI queries and an OSV batch query returned no listed advisories for those exact versions. Coverage is limited to published advisories for the named distributions. Release hashes are unsigned. [PyPI JSON API](https://docs.pypi.org/api/json/) · [OSV version queries](https://google.github.io/osv.dev/post-v1-querybatch/)

## Licenses in the Windows kit

| Distribution license | Packages |
|---|---|
| MIT | annotated-doc, annotated-types, anyio, fastapi, h11, iniconfig, pluggy, pydantic, pydantic-core, pytest, typing-inspection |
| BSD-3-Clause | click, colorama, httpcore, httpx, idna, starlette, uvicorn |
| BSD-2-Clause | pygments |
| Apache-2.0 | opentelemetry-api |
| Apache-2.0 OR BSD-2-Clause | packaging |
| PSF-2.0 | typing-extensions |
| MPL-2.0 | certifi |

Each wheel retains its upstream notices, including file-specific attributions. The inventory's `source_release` links point to the upstream files for the exact versions, including the [certifi source distribution](https://pypi.org/project/certifi/2026.10.23/#files). These licenses apply to the corresponding third-party components.

The project grants Apache-2.0 rights in its original material to the extent authorized by its rights holders. Keep the upstream license, attribution and source information with any redistributed kit. The compiled pydantic-core wheel also contains a CycloneDX software bill of materials. The kit supplies supplementary notices for its upstream Rust dependency list. [Project license](../LICENSE) · [Rust dependency notices](../offline/pydantic-core-notices.txt)

The updated wheel pairs Pydantic 2.14.4 with pydantic-core 2.50.5. Its PyO3 0.30.1 dependency is outside the affected ranges for two advisories identified in the previous wheel. A separate OSV check of the 101 registry packages in the upstream Cargo lockfile identified one advisory for `url` 2.5.8. [PyO3 iterator advisory](https://rustsec.org/advisories/RUSTSEC-2026-0176.html) · [PyO3 closure advisory](https://rustsec.org/advisories/RUSTSEC-2026-0177.html) · [Application exposure](../SECURITY.md#native-dependency-advisory)

For a new release, collect the compatible upstream wheels, review changes and notices, update the inventory and lock, and verify an empty-environment installation against the bundled files. Generic Linux pins are separate from the Windows wheel lock.
