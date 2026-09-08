# Your learning journey

Start with the vessel. Finish by defending an investigation with evidence.
You do not need Docker to begin. Read the chapters and complete the paper
exercises first; live exercises require an isolated, commissioned lab.

If you already started the executable lab with `./labctl build`, open
**http://127.0.0.1:8500** and complete **Guided start** first. It is the default
portal view and walks through one Cargo transfer in seven connected steps:
process, power, transfer, packet, sensor bias, supervision and explain-back.
The portal remains readable when model telemetry is unavailable and never
substitutes a sample value for a missing live value. Its saved notes are private
practice, not commissioning evidence.

Choose a path below. Progress stays in this browser on this device. Check a
module only after attempting its explain-back without notes. It is a practice
record, **not a certificate, verified evidence or a commissioned release**.

<section id="learning-journey" aria-label="Learning journey">
<p>Loading the learning path. If scripting or storage is unavailable, use the chapter list below; no account is required.</p>
</section>

## The course without scripting

1. [Define the project and its limits](../course/01-project-orientation.md).
2. [Understand the connected vessel](../course/02-lng-carrier-system.md).
3. [Separate command, feedback and process consequence](../course/03-ot-foundations.md).
4. [Trace the architecture and trust boundaries](../course/04-architecture.md).
5. [Build and commission on your Linux host](../course/05-build-and-commission.md).
6. [Explain Cargo behavior with physics](../course/06-cargo.md).
7. [Read protocols at message level](../course/07-protocol-academy.md).
8. [Reason from alarms to operator decisions](../course/08-safety-hmi-alarms.md).
9. [Keep navigation claims inside the evidence](../course/09-navigation.md).
10. [Defend a cross-layer reconstruction](../course/10-detection-reconstruction.md).

The builder path focuses on the executable Cargo/PMS/Propulsion stack. The reader
path deliberately excludes live commissioning and the assessed capstone.
The investigator path includes all ten modules. Paths filter emphasis, not access.
You may open any chapter at any time; prerequisites guide the next recommended step.

## A repeatable study session

**See:** inspect the attributed real-system reference linked by the chapter.
**Trace:** map one signal through code, I/O and protocols.
**Do:** follow the worked example and predict the next observation.
**Break:** change only one declared condition in the isolated lab.
**Explain:** close the notes and defend the causal chain and one limitation.

Revisit your explanation after approximately **1, 7 and 21 days**. This is a
practical study schedule, not a measured optimum for this course. Mix one Cargo
question with one PMS, propulsion or OPC UA question. The
[memory guide](memory-and-explain-back.md) and `./labctl quiz` provide prompts.
No background reminders or tracking are enabled by this page.

## Readiness is not a checkbox

| Milestone | What it establishes | What it does not establish |
|---|---|---|
| Learning checkpoint | You attempted a causal explanation | Independent competence or certification |
| Automated source review | The tested contracts and regressions pass | Live PLC, HMI or historian operation |
| Gates A–G dossier | Required retained acceptance evidence passes its checks | Certified safety or tamper-proof observation authenticity |
| Repeated experiments | Comparable retained runs meet the stated checks | Generalized superiority or research novelty |

Finish with the [investigation capstone](investigation-capstone.md). Builders
should use the [safe setup guide](../04-build/first-run.md), then preserve the
exact commissioning run and source commit throughout acceptance.

## The same path in your terminal

```bash
./labctl learn
./labctl learn show 06
./labctl learn check
```

The terminal and website read one versioned learning contract. Terminal commands
above do not start Docker, change PLC state or mark progress complete.
