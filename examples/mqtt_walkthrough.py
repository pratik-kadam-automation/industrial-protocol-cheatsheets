"""Build an MQTT 3.1.1 PUBLISH packet by hand. Run: python examples/mqtt_walkthrough.py"""


def encode_remaining_length(n):
    """MQTT's variable length field: 7 bits per byte, top bit means 'more follows'."""
    out = bytearray()
    while True:
        digit, n = n % 128, n // 128
        out.append(digit | 0x80 if n else digit)
        if not n:
            return bytes(out)


def publish_qos0(topic, payload, retain=False):
    t = topic.encode()
    body = len(t).to_bytes(2, "big") + t + payload
    return bytes([0x30 | int(retain)]) + encode_remaining_length(len(body)) + body


if __name__ == "__main__":
    pkt = publish_qos0("plant/line1/temp", b"23.5")
    print(pkt.hex(" ").upper())
    print(f"{len(pkt)} bytes on the MQTT layer for a 4 byte payload")
    j = publish_qos0("plant/line1/temp", b'{"v":23.5,"q":"good"}')
    print(f"same topic with a small JSON payload: {len(j)} bytes")
    print("remaining length 321 encodes as", encode_remaining_length(321).hex(" ").upper())
