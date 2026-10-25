"""
test_sensors.py — pass/fail checks of the sensor drivers against simulated chips (WP8).

    ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/test_sensors.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fake_sensors as F  # noqa: E402
import sensors as S  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


bus = F.FakeI2C()

# TMP117: the data sheet's Table 7-1 examples
bus.tmp[0x49] = 25.0
t = S.TMP117(bus, 0x49)
check("TMP117 device ID reads 0x0117", t.check() == 0x0117)
for temp, raw in ((128.0, 0x4000), (25.0, 0x0C80), (0.0078125, 0x0001), (-0.0078125, 0xFFFF), (-10.0, 0xFB00), (-256.0, 0x8000)):
    bus.tmp[0x49] = temp
    check("TMP117 raw 0x%04X reads %.7g degC (Table 7-1)" % (raw, temp), abs(t.read_c() - temp) < 1e-9, "%.7f" % t.read_c())
check("TMP117 reports Data_Ready from the configuration register", t.data_ready())
try:
    S.TMP117(bus, 0x4A).check()
    check("a missing TMP117 raises", False)
except OSError:
    check("a missing TMP117 raises OSError", True)

# MMC5983MA
bus.mag[0x30] = {"field": (0.5, -2.0, 0.123), "offset": (0.03, -0.02, 0.0)}
m = S.MMC5983MA(bus)
check("MMC5983MA product ID reads 0x30", m.check() == 0x30)
field, offset = m.read_gauss()
lsb = 1 / 16384
check("SET/RESET measurement recovers the field within 1 count: (0.5, -2.0, 0.123) G", all(abs(a - b) <= lsb for a, b in zip(field, (0.5, -2.0, 0.123))), str(tuple(round(x, 5) for x in field)))
check("SET/RESET measurement recovers the bridge offset within 1 count: (0.03, -0.02, 0) G", all(abs(a - b) <= lsb for a, b in zip(offset, (0.03, -0.02, 0.0))), str(tuple(round(x, 5) for x in offset)))
writes = [v for a, r, v in bus.log if a == 0x30 and r == 0x09]
check("the procedure is SET, measure, RESET, measure (control register 0 writes 0x08, 0x01, 0x10, 0x01)", writes == [0x08, 0x01, 0x10, 0x01], str([hex(w) for w in writes]))
bus.mag[0x30]["slow"] = 3
check("a slow measurement (3 polls) is waited for", len(m.read_gauss()[0]) == 3)
bus.mag[0x30]["dead"] = True
try:
    m.read_gauss()
    check("a measurement that never completes raises SensorError", False)
except S.SensorError:
    check("a measurement that never completes raises SensorError", True)
bus.mag[0x31] = {"field": (0, 0, 0), "offset": (0, 0, 0), "product": 0x55}
try:
    S.MMC5983MA(bus, 0x31).check()
    check("a wrong product ID raises SensorError", False)
except S.SensorError:
    check("a wrong product ID raises SensorError", True)

# LIS2DW12 (register values unverified: the test proves the driver's arithmetic, not the chip)
bus.acc[0x18] = {"g": (0.01, -0.02, 1.0)}
a = S.LIS2DW12(bus)
check("LIS2DW12 WHO_AM_I reads 0x44 (as remembered; unverified)", a.check() == 0x44)
a.configure()
regs = {r: v for ad, r, v in bus.log if ad == 0x18}
check("LIS2DW12 configuration writes CTRL1 0x44, CTRL2 0x0C, CTRL6 0x04", regs == {0x20: 0x44, 0x21: 0x0C, 0x25: 0x04}, str({hex(k): hex(v) for k, v in regs.items()}))
mg = a.read_mg()
check("LIS2DW12 decodes (10, -20, 1000) mg within 1 LSB (0.244 mg)", all(abs(x - y) <= 0.244 for x, y in zip(mg, (10, -20, 1000))), str(tuple(round(x, 2) for x in mg)))
bus.acc[0x18]["who"] = 0x33
try:
    a.check()
    check("a wrong WHO_AM_I raises SensorError", False)
except S.SensorError:
    check("a wrong WHO_AM_I raises SensorError", True)

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
