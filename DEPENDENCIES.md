# Reviewed Dependencies

Explicit pins avoid silent drift:

- OpenModelica **1.27.0** — official stable release (July 2026).
- OpenPLC Runtime **4.1.9**.
- OpenPLC Editor **4.2.10**.
- FUXA **1.3.4**.
- Telegraf **1.39.3**.
- InfluxDB OSS **2.9.1** — current reviewed 2.x patch; retains the Flux/InfluxDB v2 contract used by this lab while fixing compaction issues. InfluxDB 2.9 hashes API tokens by default, so preserve any plaintext token needed by clients before upgrading an existing persistent volume.
- Grafana **13.2**.
- Zeek **8.0.10 LTS** for evidence analysis.
- Containerlab **0.77.0** — reviewed optional network-fidelity extension only; not required by the canonical Compose runtime.

Do not replace pinned images with `latest`. InfluxDB's Docker documentation specifically warns that the `latest` tag will change major product line in September 2026.

## Upgrade rule

1. Review upstream release/security notes.
2. Update this file and the technology-selection chapter.
3. Run static tests/traceability/research gates.
4. Run a Docker commissioning suite on a test server.
5. Compare normal baseline process and PCAP behavior.
6. For InfluxDB 2.9 upgrades, verify token continuity and a backup/restore before accepting the new historian baseline.

## Publication/CI dependencies reviewed 2026-08-27

- PyYAML **6.0.3** — exact direct CI dependency.
- pytest **9.1.1** — exact direct test dependency.
- MkDocs Material **9.7.7** — exact direct documentation dependency.
- `actions/checkout` **v6.1.0**, pinned in CI to commit `d23441a48e516b6c34aea4fa41551a30e30af803`.
- `actions/setup-python` **v6.3.0**, pinned in CI to commit `ece7cb06caefa5fff74198d8649806c4678c61a1`.

The current GitHub Actions major pins are intentionally one reviewed generation behind newly released v7 lines rather than adopting a fresh major without a project-specific CI migration test. Dependabot may propose updates, but the upgrade rule above still applies.
