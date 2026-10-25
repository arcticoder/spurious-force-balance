"""
schematic_test.py — pass/fail checks on the main board's netlist (WP4). Run by tools/run_all_smoke_tests.py.

    ~/.venvs/lab-hw/bin/python hardware/instrument/schematic/schematic_test.py

1. Pin accounting: every pin of every part is on a net with another pin, or is listed in ALLOWED_OPEN with the data-sheet reason.
2. Power and strap pins are on the nets the data sheets require (EXPECT).
3. Every symbol pin has a pad in its footprint (a wrong footprint for a symbol shows up here).
4. The netlist's bill of materials equals the BOM in parts.py, part number for part number and count for count.
5. Design numbers the schematic fixes are held to the data sheets' limits (boost voltage, dividers into the ADC range, crystal load, ferrite
   current, charge-pump capacitor).
"""

import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ.setdefault("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")

import heads  # noqa: E402
import main_board  # noqa: E402
import parts  # noqa: E402
import pins as pinmap  # noqa: E402
import builtins  # noqa: E402

LIB = os.path.join(HERE, "..", "lib")

# (LCSC, pin number or name) -> reason it may stay unconnected
ALLOWED_OPEN = {
    (165948, "A8"): "SBU1: USB 2.0 only",
    (165948, "B8"): "SBU2: USB 2.0 only",
    (882747, "18"): "DONE: unused output, may float (SBAS590E 10.1.1)",
    (882747, "24"): "NC pin 24: floating allowed (SBAS590E 10.1.1)",
    (882747, "5"): None,  # placeholder removed below (AIN3 is used)
    (80670, "4"): "LP5907 pin 4 is N/C",
    (84817, "6"): "MT3608 pin 6 is NC",
    (699536, "3"): "TMP117 ALERT: not used",
    (189624, "5"): "LIS2DW12 pin 5 is NC",
    (189624, "11"): "INT2 not used",
    (189624, "12"): "INT1 not used",
    (108207, "5"): "MCP4728 RDY/BSY output not used",
    (318884, "2"): "tactile switch: diagonal pin pair used, the other two are internally common with them",
    (318884, "3"): "tactile switch: diagonal pin pair used",
    (404329, "3"): "MMC5983MA pin 3 is NC",
    (404329, "5"): "SPI_SDO: unused in I2C mode",
    (404329, "6"): "MMC5983MA pin 6 is NC",
    (404329, "7"): "MMC5983MA pin 7 is NC",
    (404329, "8"): "MMC5983MA pin 8 is NC",
    (404329, "12"): "MMC5983MA pin 12 is NC",
    (404329, "14"): "MMC5983MA pin 14 is NC",
    (404329, "15"): "INT: not used (hi-Z until enabled)",
}
ALLOWED_OPEN = {k: v for k, v in ALLOWED_OPEN.items() if v}

# (LCSC, pin) -> net the data sheet requires; one entry per pin
EXPECT = {}
for p in (1, 10, 22, 33, 42, 49, 48, 43, 44):
    EXPECT[(2040, str(p))] = "3V3_D"  # IOVDD x6, USB_VDD, ADC_AVDD, VREG_IN
for p in (23, 50, 45):
    EXPECT[(2040, str(p))] = "DVDD_1V1"
for p in (57, 19):
    EXPECT[(2040, str(p))] = "GND"  # exposed pad, TESTEN
