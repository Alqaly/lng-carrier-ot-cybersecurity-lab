# Cargo System — From Process Meaning to Control Signals

The executable lab focuses deeply on Cargo because it is the easiest place to connect:

- process physics,
- PLC logic,
- I/O,
- Modbus,
- OPC UA,
- alarms,
- historian data,
- cyber investigation.

## Simplified loading story

```text
Loading requested
      ↓
transfer permissives true
      ↓
valve opens
      ↓
pump runs
      ↓
flow begins
      ↓
source level falls
destination level rises
      ↓
pressure and feedback update
```

The software process model calculates those state changes from conservation equations.

## LNG mapping

The software model uses a generic liquid-transfer system because reproducing cryogenic LNG thermodynamics correctly would require a much larger specialized model.

The marine reference layer explains the LNG-specific differences:

- cryogenic temperature,
- cargo tank design,
- BOG,
- specialized pumps/valves,
- reliquefaction,
- ship/shore transfer safety.

Wärtsilä public gas-system material is used as one real-world reference.


## Public equipment anchor used by the software model

A Wärtsilä public reference for a typical 138,000 m³ LNG tanker describes:

- four membrane cargo tanks,
- two 1700 m³/h electric submerged cargo pumps in each tank.

The executable Cargo model therefore uses an **aggregate eight-pump bank** with nominal combined flow of:

```text
8 × 1700 m³/h = 13,600 m³/h
```

This does **not** mean the model is a digital twin of that ship. Tank geometry, pump head, efficiency, cryogenic thermodynamics and control logic remain documented teaching assumptions.

The point is that the scale and equipment relationship are anchored to an actual public LNG-carrier example rather than chosen only because the numbers look industrial.
