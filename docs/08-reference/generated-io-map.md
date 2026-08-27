# Generated I/O Map

> Generated from `io_emulator/configs/*.json` + `openplc/mapping_contract.json`. Do not hand-edit this page.

Configuration digest: `aa3ad6ec57f04eab`

## Cargo

Endpoint: TCP `5020`, Unit ID `1`

### Commands / instructor inputs

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Coil | 0 | `pumpCmd` | `DO_Pump` | Pump bank run command | Operator/PLC command | 0 / 1 |
| Holding Register | 0 | `valveCommand` | `AO_ValvePermille` | Cargo transfer valve position command | Operator/PLC command | model = raw × 0.001 p.u. |
| Coil | 20 | `faultPumpFail` | `— instructor only —` | Instructor pump-bank failure injection | Instructor-only fault | 0 / 1 |
| Coil | 21 | `faultValveStuck` | `— instructor only —` | Instructor valve-stuck failure injection | Instructor-only fault | 0 / 1 |
| Holding Register | 20 | `flowSensorBiasPct` | `— instructor only —` | Instructor positive flow-transmitter bias | Instructor-only fault | model = raw × 0.1 % |
| Coil | 22 | `faultFlowPathBlocked` | `— instructor only —` | Instructor hydraulic transfer-path blockage injection | Instructor-only fault | 0 / 1 |

### Measurements / feedback

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Input Register | 0 | `levelSource` | `AI_LevelSource_mm` | Aggregate ship cargo-tank liquid level in the selected unloading profile | Process measurement | model = raw × 0.001 m |
| Input Register | 1 | `levelDestination` | `AI_LevelDestination_mm` | Terminal-side receiving inventory proxy for mass-balance teaching; not an onboard tank measurement | Process measurement | model = raw × 0.001 m |
| Input Register | 2 | `flowMeasured` | `AI_Flow_m3h` | Lagged aggregate measured transfer flow | Process measurement | model = raw × 0.000277778 m3/s |
| Input Register | 3 | `pressureSource` | `AI_Pressure_kPa_x10` | Hydrostatic source pressure teaching value | Process measurement | model = raw × 0.1 kPa |
| Input Register | 4 | `valvePosition` | `AI_ValvePosition_x1000` | Actual cargo transfer valve position | Equipment feedback | model = raw × 0.001 p.u. |
| Input Register | 5 | `pumpSpeed` | `AI_PumpSpeed_x1000` | Aggregate cargo pump-bank speed | Equipment feedback | model = raw × 0.001 p.u. |
| Discrete Input | 0 | `valveFeedback` | `DI_ValveOpenFB` | Valve fully-open feedback | Equipment feedback | 0 / 1 |
| Discrete Input | 1 | `pumpFeedback` | `DI_PumpRunFB` | Pump bank running feedback | Equipment feedback | 0 / 1 |
| Discrete Input | 2 | `highHighDestination` | `DI_HighHighDestination` | Receiving-boundary high-high limit in the teaching model; not a vessel cargo-tank trip | Lab-model boundary state | 0 / 1 |
| Discrete Input | 3 | `lowLowSource` | `DI_LowLowSource` | Source tank low-low condition | Protective condition | 0 / 1 |
| Input Register | 6 | `pumpPowerKW` | `AI_PumpPower_kW` | Calculated aggregate cargo-pump electrical demand | Cross-system measurement | model = raw × 1 kW |

## Pms

Endpoint: TCP `5021`, Unit ID `1`

### Commands / instructor inputs

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Coil | 0 | `gen1StartCmd` | `DO_Gen1Start` | Generator 1 start command | PLC command | 0 / 1 |
| Coil | 1 | `gen2StartCmd` | `DO_Gen2Start` | Generator 2 start command | PLC command | 0 / 1 |
| Coil | 2 | `gen1BreakerCmd` | `DO_Gen1Breaker` | Generator 1 breaker close command | PLC command | 0 / 1 |
| Coil | 3 | `gen2BreakerCmd` | `DO_Gen2Breaker` | Generator 2 breaker close command | PLC command | 0 / 1 |
| Coil | 4 | `shedHotel` | `DO_ShedHotel` | Hotel/auxiliary load shed command | PLC command | 0 / 1 |
| Coil | 5 | `shedCargo` | `DO_ShedCargo` | Cargo electrical load shed command | PLC command | 0 / 1 |
| Holding Register | 0 | `loadHotelDemand` | `AO_LoadHotel` | Standalone hotel-load demand selector | Commissioning demand | model = raw × 1 BOOL |
| Holding Register | 1 | `loadCargoDemand` | `AO_LoadCargo` | Standalone cargo-load demand selector | Commissioning demand | model = raw × 1 BOOL |
| Holding Register | 2 | `loadPropulsionDemand` | `AO_LoadPropulsion` | Optional electric-propulsion load selector | Commissioning demand | model = raw × 1 BOOL |
| Coil | 20 | `faultGen1Trip` | `— instructor only —` | Instructor generator 1 trip | Instructor-only fault | 0 / 1 |
| Coil | 21 | `faultGen2Trip` | `— instructor only —` | Instructor generator 2 trip | Instructor-only fault | 0 / 1 |

