import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "examples"))

import modbus_walkthrough as mb
import mqtt_walkthrough as mq
import number_formats as nf
import slmp_walkthrough as sl


def test_signed_conversion():
    assert nf.as_signed(0xFFBC, 16) == -68
    assert nf.as_signed(0xBC, 8) == -68
    assert nf.as_signed(0x7FFF, 16) == 32767


def test_float_23_5_parts():
    s, e, m, h = nf.float32_parts(23.5)
    assert (s, e) == ("0", "10000011")
    assert m == "01111000000000000000000"
    assert h == "41 BC 00 00"


def test_word_orders_of_23_5():
    assert nf.word_orders(23.5) == {
        "ABCD": [0x41BC, 0x0000], "CDAB": [0x0000, 0x41BC],
        "BADC": [0xBC41, 0x0000], "DCBA": [0x0000, 0xBC41]}


def test_counter_delta_wraps():
    assert nf.counter_delta(65534, 3, 16) == 5
    assert nf.counter_delta(4294967295, 0, 32) == 1
    assert nf.counter_delta(10, 15, 16) == 5


def test_modbus_frames():
    assert mb.tcp_read_request(1, 1, 3, 0, 2).hex() == "000100000006010300000002"
    assert mb.tcp_read_response(1, 1, 3, [0x41BC, 0]).hex() == "000100000007010304" "41bc0000"


def test_crc_known_example():
    import struct
    assert mb.rtu_frame(1, struct.pack(">BHH", 3, 0, 10)).hex() == "01030000000ac5cd"


def test_rtu_timing_is_sane():
    slow, fast = mb.rtu_timing_ms(9600, 8, 9), mb.rtu_timing_ms(115200, 8, 9)
    assert 20 < slow < 40 and fast < slow / 10


def test_mqtt_publish_bytes():
    pkt = mq.publish_qos0("plant/line1/temp", b"23.5")
    assert pkt[0] == 0x30 and pkt[1] == 22 and len(pkt) == 24
    assert pkt[4:20] == b"plant/line1/temp"


@pytest.mark.parametrize("n,enc", [(0, "00"), (127, "7f"), (128, "8001"), (321, "c102"), (16383, "ff7f"), (16384, "808001")])
def test_remaining_length_examples(n, enc):
    # values from the MQTT 3.1.1 spec, section 2.2.3
    assert mq.encode_remaining_length(n).hex() == enc


def test_slmp_request_layout():
    assert sl.read_request("D", 100, 2).hex(" ").upper() == (
        "50 00 00 FF FF 03 00 0C 00 10 00 01 04 00 00 64 00 00 A8 02 00")


def test_slmp_bit_device_uses_bit_subcommand():
    assert sl.read_request("M", 0, 8)[13:15] == bytes([0x01, 0x00])


def test_slmp_response_ok_and_error():
    ok = bytes.fromhex("D0 00 00 FF FF 03 00 06 00 00 00 34 12 01 00")
    assert sl.parse_word_response(ok) == [0x1234, 1]
    bad = bytes.fromhex("D0 00 00 FF FF 03 00 02 00 61 C0")
    with pytest.raises(ValueError):
        sl.parse_word_response(bad)