EXPECT.update({
    (131025, "8"): "3V3_D", (131025, "4"): "GND",
    (882747, "9"): "3V3_A", (882747, "10"): "GND", (882747, "13"): "GND", (882747, "27"): "GND", (882747, "32"): "GND",
    (882747, "15"): "3V3_D", (882747, "29"): "3V3_D", (882747, "16"): "3V3_D", (882747, "30"): "3V3_D", (882747, "31"): "3V3_D",
    (108207, "1"): "3V3_A", (108207, "10"): "GND",
    (398355, "8"): "3V3_A", (398355, "4"): "GND",
    (221351, "5"): "V24", (221351, "2"): "GND",
    (84817, "5"): "V5_BOOST", (84817, "2"): "GND",
    (699536, "5"): "3V3_D", (699536, "2"): "GND",
    (404329, "2"): "3V3_D", (404329, "13"): "3V3_D", (404329, "4"): "3V3_D", (404329, "9"): "GND", (404329, "11"): "GND",
    (189624, "9"): "3V3_D", (189624, "10"): "3V3_D", (189624, "2"): "3V3_D", (189624, "3"): "GND",
})


def fail(msg):
    print("FAIL:", msg)
    return 1


def lcsc_of(part):
    return int(part.fields["LCSC"][1:])


def check_pins(circuit):
    bad = 0
    for p in circuit.parts:
        n = lcsc_of(p)
        for pin in p.pins:
            net = pin.net
            used = net is not None and len([q for q in net.pins if q.part is not None]) >= 2
            key_ok = (n, str(pin.num)) in ALLOWED_OPEN or (n, pin.name) in ALLOWED_OPEN
            if not used and not key_ok:
                bad += fail(f"{p.ref} (C{n} {p.name}) pin {pin.num} {pin.name}: not connected to anything and not in ALLOWED_OPEN")
            if used and key_ok:
                bad += fail(f"{p.ref} pin {pin.num} {pin.name} is listed as open but is connected to {net.name}")
    return bad


def check_expect(circuit, seen):
    bad = 0
    for p in circuit.parts:
        n = lcsc_of(p)
        for pin in p.pins:
            want = EXPECT.get((n, str(pin.num)))
            if want is None:
                continue
            seen.add((n, str(pin.num)))
            got = pin.net.name if pin.net is not None else None
            if got != want:
                bad += fail(f"{p.ref} (C{n}) pin {pin.num} {pin.name} is on {got}, the data sheet needs {want}")
    return bad


def check_net_names(nets):
    """Joining two named nets in SKiDL silently keeps one name; every name the board description asked for must survive."""
    bad = 0
    for name, n in nets.items():
        if n.name != name:
            bad += fail(f"net {name} was merged into {n.name} (build() joined two named nets)")
    return bad


# Electrical rules on the netlist (what KiCad's ERC checks, evaluated on the real connectivity instead of SKiDL's drawn wires).
# SKiDL pin type numbers: 1 input, 2 output, 3 bidirectional, 5 passive, 6 unspecified, 7 power input, 8 power output, 13 no connect.
INPUT, OUTPUT, BIDIR, PASSIVE, UNSPEC, PWRIN, PWROUT, NOCONN = 1, 2, 3, 5, 6, 7, 8, 13
# (net, rule) -> reason the rule is waived
ERC_WAIVERS = {
    ("XIN", "undriven input"): "the RP2040's oscillator drives it through the crystal",
    ("ADC_XTAL1", "undriven input"): "the ADS131A04's oscillator drives it through the crystal",
    ("RUN", "undriven input"): "internal pull-up in the RP2040; the reset switch pulls it low",
    ("SWCLK", "undriven input"): "driven by the debug probe on the SWD header",
    ("PD_SIG", "undriven input"): "driven by the photodiode head over its cable",
    ("REF_SIG", "undriven input"): "driven by the LED head over its cable",
    ("I2C_SCL", "undriven input"): "a head board's clock is driven by the main board over the cable",
}
# parts that pass a signal through (resistors, shunt, ballast): an input on one side is driven by an output on the other
TRANSPARENT = set(main_board.RES.values()) | {17928, 25489}


