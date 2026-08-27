# Learn It, Remember It, Explain It

The course is designed for **transfer**, not recognition.

Research on learning supports worked examples, retrieval practice, concrete examples, dual coding, spacing and progressively faded guidance. This course turns those ideas into an engineering pattern.

## The five-line memory model

For every OT concept, remember:

```text
PURPOSE → SIGNAL → DECISION → ACTION → EVIDENCE
```

Example — Cargo flow:

```text
PURPOSE   move cargo during the selected unloading profile
SIGNAL    measured flow + valve/pump feedback
DECISION  PLC permissive/interlock logic
ACTION    valve/pump command
EVIDENCE  Modbus + PLC state + process response + historian
```

## Three-pass learning

### Pass 1 — I show you
Read a fully worked example with the real-system visual and the exact lab evidence chain.

### Pass 2 — we do it
Follow the guided walkthrough, but predict the next state before revealing it.

### Pass 3 — you explain it
Close the page and answer:

1. What problem does this component solve?
2. What signal enters it?
3. What decision is made?
4. What physical/operational action follows?
5. What evidence would prove that happened?

If you cannot answer those five questions, repeat the worked example rather than memorizing vocabulary.

## Protocol memory model

For every protocol remember:

```text
WHERE → WHO TALKS → MESSAGE → MEANING → PROOF
```

For Modbus in this lab:

```text
WHERE    PLC ↔ remote I/O conduit
WHO      client requests; server responds
MESSAGE  MBAP + function + address + data
MEANING  address is mapped to an I/O/process point
PROOF    capture packet + correlate with tag/process change
```

## Explain-back standard

At the end of every major chapter, give a 60-second explanation to an engineer who has not read it. Avoid jargon that you cannot immediately define.
