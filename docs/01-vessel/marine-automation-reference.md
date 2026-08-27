# Marine Automation Reference

The project does not invent its vessel architecture from a generic factory diagram.

## Kongsberg K-Chief

Public Kongsberg material describes K-Chief 600 as a distributed marine automation system supporting functions including:

- alarm and monitoring,
- auxiliary control,
- power management,
- propulsion control,
- ballast automation,
- cargo control and monitoring,
- HVAC,
- fire systems.

Kongsberg also describes standard modules communicating through dual redundant process buses/networks. Public hardware lists include operator panels, segment controllers, remote analog/digital I/O and CAN/Ethernet gateways.

This tells us several useful truths:

1. marine automation is distributed,
2. remote I/O is normal,
3. Ethernet is not the only communication medium,
4. CAN and serial/vendor interfaces can coexist with IP networks,
5. operator stations are separate from field acquisition,
6. type approval and class requirements matter.

## Current cyber-resilience evidence

Kongsberg has current class certificates listing K-Chief/K-Safe/AutoChief systems with IACS UR E27.

The lab uses this as a reference point for architecture thinking, not as a claim that our software stack is equivalent.
