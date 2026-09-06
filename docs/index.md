# LNG Carrier Virtual Engineering Lab

Learn to follow a vessel event from **process equation to controller, packet,
operator response and defensible evidence**.

Start the [learning journey](00-learning/learning-journey.md): choose a reader,
builder or investigator path, follow the prerequisites, and retain an
explanation at each checkpoint. No Docker is required to start reading.

Ready for hands-on work? Use [safe first run](04-build/first-run.md).
Already collecting evidence? Take the
[investigation capstone](00-learning/investigation-capstone.md).

> **Publication boundary:** this website teaches the lab. It does not operate
> PLCs or certify a vessel system. Source validation, learning progress and live
> Gates A–G acceptance are separate claims.

> **Visual tour:** Begin with the real LNGC PMS-HIL architecture and network in Figures 3 and 10 of Lee (2024, CC BY 4.0): https://www.mdpi.com/2077-1312/12/7/1236
>
> Then compare that real test-bed concept with the executable topology described below.

This documentation is meant to be read as a course and used as a build guide.

The project combines:

- marine-system research,
- process modelling,
- PLC programming,
- industrial protocols,
- network architecture,
- logging and historical data,
- packet analysis,
- incident investigation.

The executable environment is deliberately separated from the real-vessel reference layer so the reader always knows what is being **simulated**, what is being **implemented as a real protocol/runtime**, and what is being **described from marine industry sources**.

Start with [Start Here](start-here.md).
