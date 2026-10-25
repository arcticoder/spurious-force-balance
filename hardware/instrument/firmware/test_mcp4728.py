"""
test_mcp4728.py — pass/fail checks of the MCP4728 driver and its safety limits against a simulated chip (WP8).

    ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/test_mcp4728.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fake_mcp4728 as F  # noqa: E402
import mcp4728 as M  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


def make():
    bus = F.FakeI2C()
    return bus, M.MCP4728(bus)


bus, dac = make()
check("the factory power-up state is 0 V on every channel (internal reference, gain 1, data 0)", all(bus.volts(c) == 0 for c in range(4)) and bus.vref == [1, 1, 1, 1])

# scaling
dac.set_led_current(M.CH_LED1, 0.020)
check("LED1 at 20 mA writes 1.02 V across 51 ohm: code 2040 on the 2.048 V reference", bus.code[0] == 2040 and bus.vref[0] == 1 and abs(bus.volts(0) - 1.02) < 1e-9, "code %d, %.4f V" % (bus.code[0], bus.volts(0)))
dac.set_plate_voltage(10.0)
check("plate 10 V writes 1.7544 V on the VDD reference (gain 5.7)", bus.vref[1] == 0 and abs(bus.volts(1) * 5.7 - 10.0) < 5.7 * 3.3 / 4096, "%.3f V out" % (bus.volts(1) * 5.7))
dac.set_dut_current(0.300)
check("device current 300 mA writes 3.3 V (set point 0.30 V after the divider by 11 across 1 ohm)", abs(bus.volts(2) / 11 - 0.300) < 3.3 / 4096 / 11 * 1.01 and bus.code[2] == 4095, "code %d, %.4f V" % (bus.code[2], bus.volts(2)))
dac.set_plate_voltage(M.PLATE_MAX_V)
check("plate at its 18.8 V limit stays within the DAC's range (code <= 4095)", bus.code[1] <= 4095 and abs(bus.volts(1) * 5.7 - 18.8) < 0.05, "code %d" % bus.code[1])

# monotonic and accurate over the range
errs = []
prev = -1
for i in range(0, 189):
    v = i * 0.1
    dac.set_plate_voltage(v)
    errs.append(abs(bus.volts(1) * 5.7 - v))
    if bus.code[1] < prev:
        errs.append(9)
    prev = bus.code[1]
check("plate voltage: monotonic codes and every setpoint within half a step (%.1f mV) over 0-18.8 V" % (3.3 / 4096 * 5.7 / 2 * 1000), max(errs) <= 3.3 / 4096 * 5.7 / 2 * 1.001, "worst %.2f mV" % (max(errs) * 1000))

# limits write nothing
before = len(bus.writes)
for label, fn in (("LED current above 20 mA", lambda: dac.set_led_current(M.CH_LED1, 0.0201)), ("negative LED current", lambda: dac.set_led_current(M.CH_LED2, -0.001)),
                  ("plate above 18.8 V", lambda: dac.set_plate_voltage(18.81)), ("negative plate voltage", lambda: dac.set_plate_voltage(-0.1)),
                  ("device current above 300 mA", lambda: dac.set_dut_current(0.3001)), ("an LED setter on the plate channel", lambda: dac.set_led_current(M.CH_PLATE, 0.01))):
    try:
        fn()
        check("%s is refused" % label, False)
    except ValueError:
        check("%s is refused" % label, True)
check("refused requests wrote nothing to the bus", len(bus.writes) == before)

# EEPROM discipline
dac.fast_write([1, 2, 0x345, 4095])
fast = bus.writes[-1]
dac.all_off()
check("no command that programs the EEPROM was ever sent (Single and Sequential Write)", bus.eeprom_writes == 0 and all(w[0] >> 3 not in (0b01010, 0b01011) for w in bus.writes))
check("Fast Write sends 8 bytes (PD bits 00, 12-bit codes, channel A first) and the chip took the codes", fast == bytes((0x00, 0x01, 0x00, 0x02, 0x03, 0x45, 0x0F, 0xFF)), fast.hex())
check("all_off() leaves every channel at code 0", bus.code == [0, 0, 0, 0], str(bus.code))

# read back
dac.write_channel(M.CH_PLATE, 1234)
rb = dac.read_back()
check("read_back() returns the written reference, power-down state and code", rb[1] == (False, 0, False, 1234) and rb[0][0] is True, str(rb[1]))

# bus errors surface
bad = M.MCP4728(F.FakeI2C(addr=0x61))
try:
    bad.write_channel(0, 1)
    check("a missing device raises OSError", False)
except OSError:
    check("a missing device raises OSError", True)

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
