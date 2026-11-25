# Security boundary

Run the preview on one operator-controlled workstation with a mapping approved for one reseller. Start the service using the [Windows setup](docs/deployment.md). The documented command binds to 127.0.0.1, disables forwarded headers and access logging, and limits Uvicorn concurrency to eight. Binding and connection limits are server settings. A Host allowlist alone cannot restrict network access.

The API requires a bearer credential for every preview and compares it before reading the body. Health and the OpenAPI contract are readable locally. A holder of the token can query the active mapping through previews. Generate a fresh random token, protect the terminal and rotate the token by restarting the process. Protect the approved catalog with the workstation's filesystem permissions. Restart after replacing it.

Both input files have a 512 KiB and 5,000-record ceiling. The API checks cumulative bytes while streaming and gives the authenticated client 30 seconds to finish the body. Invalid files produce bounded diagnostic fields without quoting the supplied value. The application logs aggregate counts on completed previews. A response includes order IDs and mapped codes. Preview responses and application-handled errors carry `Cache-Control: no-store`. A saved response, shell transcript or screen capture needs the same protection as the source file.

The body deadline starts after authorization. Header reception, machine access, client-side retention and protection from another local process are workstation or server concerns. Shared hosting would require an authentication and isolation design, TLS, request and connection controls at ingress, and operational monitoring. The current support boundary is a single local operator.

## Native dependency advisory

The Windows pydantic-core 2.50.5 wheel lists Rust `url` 2.5.8 in its software bill of materials. RustSec reports a denial of service in the URL origin operation, fixed in `url` 2.5.9. Order Intake Check accepts CSV identifiers and quantities. Its preview API has no URL-typed business field, and the source review found no origin call on supplied data. Exploitability through this application has not been established. Reassess before adding URL inputs and adopt a compatible upstream wheel with the fix when available. The standalone CLI has no Pydantic dependency. [RustSec advisory](https://rustsec.org/advisories/RUSTSEC-2026-0592.html)

## Report a vulnerability

On the repository's [Security advisories page](https://github.com/mohammadabidizadeh/order-intake-check/security/advisories), use **Report a vulnerability** if the button is available. If it is unavailable, contact the maintainer through an existing private channel. If you have no private contact, request one in a repository issue using only the subject “Private security contact requested”. Share technical details after the maintainer establishes a private channel.

Include the version or commit, expected behavior and a minimal example with invented identifiers. Keep tokens, customer files, real mappings and identifying screenshots out of reports. Review the dated [dependency checks](docs/dependencies.md) before using a new release.
