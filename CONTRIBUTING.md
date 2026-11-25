# Working on Order Intake Check

Describe a rule change with a small synthetic file and its expected order-level result. Keep CSV and grouping decisions in `ordercheck/intake.py`. Both entry points consume that result. Add a regression test for the changed behavior and run the core suite, full suite and live smoke check. [Developer commands](docs/developer-guide.md)

For an HTTP contract change, regenerate `docs/openapi.json`. For a dependency change, update the platform pins, rebuild the Windows inventory and hash lock, retain upstream notices and repeat the offline installation. Document user-visible changes in the changelog.

Use invented examples in source control. The ZIP is a clean source snapshot. Earlier private planning documents and the original local history remain in the owner's 0.1.0 archive. Review history, authorship, data rights and the intended license before making a repository public.
