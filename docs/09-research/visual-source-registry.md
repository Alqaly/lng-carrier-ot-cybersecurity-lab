# Visual Evidence Registry

The public course does **not** use generic homemade block diagrams as its primary teaching visuals.

The source of truth is `visual-manifest.json`, which assigns real visual references to Chapters 1–10.

## Publication order

Prefer:

1. official manufacturer / industry visual,
2. open-license academic figure,
3. screenshot from the running lab,
4. packet capture / Wireshark / Zeek output,
5. OPC UA browser evidence,
6. HMI / historian trend,
7. custom explanatory figure only when none of the above can teach the concept.

Every external visual must be accompanied by four annotations:

**Source** — where the figure came from.  
**What to notice** — the two or three details the learner should inspect.  
**Lab mapping** — which executable component teaches the same concept.  
**Limitation** — what the lab does not reproduce.

## Open-license LNGC visual set

K. Lee, *Development of Hardware-in-the-Loop Simulation Test Bed to Verify and Validate Power Management System for LNG Carriers*, JMSE 2024, is CC BY 4.0.

Use these figures where they improve the lesson:

- Figure 3 — HIL simulator and target-system concept.
- Figure 9 — integrated PMS-HIL test bed.
- Figure 10 — network configuration.
- Figure 11 — condition-monitoring GUI.

Official article: https://www.mdpi.com/2077-1312/12/7/1236

## Runtime visual evidence

The repository must not ship invented screenshots. During commissioning, capture:

- OpenPLC online values for each domain,
- FUXA operator display,
- OPC UA browser with exact NodeIds and Quality,
- Grafana trends from the current experiment,
- Wireshark Modbus transaction decode,
- Zeek `conn.log` / Modbus evidence,
- alarm chronology,
- full-vessel event timeline.

Store them in the experiment run directory and use those screenshots in the final website/Notion publication.
