# LNG Carrier Virtual Engineering Lab

**A pump reports running. Cargo flow has disappeared. Can you explain why?**

Learn the process, operate the model, inspect the controller and decode the packet.
Then use those observations to distinguish equipment failure, lost electrical supply
and a misleading measurement.

![Cargo process with the ship tank, pump, valve, shore receiver, electrical supply and controller signals](assets/visuals/cargo-system.svg)

*Teaching schematic of this lab's aggregate model. It is not a vessel piping design or a captured operator screen.*

## Get oriented

Start with the [visual guide](00-learning/visual-guide.md). It walks through one
process, one signal and one packet. You can read it without Docker.

| Your next step | What you will do |
|---|---|
| [Read and practise](00-learning/learning-journey.md) | Follow the course and explain each checkpoint in your own words |
| [Set up the lab](04-build/first-run.md) | Clone safely, check prerequisites and open the right interface |
| [Run the first Cargo investigation](06-scenarios/first-cargo-investigation.md) | Compare command, feedback, measured flow and tank-level movement |
| [Commission the complete stack](04-build/commissioning-orchestrator.md) | Validate PLC, OPC UA, HMI, historian and retained experiment evidence |

## What you are looking at

The **course website** is static documentation.
The **Learning Portal** reads the local model APIs and explains their state.
**FUXA** is the separate operator HMI and requires live OPC UA binding.
See the [interface map](04-build/first-run.md#which-page-should-open) before troubleshooting a blank screen.

The Cargo, PMS and Propulsion processes are dynamic Modelica/FMU teaching models.
OpenPLC executes control logic; Modbus and OPC UA are real protocol implementations.
Public marine material provides reference context, not a claim that this reproduces a particular vessel.

## Publication status

Source checks and container health do not prove a usable course or a commissioned lab.
The [learner-experience backlog](00-learning/learner-experience-backlog.md) records missing
runtime screenshots, detailed commissioning walkthroughs and learner review.
The [experimental claim boundaries](09-research/experimental-claim-boundaries.md)
explain what evidence is required before reporting runtime results.

For real hardware context, compare our software model with Figures 3, 9 and 10 in
[Lee's LNG-carrier PMS HIL study](https://www.mdpi.com/2077-1312/12/7/1236).
Continue with [the vessel introduction](01-vessel/lng-carrier-101.md).
