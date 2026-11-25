# Dependency provenance

The CLI uses the Python standard library. Runtime and development pins live in `requirements.txt` and `requirements-dev.txt`. The private release ZIP includes 23 original wheels for standard 64-bit CPython 3.14 on Windows. The platform-specific lock adds SHA-256 checks during installation and includes the development requirements so incompatible pin changes fail resolution. [Windows setup](deployment.md)

On 24 November 2026, every shipped wheel matched the filename, SHA-256 and download URL of a non-yanked file on its version-specific PyPI release. The review read each wheel as a ZIP, verified the entries and hashed records in its RECORD, matched distribution name and version, and checked its listed notice paths. The machine-readable inventory links to each upstream release and lists its notices. [Wheel inventory](../offline/wheels.json)

Version-specific PyPI queries and an OSV batch query returned no listed advisories for the 23 exact versions on that date. Coverage is limited to published advisories for the named distributions. Upstream updates and the Windows/Python runtime have their own support cycles. Release hashes are unsigned. License terms for dependencies remain in their original wheels. [PyPI JSON API](https://docs.pypi.org/api/json/) · [OSV version queries](https://google.github.io/osv.dev/post-v1-querybatch/)

For a new release, collect the compatible upstream wheels, review changes and notices, update the inventory and lock, and verify an empty-environment installation against the bundled files. Generic Linux pins are separate from the Windows wheel lock.
