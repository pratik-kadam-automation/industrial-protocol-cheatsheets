# industrial-protocol-cheatsheets

![ci](https://github.com/pratik-kadam-automation/industrial-protocol-cheatsheets/actions/workflows/ci.yml/badge.svg)

Short notes on the protocols I keep running into when connecting PLCs, drives and gateways to a data platform: Modbus, MQTT, OPC UA, Siemens S7 and Mitsubishi SLMP.

I work on industrial IoT gateways, and most of the delays on a new site are small things: an address off by one, a float that reads as 2.3e-41, a request that times out because of a wrong unit ID. These are the notes I use to avoid repeating those mistakes.

Two rules for the repo:

1. **Numbers are computed, not typed.** The hex examples come from the scripts in `examples/`, and the tests check them. If a table says a frame is `00 01 00 00 00 06 ...`, a script built it.
2. **Unverified things are marked as unverified.** If I have not confirmed something against a manual or a device, the note says so.

## Contents

| Note | What is in it |
|---|---|
| [01 Numbers and bytes](docs/01-numbers-and-bytes.md) | Signed values, float32, 16-bit registers to 32-bit values, word order, counter rollover |
| [02 Modbus](docs/02-modbus.md) | Data model, addressing, TCP and RTU frames, exceptions, polling time at different baud rates |
| [03 MQTT](docs/03-mqtt.md) | Topics, QoS, retained messages, last will, client IDs, one packet built by hand |
| [04 OPC UA](docs/04-opc-ua.md) | Nodes, subscriptions, security modes, certificates, data type IDs |
| [05 PLC addressing](docs/05-plc-addressing.md) | Siemens S7 addresses, Mitsubishi SLMP frame and device codes |
| [06 When a device won't talk](docs/06-device-wont-talk.md) | The order I check things in, with commands |

Diagrams are in [docs/diagrams](docs/diagrams).

## Run the examples

Python 3.10 or newer, no packages needed.

```bash
python examples/number_formats.py
python examples/modbus_walkthrough.py
python examples/mqtt_walkthrough.py
python examples/slmp_walkthrough.py

pip install pytest
pytest
```

## A taste

The same two registers, `0x0000 0x4088`, read four ways:

| Word order | Value |
|---|---|
| ABCD | 2.3e-41 (nonsense) |
| CDAB | 4.25 |
| BADC | 4.9e-41 (nonsense) |
| DCBA | -5.8e-34 (nonsense) |

Only one order gives a number that makes sense. That is why the first thing to do with an unknown device is read a value you can see on its display.

## Related

- [plc-simulators](https://github.com/pratik-kadam-automation/plc-simulators): a Modbus TCP simulator you can test these against without hardware.

## Limits

These are notes from my own work, not a standard. Vendors differ, firmware differs, and manuals win. Check anything important against the official documents linked in each note.

MIT licensed.
