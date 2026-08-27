# System Design

## Visual tour

Compare two real references before the software architecture:

- K-Chief distributed marine automation: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/
- LNGC PMS-HIL network, Figure 10 (CC BY 4.0): https://www.mdpi.com/2077-1312/12/7/1236

**Notice:** distributed control, named interfaces and separation between simulator/test object/operator systems. The lab preserves these architectural ideas without claiming vendor equivalence.

The architecture is organized around functions and trust boundaries.

## Zones

- Engineering
- Cargo Control
- Process / I/O
- Historian / Operations
- Navigation
- Security Monitoring
- External / Ship-Shore reference

## Conduits

A conduit exists only when there is an operational reason.

Example:

```text
OpenPLC → Virtual I/O
Purpose: read measurements and command actuators
Protocol: Modbus TCP
```

```text
Telegraf → OpenPLC
Purpose: collect process state
Protocol: OPC UA
```

## Why this is better than a flat lab

If every service can reach every other service, the learner cannot distinguish:

- operational traffic,
- maintenance traffic,
- monitoring traffic,
- safety-related traffic,
- unnecessary reachability.

Segmentation is part of the lesson, not decoration.

## Remember it

**Zone = assets with a reason to trust/group them. Conduit = justified communication between zones.**

## Explain it in 60 seconds

Pick one allowed conduit and explain why it exists, what protocol crosses it and what should *not* cross it.
