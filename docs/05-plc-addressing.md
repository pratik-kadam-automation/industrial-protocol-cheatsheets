# 05 PLC addressing

## Siemens S7 (S7-1200 / S7-1500)

Address format in a data block:

| Address | Meaning | Size |
|---|---|---|
| `DB1.DBX0.0` | bit 0 of byte 0 | 1 bit |
| `DB1.DBB2` | byte at offset 2 | 8 bit |
| `DB1.DBW4` | word at offset 4 | 16 bit |
| `DB1.DBD6` | double word at offset 6 | 32 bit |

Other areas: `I` inputs, `Q` outputs, `M` memory bits. S7 data is big-endian, so a REAL in `DBD6` is a normal ABCD float32.

Offsets count bytes, so a DBW at offset 4 occupies bytes 4 and 5, and the next free word is at offset 6.

To read a data block from outside with an S7 library (port 102), the CPU has to allow it:

1. In the data block's properties, turn **off** "Optimized block access". With it on, there are no fixed offsets.
2. In the CPU's protection settings, allow **PUT/GET** access from remote partners.

Rack and slot are usually 0 and 1 for S7-1200 and S7-1500. Check for your CPU.

Three ways I know to get S7 data into a gateway:

| Route | Notes |
|---|---|
| Modbus TCP server function block in the PLC | Needs a PLC program change |
| S7 library (for example a Python or Node.js S7 driver) | No PLC program change, but the settings above |
| OPC UA server on the CPU | Depends on CPU and firmware, and may need a license |

## Mitsubishi SLMP / MC protocol (3E frame, binary)

Official reference: Mitsubishi's SLMP reference manual for your series. Frame example from `examples/slmp_walkthrough.py`.

Reading D100 and D101:

```
50 00 00 FF FF 03 00 0C 00 10 00 01 04 00 00 64 00 00 A8 02 00
```

| Bytes | Field |
|---|---|
| `50 00` | Subheader: 3E binary request |
| `00` | Network number |
| `FF` | PLC number (own station) |
| `FF 03` | Request destination module I/O, 0x03FF |
| `00` | Destination station |
| `0C 00` | Length of everything after this field = 12 |
| `10 00` | Monitoring timer |
| `01 04` | Command 0x0401, batch read |
| `00 00` | Subcommand 0x0000, word units (`01 00` for bit units) |
| `64 00 00` | Start device number 100, 3 bytes, low byte first |
| `A8` | Device code for D |
| `02 00` | Number of points = 2 |

All multi-byte fields are little-endian. The response begins `D0 00`, then the same routing bytes, a length, a 2-byte **end code**, and the data. End code `0x0000` means success.

```
D0 00 00 FF FF 03 00 06 00 00 00 34 12 01 00     -> values 0x1234 and 0x0001
```

**Check the end code before reading the data.** If you skip that, the error bytes get parsed as register values and you chase a data problem that does not exist.

Device codes (binary), confirmed against several independent references:

| Device | Code | Type |
|---|---|---|
| D data register | `A8` | word |
| W link register | `B4` | word |
| M internal relay | `90` | bit |
| X input | `9C` | bit |
| Y output | `9D` | bit |
| B link relay | `A0` | bit |

Notes:

- SLMP can run over TCP or UDP, depending on how the Ethernet port on the PLC is configured. Find out which before debugging frames. The port number is whatever is set in the PLC's Ethernet settings.
- The number base for X and Y device numbers differs between series (some are octal or hexadecimal in the programming tool). I have not verified how that carries into the request, so check the manual for your series before reading X and Y.
- Reads are harmless in principle. Writes (command 1401) can change a running machine. Try the frame on a bench PLC or a simulator first.