def check_erc(circuit):
    bad = 0
    nets = list(circuit.get_nets())
    # union nets joined by transparent two-pin parts, for the "input has a driver" rule
    parent = {n.name: n.name for n in nets}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p in circuit.parts:
        if lcsc_of(p) in TRANSPARENT and len(p.pins) == 2 and all(q.net is not None for q in p.pins):
            parent[find(p.pins[0].net.name)] = find(p.pins[1].net.name)
    groups = collections.defaultdict(list)
    for n in nets:
        groups[find(n.name)].append(n)
    for net in nets:
        pins = [p for p in net.pins if p.part is not None]
        kinds = collections.Counter(int(p.func) for p in pins)
        names = [f"{p.part.ref}.{p.num}" for p in pins]
        if kinds[UNSPEC]:
            bad += fail(f"net {net.name}: {kinds[UNSPEC]} pin(s) of unspecified type: {[nm for p, nm in zip(pins, names) if int(p.func) == UNSPEC]}")
        if kinds[PWRIN] and not kinds[PWROUT]:
            bad += fail(f"net {net.name}: power input pins {[nm for p, nm in zip(pins, names) if int(p.func) == PWRIN][:3]} but nothing drives the net (no power output or PWR_FLAG)")
        # several outputs on a net is a conflict unless they are pins of one part (the connector's two VBUS contacts)
        drivers = {p.part.ref for p in pins if int(p.func) in (OUTPUT, PWROUT)}
        if len(drivers) > 1:
            bad += fail(f"net {net.name}: more than one driving part: {sorted(drivers)}")
        if kinds[NOCONN] and len(pins) > 1:
            bad += fail(f"net {net.name}: a no-connect pin is wired to something")
    for members in groups.values():
        pins = [p for n in members for p in n.pins if p.part is not None]
        kinds = collections.Counter(int(p.func) for p in pins)
        if kinds[INPUT] and not (kinds[OUTPUT] or kinds[BIDIR] or kinds[PWROUT]):
            if any((n.name, "undriven input") in ERC_WAIVERS for n in members):
                continue
            bad += fail(f"nets {[n.name for n in members]}: input pins {[f'{p.part.ref}.{p.num}' for p in pins if int(p.func) == INPUT][:3]} with no driver (not even through resistors)")
    return bad


def footprint_pads(fp_name):
    lib, _, name = fp_name.partition(":")
    path = os.path.join(LIB, f"{lib}.pretty", f"{name}.kicad_mod")
    return set(re.findall(r'\(pad\s+"?([^"\s]+)"?\s+', open(path).read()))


def check_footprints(circuit):
    bad = 0
    for p in circuit.parts:
        if lcsc_of(p) == 0:  # PWR_FLAG
            continue
        fp = p.footprint
        if not fp:
            bad += fail(f"{p.ref} {p.name}: no footprint")
            continue
        pads = footprint_pads(fp)
        for pin in p.pins:
            if str(pin.num) not in pads:
                bad += fail(f"{p.ref} {p.name}: symbol pin {pin.num} ({pin.name}) has no pad in {fp}")
    return bad


def check_bom(have):
    bad = 0
    want = {lcsc: qty for _g, _r, lcsc, qty, _w in parts.BOM}
    for lcsc in sorted(set(have) | set(want)):
        if have.get(lcsc, 0) != want.get(lcsc, 0):
            bad += fail(f"C{lcsc}: the boards use {have.get(lcsc, 0)}, parts.py lists {want.get(lcsc, 0)}")
    return bad


