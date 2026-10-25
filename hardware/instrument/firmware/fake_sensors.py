"""
fake_sensors.py — simulated TMP117, MMC5983MA and LIS2DW12 on one I2C bus for host tests (WP8).
The models follow the data sheets as read (TMP117, MMC5983MA) or from memory (LIS2DW12); they record register writes so tests can check procedures.
"""


class FakeI2C:
    def __init__(self):
        self.tmp = {}  # addr -> temperature in degC
        self.mag = {}  # addr -> dict(field=(x,y,z) gauss, offset=(x,y,z) gauss, product=0x30, slow=N polls before Meas_M_Done, dead=False)
        self.acc = {}  # addr -> dict(g=(x,y,z), who=0x44)
        self.log = []  # (addr, reg, byte) writes
        self._state = {}

    def readfrom_mem(self, addr, reg, n):
        if addr in self.tmp:
            if reg == 0x0F:
                return bytes((0x01, 0x17))
            if reg == 0x00:
                raw = int(round(self.tmp[addr] / 0.0078125)) & 0xFFFF
                return bytes((raw >> 8, raw & 0xFF))
            if reg == 0x01:
                return bytes((0x22, 0x20))  # Data_Ready set, factory configuration 0x0220
        if addr in self.mag:
            m = self.mag[addr]
            st = self._state.setdefault(addr, {"polarity": 1, "measured": False, "polls": 0, "set": False})
            if reg == 0x2F:
                return bytes((m.get("product", 0x30),))
            if reg == 0x08:
                st["polls"] += 1
                done = st["measured"] and st["polls"] > m.get("slow", 0) and not m.get("dead")
                return bytes((0x01 if done else 0x00,))
            if reg == 0x00:
                out = []
                for h, o in zip(m["field"], m["offset"]):
                    counts = 131072 + int(round((st["polarity"] * h + o) * 16384))
                    out.append(counts)
                x, y, z = out
                return bytes((x >> 10, (x >> 2) & 0xFF, y >> 10, (y >> 2) & 0xFF, z >> 10, (z >> 2) & 0xFF, ((x & 3) << 6) | ((y & 3) << 4) | ((z & 3) << 2)))[:n]
        if addr in self.acc:
            a = self.acc[addr]
            if reg == 0x0F:
                return bytes((a.get("who", 0x44),))
            if reg == 0x28:
                out = bytearray()
                for g in a["g"]:
                    raw = int(round(g * 1000 / 0.244)) << 2
                    raw &= 0xFFFF
                    out += bytes((raw & 0xFF, raw >> 8))
                return bytes(out)
        raise OSError(19)

    def writeto_mem(self, addr, reg, buf):
        self.log.append((addr, reg, buf[0]))
        if addr in self.mag and reg == 0x09:
            st = self._state.setdefault(addr, {"polarity": 1, "measured": False, "polls": 0, "set": False})
            v = buf[0]
            if v & 0x08:  # SET
                st["polarity"] = 1
            if v & 0x10:  # RESET
                st["polarity"] = -1
            if v & 0x01:  # TM_M
                st["measured"] = True
                st["polls"] = 0
