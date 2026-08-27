# Data Provenance Register

Every user-facing value must have a documented source.

## Cargo

| Tag | Source | I/O | PLC / use | Downstream |
|---|---|---|---|---|
| Source level | Modelica tank state | IR0, mm | transfer/safety context | OPC UA / HMI / historian |
| Destination level | Modelica tank state | IR1, mm | high-high context | OPC UA / HMI / historian |
| Measured flow | Modelica hydraulic flow + transmitter lag/bias | IR2, m³/h | no-flow verification | OPC UA / HMI / historian |
| Source pressure | `ρgh` teaching calculation | IR3, kPa×10 | process context | OPC UA |
| Pump power | hydraulic power estimate | IR6, kW | energy context | Vessel Coordinator / PMS |
| Pump feedback | dynamic pump speed threshold | DI1 | mismatch/no-flow logic | OPC UA / alarms |
| Valve feedback | dynamic valve-position threshold | DI0 | pump permissive | OPC UA / alarms |

## Power Management

| Tag | Source | I/O | PLC / use | Downstream |
|---|---|---|---|---|
| Frequency | PMS dynamic bus equation | IR0, Hz×100 | under-frequency / shedding | OPC UA / HMI / alarms |
| Total load | sum of active load components | IR4, kW | operator context | OPC UA / historian |
| Reserve | online capacity − load | IR5, kW | Gen 2 start decision | OPC UA / HMI / alarm |
| Cargo load | Cargo pumpPowerKW via coordinator | IR8, kW | dependency visibility | HMI / historian |
| Aux load | propulsion auxiliary output via coordinator | IR9, kW | dependency visibility | HMI / historian |
| Breaker feedback | PMS generator/breaker state | DI2/DI3 | sequencing | HMI / alarm context |

## Propulsion

| Tag | Source | I/O | PLC / use | Downstream |
|---|---|---|---|---|
| Engine RPM | shaft dynamic equation | IR0, RPM×10 | speed control/trip | OPC UA / HMI |
| Lube pressure | lube-system state equation | IR1, bar×100 | start permissive / trip | OPC UA / alarm |
| Coolant temperature | thermal state equation | IR2, °C×10 | machinery alarm | OPC UA / alarm |
| Propeller torque | speed/pitch load relationship | IR5, 10 N·m/count | load context | OPC UA |
| Auxiliary electrical load | machinery operating state | IR6, kW | Vessel Coordinator → PMS | HMI / historian |

## Cross-system provenance

The important integrated chain is:

```text
Cargo pump dynamics
→ pumpPowerKW
→ Vessel Coordinator
→ PMS externalCargoLoadKW
→ frequency / reserve / bus state
→ Vessel Coordinator
→ Cargo powerAvailable
→ Cargo pump dynamics
```

This closes a real causal loop between two software process models.

The provenance register exists to stop the HMI/historian from drifting away from the engineering model.
