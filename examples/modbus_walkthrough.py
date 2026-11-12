"""One Modbus TCP read, byte by byte, plus RTU CRC and timing. Run: python examples/modbus_walkthrough.py"""
import struct


def tcp_read_request(tid, unit, fc, addr, qty):
    pdu = struct.pack(">BHH", fc, addr, qty)
    return struct.pack(">HHHB", tid, 0, len(pdu) + 1, unit) + pdu


def tcp_read_response(tid, unit, fc, registers):
    data = struct.pack(f">{len(registers)}H", *registers)
    pdu = bytes([fc, len(data)]) + data
    return struct.pack(">HHHB", tid, 0, len(pdu) + 1, unit) + pdu


def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def rtu_frame(unit, pdu):
    body = bytes([unit]) + pdu
    return body + struct.pack("<H", crc16(body))  # CRC goes out low byte first


def rtu_timing_ms(baud, request_len, response_len, bits_per_char=11):
    """Rough time on the wire for one poll: both frames plus the 3.5 char silent gap after each.
    11 bits per character is 1 start + 8 data + parity + 1 stop. Ignores device processing time."""
    char_ms = bits_per_char / baud * 1000
    return (request_len + response_len) * char_ms + 2 * 3.5 * char_ms


if __name__ == "__main__":
    req = tcp_read_request(1, 1, 3, 0, 2)
    resp = tcp_read_response(1, 1, 3, [0x41BC, 0x0000])
    print("TCP request :", req.hex(" ").upper())
    print("TCP response:", resp.hex(" ").upper())
    pdu = struct.pack(">BHH", 3, 0, 10)
    print("RTU request :", rtu_frame(1, pdu).hex(" ").upper(), "(read 10 registers from 0)")
    for baud in (9600, 19200, 115200):
        ms = rtu_timing_ms(baud, 8, 5 + 2 * 2)
        print(f"RTU poll of 2 registers at {baud:>6} baud: about {ms:.1f} ms")
