# Working on Order Intake Check

Describe a rule change with a small synthetic file and its expected order-level result. Keep CSV and grouping decisions in `ordercheck/intake.py`. Both entry points consume that result. Add a regression test for the changed behavior and run the core suite, full suite and live smoke check. [Developer commands](docs/developer-guide.md)

For an HTTP contract change, regenerate `docs/openapi.json`. For a dependency change, update the platform pins, rebuild the Windows inventory and hash lock, retain upstream notices and repeat the offline installation. Document user-visible changes in the changelog.

Use invented order and catalog values in examples, tests and pull requests. For a suspected vulnerability, follow the [private reporting instructions](SECURITY.md#report-a-vulnerability).

Submit only work you have permission to contribute. Unless explicitly stated otherwise, contributions intentionally submitted for inclusion are subject to section 5 of the Apache License, Version 2.0. Identify third-party material, its source and its terms, and preserve required notices. [Project license](LICENSE) · [Dependency provenance](docs/dependencies.md)