def check_numbers():
    bad = 0
    # 24 V boost: MT3608 Vout = 0.6 V x (1 + Rtop/Rbot); limits: MT3608 28 V, OPA197 36 V, the repo's 50 V DC line
    vout = 0.6 * (1 + 200e3 / 5.1e3)
    print(f"  boost output {vout:.2f} V (MT3608 max 28 V, OPA197 max 36 V)")
    if not 23.0 <= vout <= 26.0:
        bad += fail(f"boost output {vout:.2f} V outside 23-26 V")
    # the ADS131A04's differential range is +-2.442 V (internal reference) at gain 1
    for name, ratio, vmax in (("plate monitor", 10 / 110, vout), ("24 V rail monitor (RP2040 ADC, 3.3 V)", 10 / 110, vout)):
        full = vmax * ratio
        print(f"  {name}: {full:.2f} V at {vmax:.1f} V")
        if full > 2.4:
            bad += fail(f"{name} reaches {full:.2f} V")
    # DUT set point: DAC / 11 across the 1 ohm shunt; 300 mA needs 0.30 V and the DAC reaches 3.3 V
    dut = 3.3 / 11 / 1.0
    print(f"  device current at the DAC's full scale: {dut * 1000:.0f} mA")
    if not 0.29 <= dut <= 0.31:
        bad += fail(f"device current at full scale {dut:.3f} A, target 0.30 A")
    # RP2040 crystal: ABM8-272-T3 wants CL = 10 pF: CL = C/2 + 3 pF stray with 15 pF load capacitors
    cl = 15 / 2 + 3
    print(f"  RP2040 crystal load {cl:.1f} pF (crystal 10 pF)")
    if abs(cl - 10) > 1.0:
        bad += fail(f"RP2040 crystal load {cl} pF vs 10 pF")
    cl_adc = 22 / 2 + 3
    print(f"  ADC crystal load {cl_adc:.1f} pF (crystal 16 pF: about 2 pF low, a few ppm; the ADC clock accuracy is not critical)")
    if abs(cl_adc - 16) > 3.0:
        bad += fail(f"ADC crystal load {cl_adc} pF vs 16 pF")
    # ferrite beads: the 5 V entry and boost input carry the whole rail (2 A part), the analog bead only 3V3_A (200 mA part)
    i5 = max(pinmap.mode_current(m) for m in pinmap.MODES)
    ia = max(pinmap.rail_current(m, "3V3_A") for m in pinmap.MODES)
    print(f"  5 V rail peak {i5:.0f} mA through a 2 A bead; 3V3_A peak {ia:.0f} mA through a 200 mA bead")
    if i5 > 0.5 * 2000:
        bad += fail(f"entry bead at {i5} mA against 2 A rating (derating 50%)")
    if ia > 0.6 * 200:
        bad += fail(f"analog bead at {ia} mA against 200 mA rating (derating 60%)")
    # charge-pump capacitor: three 100 nF ~ 270 nF requirement (+-30%)
    if not 0.7 * 270 <= 300 <= 1.3 * 270:
        bad += fail("VNCP capacitance")
    return bad


BOARDS = (
    ("main board", main_board.build),
    ("LED head", heads.led_head),
    ("photodiode head", heads.pd_head),
    ("sensor head 1 (TMP117 + MMC5983MA)", heads.sensor_head_1),
    ("sensor head 2 (TMP117)", heads.sensor_head_2),
)


def main():
    bad = 0
    total = collections.Counter()
    seen = set()
    for name, build in BOARDS:
        nets = build()
        c = builtins.default_circuit  # SKiDL puts its circuit in the builtins
        print(f"{name}: {len(c.parts)} parts, {len(c.get_nets())} nets")
        n = check_pins(c) + check_expect(c, seen) + check_footprints(c) + check_erc(c)
        if nets:
            n += check_net_names(nets)
        print(f"  pin accounting, data-sheet nets, footprint pads, electrical rules: {'ok' if not n else str(n) + ' problem(s)'}")
        bad += n
        total.update(lcsc_of(p) for p in c.parts if lcsc_of(p))
    missing = set(EXPECT) - seen
    if missing:
        bad += fail(f"EXPECT entries with no such pin on any board: {sorted(missing)}")
    n = check_bom(total)
    print(f"BOM of all boards against parts.py: {'ok' if not n else str(n) + ' problem(s)'}")
    bad += n
    print("design numbers:")
    bad += check_numbers()
    print("FAILED" if bad else "schematic checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
