# Endpoints and Interfaces

This page answers a simple commissioning question: **what talks to what, and why?**

## Host-facing services

| Service | Host endpoint | Purpose |
|---|---|---|
| Learning Portal | `http://127.0.0.1:8500` | read-only teaching/explainability |
| FUXA | `http://127.0.0.1:1881` | operator HMI engineering/runtime |
| Alarm API | `http://127.0.0.1:8400` | teaching alarm chronicle |
| Cargo process | `http://127.0.0.1:8100` | plant state/contract |
| PMS process | `http://127.0.0.1:8200` | plant state/contract |
| Propulsion process | `http://127.0.0.1:8300` | plant state/contract |
| Vessel Coordinator | `http://127.0.0.1:8600` | cross-system dependency state |
| Grafana | `http://127.0.0.1:3000` | historical visualization |
| InfluxDB | `http://127.0.0.1:8086` | time-series database |
| Cargo OpenPLC | `https://127.0.0.1:8443` | engineering/deployment API |
| PMS OpenPLC | `https://127.0.0.1:8444` | engineering/deployment API |
| Propulsion OpenPLC | `https://127.0.0.1:8445` | engineering/deployment API |

## Modbus I/O interfaces

| Domain | Host port | Compose endpoint | Purpose |
|---|---:|---|---|
| Cargo | `5020` | `cargo-io:5020` | PLC ↔ Cargo I/O |
| PMS | `5021` | `pms-io:5021` | PLC ↔ PMS I/O |
| Propulsion | `5022` | `propulsion-io:5022` | PLC ↔ machinery I/O |

## OPC UA interfaces

| Domain | Host port | Operations-network endpoint |
|---|---:|---|
| Cargo | `4840` | `openplc-cargo:4840` |
| PMS | `4841` | `openplc-pms:4840` |
| Propulsion | `4842` | `openplc-propulsion:4840` |

## Important distinction

The exposed host ports exist for the learning environment.

They are **not** a recommendation to expose OT services broadly on a real vessel. The production design lesson remains segmentation and justified conduits.
