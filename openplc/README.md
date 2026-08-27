# OpenPLC Commissioning

The repository contains three IEC 61131-3 Structured Text controller programs:

```text
openplc/cargo/CargoControl.st
openplc/pms/PowerManagement.st
openplc/propulsion/PropulsionControl.st
```

The OpenPLC Runtime containers execute the control programs. OpenPLC Editor is the engineering workstation used to build and deploy those projects.

## Runtime endpoints

| Domain | Runtime management | Remote I/O |
|---|---|---|
| Cargo | `https://localhost:8443` | `cargo-io:5020` |
| Power Management | `https://localhost:8444` | `pms-io:5021` |
| Propulsion | `https://localhost:8445` | `propulsion-io:5022` |

## Commissioning sequence

For each controller:

1. Open/import the corresponding Structured Text logic in OpenPLC Editor.
2. Add one Modbus TCP Remote I/O device.
3. Use the service hostname and port from the table above.
4. Use Unit ID `1`.
5. Add the I/O groups from `docs/08-reference/tag-registers.md`.
6. Map PLC variables to those groups.
7. Enable the OPC UA server for the engineering values that should be visible to HMI/historian clients.
8. Deploy the project to its runtime.
9. Verify live values in the Editor before commissioning FUXA or Telegraf.

## Why configuration is explicit

Current OpenPLC Runtime/Editor workflows generate runtime Modbus and OPC UA configuration from the Editor project. This project documents the engineering step instead of pretending a static runtime file is the authoritative configuration.

See:

- `docs/04-build/openplc-editor-commissioning.md`
- `docs/08-reference/tag-registers.md`
