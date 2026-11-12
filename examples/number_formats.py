"""Number formats that cause trouble on the shop floor. Run it: python examples/number_formats.py"""
import struct


def as_signed(value, bits):
    """Read an unsigned register value as two's complement."""
    return value - (1 << bits) if value >= 1 << (bits - 1) else value


def float32_parts(x):
    """Split a float32 into sign / exponent / mantissa bit strings plus the hex bytes."""
    raw = struct.pack(">f", x)
    n = int.from_bytes(raw, "big")
    bits = f"{n:032b}"
    return bits[0], bits[1:9], bits[9:], raw.hex(" ").upper()


def word_orders(x):
    """The two registers a device would send for float32 x, in each common order."""
    a, b, c, d = struct.pack(">f", x)
    orders = {"ABCD": (a, b, c, d), "CDAB": (c, d, a, b), "BADC": (b, a, d, c), "DCBA": (d, c, b, a)}
    return {k: [v[0] << 8 | v[1], v[2] << 8 | v[3]] for k, v in orders.items()}


def counter_delta(previous, current, bits):
    """Increase of a free-running counter, treating wrap-around as normal."""
    return (current - previous) % (1 << bits)


if __name__ == "__main__":
    print("0xFFBC as int16 =", as_signed(0xFFBC, 16))
    print("0xBC as int8    =", as_signed(0xBC, 8), "(188 unsigned)")
    s, e, m, h = float32_parts(23.5)
    print(f"23.5 as float32: sign={s} exponent={e} mantissa={m} bytes={h}")
    for name, regs in word_orders(23.5).items():
        print(f"  {name}: {regs[0]:04X} {regs[1]:04X}")
    print("counter 65534 -> 3 (16-bit) delta =", counter_delta(65534, 3, 16))