### Measurements / feedback

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Input Register | 0 | `frequencyHz` | `AI_Frequency_x100` | Electrical bus frequency | Process measurement | model = raw × 0.01 Hz |
| Input Register | 1 | `voltagePU` | `AI_Voltage_x1000` | Electrical bus voltage | Process measurement | model = raw × 0.001 p.u. |
| Input Register | 2 | `gen1PowerKW` | `AI_Gen1Power_kW` | Generator 1 active power | Equipment measurement | model = raw × 1 kW |
| Input Register | 3 | `gen2PowerKW` | `AI_Gen2Power_kW` | Generator 2 active power | Equipment measurement | model = raw × 1 kW |
| Input Register | 4 | `totalLoadKW` | `AI_TotalLoad_kW` | Total connected model load | Process measurement | model = raw × 1 kW |
| Input Register | 5 | `spinningReserveKW` | `AI_Reserve_kW` | Online generation capacity minus current load | Derived process value | model = raw × 1 kW |
| Input Register | 6 | `gen1SpeedPU` | `AI_Gen1Speed_x1000` | Generator 1 prime-mover speed | Equipment measurement | model = raw × 0.001 p.u. |
| Input Register | 7 | `gen2SpeedPU` | `AI_Gen2Speed_x1000` | Generator 2 prime-mover speed | Equipment measurement | model = raw × 0.001 p.u. |
| Discrete Input | 0 | `gen1Ready` | `DI_Gen1Ready` | Generator 1 ready | Equipment feedback | 0 / 1 |
| Discrete Input | 1 | `gen2Ready` | `DI_Gen2Ready` | Generator 2 ready | Equipment feedback | 0 / 1 |
| Discrete Input | 2 | `gen1BreakerFB` | `DI_Gen1BreakerFB` | Generator 1 breaker closed feedback | Equipment feedback | 0 / 1 |
| Discrete Input | 3 | `gen2BreakerFB` | `DI_Gen2BreakerFB` | Generator 2 breaker closed feedback | Equipment feedback | 0 / 1 |
| Discrete Input | 4 | `underFrequency` | `DI_UnderFrequency` | Bus under-frequency condition | Protective condition | 0 / 1 |
| Discrete Input | 5 | `blackout` | `DI_Blackout` | Bus blackout/unavailable condition | Protective condition | 0 / 1 |
| Discrete Input | 6 | `gen1SyncPermissive` | `DI_Gen1SyncPermissive` | Generator 1 simplified synchronizing permissive | Interlock/permissive | 0 / 1 |
| Discrete Input | 7 | `gen2SyncPermissive` | `DI_Gen2SyncPermissive` | Generator 2 simplified synchronizing permissive | Interlock/permissive | 0 / 1 |
| Discrete Input | 8 | `busEnergized` | `DI_BusEnergized` | Electrical bus available/energized | Process state | 0 / 1 |
| Input Register | 8 | `cargoLoadActualKW` | `AI_CargoLoad_kW` | Actual cargo electrical load seen by PMS | Cross-system measurement | model = raw × 1 kW |
| Input Register | 9 | `auxiliaryLoadActualKW` | `AI_AuxLoad_kW` | Actual propulsion/machinery auxiliary load seen by PMS | Cross-system measurement | model = raw × 1 kW |

## Propulsion

Endpoint: TCP `5022`, Unit ID `1`

### Commands / instructor inputs

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Coil | 0 | `preLubeCmd` | `DO_PreLube` | Pre-lubrication pump command | PLC command | 0 / 1 |
| Coil | 1 | `engineEnable` | `DO_EngineEnable` | Main engine enable command | PLC command | 0 / 1 |
| Holding Register | 0 | `fuelCommand` | `AO_FuelPermille` | Normalized fuel/torque command | PLC command | model = raw × 0.001 p.u. |
| Holding Register | 1 | `pitchCommand` | `AO_PitchPermille` | Normalized propeller pitch/load command | PLC command | model = raw × 0.001 p.u. |
| Coil | 20 | `faultLubePumpFail` | `— instructor only —` | Instructor lube-pump failure injection | Instructor-only fault | 0 / 1 |
| Coil | 21 | `faultCoolingFail` | `— instructor only —` | Instructor cooling-system impairment injection | Instructor-only fault | 0 / 1 |

### Measurements / feedback

| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |
|---|---:|---|---|---|---|---|
| Input Register | 0 | `engineRPM` | `AI_EngineRPM_x10` | Main engine/shaft speed | Machinery measurement | model = raw × 0.1 rpm |
| Input Register | 1 | `lubeOilPressureBar` | `AI_LubeBar_x100` | Lube-oil pressure | Machinery measurement | model = raw × 0.01 bar |
| Input Register | 2 | `coolantTempC` | `AI_CoolantC_x10` | Cooling-water temperature | Machinery measurement | model = raw × 0.1 degC |
| Input Register | 3 | `vesselSpeedKn` | `AI_VesselSpeed_kn_x100` | Teaching vessel-speed response | Process measurement | model = raw × 0.01 kn |
| Input Register | 4 | `engineLoadPct` | `AI_EngineLoad_pct_x10` | Normalized engine load | Derived process value | model = raw × 0.1 % |
| Discrete Input | 0 | `engineRunning` | `DI_EngineRunning` | Engine running feedback | Equipment feedback | 0 / 1 |
| Discrete Input | 1 | `lowLubePressure` | `DI_LowLubePressure` | Low lube-oil protective condition | Protective condition | 0 / 1 |
| Discrete Input | 2 | `highCoolantTemp` | `DI_HighCoolantTemp` | High coolant-temperature condition | Protective condition | 0 / 1 |
| Discrete Input | 3 | `overspeed` | `DI_Overspeed` | Engine overspeed condition | Protective condition | 0 / 1 |
| Input Register | 5 | `propellerTorqueNm` | `AI_PropellerTorque_10Nm` | Propeller load torque | Machinery measurement | model = raw × 10 N*m |
| Input Register | 6 | `auxiliaryElectricalLoadKW` | `AI_AuxLoad_kW` | Propulsion/machinery auxiliary electrical demand | Cross-system measurement | model = raw × 1 kW |

