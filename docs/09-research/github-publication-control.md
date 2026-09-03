# GitHub Publication Control

Canonical remote: `https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab`

GitHub is a publication and reproducibility boundary, not a substitute for runtime acceptance. The repository ships read-only CI permissions, immutable SHA-pinned GitHub Actions, exact direct Python documentation/test dependencies, Dependabot and CODEOWNERS.

A GitHub commit is publication-ready only when:

1. local recursive gates pass;
2. the GitHub `quality` workflow passes, including `mkdocs build --strict`;
3. no `.env`, real credential, private vessel data or runtime secret is committed;
4. `release-manifest.json` matches the current source tree;
5. runtime claims remain `pending_target_server` until Gates A–G are preserved as evidence.

Every experiment run should record the repository commit so evidence can be traced back to exact source. `./labctl commission start` freezes that source identity for a Gates A–G run; `commission record` copies and hashes live evidence; and `commission finalize` refuses mixed commits, missing semantic PASS fields or mismatched retained hashes.
