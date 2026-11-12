"""Mitsubishi SLMP / MC protocol 3E binary frame: read D100..D101. Run: python examples/slmp_walkthrough.py"""
import struct

DEVICE_CODES = {"D": 0xA8, "M": 0x90, "X": 0x9C, "Y": 0x9D, "W": 0xB4, "B": 0xA0}
WORD_DEVICES = {"D", "W"}


def read_request(device, number, points, timer=0x0010):
    """Command 0401 (batch read). Network 0, PLC 0xFF, module I/O 0x03FF, station 0."""
    sub = 0x0000 if device in WORD_DEVICES else 0x0001  # 0000 word units, 0001 bit units
    body = struct.pack("<HHH", timer, 0x0401, sub)
    body += number.to_bytes(3, "little") + bytes([DEVICE_CODES[device]]) + struct.pack("<H", points)
    header = bytes([0x50, 0x00, 0x00, 0xFF, 0xFF, 0x03, 0x00])
    return header + struct.pack("<H", len(body)) + body


def parse_word_response(frame):
    assert frame[:2] == bytes([0xD0, 0x00]), "not a 3E binary response"
    length, end_code = struct.unpack("<HH", frame[7:11])
    if end_code != 0:
        raise ValueError(f"PLC returned end code {end_code:#06x}")  # check this BEFORE reading data
    data = frame[11:7 + 2 + length]
    return list(struct.unpack(f"<{len(data) // 2}H", data))


if __name__ == "__main__":
    req = read_request("D", 100, 2)
    print("request :", req.hex(" ").upper())
    resp = bytes([0xD0, 0x00, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x06, 0x00, 0x00, 0x00, 0x34, 0x12, 0x01, 0x00])
    print("response:", resp.hex(" ").upper())
    print("values  :", parse_word_response(resp))
