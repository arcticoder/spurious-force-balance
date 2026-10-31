#!/usr/bin/env python3
"""validate_easyeda.py — offline validation of the EasyEDA Pro project (no EasyEDA, no MCP needed).

    python3 tools/validate_easyeda.py                      # newest .epro2 in hardware/easyeda/exports/, else the newest *_backup/
    python3 tools/validate_easyeda.py path/to/project.epro2 --json report.json [--strict] [--board main_board]
    python3 tools/validate_easyeda.py --netlists hardware/easyeda/exports/netlists   # live PCB netlists saved by an agent (no export needed)

Input: either an EasyEDA Pro project export (`.epro2`, a zip whose `*.epru` holds one JSON record per line: DEVICE, FOOTPRINT, SCH_PAGE and PCB documents).
The netlist comes from the PCB documents (designator + pad -> net), the part data from the DEVICE documents (LCSC number, library prefix, value).
or a folder of `<board>.json` files, each the text returned by `PCB_Net.getNetlist("JLCEDA")` (through the easyeda-mcp-pro `easyeda_api_call`, PCB focused),
which carries every component's properties and every pad's net; that route needs no user export but has no library prefix, so NAME-4 is skipped.
Standard library only. Exit code 1 when any ERROR is reported (with --strict also for WARN).

Checks (ids in the report):
  NAME-*   designators: placeholders ("U?"), duplicates, characters, prefix versus the library prefix and the footprint family; net names: auto names, characters, case
  CONN-*   pads without a net, single-pad nets, power nets with one pad
  PULL-*   I2C lines need a pull-up to a rail; reset/enable/run/boot/chip-select nets need a driver, a rail/ground tie or a resistor; USB-C CC pins need 5.1 k to ground
  FLOAT-*  input pins (electrical type from hardware/instrument/lib/jlc.kicad_sym) with no net, or on a net with no driver and no bias resistor
  SKIDL-*  main board only: every net's (LCSC, pin) set against hardware/instrument/schematic/out/main_board.net (the SKiDL source of truth)
  BOM-*    assembled parts without an LCSC number, library/BOM number differences
  NATIVE-* ERC and DRC results recorded by exports/native_checks.json (written by an agent with MCP access at each milestone; EasyEDA's own ERC/DRC cannot run offline)
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(ROOT, "hardware", "easyeda", "exports")
SYMLIB = os.path.join(ROOT, "hardware", "instrument", "lib", "jlc.kicad_sym")
SKIDL_DIR = os.path.join(ROOT, "hardware", "instrument", "schematic", "out")


def skidl_path(board):
    """The SKiDL netlist that describes this EasyEDA board (same name), if any."""
    p = os.path.join(SKIDL_DIR, board + ".net")
    return p if os.path.exists(p) else None

RAIL = re.compile(r"^(3V3|5V|V5|V24|V3|VCC|VDD|IOVDD|DVDD|AVDD|VBUS|VREG|\+?\d+V\d*)", re.I)
GROUND = re.compile(r"^(GND|AGND|DGND|PGND|VSS)", re.I)
I2C = re.compile(r"(^|_)(SDA|SCL)$", re.I)
CTRL = re.compile(r"(^|_)(RESET|RESET_N|RST|RUN|EN|ENABLE|BOOTSEL_N|BOOT|CS|CS_N)$", re.I)
AUTO_NET = re.compile(r"^(\$|N\$|Net-|NET\d|unnamed|\$\d)", re.I)
CRYSTAL_ALIAS = {"9002": "21900468", "9900177807": "21900468"}  # the ADC crystal uses the C9002 library part as a stand-in
CRYSTAL_NUMS = set(CRYSTAL_ALIAS) | set(CRYSTAL_ALIAS.values()) | {"9002"}  # a crystal pin drives its oscillator net


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, cid, board, msg):
        self.items.append({"level": level, "id": cid, "board": board, "message": msg})

    def count(self, level):
        return sum(1 for i in self.items if i["level"] == level)


# ----------------------------------------------------------------------------------------------- loading
def newest(pattern_list):
    files = [f for p in pattern_list for f in glob.glob(p)]
    return max(files, key=os.path.getmtime) if files else None


def load_epru(path):
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith(".epru"))
        text = z.read(name).decode("utf8")
    docs = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        head, _, body = line.partition("||")
        head = json.loads(head)
        body = body.rstrip("|")
        obj = json.loads(body) if body else {}
        if head.get("type") == "DOCHEAD":
            docs.append({"head": obj, "items": []})
        else:
            docs[-1]["items"].append((head, obj))
    return docs


def index_docs(docs):
    dev, foot, pcbs, sch = {}, {}, [], []
    for d in docs:
        t, u = d["head"].get("docType"), d["head"].get("uuid")
        if t == "DEVICE":
            meta = next((o for h, o in d["items"] if h["type"] == "META"), {})
            dev[u] = meta
        elif t == "FOOTPRINT":
            meta = next((o for h, o in d["items"] if h["type"] == "META"), {})
            pads = [o["num"] for h, o in d["items"] if h["type"] == "PAD"]
            foot[u] = {"title": meta.get("title", ""), "pads": pads}
        elif t == "PCB":
            pcbs.append(d)
        elif t in ("SCH_PAGE", "SCH"):
            sch.append(d)
    return dev, foot, pcbs, sch


def pcb_netlist(doc, dev, foot):
    """-> title, comps {designator: {...}}, nets {name: [(designator, pad)]}, unconnected [(designator, pad)]"""
    title = next((o.get("title") for h, o in doc["items"] if h["type"] == "META"), doc["head"].get("uuid"))
    attrs = defaultdict(dict)
    for h, o in doc["items"]:
        if h["type"] == "ATTR":
            attrs[o["parentId"]][o["key"]] = o["value"]
    comps, by_id = {}, {}
    for h, o in doc["items"]:
        if h["type"] == "COMPONENT":
            a = attrs.get(h["id"], {})
            des = a.get("Designator", "")
            d = dev.get(a.get("Device"), {})
            da = d.get("attributes", {})
            f = foot.get(a.get("Footprint"), {"title": "", "pads": []})
            rec = {"id": h["id"], "des": des, "device": d.get("title", ""), "lcsc": da.get("Supplier Part", ""), "prefix": da.get("Designator", "").rstrip("?"),
                   "value": da.get("Value", ""), "bom": da.get("Add into BOM", "yes"), "footprint": f["title"], "pads": f["pads"], "mpn": da.get("Manufacturer Part", "")}
            comps.setdefault(des or "?" + h["id"], []).append(rec)
            by_id[h["id"]] = rec
    nets = defaultdict(list)
    padnet = {}
    for h, o in doc["items"]:
        if h["type"] == "PAD_NET":
            _, cid, pad, _e = json.loads(h["id"])
            padnet[(cid, pad)] = o.get("padNet") or ""
    for cid, rec in by_id.items():
        for pad in rec["pads"]:
            n = padnet.get((cid, pad), "")
            if n:
                nets[n].append((rec["des"], pad))
    unconnected = [(rec["des"], pad) for cid, rec in by_id.items() for pad in rec["pads"] if not padnet.get((cid, pad))]
    return title, comps, nets, unconnected


def load_pin_types():
    """LCSC number -> {pin number: electrical type} from the JLC KiCad symbol library."""
    out = {}
    if not os.path.exists(SYMLIB):
        return out
    text = open(SYMLIB, encoding="utf8").read()
    starts = [m.start() for m in re.finditer(r'\n  \(symbol "[^"]+"\n', text)] + [len(text)]
    for a, b in zip(starts, starts[1:]):
        blk = text[a:b]
        m = re.search(r'"LCSC Part"\s+"C(\d+)"', blk)
        if not m:
            continue
        pins = {}
        for pm in re.finditer(r'\(pin (\w+) \w+\s+\(at [^)]*\)\s+\(length [^)]*\)\s+\(name "([^"]*)".*?\(number "([^"]*)"', blk, re.S):
            pins[pm.group(3)] = (pm.group(1), pm.group(2))
        out[m.group(1)] = pins
    return out


# ----------------------------------------------------------------------------------------------- KiCad netlist (SKiDL)
def sexp(text):
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', text)
    pos = 0

    def parse():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            lst = []
            while tokens[pos] != ")":
                lst.append(parse())
            pos += 1
            return lst
        return tok.strip('"')

    return parse()


def load_skidl(path):
    tree = sexp(open(path, encoding="utf8").read())
    comps, nets = {}, {}
    for sec in tree:
        if isinstance(sec, list) and sec and sec[0] == "components":
            for c in sec[1:]:
                ref = next(x[1] for x in c if isinstance(x, list) and x[0] == "ref")
                lcsc = ""
                for x in c:
                    if isinstance(x, list) and x[0] == "fields":
                        for f in x[1:]:
                            if f[1][1] == "LCSC":
                                lcsc = f[2] if len(f) > 2 else ""
                comps[ref] = lcsc.lstrip("C")
        if isinstance(sec, list) and sec and sec[0] == "nets":
            for n in sec[1:]:
                name = next(x[1] for x in n if isinstance(x, list) and x[0] == "name")
                nodes = [(next(y[1] for y in x if isinstance(y, list) and y[0] == "ref"), next(y[1] for y in x if isinstance(y, list) and y[0] == "pin")) for x in n if isinstance(x, list) and x[0] == "node"]
                nets[name] = nodes
    return comps, nets


# ----------------------------------------------------------------------------------------------- checks
def lcsc_num(s):
    s = (s or "").lstrip("C")
    return CRYSTAL_ALIAS.get(s, s)


def parse_value(v):
    m = re.match(r"([\d.]+)\s*([kKMmuµnpΩ]*)", v or "")
    if not m:
        return None
    x, u = float(m.group(1)), m.group(2)
    return x * (1e3 if u.startswith("k") or u.startswith("K") else 1e6 if u.startswith("M") else 1)


def check_names(rep, b, comps, nets):
    seen = defaultdict(int)
    for des, recs in comps.items():
        for r in recs:
            d = r["des"]
            if not d or "?" in d:
                rep.add("ERROR", "NAME-1", b, f"placeholder or empty designator on {r['device'] or r['id']} ({d!r})")
                continue
            seen[d] += 1
            if not re.fullmatch(r"[A-Z]+\d+", d):
                rep.add("WARN", "NAME-3", b, f"designator {d} is not LETTERS+DIGITS")
            pre = re.match(r"[A-Z]+", d).group(0) if re.match(r"[A-Z]+", d) else ""
            lib = r["prefix"]
            if lib and pre != lib and not (lib == "C" and pre == "CN"):
                rep.add("WARN", "NAME-4", b, f"{d} ({r['device']}): library prefix is {lib}, designator prefix {pre}")
            fp = r["footprint"]
            fam = ("R" if re.match(r"R\d{4}$", fp) else "C" if re.match(r"C\d{4}$", fp) else "L" if re.match(r"L\d{4}$", fp) else "")
            if fam and pre != fam:
                rep.add("ERROR", "NAME-5", b, f"{d}: footprint {fp} is a {fam} family part but the designator prefix is {pre}")
    for d, n in seen.items():
        if n > 1:
            rep.add("ERROR", "NAME-2", b, f"duplicate designator {d} ({n} components)")
    for name in nets:
        if AUTO_NET.match(name):
            rep.add("WARN", "NAME-6", b, f"net {name!r} looks auto-generated: name it")
        elif not re.fullmatch(r"[A-Za-z0-9_+\-./]+", name):
            rep.add("WARN", "NAME-7", b, f"net {name!r} has characters outside A-Z a-z 0-9 _ + - . /")
        elif name != name.upper() and not name.startswith("$"):
            rep.add("INFO", "NAME-8", b, f"net {name!r} is not upper case (project convention: UPPER_SNAKE)")


def check_conn(rep, b, comps, nets, unconnected, nc_allow):
    for name, pads in nets.items():
        if len(pads) == 1 and not GROUND.match(name):
            rep.add("WARN", "CONN-2", b, f"net {name} has a single pad ({pads[0][0]}.{pads[0][1]})")
    flat = {r["des"]: r for recs in comps.values() for r in recs}
    for des, pad in unconnected:
        r = flat.get(des, {})
        if (lcsc_num(r.get("lcsc")), pad) in nc_allow:
            continue
        sev = "ERROR" if r.get("prefix") in ("U", "Q") else "WARN"
        rep.add(sev, "CONN-1", b, f"{des} ({r.get('device', '')}) pad {pad} has no net and is not a declared no-connect")


def pad_index(nets):
    idx = {}
    for n, pads in nets.items():
        for des, pad in pads:
            idx[(des, pad)] = n
    return idx


def other_pad_net(des, pad, nets_idx, comps_flat):
    r = comps_flat[des]
    for p in r["pads"]:
        if p != pad:
            return nets_idx.get((des, p))
    return None


def check_pull(rep, b, comps, nets):
    flat = {r["des"]: r for recs in comps.values() for r in recs}
    idx = pad_index(nets)

    def resistors(net):
        out = []
        for des, pad in nets.get(net, []):
            if des.startswith("R") and des in flat:
                out.append((des, parse_value(flat[des]["value"]), other_pad_net(des, pad, idx, flat)))
        return out

    host = any(lcsc_num(r["lcsc"]) == "2040" for r in flat.values())  # the I2C master (RP2040) sits on this board
    for name in nets:
        if I2C.search(name) and not host:
            rep.add("INFO", "PULL-0", b, f"I2C line {name}: no master on this board, the pull-ups belong to the host board")
        elif I2C.search(name):
            ups = [(d, v, o) for d, v, o in resistors(name) if o and RAIL.match(o)]
            if not ups:
                rep.add("ERROR", "PULL-1", b, f"I2C line {name} has no pull-up resistor to a supply rail")
            elif not any(v and 1e3 <= v <= 10e3 for _, v, _ in ups):
                rep.add("WARN", "PULL-2", b, f"I2C line {name}: pull-up value outside 1-10 k ({[(d, flat[d]['value']) for d, _, _ in ups]})")
        elif CTRL.search(name):
            pads = nets[name]
            biased = [1 for d, v, o in resistors(name) if o and (RAIL.match(o) or GROUND.match(o))]
            tied = any(RAIL.match(name) or GROUND.match(name) for _ in [0])
            if len(pads) >= 2 or biased or tied:
                if not biased and all(d.startswith(("C", "R")) for d, _ in pads):
                    rep.add("WARN", "PULL-3", b, f"control net {name} only touches passives with no tie to a rail or ground")
            else:
                rep.add("WARN", "PULL-3", b, f"control net {name} has one pad and no bias")
    for name in ("CC1", "CC2"):
        if name in nets:
            ok = [d for d, v, o in resistors(name) if o and GROUND.match(o) and v and 4.9e3 <= v <= 5.3e3]
            if not ok:
                rep.add("ERROR", "PULL-4", b, f"USB-C {name} needs a 5.1 k resistor to ground")


def check_float(rep, b, comps, nets, pin_types, nc_allow):
    flat = {r["des"]: r for recs in comps.values() for r in recs}
    idx = pad_index(nets)
    drivers = {"output", "bidirectional", "tri_state", "power_out", "open_collector", "open_emitter"}
    for des, r in flat.items():
        types = pin_types.get(lcsc_num(r["lcsc"]))
        if not types or r["prefix"] not in ("U", "Q"):
            continue
        for pad in r["pads"]:
            t = types.get(pad)
            if not t or t[0] != "input":
                continue
            if (lcsc_num(r["lcsc"]), pad) in nc_allow:
                continue
            net = idx.get((des, pad))
            if not net:
                rep.add("ERROR", "FLOAT-1", b, f"input {des}.{pad} ({t[1]}) is not connected")
                continue
            if RAIL.match(net) or GROUND.match(net):
                continue
            members = nets[net]
            has_driver = False
            for d2, p2 in members:
                if (d2, p2) == (des, pad):
                    continue
                r2 = flat.get(d2)
                if not r2:
                    continue
                t2 = pin_types.get(lcsc_num(r2["lcsc"]), {}).get(p2)
                if r2["prefix"] in ("CN", "H", "J", "SW") or lcsc_num(r2["lcsc"]) in CRYSTAL_NUMS or (t2 and (t2[0] in drivers or t2[0] == "passive" and r2["prefix"] not in ("C",))):
                    if r2["prefix"] == "R":
                        o = other_pad_net(d2, p2, idx, flat)
                        if o and (RAIL.match(o) or GROUND.match(o)):
                            has_driver = True
                        elif o:
                            has_driver = True  # resistor into another net: that net's driver is checked there
                    else:
                        has_driver = True
                if r2["prefix"] == "R" and not t2:
                    o = other_pad_net(d2, p2, idx, flat)
                    if o:
                        has_driver = True
            if not has_driver:
                rep.add("WARN", "FLOAT-2", b, f"input {des}.{pad} ({t[1]}) on net {net} has no driver or bias resistor")


def check_bom(rep, b, comps):
    for recs in comps.values():
        for r in recs:
            if r["bom"] == "yes" and not r["lcsc"] and r["prefix"] not in ("H", "TP"):
                rep.add("ERROR", "BOM-1", b, f"{r['des']} ({r['device']}) has no LCSC number: JLC cannot place it")
            if r["lcsc"] and r["lcsc"].lstrip("C") in CRYSTAL_ALIAS:
                rep.add("WARN", "BOM-2", b, f"{r['des']} carries library part {r['lcsc']} as a stand-in for C21900468: set the LCSC and MPN fields before ordering")


def check_skidl(rep, b, comps, nets):
    path = skidl_path(b)
    if not path:
        rep.add("INFO", "SKIDL-0", b, "no SKiDL netlist of this name: cross-check skipped")
        return
    sk_comps, sk_nets = load_skidl(path)
    flat = {r["des"]: r for recs in comps.values() for r in recs}

    def sig(pins):
        return sorted(pins)

    ee = {n: sig([(lcsc_num(flat[d]["lcsc"]), p) for d, p in pads if d in flat]) for n, pads in nets.items()}
    sk = {}
    for n, nodes in sk_nets.items():
        pins = [(lcsc_num(sk_comps.get(r, "")), p) for r, p in nodes if sk_comps.get(r, "") not in ("0", "")]
        if len(pins) >= 2:
            sk[n] = sig(pins)
    for n, pins in sk.items():
        if n not in ee:
            rep.add("ERROR", "SKIDL-1", b, f"net {n} exists in the SKiDL netlist but not in EasyEDA")
        elif ee[n] != pins:
            miss = [p for p in pins if p not in ee[n] or pins.count(p) > ee[n].count(p)]
            extra = [p for p in ee[n] if p not in pins or ee[n].count(p) > pins.count(p)]
            rep.add("ERROR", "SKIDL-2", b, f"net {n} differs: missing (LCSC, pin) {sorted(set(miss))[:6]}, extra {sorted(set(extra))[:6]}")
    for n in ee:
        if n not in sk and len(ee[n]) >= 2:
            rep.add("WARN", "SKIDL-3", b, f"net {n} exists in EasyEDA but not in the SKiDL netlist")
    want = defaultdict(int)
    for r, l in sk_comps.items():
        if l not in ("0", ""):
            want[lcsc_num(l)] += 1
    have = defaultdict(int)
    for r in flat.values():
        have[lcsc_num(r["lcsc"])] += 1
    for l in sorted(set(want) | set(have)):
        if want.get(l, 0) != have.get(l, 0):
            rep.add("ERROR", "SKIDL-4", b, f"part count for C{l}: SKiDL {want.get(l, 0)}, EasyEDA {have.get(l, 0)}")


def sk_nc_allow(board, pin_types):
    """(LCSC, pin) pairs that the SKiDL design of this board leaves unconnected on purpose."""
    allow = set()
    path = skidl_path(board)
    if not path:
        return allow
    comps, nets = load_skidl(path)
    used = {(r, p) for nodes in nets.values() if len(nodes) >= 2 for r, p in nodes}
    for ref, l in comps.items():
        if l in ("0", ""):
            continue
        for pad in pin_types.get(lcsc_num(l), {}):
            if (ref, pad) not in used:
                allow.add((lcsc_num(l), pad))
    return allow


def check_native(rep, boards, path, newest_doc_time):
    if not os.path.exists(path):
        rep.add("WARN", "NATIVE-0", "-", f"{os.path.relpath(path, ROOT)} missing: no record of EasyEDA's own ERC/DRC for this export")
        return
    data = json.load(open(path))
    for b in boards:
        e = data.get("boards", {}).get(b)
        if not e:
            rep.add("WARN", "NATIVE-1", b, "no ERC/DRC record for this board")
            continue
        sev = "WARN" if e.get("wip") else "ERROR"  # a board marked wip is still being placed and routed
        if e.get("erc_errors") not in (None, 0):
            rep.add(sev, "NATIVE-2", b, f"native ERC reports {e['erc_errors']} errors")
        if e.get("drc_violations") not in (None, 0):
            rep.add(sev, "NATIVE-3", b, f"native DRC reports {e['drc_violations']} violations ({e.get('note', '')})")
        if e.get("drc_violations") is None and e.get("kind") == "pcb":
            rep.add("WARN", "NATIVE-4", b, "no DRC result recorded")
    rep.add("INFO", "NATIVE-5", "-", f"native results generated {data.get('generated')}; project saved {data.get('project_saved_at')}")


def live_netlist(path):
    """A `PCB_Net.getNetlist` JSON file -> title, comps, nets, unconnected (same shape as pcb_netlist)."""
    data = json.load(open(path))
    title = os.path.splitext(os.path.basename(path))[0]
    comps, nets, unconnected = {}, defaultdict(list), []
    for cid, c in data.get("components", {}).items():
        p = c.get("props", {})
        des = p.get("Designator", "")
        pre = re.match(r"[A-Za-z]*", des).group(0)
        pins = c.get("pinInfoMap", {})
        rec = {"id": cid, "des": des, "device": p.get("DeviceName", ""), "lcsc": p.get("Supplier Part", ""), "prefix": pre, "value": p.get("Value", ""),
               "bom": p.get("Add into BOM", "yes"), "footprint": p.get("FootprintName", ""), "pads": list(pins), "mpn": p.get("Manufacturer Part", "")}
        comps.setdefault(des or "?" + cid, []).append(rec)
        for pad, info in pins.items():
            if info.get("net"):
                nets[info["net"]].append((des, pad))
            else:
                unconnected.append((des, pad))
    return title, comps, nets, unconnected


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", help=".epro2 export (default: newest in hardware/easyeda/exports, else newest *_backup)")
    ap.add_argument("--netlists", help="folder of <board>.json live netlists (PCB_Net.getNetlist text), used instead of an .epro2")
    ap.add_argument("--json", help="write the machine-readable report here")
    ap.add_argument("--strict", action="store_true", help="exit 1 on WARN as well")
    ap.add_argument("--board", action="append", help="limit to these PCB names")
    ap.add_argument("-v", "--verbose", action="store_true", help="also print INFO lines")
    ap.add_argument("--native", default=os.path.join(EXPORTS, "native_checks.json"))
    a = ap.parse_args()
    pin_types = load_pin_types()
    rep = Report()
    boards = []
    if a.netlists:
        path, newest_doc = a.netlists, 0
        sources = [(live_netlist(f), None) for f in sorted(glob.glob(os.path.join(a.netlists, "*.json")))]
        newest_doc = max((os.path.getmtime(f) * 1000 for f in glob.glob(os.path.join(a.netlists, "*.json"))), default=0)
    else:
        path = a.project or newest([os.path.join(EXPORTS, "*.epro2"), os.path.join(ROOT, "hardware", "easyeda", "*_backup", "*.epro2")])
        if not path:
            print("no .epro2 found and no --netlists folder: see docs/kb/easyeda_validation.md")
            return 2
        docs = load_epru(path)
        dev, foot, pcbs, sch = index_docs(docs)
        sources = [(pcb_netlist(d, dev, foot), d) for d in pcbs]
        newest_doc = max((d["head"].get("updateTime", 0) for d in docs), default=0)
    for (title, comps, nets, unconnected), d in sources:
        if a.board and title not in a.board:
            continue
        boards.append(title)
        if not comps:
            rep.add("INFO", "INFO-0", title, "no components (a mechanical board)")
            if d is not None and not any(h["type"] == "POLY" for h, _ in d["items"]):
                rep.add("WARN", "CONN-3", title, "no board outline (POLY) found")
            continue
        n = sum(len(v) for v in comps.values())
        rep.add("INFO", "INFO-1", title, f"{n} components, {len(nets)} nets, {len(unconnected)} pads without a net")
        check_names(rep, title, comps, nets)
        nc_allow = sk_nc_allow(title, pin_types)
        check_conn(rep, title, comps, nets, unconnected, nc_allow)
        check_pull(rep, title, comps, nets)
        check_float(rep, title, comps, nets, pin_types, nc_allow)
        check_bom(rep, title, comps)
        check_skidl(rep, title, comps, nets)
    check_native(rep, boards, a.native, newest_doc)
    sha = "-" if a.netlists else hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    print(f"project: {os.path.relpath(path, ROOT)}  sha256:{sha}  boards: {', '.join(boards)}")
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for i in sorted(rep.items, key=lambda i: (order[i["level"]], i["id"], i["board"])):
        if i["level"] != "INFO" or a.verbose:
            print(f"{i['level']:5} {i['id']:9} [{i['board']}] {i['message']}")
    print(f"\n{rep.count('ERROR')} error(s), {rep.count('WARN')} warning(s), {rep.count('INFO')} info")
    if a.json:
        json.dump({"project": os.path.basename(path), "sha256": sha, "boards": boards, "items": rep.items}, open(a.json, "w"), indent=1)
    return 1 if rep.count("ERROR") or (a.strict and rep.count("WARN")) else 0


if __name__ == "__main__":
    sys.exit(main())
