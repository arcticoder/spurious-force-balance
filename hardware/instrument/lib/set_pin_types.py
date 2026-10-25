"""
set_pin_types.py — give the generated jlc.kicad_sym symbols electrical pin types from the data sheets (WP4b).

    ~/.venvs/lab-hw/bin/python hardware/instrument/lib/set_pin_types.py

easyeda2kicad writes most IC pins as "unspecified", which makes KiCad's ERC meaningless. The table below lists, per LCSC number, the type of each pin
(by pin number); anything not listed keeps its generated type. Rerun after regenerating the library (idempotent).
Types: i input, o output, b bidirectional, pi power_in, po power_out, p passive, nc no_connect.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIND = {"i": "input", "o": "output", "b": "bidirectional", "pi": "power_in", "po": "power_out", "p": "passive", "nc": "no_connect"}


def spread(spec):
    """'1,10,22:pi 57:pi' -> {pin: kind}"""
    out = {}
    for tok in spec.split():
        pins, kind = tok.split(":")
        for p in pins.split(","):
            out[p] = kind
    return out


TABLE = {
    # RP2040 (data sheet pin list): GPIOs bidirectional; DVDD/IOVDD/USB_VDD/ADC_AVDD/VREG_IN supplies; VREG_VOUT the core supply output
    2040: spread("2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,27,28,29,30,31,32,34,35,36,37,38,39,40,41:b 1,10,22,33,42,49,48,43,44,23,50:pi 45:po 57:pi 19:i 26:i 24:i 25:b 20:i 21:o 46,47:b 51,52,53,54,55,56:b"),
    # W25Q16JV
    131025: spread("1:i 2,3,5,7:b 6:i 4:pi 8:pi"),
    # ADS131A04 (SBAS590E pin functions)
    882747: spread("1,2,3,4,5,6,7,8:i 9,15,29,10,27:pi 11:po 12:o 13:pi 14:p 16:i 17:i 18:o 19:b 20:i 21:o 22:i 23:i 24:nc 25:i 26:o 28:po 30,31,32:i"),
    # LP5907-3.3
    80670: spread("1:pi 2:pi 3:i 4:nc 5:po"),
    # MT3608: SW drives the inductor/diode node
    84817: spread("1:p 2:pi 3:i 4:i 5:pi 6:nc"),
    # MCP4728
    108207: spread("1:pi 10:pi 2:i 3:b 4:i 5:o 6,7,8,9:o"),
    # TLV9062 (dual): 1 OUTA 2 INA- 3 INA+ 4 V- 5 INB+ 6 INB- 7 OUTB 8 V+
    398355: spread("1,7:o 2,3,5,6:i 4:pi 8:pi"),
    # OPA197 (SOT-23-5)
    221351: spread("1:o 2:pi 3,4:i 5:pi"),
    # SN74LVC1G3157: B2, GND, B1, A, VCC, S
    10426: spread("1,3,4:b 2:pi 5:pi 6:i"),
    # TMP117
    699536: spread("1:i 2:pi 3:o 4:i 5:pi 6:b 7:pi"),
    # LIS2DW12 (I2C use)
    189624: spread("1:i 2:i 3:i 4:b 5:nc 6,8:pi 7:i 9,10:pi 11,12:o"),
    # MMC5983MA
    404329: spread("1:i 2:pi 3,6,7,8,12,14:nc 4:i 5:o 9,11:pi 10:p 13:pi 15:o 16:b"),
    # USB-C receptacle: VBUS is the source of the board's supply; the rest are connector contacts
    165948: spread("A4B9,B4A9:po A1B12,B1A12:p A5,B5,A6,A7,B6,B7,A8,B8:p 1,2,3,4:p"),
}


def main():
    path = os.path.join(HERE, "jlc.kicad_sym")
    text = open(path).read()
    starts = [m.start() for m in re.finditer(r'\n  \(symbol "[^"]+"\n', text)] + [text.rindex("\n)")]
    out = text[: starts[0]]
    changed = 0
    for a, b in zip(starts, starts[1:]):
        blk = text[a:b]
        m = re.search(r'"LCSC Part"\s+"C(\d+)"', blk)
        table = TABLE.get(int(m.group(1))) if m else None
        if m and table is None:  # resistors, capacitors, connectors, MOSFETs, diodes, LEDs, switches, crystals: all pins passive
            table = {p: "p" for p in re.findall(r'\(number "([^"]+)"', blk)}
        if table:
            def fix(pm):
                nonlocal changed
                kind = table.get(pm.group(3))
                if kind and KIND[kind] != pm.group(1):
                    changed += 1
                    return pm.group(0).replace(f"(pin {pm.group(1)} ", f"(pin {KIND[kind]} ", 1)
                return pm.group(0)

            blk = re.sub(r'\(pin (\w+) (\w+)\n(?:(?!\(pin ).)*?\(number "([^"]+)"', fix, blk, flags=re.S)
        out += blk
    out += text[starts[-1]:]
    open(path, "w").write(out)
    print(f"{changed} pin types set")


if __name__ == "__main__":
    sys.exit(main())
