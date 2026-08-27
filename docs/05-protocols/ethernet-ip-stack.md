# Ethernet / IP / TCP — The Layers Under the Lab

## Memory model

```text
Ethernet: who is on this local network?
IP: where is the host?
TCP: how do we deliver an ordered stream?
Application protocol: what does the message mean?
```

## Worked example — one Modbus read

A Wireshark frame can simultaneously contain:

1. Ethernet source/destination MAC,
2. IPv4 source/destination,
3. TCP source port → destination port 5020,
4. Modbus/TCP MBAP header,
5. function code and register request.

Do not stop at “port 502”. Follow the frame until you can name the exact process variable returned by that register.
