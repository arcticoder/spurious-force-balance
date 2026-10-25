"""
protocol.py — the USB streaming protocol between the instrument and the host logger (WP8). MicroPython-compatible (struct, no dataclasses); the host imports the same file.

Packet:  0xA5 0x5A | type u8 | seq u8 | length u16 LE | payload | CRC-16/CCITT u16 LE over (type, seq, length, payload)
The sequence number counts packets and wraps at 256; the host reports gaps. The CRC is the ADS131A04's (poly 0x1021, init 0xFFFF).
Payloads (all little-endian; timestamps are the device's microsecond counter, u32, which wraps every 71.6 minutes: the host unwraps it):
    T_ADC     1  t_us u32, n u8, then n frames of 4 x int32 (the ADS131A04's signed 24-bit codes)
    T_LOCKIN  2  t_us u32, then I and Q of the 4 channels: 8 x int32 (lock-in per-period sums, A = I / 4)
    T_ENV     3  t_us u32, 3 x int16 TMP117 raw (1/128 degC), 3 x int16 LIS2DW12 raw (0.244 mg), 3 x int32 field in micro-gauss, 3 x int32 field offset in micro-gauss
    T_TEXT    4  UTF-8 text (a log line)
"""

import struct

SYNC = b"\xA5\x5A"
T_ADC, T_LOCKIN, T_ENV, T_TEXT = 1, 2, 3, 4
MAX_PAYLOAD = 1024


def crc16(data, crc=0xFFFF):
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def packet(ptype, seq, payload):
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload too long")
    body = struct.pack("<BBH", ptype, seq & 0xFF, len(payload)) + bytes(payload)
    return SYNC + body + struct.pack("<H", crc16(body))


def adc_payload(t_us, frames):
    out = struct.pack("<IB", t_us & 0xFFFFFFFF, len(frames))
    for f in frames:
        out += struct.pack("<4i", *f)
    return out


def lockin_payload(t_us, i4, q4):
    return struct.pack("<I8i", t_us & 0xFFFFFFFF, *(list(i4) + list(q4)))


def env_payload(t_us, temps_raw, acc_raw, field_ug, offset_ug):
    return struct.pack("<I3h3h3i3i", t_us & 0xFFFFFFFF, *(list(temps_raw) + list(acc_raw) + list(field_ug) + list(offset_ug)))


def parse_payload(ptype, payload):
    """-> dict (host side)."""
    if ptype == T_ADC:
        t, n = struct.unpack_from("<IB", payload, 0)
        if len(payload) != 5 + 16 * n:
            raise ValueError("ADC payload length")
        return {"t_us": t, "frames": [struct.unpack_from("<4i", payload, 5 + 16 * k) for k in range(n)]}
    if ptype == T_LOCKIN:
        v = struct.unpack("<I8i", payload)
        return {"t_us": v[0], "i": v[1:5], "q": v[5:9]}
    if ptype == T_ENV:
        v = struct.unpack("<I3h3h3i3i", payload)
        return {"t_us": v[0], "temps_raw": v[1:4], "acc_raw": v[4:7], "field_ug": v[7:10], "offset_ug": v[10:13]}
    if ptype == T_TEXT:
        return {"text": bytes(payload).decode("utf-8", "replace")}
    raise ValueError("unknown packet type %d" % ptype)


class Decoder:
    """Feed bytes; get packets. Resynchronizes on the next sync pattern after garbage or a bad CRC; counts what it dropped."""

    def __init__(self):
        self.buf = bytearray()
        self.bad_crc = 0
        self.skipped_bytes = 0
        self.gaps = 0  # missing packets by sequence number
        self._last_seq = None

    def feed(self, data):
        self.buf += data
        out = []
        while True:
            i = self.buf.find(SYNC)
            if i < 0:
                keep = 1 if self.buf[-1:] == SYNC[:1] else 0  # the first sync byte may be the end of the buffer
                self.skipped_bytes += len(self.buf) - keep
                self.buf = self.buf[len(self.buf) - keep:]
                return out
            if i:
                self.skipped_bytes += i
                del self.buf[:i]
            if len(self.buf) < 6:
                return out
            ptype, seq, length = struct.unpack_from("<BBH", self.buf, 2)
            if length > MAX_PAYLOAD:  # not a real header: skip this sync pattern
                self.skipped_bytes += 2
                del self.buf[:2]
                continue
            end = 6 + length + 2
            if len(self.buf) < end:
                return out
            body = bytes(self.buf[2:6 + length])
            (crc,) = struct.unpack_from("<H", self.buf, 6 + length)
            if crc16(body) != crc:
                self.bad_crc += 1
                self.skipped_bytes += 2
                del self.buf[:2]  # a false sync inside data, or damage: look for the next pattern
                continue
            if self._last_seq is not None:
                self.gaps += (seq - self._last_seq - 1) & 0xFF
            self._last_seq = seq
            out.append((ptype, seq, bytes(self.buf[6:6 + length])))
            del self.buf[:end]
