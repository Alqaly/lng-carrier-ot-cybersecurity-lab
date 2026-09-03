# Experimental Claim Boundaries

## Why this matters

A plausible trace is not a research result. This project tests whether cross-layer evidence improves reconstruction; it does not assume that conclusion.

## Required comparison

Each controlled event is reconstructed from three views:

1. network-only evidence;
2. process/controller evidence without network metadata;
3. combined network, controller, process, alarm, historian and dependency evidence.

Event-order accuracy and reconstruction completeness must be defined before analysis. Each metric records its evidence source, unit and timestamp semantics. An unavailable measurement stays unavailable.

## Repetition and provenance

Use `./labctl aggregate-runs` on evaluated runs from the same experiment and clean Git commit. The aggregator reports mixed commits, dirty runs and insufficient repetitions instead of combining them silently. Three repetitions are the default minimum for a candidate comparison; the research design may require more after variance is observed.

## OPC UA observation boundary

The executable experiment isolates the PLC operations-network attachment, preserves the Modbus control conduit and observes publication/historian freshness loss. It does not validate production PKI, certificate lifecycle, user authorization, every security policy/mode, formal conformance or exploit resistance. `config/opcua-security-boundary.json` is authoritative.

## Detection language

Before repeated evidence exists, say “the project tests whether” or “the prospective contribution is.” Do not say the platform improves detection, proves root cause or outperforms network-only monitoring. The machine-readable gate is `config/detection-claims.json`.

## Acceptance dossier

Target-server acceptance requires retained artifacts for Gates A–G. `./labctl acceptance-dossier` hashes each required artifact and fails while anything is missing. A manually checked box or healthy-container screenshot is not a substitute.
