# Verification record for 0.1.1

## GitHub Actions

On 25 November 2026, GitHub recorded a successful push run of `Verify preview` on `main` at `fc5c18d466899b02a29ade897787e76ef81b0af6`. Run 45570396805, attempt 1, finished at 07:44:16 UTC. The run and all three job conclusions were checked through the GitHub API. [Workflow run](https://github.com/mohammadabidizadeh/order-intake-check/actions/runs/45570396805)

| Job | Steps completed successfully |
|---|---|
| [Windows Server 2022](https://github.com/mohammadabidizadeh/order-intake-check/actions/runs/45570396805/job/139055335503) | Hash-checked installation, pip check, pytest and live CLI/API smoke test |
| [Ubuntu 24.04](https://github.com/mohammadabidizadeh/order-intake-check/actions/runs/45570396805/job/139055335540) | Dependency installation, pip check, pytest and live CLI/API smoke test |
| [Database schema](https://github.com/mohammadabidizadeh/order-intake-check/actions/runs/45570396805/job/139055335035) | PostgreSQL container startup, schema installation and two constraint runs |

This hosted run precedes the Apache-2.0 release changes and the Pydantic update. The release notes identify the exact Git commit used for the offline ZIP. Use that SHA when checking the subsequent hosted run.

## Local checks of fc5c18d on 25 November 2026

The checked-out branch, origin tracking branch and remote `main` all pointed to the commit above. On Windows, pytest reported 41 tests and 33 subtests passed. The standard-library suite passed all 17 tests on both CPython 3.14.10 and 3.15.2. The live CLI/HTTP check held PO-101 at record 5 and released both orders after correction.

In a new PostgreSQL 18.6 cluster, the schema installed and the constraint suite passed twice. All five tables were empty after rollback. A concurrent insert on the same replay key and a conflicting external order were rejected. A custom-format dump restored matching table contents and identity sequence values in a fresh database. The constraint suite passed again after restore.

The independent synthetic checks also passed for 200 interleaved files and 30 concurrent-client HTTP requests of 5,000 lines each. All order data used for verification were invented.

## Local comparison on 24 November 2026

The original baseline and revised implementation were exercised on Windows 10 x64 (build 19045), CPython 3.14.10 and PostgreSQL 18.6. The following comparison and performance measurements describe those earlier runs.

| Check | 0.1.0 baseline | 0.1.1 review |
|---|---|---|
| Standard-library tests on Python 3.14 | 13 passed | 17 passed. The same core suite also passed on 3.15.2. The HTTP wheel kit targets 3.14. |
| Full Python suite | 25 passed, 22 subtests passed | 41 passed, 33 subtests passed. Subtests are reported separately by pytest. |
| Original and corrected CSV | 1 ready / 1 held, then 2 ready / 0 held | Same results. CLI exits 2 then 0. Live Uvicorn returned the complete CLI JSON for each file. Health and authentication also passed. |
| Windows dependency installation | 23 wheels installed offline, pip check passed | Hash-checked offline install with a fresh environment and pip check. PyPI file digests, internal wheel records and notices checked. [Audit scope](dependencies.md) |
| PostgreSQL schema | Installation and first check passed. Second run failed on a foreign key because the test assumed source ID 1. | Atomic DDL succeeded. Two successive constraint runs passed. All five tables remained empty after both rollbacks. |
| Workflow | Supplied Linux and SQL jobs | actionlint 1.7.12 passed for the Windows/Linux/SQL workflow. Both action pins matched upstream tags. |

The first baseline pytest attempt had 24 passes and one fixture setup error. The Windows default pytest temp directory denied access. Redirecting TEMP and TMP to a writable review directory produced the clean baseline above. No existing temp-directory ACL was changed.

## Changes exercised

- The baseline returned HTTP 200 for valid UTF-8 bytes even when the caller declared Latin-1, an absent header, or conflicting charsets. These cases now return 415. UTF-8 with a quoted charset and a present header still succeeds.
- A completed body, interrupted stream, expired body deadline, cumulative byte excess and an unauthorized request with an unreadable body were exercised separately. Deadline coverage uses a short test override. The production setting is 30 seconds.
- New checks cover multiple HTTP header values, startup catalog snapshots, exactly 512 KiB, both record limits, Unicode and identifier boundaries, logical numbering after a quoted multiline field, and a late file error yielding no partial CLI output. An unreadable path now has a parseable JSON problem on stderr.
- An independent review script assembled full expected results for 200 seeded CSVs with 10,000 interleaved records. It compared order, line and issue order, mapped codes, quantities and counts. All matched. The revised identifier predicate matched the specified alphanumeric/punctuation rules at both positions for all 1,114,112 Unicode code points under Python 3.14.

## PostgreSQL experiment

A fresh UTF-8, SCRAM-authenticated cluster listened on a private loopback port. The existing Windows database service stayed stopped. The SQL suite checked five original rejection cases plus maximum quantity overflow, malformed file and catalog digests, and unsupported event type. Positive checks covered quantity endpoints, leading zeroes, shared external IDs across sources, and scoped replay keys.

In a populated test database, session A held an uncommitted insert and session B attempted the same source/key. An independent session observed the wait using `pg_blocking_pids`. After A committed, B returned SQLSTATE 23505. One batch remained. A different key attempting an existing external order also raised 23505, and the new batch rolled back.

The review inserted an order, line and event, ran `pg_dump -Fc`, and used `pg_restore --single-transaction` into a new empty database. Full row values matched for each of the five populated tables, identity sequence values matched, and the constraint suite passed on the restored schema. The temporary server was stopped. These are database-level checks. The preview has no write endpoint, accepted-order transaction or automated backup policy.

## Performance observations

Each validation run used 5,000 lines, 1,000 orders and 54,487 bytes, with one warm-up followed by ten timed calls in a fresh Python process. The two versions used the same interpreter and inputs. The run order was baseline, revised, revised, baseline.

| Version / run | Min ms | Median ms | Max ms |
|---|---:|---:|---:|
| 0.1.0 / 1 | 26.86 | 34.82 | 42.08 |
| 0.1.1 / 1 | 22.73 | 28.31 | 33.61 |
| 0.1.1 / 2 | 20.11 | 28.83 | 29.81 |
| 0.1.0 / 2 | 36.58 | 41.69 | 45.08 |

In a separate loopback test, three clients completed 30 authenticated requests after one warm-up. Each request contained 5,000 lines and 74,487 bytes. All 30 full responses matched an independently constructed expected result. Median time to receive the response body was 68.99 ms, nearest-rank p95 was 95.03 ms and maximum was 109.69 ms. Client JSON comparison ran outside the timer. The machine, OS scheduling and synthetic input affect these figures. Customer latency, operator time saved and a production SLA require different measurements.

## Readiness

The source and examples support a portfolio demonstration and a local read-only trial after an operator supplies an approved feed, mapping and answer key. A production deployment would need a destination agreement, reconciliation, access controls and recovery appropriate to its operating model. Customer interviews, a paid trial, real-order accuracy and measured business savings have no evidence in this review. [Pilot acceptance](product.md) · [Reproduction commands](developer-guide.md)
