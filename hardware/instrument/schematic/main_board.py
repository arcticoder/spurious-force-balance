"""
main_board.py — the instrument's main board as a SKiDL description (WP4).

    ~/.venvs/lab-hw/bin/python hardware/instrument/schematic/main_board.py     # writes out/main_board.net and .kicad_sch

Every part is a JLC-stocked SMT part from lib/jlc.kicad_sym (made by easyeda2kicad from the LCSC numbers in parts.py);
`build()` returns the circuit so that schematic_test.py can check pin accounting, footprints and the BOM against it.
Pin numbers are used for multi-pin ICs (IOVDD and GND appear on several pins), names where a name is unique.
The GPIO assignment is read from pins.py (one source of truth for the firmware and this file).
Sources of the circuit values are the data sheets and design guides named in the comments (RP2040 hardware design guide,
ADS131A04 SBAS590E), the ngspice blocks in ../sim/, and ../requirements.md.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ.setdefault("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")

from skidl import KICAD9, Net, Part, set_default_tool, lib_search_paths, reset, SKIDL  # noqa: E402
import pins as pinmap  # noqa: E402

LIB = os.path.join(HERE, "..", "lib", "jlc.kicad_sym")

# value -> LCSC number of the passive (the BOM in ../parts.py lists the same numbers)
RES = {"0": 21189, "27": 17594, "51": 23197, "1k": 21190, "2.2k": 4190, "5.1k": 23186, "10k": 25804, "33k": 4216, "47k": 25819, "100k": 25803}
CAP = {"10p": 1634, "10n": 57112, "15p": 1644, "22p": 1653, "1n": 1588, "100n": 14663, "1u": 15849, "4.7u": 1779, "10u": 15850, "4.7u50": 132170}

_symbols = {}
# EasyEDA has no entry for C21900468 (HTTP 403 from its API, 2026-10-24): the ADC crystal uses the symbol and footprint of C9002, a 3.2 x 2.5 mm
# 4-pad crystal (pads 1 and 3 the crystal, 2 and 4 case ground, the standard 3225 pinout; verify against the 3X016384UP data sheet before layout)
_ALIAS = {21900468: 9002}


def _load_symbols():
    """LCSC number -> (symbol name, footprint) read from the generated library."""
    text = open(LIB).read()
    starts = [m.start() for m in re.finditer(r'\n  \(symbol "[^"]+"\n', text)] + [len(text)]
    for a, b in zip(starts, starts[1:]):
        blk = text[a:b]
        name = re.search(r'\(symbol "([^"]+)"', blk).group(1)
        lcsc = re.search(r'"LCSC Part"\s+"C(\d+)"', blk)
        if lcsc:
            _symbols[int(lcsc.group(1))] = name


def part(lcsc, note=None):
    if not _symbols:
        _load_symbols()
    p = Part(LIB, _symbols[_ALIAS.get(lcsc, lcsc)], tool=KICAD9)
    p.fields["LCSC"] = f"C{lcsc}"
    if note:
        p.fields["Role"] = note
    return p


def flag(n):
    """PWR_FLAG on a net: tells KiCad's ERC the net is driven from outside the schematic (a connector, or a source it cannot see). LCSC 0 = not a BOM part."""
    f = Part("power", "PWR_FLAG", tool=KICAD9)
    f.fields["LCSC"] = "C0"
    n += f[1]
    return f


def R(value, a, b, note=None):
    r = part(RES[value], note)
    a += r[1]
    b += r[2]
    return r


def C(value, a, b=None):
    c = part(CAP[value])
    a += c[1]
    (b if b is not None else GND_NET[0]).__iadd__(c[2])
    return c


GND_NET = []  # [the GND net], set in build() so that C() defaults to ground


