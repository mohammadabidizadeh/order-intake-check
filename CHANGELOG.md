# Changelog

## 0.1.1 (prepared for release)

- Reject conflicting HTTP media declarations, duplicate credentials and unsupported charset or header settings. Bound upload time to 30 seconds and handle interrupted bodies. Validation runs off the ASGI event loop.
- Return a structured CLI error for unreadable input paths. Preview JSON, line ordering, whole-order holds and the valid-invocation exit codes are preserved.
- Parse quantities once, avoid retaining invalid line IDs, and release buffered lines for held orders while continuing to report subsequent issues.
- Make the reference schema installation transactional and its SQL checks repeatable. Exercise overlapping writes and dump/restore on an isolated PostgreSQL 18.6 instance.
- Verify Windows offline installs against package hashes. Add Windows to the CI matrix and compare the real CLI output to live HTTP responses.
- Document pilot acceptance criteria and provide a separate Windows offline kit with pinned, hash-checked wheels.
- License original project material under Apache-2.0 and document the upstream terms for the offline kit.
- Update Pydantic to 2.14.4 and pydantic-core to 2.50.5. The Windows wheel uses PyO3 0.30.1. The dependency review records the remaining native URL-library advisory and its scope.

## 0.1.0 — 2026-11-24

- Added a dependency-free command-line preview and an authenticated FastAPI adapter for one distributor's order feed.
- Added whole-order holds, exact SKU mapping, duplicate line checks, three numeral sets for quantities, streaming limits and actionable record-level issues.
- Added mixed and corrected synthetic examples, unit and API checks, a real loopback smoke test, a validation benchmark and an OpenAPI snapshot.
- Documented pilot acceptance criteria, operating constraints and a proposed PostgreSQL model.
- Included an optional offline dependency kit for CPython 3.14 on 64-bit Windows.

No customer deployment, external integration or paid engagement has taken place in this release.
