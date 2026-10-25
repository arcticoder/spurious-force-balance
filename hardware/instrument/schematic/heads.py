"""
heads.py — the small head boards on the main board's JST-SH cables (WP4): the LED head, the photodiode head and the two sensor heads.

    each function builds one board into SKiDL's default circuit (like main_board.build) and returns its nets.

Head connector pinouts (4-pin JST-SH, pin 1 first), matching main_board.py:
    LED head        3V3_A, GND, LED cathode (to the main board's current sink), reference-photodiode TIA output
    photodiode head 3V3_A, GND, TIA output, GND
    sensor head     3V3_D, GND, SDA, SCL
Transimpedance stage (sim/tia.spice): the photodiode cathode on the inverting input, anode on ground, the non-inverting input at
3.3 V x 1 kohm / 34 kohm = 97 mV (a small reverse bias), Rf 10 kohm with Cf 1 nF: 10 kV/A, corner 16 kHz.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")

import main_board as mb  # noqa: E402
from skidl import KICAD9, Net, lib_search_paths, reset, set_default_tool  # noqa: E402


def _start():
    reset()
    set_default_tool(KICAD9)
    lib_search_paths[KICAD9].append(os.path.join(HERE, "..", "lib"))
    gnd = Net("GND")
    mb.GND_NET[:] = [gnd]
    return gnd


def _tia(v3a, gnd, sig, label):
    """Photodiode + TLV9062 half A as a transimpedance amplifier into `sig`; half B parked as a grounded follower."""
    pd = mb.part(145262, f"{label} photodiode")  # VBPW34S: 1 anode, 2 cathode
    op = mb.part(398355, f"{label} transimpedance amplifier")
    v3a += op[8]
    gnd += op[4]
    mb.C("100n", v3a)
    mb.C("1u", v3a)
    vb, inm = Net(f"{label}_VB"), Net(f"{label}_IN")
    mb.R("33k", v3a, vb, "bias divider, top (97 mV)")
    mb.R("1k", vb, gnd, "bias divider, bottom")
    mb.C("100n", vb)
    vb += op[3]
    inm += op[2], pd[2]  # cathode on the inverting input
    gnd += pd[1]
    sig += op[1]
    mb.R("10k", sig, inm, "Rf: 10 kV/A")
    mb.C("1n", sig, inm)  # Cf
    park = Net(f"{label}_PARK")
    park += op[6], op[7]
    gnd += op[5]


def led_head():
    gnd = _start()
    v3a, kat, ref = Net("3V3_A"), Net("LED_K"), Net("REF_SIG")
    j = mb.part(160404, "LED head cable")
    v3a += j[1]
    gnd += j[2], j[5], j[6]
    kat += j[3]
    ref += j[4]
    led = mb.part(131280, "940 nm IR LED")  # 2 anode, 1 cathode
    v3a += led[2]
    kat += led[1]
    _tia(v3a, gnd, ref, "REF")


def pd_head():
    gnd = _start()
    v3a, sig = Net("3V3_A"), Net("PD_SIG")
    j = mb.part(160404, "photodiode head cable")
    v3a += j[1]
    gnd += j[2], j[4], j[5], j[6]
    sig += j[3]
    _tia(v3a, gnd, sig, "PD")


def _sensor_connector(gnd):
    v3d, sda, scl = Net("3V3_D"), Net("I2C_SDA"), Net("I2C_SCL")
    j = mb.part(160404, "sensor head cable")
    v3d += j[1]
    gnd += j[2], j[5], j[6]
    sda += j[3]
    scl += j[4]
    return v3d, sda, scl


def sensor_head_1():
    """TMP117 at 0x48 and the MMC5983MA magnetometer (0x30). Supply 2.8-3.6 V for both."""
    gnd = _start()
    v3d, sda, scl = _sensor_connector(gnd)
    t = mb.part(699536, "head temperature")
    v3d += t[5]
    gnd += t[2], t[7], t[4]  # ADD0 low: 0x48
    sda += t[6]
    scl += t[1]
    mb.C("100n", v3d)
    m = mb.part(404329, "magnetic field at the device mount")
    v3d += m[2], m[13], m[4]  # VDD, VDDIO, SPI_CS tied to VDDIO for I2C
    gnd += m[9], m[11]
    sda += m[16]
    scl += m[1]
    cap = Net("MAG_CAP")
    cap += m[10]  # SET/RESET reservoir: 10 uF low ESR to ground (data sheet)
    mb.C("10u", cap)
    mb.C("1u", v3d)
    mb.C("100n", v3d)


def sensor_head_2():
    """TMP117 only, ADD0 on SDA: 0x4A."""
    gnd = _start()
    v3d, sda, scl = _sensor_connector(gnd)
    t = mb.part(699536, "head temperature")
    v3d += t[5]
    gnd += t[2], t[7]
    sda += t[4], t[6]
    scl += t[1]
    mb.C("100n", v3d)