def build():
    reset()
    set_default_tool(KICAD9)
    lib_search_paths[KICAD9].append(os.path.join(HERE, "..", "lib"))
    N = {}

    def net(name):
        if name not in N:
            N[name] = Net(name)
        return N[name]

    gnd = net("GND")
    GND_NET[:] = [gnd]
    v5, v5b, v3d, v3a, v3ar = net("V5"), net("V5_BOOST"), net("3V3_D"), net("3V3_A"), net("3V3_AR")

    def gpio_pin(rp, n):
        return rp[f"GPIO{n}_ADC{n - 26}"] if n >= 26 else rp[f"GPIO{n}"]

    # ------------------------------------------------------------------ USB-C input, fuse, ESD
    j1 = part(165948, "USB-C power and data")
    vbus, dp_c, dm_c = net("VBUS"), net("USB_DP_C"), net("USB_DM_C")
    gnd += j1["A1B12"], j1["B1A12"], j1[1], j1[2], j1[3], j1[4]  # shield tabs to ground
    vbus += j1["A4B9"], j1["B4A9"]
    dp_c += j1["A6"], j1["B6"]
    dm_c += j1["A7"], j1["B7"]
    R("5.1k", net("CC1"), gnd, "CC1 pulldown: sink, 5 V 3 A not requested")
    R("5.1k", net("CC2"), gnd, "CC2 pulldown")
    net("CC1").__iadd__(j1["A5"])
    net("CC2").__iadd__(j1["B5"])
    # SBU1/SBU2 stay unconnected (USB 2.0 only)

    esd = part(7519, "USB ESD protection")  # USBLC6-2SC6: 1,6 = I/O1; 3,4 = I/O2; 2 GND; 5 VBUS
    dp_c += esd[1], esd[6]
    dm_c += esd[3], esd[4]
    gnd += esd[2]
    vbus += esd[5]

    fuse = part(20987, "input polyfuse 0.75 A hold")
    vbus += fuse[1]
    vbusf = net("VBUS_F")
    vbusf += fuse[2]
    fb1 = part(1002, "supply entry ferrite")
    vbusf += fb1[1]
    v5 += fb1[2]
    C("10u", v5)
    C("100n", v5)

    # ------------------------------------------------------------------ two 3.3 V rails (LP5907, one part number)
    ldo_d = part(80670, "digital 3.3 V")
    v5 += ldo_d["IN"], ldo_d["EN"]
    gnd += ldo_d["GND"]
    v3d += ldo_d["OUT"]
    C("1u", v5)
    C("1u", v3d)
    C("10u", v3d)

    ldo_a = part(80670, "analog 3.3 V")
    v5 += ldo_a["IN"], ldo_a["EN"]
    gnd += ldo_a["GND"]
    v3ar += ldo_a["OUT"]
    C("1u", v5)
    C("1u", v3ar)
    fb2 = part(1002, "analog rail ferrite")
    v3ar += fb2[1]
    v3a += fb2[2]
    C("10u", v3a)

    # ------------------------------------------------------------------ RP2040 (hardware design guide, section 2)
    rp = part(2040, "RP2040")
    for pin in (1, 10, 22, 33, 42, 49):  # IOVDD, one 100 nF each
        v3d += rp[pin]
        C("100n", v3d)
    v3d += rp[48]  # USB_VDD
    v3d += rp[43]  # ADC_AVDD
    C("100n", v3d)
    v3d += rp[44]  # VREG_IN, 1 uF close by
    C("1u", v3d)
    dvdd = net("DVDD_1V1")
    dvdd += rp[45], rp[23], rp[50]  # VREG_VOUT feeds DVDD
    C("1u", dvdd)
    C("100n", dvdd)
    C("100n", dvdd)
    gnd += rp[57], rp[19]  # exposed pad, TESTEN

    # USB data through 27 ohm series resistors
    R("27", dp_c, net("USB_DP"), "USB series termination")
    R("27", dm_c, net("USB_DM"), "USB series termination")
    net("USB_DP").__iadd__(rp[47])
    net("USB_DM").__iadd__(rp[46])

    # crystal: ABM8-272-T3 (12 MHz, CL 10 pF, ESR 50 ohm max) with 15 pF load caps and a 1 kohm series resistor, as the guide prescribes
    xt = part(20625731, "RP2040 12 MHz crystal")
    xin, xo = net("XIN"), net("XOSC_OUT")
    xin += xt[1], rp[20]
    xo += xt[3]
    gnd += xt[2], xt[4]
    C("15p", xin)
    C("15p", xo)
    R("1k", xo, net("XOUT"), "XOUT damping (guide: 1 kohm)")
    net("XOUT").__iadd__(rp[21])

    # QSPI flash, wired straight to the RP2040
    fl = part(131025, "QSPI flash 16 Mbit")
    for fpin, sig in ((1, "QSPI_SS"), (2, "QSPI_SD1"), (3, "QSPI_SD2"), (5, "QSPI_SD0"), (6, "QSPI_SCLK"), (7, "QSPI_SD3")):
        net(sig).__iadd__(fl[fpin])
    for sig, rpin in (("QSPI_SS", 56), ("QSPI_SD1", 55), ("QSPI_SD2", 54), ("QSPI_SD0", 53), ("QSPI_SCLK", 52), ("QSPI_SD3", 51)):
        net(sig).__iadd__(rp[rpin])
    gnd += fl[4]
    v3d += fl[8]
    C("100n", v3d)

    # BOOTSEL: QSPI_SS through 1 kohm to a switch. The switch's diagonal pins (1 and 4) are always on opposite sides of the contact.
    boot = net("BOOTSEL_N")
    R("1k", net("QSPI_SS"), boot, "QSPI_SS boot strap (guide: 1 kohm)")
    sw_boot = part(318884, "BOOTSEL")
    boot += sw_boot[1]
    gnd += sw_boot[4]
    sw_rst = part(318884, "RESET")
    run = net("RUN")
    run += rp[26], sw_rst[1]
    gnd += sw_rst[4]
    C("100n", run)

    # ------------------------------------------------------------------ RP2040 signals (pins.py)
    for sig, (gp, _fn, _note) in pinmap.PINS.items():
        net(sig).__iadd__(gpio_pin(rp, gp))

    # status LEDs: 1 kohm from the GPIO, about 1.2 mA at 3.3 V
    for sig in ("STATUS_LED1", "STATUS_LED2"):
        led = part(2286, "status")
        k = net(sig + "_A")
        R("1k", net(sig), k, "LED current limit")
        k += led[1]
        gnd += led[2]

    # debug serial header (4-pin JST-SH): 3V3_D, GND, TX, RX
    jd = part(160404, "debug UART")
    v3d += jd[1]
    gnd += jd[2]
    net("DEBUG_TX").__iadd__(jd[3])
    net("DEBUG_RX").__iadd__(jd[4])
    gnd += jd[5], jd[6]  # mounting tabs

    # SWD and the spare GPIOs on 2-pin 2.54 mm headers: (A,B) (C,D) (E,F) (G,H), and SWD/SWCLK
    for a, b in (("SPARE_A", "SPARE_B"), ("SPARE_C", "SPARE_D"), ("SPARE_E", "SPARE_F"), ("SPARE_G", "SPARE_H")):
        h = part(41417359, "spare GPIOs")
        net(a).__iadd__(h[1])
        net(b).__iadd__(h[2])
    hs = part(41417359, "SWD")
    net("SWCLK").__iadd__(hs[1], rp[24])
    net("SWD").__iadd__(hs[2], rp[25])

    # ------------------------------------------------------------------ I2C: pull-ups, on-board sensors, head connectors
    sda, scl = net("I2C_SDA"), net("I2C_SCL")
    R("2.2k", v3d, sda, "I2C pull-up")
    R("2.2k", v3d, scl, "I2C pull-up")

    tmp = part(699536, "ambient temperature")  # ADD0 high = address 0x49 (heads use 0x48 and 0x4A)
    v3d += tmp[5], tmp[4]
    gnd += tmp[2], tmp[7]
    sda += tmp[6]
    scl += tmp[1]
    C("100n", v3d)

    acc = part(189624, "floor motion and level")  # I2C mode: CS high, SA0 low (address 0x18)
    v3d += acc[9], acc[10], acc[2]
    gnd += acc[3], acc[6], acc[7], acc[8]
    sda += acc[4]
    scl += acc[1]
    C("100n", v3d)
    C("100n", v3d)

    for k, desc in ((1, "sensor head 1 (TMP117 at 0x48 + MMC5983MA)"), (2, "sensor head 2 (TMP117 at 0x4A)")):
        jh = part(160404, desc)
        v3d += jh[1]
        gnd += jh[2]
        sda += jh[3]
        scl += jh[4]
        gnd += jh[5], jh[6]

    # ------------------------------------------------------------------ DAC (MCP4728): A LED1 ref, B plate, C device current, D LED2 ref
    dac = part(108207, "quad DAC")
    v3a += dac["VDD"]
    gnd += dac["VSS"], dac["~{LDAC}"]
    sda += dac["SDA"]
    scl += dac["SCL"]
    C("1u", v3a)
    C("100n", v3a)
    dac_a, dac_b, dac_c, dac_d = net("DAC_LED1"), net("DAC_PLATE"), net("DAC_DUT"), net("DAC_LED2")
    dac_a += dac["VOUTA"]
    dac_b += dac["VOUTB"]
    dac_c += dac["VOUTC"]
    dac_d += dac["VOUTD"]

    # ------------------------------------------------------------------ ADS131A04 (SBAS590E)
    adc = part(882747, "24-bit simultaneous ADC")
    v3a += adc[9]  # AVDD
    C("1u", v3a)
    C("100n", v3a)
    gnd += adc[10]  # AVSS = GND with the negative charge pump enabled (inputs may swing to -1.65 V)
    vncp = net("ADC_VNCP")
    vncp += adc[11]
    for _ in range(3):
        C("100n", vncp, gnd)  # three 100 nF in parallel ~ the required 270 nF
    refp = net("ADC_REFP")
    refp += adc[12]
    C("1u", refp, gnd)  # REFP to REFN (= AVSS)
    gnd += adc[13]  # REFN
    refx = net("ADC_REFEXT")
    refx += adc[14]
    C("1u", refx, gnd)  # internal reference: REFEXT to AVSS through 1 uF
    iov = v3d  # IOVDD runs from the digital rail (one Net object: merging two named nets would drop a name)
    iov += adc[15], adc[29], adc[16], adc[30], adc[31]  # IOVDD x2, RESV, M0 (asynchronous interrupt mode), M1 (32-bit words)
    C("1u", iov)
    C("1u", iov)
    C("100n", iov)
    gnd += adc[32]  # M2: Hamming word validation off
    gnd += adc[27]  # digital ground
    cap = net("ADC_CAP")
    cap += adc[28]
    C("1u", cap)
    net("ADC_RESET").__iadd__(adc[17])
    R("10k", iov, net("ADC_RESET"), "RESET pull-up")
    net("ADC_DRDY").__iadd__(adc[19])
    net("ADC_MOSI").__iadd__(adc[20])
    net("ADC_MISO").__iadd__(adc[21])
    R("100k", iov, net("ADC_MISO"), "DOUT pull-up (data sheet)")
    net("ADC_SCK").__iadd__(adc[22])
    net("ADC_CS").__iadd__(adc[23])
    R("10k", iov, net("ADC_CS"), "CS pull-up")
    # DONE (18) and NC (24) float, as the data sheet allows

    # 16.384 MHz crystal across XTAL1/CLKIN and XTAL2 (Figure 36b); load caps to digital ground
    xa = part(21900468, "ADC 16.384 MHz crystal")
    ck1, ck2 = net("ADC_XTAL1"), net("ADC_XTAL2")
    ck1 += xa[1], adc[25]
    ck2 += xa[3], adc[26]
    gnd += xa[2], xa[4]
    C("22p", ck1)
    C("22p", ck2)

    # input filters: 1 kohm in each leg, 1 nF across the pair (anti-alias, and limits fault current to the pins)
    def adc_input(ch, sig, pinp, pinn):
        p, n = net(f"ADC_IN{ch}P"), net(f"ADC_IN{ch}N")
        R("1k", net(sig), p, f"channel {ch} input filter")
        R("1k", gnd, n, f"channel {ch} reference leg")
        C("1n", p, n)
        p += adc[pinp]
        n += adc[pinn]

    adc_input(1, "PD_SIG", 2, 1)  # AIN1P/N: signal photodiode head
    adc_input(2, "REF_SIG", 4, 3)  # AIN2P/N: reference photodiode (LED head)
    adc_input(3, "SHUNT", 6, 5)  # AIN3P/N: device-current shunt
    adc_input(4, "PLATE_MON", 8, 7)  # AIN4P/N: plate voltage divider

    # ------------------------------------------------------------------ LED sinks (x2): TLV9062 half + AO3400A + 51 ohm, reference gated by SN74LVC1G3157
    ops = [part(398355, "LED sinks"), part(398355, "device-current loop + spare")]
    for op in ops:
        v3a += op[8]
        gnd += op[4]
        C("100n", v3a)

    def led_sink(k, dac_net, op_in_p, op_in_m, op_out, mod_sig, mon=False):
        sw = part(10426, f"LED{k} reference gate")  # S low = B1, S high = B2: B2 = DAC level, B1 = 0 V
        net("3V3_A").__iadd__(sw[5])
        net("GND").__iadd__(sw[2], sw[3])
        dac_net += sw[1]
        net(mod_sig).__iadd__(sw[6])
        R("100k", net(mod_sig), net("GND"), "gate pulldown while the GPIO floats")
        ref = net(f"LED{k}_REF")
        ref += sw[4], op_in_p
        C("10p", ref)
        src, gate, kat = net(f"LED{k}_SRC"), net(f"LED{k}_G"), net(f"LED{k}_K")
        fet = part(20917, f"LED{k} current sink")
        gate += op_out, fet["G"]
        kat += fet["D"]
        src += fet["S"], op_in_m
        R("51", src, net("GND"), "LED current sense (1.02 V = 20 mA)")
        return src, kat

    # package 1: half A = LED1 sink, half B = LED2 sink
    src1, k1 = led_sink(1, dac_a, ops[0][3], ops[0][2], ops[0][1], "LED1_MOD")
    src2, k2 = led_sink(2, dac_d, ops[0][5], ops[0][6], ops[0][7], "LED2_MOD")

    # ------------------------------------------------------------------ device-under-test current sink (AOD4184A in an op-amp loop)
    # package 2 half A; DAC level divided by 11 (10 kohm / 1 kohm): 300 mA = 0.30 V across the 1 ohm shunt at 3.3 V DAC
    sw = part(10426, "device-current enable gate")
    v3a += sw[5]
    gnd += sw[2], sw[3]
    net("DUT_EN").__iadd__(sw[6])
    R("100k", net("DUT_EN"), gnd, "pulldown while the GPIO floats: current off at reset")
    dut_div = net("DUT_DIV")
    R("10k", dac_c, dut_div, "set-point divider, top")
    R("1k", dut_div, gnd, "set-point divider, bottom")
    dut_div += sw[1]
    dset = net("DUT_SET")
    dset += sw[4], ops[1][3]
    fb = net("DUT_FB")
    dsrc, dgate, ddrain = net("SHUNT"), net("DUT_G"), net("DUT_D")
    fb += ops[1][2]
    gate_fet = part(99124, "device-current sink")  # AOD4184A: 1 G, 2 D, 3 S
    dgate += ops[1][1], gate_fet[1]
    ddrain += gate_fet[2]
    dsrc += gate_fet[3]
    R("1k", fb, dsrc, "loop integrator resistor")
    C("10n", dgate, fb)  # with the 1 kohm: integrator, crossover far below the gate pole (sim/dut_source.spice)
    R("100k", dgate, gnd, "gate pulldown while the op-amp powers up")
    shunt = part(17928, "device-current shunt, 1 ohm")
    dsrc += shunt[1]
    gnd += shunt[2]
    bal = part(25489, "ballast, 4.7 ohm")
    dret = net("DUT_RET")
    ddrain += bal[1]
    dret += bal[2]
    jdut = part(160402, "device leads: 5 V out, return in")
    v5 += jdut[1]
    dret += jdut[2]
    gnd += jdut[3], jdut[4]
    # spare half of package 2: unity follower with its input grounded (no floating op-amp input)
    spare = net("SPARE_OP")
    spare += ops[1][6], ops[1][7]
    gnd += ops[1][5]

    # ------------------------------------------------------------------ 24 V boost (MT3608) and its filter
    # 400 kohm / 5.1 kohm: 0.6 V * (1 + 200k/5.1k) = 24.1 V. The input bead is the 2 A part (the board's 5 V rail passes 0.4 A).
    fb3 = part(14709, "boost input ferrite")
    v5 += fb3[1]
    v5b += fb3[2]
    C("10u", v5b)
    C("10u", v5b)
    mt = part(84817, "24 V boost")
    bsw = net("BOOST_SW")
    v5b += mt[5]
    gnd += mt[2]
    bsw += mt[1]
    net("BOOST_EN").__iadd__(mt[4])
    R("100k", net("BOOST_EN"), gnd, "boost off while the GPIO floats")
    ind = part(128694, "boost inductor 22 uH")
    v5b += ind[1]
    bsw += ind[2]
    v24r, v24 = net("V24_RAW"), net("V24")
    dd = part(2480, "boost rectifier")
    bsw += dd["A"]
    v24r += dd["K"]
    C("4.7u50", v24r)
    C("4.7u50", v24r)
    bmid, bfb = net("BOOST_FB_MID"), net("BOOST_FB")
    R("100k", v24r, bmid, "boost feedback, top")
    R("100k", bmid, bfb, "boost feedback, top")
    R("5.1k", bfb, gnd, "boost feedback, bottom")
    bfb += mt[3]
    R("51", v24r, v24, "ripple filter into the plate driver")
    C("4.7u50", v24)

    # ------------------------------------------------------------------ plate driver (OPA197, gain 5.7, sim/plate_driver.spice)
    pd = part(221351, "electrostatic plate driver")
    gnd += pd[2]
    v24 += pd[5]
    dac_b += pd[3]
    pop, pfb = net("PLATE_OP"), net("PLATE_FB")
    pop += pd[1]
    pfb += pd[4]
    R("47k", pop, pfb, "gain 5.7")
    R("10k", pfb, gnd, "gain 5.7")
    C("10p", pop, pfb)
    pmid, pout = net("PLATE_SR"), net("PLATE_OUT")
    R("51", pop, pmid, "cable isolation 102 ohm (two 51 ohm)")
    R("51", pmid, pout, "cable isolation")
    jpl = part(160402, "plate drive out")
    pout += jpl[1]
    gnd += jpl[2], jpl[3], jpl[4]
    # monitors: plate voltage to the ADS131A04 channel 4, boost rail to the RP2040's ADC0, both divided by 11
    pm = net("PLATE_MON")
    R("100k", pout, pm, "plate monitor divider")
    R("10k", pm, gnd, "plate monitor divider")
    C("100n", pm)
    rm = net("RAIL_MON")
    R("100k", v24, rm, "24 V monitor divider")
    R("10k", rm, gnd, "24 V monitor divider")
    R("1k", rm, net("MON_24V"), "ADC input series resistor")
    C("100n", net("MON_24V"))
    # 5 V and LED-current monitors on the RP2040's ADC
    m5 = net("MON_5V")
    R("10k", v5, m5, "5 V monitor divider")
    R("10k", m5, gnd, "5 V monitor divider")
    C("100n", m5)
    R("1k", src1, net("MON_LED"), "ADC input series resistor")
    C("100n", net("MON_LED"))

    # ------------------------------------------------------------------ coin-motor drivers (x2): AO3400A low side, 1N-style flyback Schottky
    for k in (1, 2):
        fet = part(20917, f"coin motor {k} driver")
        mg, md = net(f"MOTOR{k}_G"), net(f"MOTOR{k}_D")
        R("1k", net(f"MOTOR{k}_PWM"), mg, "gate resistor")
        R("100k", mg, gnd, "gate pulldown")
        mg += fet["G"]
        gnd += fet["S"]
        md += fet["D"]
        fly = part(2480, f"motor {k} flyback")
        md += fly["A"]
        v5 += fly["K"]
        jm = part(160402, f"coin motor {k}")
        v5 += jm[1]
        md += jm[2]
        gnd += jm[3], jm[4]

    # ------------------------------------------------------------------ optical head connectors (4-pin JST-SH): 3V3_A, GND, signal, signal
    jp = part(160404, "photodiode head")
    v3a += jp[1]
    gnd += jp[2], jp[4], jp[5], jp[6]
    net("PD_SIG").__iadd__(jp[3])
    for k, kat, sig in ((1, k1, "REF_SIG"), (2, k2, "MON_SPARE")):
        jl = part(160404, f"LED head {k}")
        v3a += jl[1]
        gnd += jl[2], jl[5], jl[6]
        kat += jl[3]
        net(sig).__iadd__(jl[4])

    # PWR_FLAGs: nets whose supply arrives through passive parts (fuse, beads, inductor, filter) or from the connector have no power-output pin
    for n in (gnd, v5, v3a, v5b, v24):
        flag(n)
    return N


if __name__ == "__main__":
    print("run generate.py (netlists and schematics of every board)")
