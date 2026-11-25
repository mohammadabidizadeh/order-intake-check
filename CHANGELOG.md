# Changelog

## 0.1.1 — 2026-11-24

- Reject conflicting HTTP media declarations, duplicate credentials and unsupported charset or header settings. Bound upload time to 30 seconds and handle interrupted bodies. Validation runs off the ASGI event loop.
- Return a structured CLI error for unreadable input paths. Preview JSON, line ordering, whole-order holds and the valid-invocation exit codes are preserved.
- Parse quantities once, avoid retaining invalid line IDs, and release buffered lines for held orders while continuing to report subsequent issues.
- Make the reference schema installation transactional and its SQL checks repeatable. Exercise overlapping writes and dump/restore on an isolated PostgreSQL 18.6 instance.
- Verify Windows offline installs against package hashes. Add Windows to the CI matrix and compare the real CLI output to live HTTP responses.
- Consolidate the pilot and engineering documents. The distribution contains the runnable source and wheel kit. Private career, legal and market planning and the old Git bundle remain in the original archive.

## 0.1.0 — 2026-11-24

- Added a dependency-free command-line preview and an authenticated FastAPI adapter for one distributor's order feed.
- Added whole-order holds, exact SKU mapping, duplicate line checks, three numeral sets for quantities, streaming limits and actionable record-level issues.
- Added mixed and corrected synthetic examples, unit and API checks, a real loopback smoke test, a validation benchmark and an OpenAPI snapshot.
- Recorded the market decision, hiring evidence, pilot acceptance criteria, operating constraints and a proposed PostgreSQL model.
- Included an optional offline dependency kit for CPython 3.14 on 64-bit Windows in the private release archive.

No customer deployment, external integration or paid engagement has taken place in this release.
