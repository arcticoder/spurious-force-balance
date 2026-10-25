"""
bringup_sensors.py — I2C bring-up of the DAC and the environment sensors with [PASS]/[FAIL] lines (WP8). Same script on the board and on the host.

    on the Pico:   mpremote cp ads131a04.py mcp4728.py sensors.py bringup_sensors.py ../pins.py :   then   mpremote run bringup_sensors.py
    on the host:   ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/bringup_sensors.py   (simulated chips: tests the script itself)

Required on the main board: MCP4728 (0x60), TMP117 (0x49), LIS2DW12 (0x18). Optional heads: TMP117 at 0x48 and MMC5983MA at 0x30 (head 1), TMP117 at 0x4A (head 2);
a missing head is reported, not failed. The plausibility ranges are loose (a room, a bench), they catch a dead or mis-wired part and not drift.
"""

import sys

try:  # on the host the modules sit next to this file (python -I does not add the script directory)
    sys.path.insert(0, __file__.rsplit("/", 1)[0] or ".")
except NameError:  # mpremote run on the board
    pass

try:
    from machine import I2C, Pin
    ON_BOARD = True
except ImportError:
    ON_BOARD = False

import mcp4728
import sensors as S

try:
    import pins as P
except ImportError:
    sys.path.append("..")
    import pins as P

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + ((": " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def make_bus():
    if ON_BOARD:
        gp = {n: v[0] for n, v in P.PINS.items()}
        return I2C(0, sda=Pin(gp["I2C_SDA"]), scl=Pin(gp["I2C_SCL"]), freq=400_000)
    import fake_mcp4728
    import fake_sensors

    class Bus(fake_sensors.FakeI2C):  # one simulated bus: the sensors plus the DAC at 0x60 (writes only)
        def __init__(self):
            super().__init__()
            self.tmp = {0x49: 22.4, 0x48: 22.1}
            self.mag = {0x30: {"field": (0.21, 0.02, 0.38), "offset": (0.01, 0.0, -0.01)}}
            self.acc = {0x18: {"g": (0.003, -0.002, 0.998)}}
            self.dac = fake_mcp4728.FakeI2C()

        def writeto(self, addr, buf):
            return self.dac.writeto(addr, buf)

        def readfrom(self, addr, n):
            return self.dac.readfrom(addr, n)

        def scan(self):
            return sorted(set(self.tmp) | set(self.mag) | set(self.acc) | {0x60})

    return Bus()


def main():
    bus = make_bus()
    found = bus.scan()
    print("       I2C scan: %s" % ", ".join("0x%02X" % a for a in found))
    for addr, name in ((0x60, "MCP4728"), (0x49, "TMP117 on the main board"), (0x18, "LIS2DW12")):
        check("%s answers at 0x%02X" % (name, addr), addr in found)
    for addr, name in ((0x48, "TMP117 on sensor head 1"), (0x30, "MMC5983MA on sensor head 1"), (0x4A, "TMP117 on sensor head 2")):
        print("       %s %s at 0x%02X" % ("found" if addr in found else "not connected:", name, addr))
    if 0x60 in found:
        dac = mcp4728.MCP4728(bus)
        dac.power_up()
        rb = dac.read_back()
        check("the DAC is written to 0 V on all four channels and reads back so", all(code == 0 for _, _, _, code in rb), str([r[3] for r in rb]))
    for addr in (0x49, 0x48, 0x4A):
        if addr in found:
            t = S.TMP117(bus, addr)
            try:
                t.check()
                c = t.read_c()
                check("TMP117 0x%02X: ID ok, %.3f degC is plausible (5 to 45)" % (addr, c), 5 < c < 45)
            except S.SensorError as e:
                check("TMP117 0x%02X ID" % addr, False, str(e))
    if 0x18 in found:
        a = S.LIS2DW12(bus)
        try:
            a.check()
            a.configure()
            import time

            time.sleep(0.1) if ON_BOARD else None
            x, y, z = a.read_mg()
            mag = (x * x + y * y + z * z) ** 0.5
            check("LIS2DW12: |a| is 1 g within 10% (it is at rest)", 900 < mag < 1100, "(%.0f, %.0f, %.0f) mg, |a| %.0f mg" % (x, y, z, mag))
        except S.SensorError as e:
            check("LIS2DW12 WHO_AM_I", False, str(e))
    if 0x30 in found:
        m = S.MMC5983MA(bus)
        try:
            m.check()
            field, off = m.read_gauss()
            mag = sum(f * f for f in field) ** 0.5
            check("MMC5983MA: |B| between 0.05 and 1.5 G (the Earth's field is 0.25-0.65 G; larger means a magnet or steel nearby)", 0.05 < mag < 1.5, "(%.3f, %.3f, %.3f) G, |B| %.3f G, offset (%.3f, %.3f, %.3f) G" % (tuple(field) + (mag,) + tuple(off)))
        except S.SensorError as e:
            check("MMC5983MA", False, str(e))
    return 1 if failures else 0


if __name__ == "__main__":
    rc = main()
    print("\n%s" % ("All checks passed." if not rc else "%d check(s) failed: %s" % (len(failures), failures)))
    sys.exit(rc)
