"""
mainboard.py — WP5: the instrument main board in KiCad format, from the SKiDL netlist, without KiCad's Python API (pcbnew segfaults headless here).

    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py place [W H]   # footprints, nets, force-directed placement -> out/main_board.kicad_pcb
    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py route         # Specctra DSN -> Freerouting -> SES -> tracks/vias in the board
    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py geometry [-v]   # 45-degree grid / acute-joint check
    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py dfm           # DRC + geometry gate, run last before the fab outputs
    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py drc           # kicad-cli pcb drc (min clearance 0.15 mm, JLC 4-layer capability)

Netlist: ../schematic/out/main_board.net. Footprints: ../lib/jlc.pretty. Four copper layers (F, In1, In2, B). Deterministic.
"""
import json
import math
import os
import re
import subprocess
import sys
import uuid
from collections import defaultdict

import numpy as np
from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Net, Position
from kiutils.items.brditems import Segment, Via
from kiutils.items.gritems import GrLine

HERE = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(HERE, "..", "schematic", "out", "main_board.net")
LIB = os.path.join(HERE, "..", "lib", "jlc.pretty")
OUT = os.path.join(HERE, "out")
PCB = os.path.join(OUT, "main_board.kicad_pcb")
DSN, SES = os.path.join(OUT, "main_board.dsn"), os.path.join(OUT, "main_board.ses")
FR = os.path.expanduser("~/tools/freerouting/freerouting-2.5.0-linux-x64/bin/freerouting")
POWER = re.compile(r"^(GND|V5|3V3_D|3V3_A|3V3_AR|VBUS|VBUS_F|V24|V24_RAW|V5_BOOST|DVDD_1V1)$")
LAYERS = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
PLANE2_NET = "3V3_D"  # the In2.Cu power plane (the board's main digital rail); other rails are routed as wide tracks on F/B
CLEAR, TRACK, VIA_D, VIA_H = 0.15, 0.2, 0.6, 0.3
# decisions 2026-11-11 against JLC's 4-layer table (kb/pcb_toolchain_notes.md): the DRC track floor is 0.10 mm (JLC's limit is 0.09; the router's class width stays
# 0.2 mm, so anything under 0.15 is a neck-down at a fine-pitch pad and is reported by `geometry`-style review, not blocked); annular ring stays at JLC's
# absolute minimum 0.15 mm (0.6/0.3 vias); pad-hole to pad-hole spacing 0.45 mm is a custom rule (write_rules) because KiCad's global hole_to_hole would also
# apply it to vias, where JLC allows 0.2 mm
MIN_TRACK = 0.10
PAD_HOLE_GAP = 0.45


def uid():
    return str(uuid.uuid4())


def parse_netlist(path):
    t = open(path).read()
    comps = {}
    for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)\s+\(value "([^"]*)"\)\s+\(description "[^"]*"\)\s+\(footprint "([^"]*)"\)', t):
        ref, val, fp = m.groups()
        if fp and not ref.startswith("#"):
            comps[ref] = (val, fp.split(":")[1])
    nets = {}
    for m in re.finditer(r'\(net\s+\(code (\d+)\)\s+\(name "([^"]+)"\)(.*?)(?=\(net\s+\(code|\Z)', t[t.index("(nets"):], re.S):
        nodes = [(n.group(1), n.group(2)) for n in re.finditer(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', m.group(3)) if n.group(1) in comps]
        if nodes:
            nets[m.group(2)] = nodes
    return comps, nets


def new_board():
    b = Board.create_new()
    from kiutils.board import LayerToken
    have = {l.name for l in b.layers}
    b.layers = [l for l in b.layers if l.name not in ("F.Cu", "B.Cu")]
    b.layers = [LayerToken(ordinal=0, name="F.Cu", type="signal"), LayerToken(ordinal=4, name="In1.Cu", type="signal"),
                LayerToken(ordinal=6, name="In2.Cu", type="signal"), LayerToken(ordinal=2, name="B.Cu", type="signal")] + b.layers
    return b



# ---------- floorplan (kb/main_board_assessment.md, SPEC.md): every part belongs to a block with a rectangular region (fractions of the board) ----------
BLOCK_ANCHORS = {
    "power": ["USBC1", "D1", "F1", "L1", "L2", "U1", "U2"],
    "mcu": ["U3", "U4", "U5", "SW1", "SW2", "LED1", "LED2"],
    "adc": ["U9", "X1", "U8"],
    "led": ["U10", "U12", "U13", "Q1", "Q2"],
    "dut": ["U11", "U14", "Q3"],
    "plate": ["U16"],
    "boost": ["U15", "L3", "L4", "D2"],
    "motor": ["Q4", "Q5", "D3", "D4"],
    "sensor": ["U6", "U7"],
}
BLOCK_REGIONS = {  # x0, y0, x1, y1 as fractions of (W, H); y grows downward, USB-C at the bottom centre, JST-SH heads along the top, headers on the right
    "power": (0.30, 0.74, 0.70, 0.99),
    "mcu": (0.13, 0.42, 0.42, 0.72),
    "adc": (0.30, 0.12, 0.70, 0.40),
    "led": (0.09, 0.12, 0.29, 0.40),
    "dut": (0.72, 0.12, 0.93, 0.42),
    "plate": (0.62, 0.44, 0.93, 0.62),
    "boost": (0.62, 0.64, 0.93, 0.98),
    "motor": (0.07, 0.74, 0.29, 0.98),
    "sensor": (0.44, 0.42, 0.61, 0.62),
}


def assign_blocks(comps, nets):
    """ref -> block. Anchors are listed above; every other part (resistors, capacitors, LEDs, ...) goes with the anchor it shares the most signal nets with
    (power nets count a third as much, GND nothing), so a decoupling capacitor follows its IC and a pull-up its driver."""
    where = {r: b for b, rs in BLOCK_ANCHORS.items() for r in rs if r in comps}
    nets_of = defaultdict(dict)
    for n, nodes in nets.items():
        w = 0.0 if n == "GND" else (0.33 if POWER.match(n) else 1.0)
        if len(nodes) > 12:
            w *= 12 / len(nodes)
        for r, _ in nodes:
            nets_of[r][n] = w
    for r in sorted(comps):
        if r in where or comps[r][1].startswith(("CONN-", "USB-C", "HDR-")):
            continue
        score = defaultdict(float)
        for a, blk in where.items():
            if a in BLOCK_ANCHORS.get(blk, []):
                score[blk] += sum(min(w, nets_of[a].get(n, 0)) for n, w in nets_of[r].items())
        where[r] = max(score, key=score.get) if score and max(score.values()) > 0 else "mcu"
    return where


def place(W, H):
    comps, nets = parse_netlist(NET)
    b = new_board()
    code = {}
    b.nets = [Net(number=0, name="")]
    for i, name in enumerate(sorted(nets), 1):
        code[name] = i
        b.nets.append(Net(number=i, name=name))
    pad_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    fps, size, refs = {}, {}, sorted(comps)
    for ref in refs:
        val, fpname = comps[ref]
        fp = Footprint.from_file(os.path.join(LIB, fpname + ".kicad_mod"))
        fp.libId = "jlc:" + fpname
        fp.tstamp = uid()
        # models and description stay as in the library (kicad-cli reports lib_footprint_mismatch when they differ); the library files have single-line
        # descriptions (see sanitise in kb/pcb_toolchain_notes.md)
        for it in fp.graphicItems:
            if hasattr(it, "text") and getattr(it, "type", "") == "reference":
                it.text = ref
            if hasattr(it, "text") and getattr(it, "type", "") == "value":
                it.text = val
        for pad in fp.pads:
            pad.tstamp = uid() if hasattr(pad, "tstamp") else None
            n = pad_net.get((ref, str(pad.number)))
            if n:
                pad.net = Net(number=code[n], name=n)
        xs, ys = [], []
        for pad in fp.pads:
            xs += [pad.position.X - pad.size.X / 2, pad.position.X + pad.size.X / 2]
            ys += [pad.position.Y - pad.size.Y / 2, pad.position.Y + pad.size.Y / 2]
        size[ref] = (max(xs) - min(xs), max(ys) - min(ys))
        fps[ref] = fp
    conn = {r: comps[r][1] for r in refs if comps[r][1].startswith(("CONN-", "USB-C", "HDR-"))}
    pos, rot, fixed = {}, defaultdict(int), set()
    groups = defaultdict(list)
    for r, f in conn.items():
        groups[f.split("_")[0] if not f.startswith("CONN-") else f.split("_")[1]].append(r)
    for r in groups.get("TYPE-C-31-M-12", []) + [r for r in conn if conn[r].startswith("USB-C")]:
        pos[r] = (W / 2, H - 5.0); fixed.add(r)
    fours = [r for r in conn if "4P" in conn[r]]
    twos = [r for r in conn if "2P" in conn[r] and conn[r].startswith("CONN-")]
    hdrs = [r for r in conn if conn[r].startswith("HDR-")]
    for i, r in enumerate(fours):
        pos[r] = (10 + i * (W - 20) / max(1, len(fours) - 1), 4.5); rot[r] = 0; fixed.add(r)
    for i, r in enumerate(twos):
        pos[r] = (4.5, 22 + i * 11); rot[r] = 90; fixed.add(r)
    for i, r in enumerate(hdrs):
        pos[r] = (W - 5.0, 18 + i * 11); rot[r] = 90; fixed.add(r)
    rng = np.random.default_rng(1)
    block = assign_blocks(comps, nets)
    reg = {r: BLOCK_REGIONS[block[r]] for r in refs if r in block}
    for r in refs:
        if r not in pos:
            x0_, y0_, x1_, y1_ = reg[r]
            pos[r] = ((x0_ + x1_) / 2 * W + rng.normal(0, 3), (y0_ + y1_) / 2 * H + rng.normal(0, 3))
    area = defaultdict(float)
    for r in reg:
        area[block[r]] += (size[r][0] + 0.8) * (size[r][1] + 0.8)
    for blk, a_ in sorted(area.items()):
        x0_, y0_, x1_, y1_ = BLOCK_REGIONS[blk]
        print(f"  block {blk:7s} {sum(1 for r in reg if block[r]==blk):3d} parts, {a_:6.0f} mm2 of parts in {(x1_-x0_)*(y1_-y0_)*W*H:6.0f} mm2 ({a_/((x1_-x0_)*(y1_-y0_)*W*H)*100:.0f} %)")
    edges = defaultdict(float)
    for name, nodes in nets.items():
        rs = sorted({r for r, _ in nodes})
        if len(rs) < 2:
            continue
        w = 0.0 if name == "GND" else (0.1 if POWER.match(name) else 1.0)
        if len(rs) > 12:
            w *= 12 / len(rs)
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                edges[(rs[i], rs[j])] += w / (len(rs) - 1)
    # decoupling: every capacitor goes toward the IC that shares its non-GND power net
    ics = {r for r in refs if comps[r][1].split("_")[0].split("-")[0] in ("LQFN", "TQFP", "SOIC", "MSOP", "WSON", "LGA", "SOT")}
    for name, nodes in nets.items():
        if POWER.match(name) and name != "GND":
            icp = sorted({r for r, _ in nodes if r in ics})
            cap = sorted({r for r, _ in nodes if r.startswith("C")})
            for c in cap:
                for ic in icp:
                    edges[tuple(sorted((c, ic)))] += 0.6 / len(icp)
    idx = {r: i for i, r in enumerate(refs)}
    P = np.array([pos[r] for r in refs], float)
    S = np.array([size[r] for r in refs], float)
    rotated = np.array([rot[r] in (90, 270) for r in refs])
    S = np.where(rotated[:, None], S[:, ::-1], S) + 0.8
    fx = np.array([r in fixed for r in refs])
    E = np.array([(idx[a], idx[b], w) for (a, b), w in edges.items()])
    ea, eb, ew = E[:, 0].astype(int), E[:, 1].astype(int), E[:, 2]
    def repulse():
        dx = P[:, None, 0] - P[None, :, 0]
        dy = P[:, None, 1] - P[None, :, 1]
        ox = (S[:, None, 0] + S[None, :, 0]) / 2 - np.abs(dx)
        oy = (S[:, None, 1] + S[None, :, 1]) / 2 - np.abs(dy)
        m = (ox > 0) & (oy > 0)
        np.fill_diagonal(m, False)
        px = m & (ox < oy)
        py = m & ~(ox < oy)
        G = np.zeros_like(P)
        G[:, 0] += np.where(px, np.where(dx >= 0, 1, -1) * ox * 0.5, 0).sum(1)
        G[:, 1] += np.where(py, np.where(dy >= 0, 1, -1) * oy * 0.5, 0).sum(1)
        return G, m

    LO = np.array([[reg[r][0] * W, reg[r][1] * H] if r in reg else [0, 0] for r in refs])
    HI = np.array([[reg[r][2] * W, reg[r][3] * H] if r in reg else [W, H] for r in refs])

    def clip():
        P[:, 0] = np.clip(P[:, 0], np.maximum(S[:, 0] / 2 + 1.5, LO[:, 0] + S[:, 0] / 2), np.minimum(W - S[:, 0] / 2 - 1.5, HI[:, 0] - S[:, 0] / 2))
        P[:, 1] = np.clip(P[:, 1], np.maximum(S[:, 1] / 2 + 1.5, LO[:, 1] + S[:, 1] / 2), np.minimum(H - S[:, 1] / 2 - 1.5, HI[:, 1] - S[:, 1] / 2))

    N = 1500
    for it in range(N):
        F = np.zeros_like(P)
        d = P[eb] - P[ea]
        np.add.at(F, ea, ew[:, None] * d * 0.012)
        np.add.at(F, eb, -ew[:, None] * d * 0.012)
        G, m = repulse()
        step = (F + 1.5 * G)
        lim = 1.0 * (1 - it / N) + 0.05
        nrm = np.linalg.norm(step, axis=1, keepdims=True) + 1e-9
        step = step * np.minimum(1.0, lim / nrm)
        P += np.where(fx[:, None], 0, step)
        clip()
        if it % 500 == 0:
            print(' iter', it, 'overlapping pairs', int(m.sum() // 2))
    for it in range(20000):  # legalise: repulsion only until no two bodies overlap
        G, m = repulse()
        if it % 1000 == 0:
            print(' legalise', it, int(m.sum() // 2), 'area ratio', round(float((S[:, 0] * S[:, 1]).sum() / (W * H)), 2))
        if m.sum() == 0:
            break
        G += rng.normal(0, 0.05, G.shape)
        nrm = np.linalg.norm(G, axis=1, keepdims=True) + 1e-9
        P += np.where(fx[:, None], 0, G * np.minimum(1.0, 0.5 / nrm))
        clip()
    overlaps = int(m.sum() // 2)
    bad = [(refs[i], refs[j]) for i, j in zip(*np.nonzero(np.triu(m)))]
    print(' overlapping examples:', bad[:12], 'fixed:', sorted(fixed))
    for r, (x, y) in zip(refs, P):
        fp = fps[r]
        a = rot[r]
        fp.position = Position(X=round(x, 3), Y=round(y, 3), angle=a)
        for pad in fp.pads:
            pad.position = Position(X=pad.position.X, Y=pad.position.Y, angle=((pad.position.angle or 0) + a) % 360 if a else pad.position.angle)
        b.footprints.append(fp)
    for (x0, y0, x1, y1) in ((0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)):
        b.graphicItems.append(GrLine(start=Position(X=x0, Y=y0), end=Position(X=x1, Y=y1), layer="Edge.Cuts", width=0.1, tstamp=uid()))
    os.makedirs(OUT, exist_ok=True)
    add_mounting_holes(b)                       # before routing, so the router treats the holes as obstacles
    b.to_file(PCB)
    json.dump({"net_settings": {"classes": [{"name": "Default", "clearance": CLEAR, "track_width": TRACK, "via_diameter": VIA_D, "via_drill": VIA_H,
                                              "diff_pair_gap": 0.2, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                                              "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}],
                                "meta": {"version": 3}},
               "board": {"design_settings": {"rules": {"min_clearance": CLEAR, "min_track_width": MIN_TRACK, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3,
                                                         "min_copper_edge_clearance": 0.2, "min_hole_to_hole": 0.25, "min_via_annular_width": 0.15}}}},
              open(os.path.join(OUT, "main_board.kicad_pro"), "w"), indent=1)
    write_rules()
    # project-local footprint library table so kicad-cli DRC can resolve the "jlc" library (otherwise every footprint is a lib_footprint_issues warning)
    open(os.path.join(OUT, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "jlc")(type "KiCad")(uri "${KIPRJMOD}/../../lib/jlc.pretty")(options "")(descr ""))\n)\n')
    print(f"{len(refs)} parts, {len(nets)} nets, board {W} x {H} mm, overlapping pairs after the force pass: {overlaps}; wrote {PCB}")


# ---------- routing ----------
def tokens(s):
    return re.findall(r'"[^"]*"|\(|\)|[^\s()]+', s)


def sexp(tok):
    stack, cur = [], []
    for t in tok:
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t.strip('"'))
    return cur


def write_dsn():
    b = Board.from_file(PCB)
    u = 1000.0  # um per mm; DSN y points up, KiCad y down
    ids = {}
    out = ['(pcb "main_board"', '  (parser (string_quote ") (space_in_quoted_tokens on) (host_cad "KiCad\'s Pcbnew") (host_version "9"))',
           "  (resolution um 1)", "  (unit um)", "  (structure"]
    for i, l in enumerate(LAYERS):
        out.append(f"    (layer {l} (type signal) (property (index {i})))")
    edge = [g for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    xs = [g.start.X for g in edge] + [g.end.X for g in edge]
    ys = [g.start.Y for g in edge] + [g.end.Y for g in edge]
    x0, x1, y0, y1 = min(xs) * u, max(xs) * u, -max(ys) * u, -min(ys) * u
    out.append(f"    (boundary (path pcb 0 {x0:.0f} {y0:.0f} {x1:.0f} {y0:.0f} {x1:.0f} {y1:.0f} {x0:.0f} {y1:.0f} {x0:.0f} {y0:.0f}))")
    out.append('    (via "Via[0-3]_600:300_um")')
    out.append(f"    (rule (width {TRACK*u:.0f}) (clearance {CLEAR*u:.0f}))")
    out.append("  )")
    # placement + library
    place_lines, images, padstacks = [], {}, {}
    nets = defaultdict(list)
    for fp in b.footprints:
        ref = [it.text for it in fp.graphicItems if getattr(it, "type", "") == "reference"][0]
        name = fp.libId.split(":")[1]
        rot = fp.position.angle or 0
        if name not in images:
            pins = []
            for pad in fp.pads:
                a = ((pad.position.angle or 0) - rot) % 360
                w, h = (pad.size.X, pad.size.Y) if a in (0, 180) else (pad.size.Y, pad.size.X)
                tht = pad.type in ("thru_hole", "np_thru_hole")
                key = (round(w, 3), round(h, 3), tht, pad.shape)
                if key not in padstacks:
                    padstacks[key] = f"P{len(padstacks)}_{w:.2f}x{h:.2f}{'T' if tht else 'S'}"
                lx, ly = pad.position.X, pad.position.Y  # at rotation 0 (kiutils keeps the footprint-local position)
                # pad positions in the file are local to the footprint; with footprint rotation `rot` they rotate with it
                pins.append(f"(pin {padstacks[key]} \"{pad.number}\" {lx*u:.0f} {-ly*u:.0f})")
            images[name] = f'    (image "{name}"\n      ' + "\n      ".join(pins) + "\n    )"
        side = "front"
        place_lines.append(f'      (place "{ref}" {fp.position.X*u:.0f} {-fp.position.Y*u:.0f} {side} {int(rot)})')
        for pad in fp.pads:
            if pad.net and pad.net.name:
                nets[pad.net.name].append(f'"{ref}"-"{pad.number}"')
    out.append(f'  (placement\n    (component "all"\n' if False else "  (placement")
    # one component entry per image name, as Specctra requires
    by_image = defaultdict(list)
    for fp in b.footprints:
        by_image[fp.libId.split(":")[1]].append(fp)
    for name, lst in by_image.items():
        out.append(f'    (component "{name}"')
        for fp in lst:
            ref = [it.text for it in fp.graphicItems if getattr(it, "type", "") == "reference"][0]
            out.append(f'      (place "{ref}" {fp.position.X*u:.0f} {-fp.position.Y*u:.0f} front {int(fp.position.angle or 0)})')
        out.append("    )")
    out.append("  )")
    out.append("  (library")
    out += list(images.values())
    for (w, h, tht, shape), nm in padstacks.items():
        lay = LAYERS if tht else ["F.Cu"]
        shapes = "".join(f"\n      (shape (rect {l} {-w*u/2:.0f} {-h*u/2:.0f} {w*u/2:.0f} {h*u/2:.0f}))" for l in lay)
        out.append(f"    (padstack {nm}{shapes}\n      (attach off)\n    )")
    r = VIA_D * u / 2
    out.append("    (padstack \"Via[0-3]_600:300_um\"" + "".join(f"\n      (shape (circle {l} {VIA_D*u:.0f} 0 0))" for l in LAYERS) + "\n      (attach off)\n    )")
    out.append("  )")
    out.append("  (network")
    for n, pins in sorted(nets.items()):
        out.append(f'    (net "{n}"\n      (pins {" ".join(p.replace(chr(34)+"-"+chr(34), "-").replace(chr(34), "") for p in pins)})\n    )')
    # net classes (SPEC.md): power trunks 0.4 mm, rails 0.25 mm, everything else the 0.2 mm default; In1 is the solid GND plane (only GND may use it), In2 carries
    # signals and the 3V3_D pour (the pour is added after routing and flows around other nets' tracks); GND may use any layer
    trunks = [n for n in sorted(nets) if n in ("V5", "VBUS", "VBUS_F", "V24", "V24_RAW", "V5_BOOST", "BOOST_SW")]
    rails = [n for n in sorted(nets) if n in ("3V3_A", "3V3_AR", "3V3_D", "DVDD_1V1")]
    sig = [n for n in sorted(nets) if n != "GND" and n not in trunks and n not in rails]
    via = '(use_via "Via[0-3]_600:300_um")'
    for cls, members, width in (("signals", sig, TRACK), ("trunks", trunks, 0.4), ("rails", rails, 0.25)):
        out.append(f'    (class {cls} ' + " ".join(f'"{n}"' for n in members) +
                   f'\n      (circuit {via} (use_layer F.Cu In2.Cu B.Cu))\n      (rule (width {width*u:.0f}) (clearance {CLEAR*u:.0f}))\n    )')
    out.append(f'    (class ground "GND"\n      (circuit {via})\n      (rule (width {TRACK*u:.0f}) (clearance {CLEAR*u:.0f}))\n    )')
    out.append("  )")
    out.append("  (wiring)\n)")
    open(DSN, "w").write("\n".join(out) + "\n")
    print("wrote", DSN, f"({len(images)} images, {len(padstacks)} padstacks, {len(nets)} nets)")


def route(minutes=8):
    write_dsn()
    if os.path.exists(SES):
        os.remove(SES)
    cmd = [FR, "-de", DSN, "-do", SES, "-mp", "40"]
    print(" ".join(cmd))
    try:
        subprocess.run(cmd, timeout=minutes * 60, capture_output=True)
    except subprocess.TimeoutExpired:
        print("freerouting hit the time limit")
    if not os.path.exists(SES):
        print("no SES written")
        return
    import_ses()


def add_planes(b):
    """Inner ground plane (user rule 2026-11-09): a filled GND zone on In1.Cu covering the board inside the edge clearance. Freerouting is told
    In1.Cu is a power plane (see write_dsn), so GND pins reach it through vias and no signal is routed on In1."""
    from kiutils.items.zones import Zone, ZonePolygon, Hatch, FillSettings
    xs = [g.start.X for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"] + [g.end.X for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    ys = [g.start.Y for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"] + [g.end.Y for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    m = 0.5
    x0, x1, y0, y1 = min(xs) + m, max(xs) - m, min(ys) + m, max(ys) - m
    b.zones = [z for z in b.zones if not ({"In1.Cu", "In2.Cu"} & set(z.layers or []))]
    gnd = {n.name: n.number for n in b.nets}["GND"]
    z = Zone(net=gnd, netName="GND", layers=["In1.Cu"], tstamp=uid(), name="GND_plane", hatch=Hatch(style="edge", pitch=0.5),
             minThickness=0.15,
             fillSettings=FillSettings(yes=True, thermalGap=0.3, thermalBridgeWidth=0.3),
             polygons=[ZonePolygon(coordinates=[Position(X=x0, Y=y0), Position(X=x1, Y=y0), Position(X=x1, Y=y1), Position(X=x0, Y=y1)])])
    b.zones.append(z)
    pw = {n.name: n.number for n in b.nets}.get(PLANE2_NET)
    if pw:
        b.zones.append(Zone(net=pw, netName=PLANE2_NET, layers=["In2.Cu"], tstamp=uid(), name=f"{PLANE2_NET}_plane", hatch=Hatch(style="edge", pitch=0.5),
                            minThickness=0.15, fillSettings=FillSettings(yes=True, thermalGap=0.3, thermalBridgeWidth=0.3),
                            polygons=[ZonePolygon(coordinates=[Position(X=x0, Y=y0), Position(X=x1, Y=y0), Position(X=x1, Y=y1), Position(X=x0, Y=y1)])]))


MH_DRILL = 3.2  # mm, M3 clearance
MH_KEEPOUT = 3.2 / 2 + 0.6  # mm from the hole centre to any copper (hole radius + 0.6 mm: clearance plus the screw head's washer land)


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def add_mounting_holes(b):
    """Four M3 non-plated holes near the corners (the board is screwed to a printed bracket). Each starts 4.5 mm in from both edges and is moved inward along
    the diagonal in 0.5 mm steps until nothing but air is within MH_KEEPOUT (tracks, vias, pad boxes and part pads are checked; the In1/In2 planes are zones and
    are cut by KiCad's clearance). Idempotent: earlier holes (reference MH*) are removed first."""
    from kiutils.footprint import Pad, DrillDefinition
    from kiutils.items.fpitems import FpText
    from kiutils.items.common import Effects, Font, Position as P2
    b.footprints = [f for f in b.footprints if not any(getattr(i, "text", "").startswith("MH") for i in f.graphicItems if getattr(i, "type", "") == "reference")]
    edge = [g for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    x0, x1 = min(g.start.X for g in edge), max(g.end.X for g in edge)
    y0, y1 = min(g.start.Y for g in edge), max(g.end.Y for g in edge)
    segs = [t for t in b.traceItems if isinstance(t, Segment)]
    vias = [t for t in b.traceItems if isinstance(t, Via)]
    boxes = []
    for fp in b.footprints:
        for pad in fp.pads:
            a = math.radians(fp.position.angle or 0)
            c, s_ = math.cos(a), math.sin(a)
            px = fp.position.X + pad.position.X * c + pad.position.Y * s_
            py = fp.position.Y - pad.position.X * s_ + pad.position.Y * c
            boxes.append((px, py, max(pad.size.X, pad.size.Y) / 2))
    def free(x, y):
        if any(_seg_dist(x, y, t.start.X, t.start.Y, t.end.X, t.end.Y) < MH_KEEPOUT + t.width / 2 for t in segs):
            return False
        if any(math.hypot(x - v.position.X, y - v.position.Y) < MH_KEEPOUT + v.size / 2 for v in vias):
            return False
        return all(math.hypot(x - bx, y - by) >= MH_KEEPOUT + r for bx, by, r in boxes)
    placed = []
    for n, (sx, sy) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1)), 1):
        cx, cy = (x0 + 4.5, y0 + 4.5) if sx > 0 else (x1 - 4.5, y1 - 4.5)
        if sx > 0 and sy < 0:
            cx, cy = x0 + 4.5, y1 - 4.5
        if sx < 0 and sy > 0:
            cx, cy = x1 - 4.5, y0 + 4.5
        step = 0
        while not free(cx, cy) and step < 40:
            cx += 0.5 if cx < (x0 + x1) / 2 else -0.5
            cy += 0.5 if cy < (y0 + y1) / 2 else -0.5
            step += 1
        if step >= 40:
            print(f"mounting hole MH{n}: no free spot within 20 mm of the corner")
            continue
        fp = Footprint()
        fp.libId, fp.tstamp, fp.position, fp.layer = "jlc:MountingHole_M3", uid(), P2(X=cx, Y=cy), "F.Cu"
        fp.graphicItems.append(FpText(type="reference", text=f"MH{n}", position=P2(X=0, Y=-3.0), layer="F.SilkS", effects=Effects(font=Font(height=0.8, width=0.8))))
        fp.graphicItems.append(FpText(type="value", text="M3 hole", position=P2(X=0, Y=3.0), layer="F.Fab", effects=Effects(font=Font(height=0.8, width=0.8))))
        fp.pads.append(Pad(number="", type="np_thru_hole", shape="circle", position=P2(X=0, Y=0), size=P2(X=MH_DRILL, Y=MH_DRILL),
                           drill=DrillDefinition(diameter=MH_DRILL), layers=["*.Cu", "*.Mask"], tstamp=uid()))
        b.footprints.append(fp)
        placed.append((n, round(cx, 1), round(cy, 1), step))
    print("mounting holes:", placed)


def clean_silk(b):
    """Silkscreen policy (2026-11-11): the fab-assembled board is built from the BOM and CPL, so reference and value texts go to the Fab layer (not printed; they
    still show in KiCad's Fab view) and only the libraries' outline graphics stay on the silk layers (polarity and pin-1 marks). One title text is added in the
    lower-left corner. Idempotent."""
    from kiutils.items.fpitems import FpText
    from kiutils.items.gritems import GrText
    from kiutils.items.common import Effects, Font, Position as P2
    for fp in b.footprints:
        for it in fp.graphicItems:
            if isinstance(it, FpText) and it.type in ("reference", "value"):
                it.layer = "B.Fab" if it.layer.startswith("B.") else "F.Fab"
    for fp in b.footprints:  # the non-polarised two-pad passives need no outline: it only overlaps its neighbours
        if re.match(r"^(C|R|L|F)\d{4}$", fp.libId.split(":")[1]):
            fp.graphicItems = [it for it in fp.graphicItems if isinstance(it, FpText) or not getattr(it, "layer", "").endswith("SilkS")]
    b.graphicItems = [g for g in b.graphicItems if not (isinstance(g, GrText) and getattr(g, "text", "").startswith("SFB main"))]
    edge = [g for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    x0, y1 = min(g.start.X for g in edge), max(g.end.Y for g in edge)
    b.graphicItems.append(GrText(text="SFB main r1 2026-11", position=P2(X=x0 + 14, Y=y1 - 2.5), layer="F.SilkS", effects=Effects(font=Font(height=1.0, width=1.0)), tstamp=uid()))


def fix_acute(b, stub=0.3, verbose=True):
    """Remove the 45-degree Y-branch joints `geometry` reports (user rule: no acute angles in copper). At a point P where two same-net segments leave 45 degrees
    apart, the shorter one (P -> E) is replaced by a three-piece dogleg: a stub of `stub` mm at 90 degrees to the longer one, then 45 degrees back, then
    parallel to the longer one into E; every bend is 45 degrees (interior 135). The pieces are checked against the 45-degree grid and skipped when the leg is
    too short (needs the leg to be at least stub x sqrt(2) + 0.3 mm). Returns the number of joints rewritten; run DRC afterwards."""
    segs = [t for t in b.traceItems if isinstance(t, Segment)]
    at = defaultdict(list)
    for sg in segs:
        for p, q, which in ((sg.start, sg.end, "s"), (sg.end, sg.start, "e")):
            at[(sg.layer, sg.net, round(p.X, 3), round(p.Y, 3))].append((sg, which, math.degrees(math.atan2(q.Y - p.Y, q.X - p.X)) % 360, math.hypot(q.X - p.X, q.Y - p.Y)))
    done, skipped = 0, 0
    for (layer, net, px, py), legs in list(at.items()):
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                (s1, w1, a1, l1), (s2, w2, a2, l2) = legs[i], legs[j]
                d = abs(a1 - a2) % 360
                d = min(d, 360 - d)
                if abs(d - 45) > 0.5 or s1 not in b.traceItems or s2 not in b.traceItems:
                    continue
                (keep, ka, kl), (move, mw, ma, ml) = ((s1, a1, l1), (s2, w2, a2, l2)) if l1 >= l2 else ((s2, a2, l2), (s1, w1, a1, l1))
                if ml < stub * math.sqrt(2) + 0.3:
                    skipped += 1
                    continue
                turn = (ma - ka + 180) % 360 - 180             # +45 (ccw) or -45 in KiCad's y-down frame as read from the file
                sgn = 1 if turn > 0 else -1
                ar, br = math.radians(ka), math.radians(ma)
                nr = math.radians(ka + 90 * sgn)
                far = move.end if mw == "s" else move.start
                Q = (px + stub * math.cos(nr), py + stub * math.sin(nr))
                kk = ml - stub * math.sqrt(2)
                R = (Q[0] + kk * math.cos(br), Q[1] + kk * math.sin(br))
                pieces = [((px, py), Q), (Q, R), (R, (far.X, far.Y))]
                b.traceItems.remove(move)
                for a_, b_ in pieces:
                    b.traceItems.append(Segment(start=Position(X=a_[0], Y=a_[1]), end=Position(X=b_[0], Y=b_[1]), width=move.width, layer=layer, net=net, tstamp=uid()))
                done += 1
    if verbose:
        print(f"fix_acute: rewrote {done} joints, skipped {skipped} (leg too short)")
    return done


def write_rules():
    """Custom DRC rules next to the board (KiCad reads main_board.kicad_dru): pad-to-pad hole spacing per JLC's 0.45 mm."""
    open(os.path.join(OUT, "main_board.kicad_dru"), "w").write(
        "(version 1)\n"
        f"(rule pad_hole_gap\n  (constraint hole_to_hole (min {PAD_HOLE_GAP}mm))\n  (condition \"A.Type == 'Pad' && B.Type == 'Pad'\"))\n")


def sync_library_fields(b):
    """Copy the library's description and 3D-model entries into each placed footprint (an older place() run blanked them, which made kicad-cli report
    lib_footprint_mismatch for every footprint that has a model)."""
    cache = {}
    for fp in b.footprints:
        name = fp.libId.split(":")[1]
        if not os.path.exists(os.path.join(LIB, name + ".kicad_mod")):
            continue                                  # generated footprints (mounting holes) have no library file
        if name not in cache:
            cache[name] = Footprint.from_file(os.path.join(LIB, name + ".kicad_mod"))
        lib = cache[name]
        fp.models = lib.models
        fp.description = lib.description
        # courtyards and unplated pegs follow the (repaired) library: duplicated courtyard lines made U3's courtyard "self-intersecting", and the USB-C
        # footprint's two 0.6 mm no-net holes were plated pads with no annulus (annular_width / padstack errors); they are non-plated holes
        fp.graphicItems = [it for it in fp.graphicItems if not getattr(it, "layer", "").endswith("CrtYd")] + [
            it for it in lib.graphicItems if getattr(it, "layer", "").endswith("CrtYd")]
        for pad in fp.pads:
            if str(pad.number) == "" and pad.type == "thru_hole" and pad.drill and pad.size.X <= (pad.drill.diameter or 0) + 1e-6:
                pad.type = "np_thru_hole"


def import_ses():
    b = Board.from_file(PCB)
    t = sexp(tokens(open(SES).read()))[0]
    res = 1.0
    def walk(node, f):
        for c in node:
            if isinstance(c, list):
                f(c); walk(c, f)
    for c in t:
        if isinstance(c, list) and c and c[0] == "routes":
            for q in c:
                if isinstance(q, list) and q and q[0] == "resolution":
                    res = float(q[2])
    code = {n.name: n.number for n in b.nets}
    b.traceItems = [x for x in b.traceItems if not isinstance(x, (Segment, Via))]
    nseg = nvia = 0
    def conv(v):
        return float(v) / res / 1000.0
    def visit(node):
        nonlocal nseg, nvia
        if node and node[0] == "net":
            name = node[1]
            for it in node[2:]:
                if not isinstance(it, list):
                    continue
                if it[0] == "wire":
                    for p in it[1:]:
                        if isinstance(p, list) and p[0] == "path":
                            layer, width = p[1], conv(p[2])
                            pts = [(conv(p[i]), -conv(p[i + 1])) for i in range(3, len(p) - 1, 2)]
                            for a, c2 in zip(pts, pts[1:]):
                                b.traceItems.append(Segment(start=Position(X=a[0], Y=a[1]), end=Position(X=c2[0], Y=c2[1]), width=width, layer=layer, net=code[name], tstamp=uid()))
                                nseg += 1
                elif it[0] == "via":
                    b.traceItems.append(Via(position=Position(X=conv(it[2]), Y=-conv(it[3])), size=VIA_D, drill=VIA_H, layers=["F.Cu", "B.Cu"], net=code[name], tstamp=uid()))
                    nvia += 1
    walk(t, lambda n: visit(n) if n and n[0] == "net" and len(n) > 2 and isinstance(n[2], list) and n[2] and n[2][0] in ("wire", "via") else None)
    sync_library_fields(b)
    add_mounting_holes(b)
    clean_silk(b)
    add_planes(b)
    b.to_file(PCB)
    print(f"imported {nseg} segments and {nvia} vias")


def drc():
    """Run kicad-cli DRC and print the violation counts. Fails loudly (exit 2) if kicad-cli fails or does not write a fresh report, so a
    stale drc.json can never be read as the result of this run."""
    from collections import Counter
    rpt = os.path.join(OUT, "drc.json")
    if os.path.exists(rpt):
        os.remove(rpt)
    r = subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--output", rpt, PCB], capture_output=True, text=True)
    if not os.path.exists(rpt):
        print("kicad-cli drc failed (exit %s): %s" % (r.returncode, (r.stderr or r.stdout).strip()[:500]))
        sys.exit(2)
    d = json.load(open(rpt))
    print("violations:", dict(Counter(v["type"] for v in d["violations"])), "| unconnected:", len(d.get("unconnected_items", [])))


def geometry(verbose=False, pcb=None):
    """Trace-shape rule (user, 2026-11-09): no acute angles (acid traps, signal integrity); bends are 45 degrees or rounded.
    Reports (a) segments whose direction is not a multiple of 45 degrees, (b) joints of same-net segments at the same endpoint whose
    interior angle is under 90 degrees (a sharp turn or an acute branch). Zero-length pieces are ignored.
    Scope (decided 2026-11-11): joints are judged per layer from segment end points, so a via needs no separate test (the tracks meeting at it are compared on
    their own layer) and a pad entry is a joint at the pad centre like any other; arcs are rounded bends the rule allows (Freerouting writes none; they are
    counted and reported, not judged)."""
    b = Board.from_file(pcb or PCB)
    segs = [t for t in b.traceItems if isinstance(t, Segment)]
    off45, acute = [], []
    ends = defaultdict(list)
    for s in segs:
        dx, dy = s.end.X - s.start.X, s.end.Y - s.start.Y
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        ang = math.degrees(math.atan2(dy, dx)) % 45
        dev = min(ang, 45 - ang)
        if dev > 0.5:
            off45.append((s.net, s.layer, round(s.start.X, 3), round(s.start.Y, 3), round(L, 3), round(dev, 1)))
        for p, q in ((s.start, s.end), (s.end, s.start)):
            ends[(s.layer, s.net, round(p.X, 3), round(p.Y, 3))].append(math.degrees(math.atan2(q.Y - p.Y, q.X - p.X)))
    for k, dirs in ends.items():
        for i in range(len(dirs)):
            for j in range(i + 1, len(dirs)):
                d = abs(dirs[i] - dirs[j]) % 360
                d = min(d, 360 - d)
                if d < 89.5:
                    acute.append((k, round(d, 1)))
    # (c) a segment end that lands in the interior of another same-net, same-layer segment (a tee the endpoint match above cannot see):
    # the branch makes an acute angle with one half of the host when its direction is under 90 degrees from either host direction.
    for s in segs:
        for p, q in ((s.start, s.end), (s.end, s.start)):
            bx, by = q.X - p.X, q.Y - p.Y
            bl = math.hypot(bx, by)
            if bl < 1e-6:
                continue
            for h in segs:
                if h is s or h.layer != s.layer or h.net != s.net:
                    continue
                hx, hy = h.end.X - h.start.X, h.end.Y - h.start.Y
                hl = math.hypot(hx, hy)
                if hl < 1e-6:
                    continue
                t = ((p.X - h.start.X) * hx + (p.Y - h.start.Y) * hy) / (hl * hl)
                dist = abs((p.X - h.start.X) * hy - (p.Y - h.start.Y) * hx) / hl
                if dist > 0.002 or not (0.001 < t * hl and t * hl < hl - 0.001):
                    continue                      # not on the host, or at one of its ends (the endpoint match covers that)
                cosang = (bx * hx + by * hy) / (bl * hl)
                d = math.degrees(math.acos(max(-1.0, min(1.0, cosang))))
                d = min(d, 180 - d)
                if d < 89.5:
                    acute.append(((s.layer, s.net, round(p.X, 3), round(p.Y, 3), "tee"), round(d, 1)))
    n_arcs = sum(1 for t in b.traceItems if type(t).__name__ == "Arc")
    if n_arcs:
        print(f"{n_arcs} arc tracks (rounded bends, not judged)")
    print(f"segments {len(segs)} | off the 45-degree grid {len(off45)} | acute joints (<90 deg) {len(acute)}")
    if verbose:
        for x in off45[:40]: print("off45", x)
        for x in acute[:40]: print("acute", x)
    return off45, acute


# DFM gate (user, 2026-11-09: run a DFM check at the end to catch manufacturing errors). Blocking = would make JLC reject or the board misbehave;
# advisory = tidy before WP7 but not a fab stop (silk comes from the library footprints; lib_footprint_issues because there is no library table).
# Fails closed: any violation of severity "error" blocks, whether or not its type is named below; the named set also blocks warnings of those types
# (e.g. via_dangling, padstack are warnings in KiCad 9.0.9 but are fab-relevant).
DFM_BLOCKING = {"clearance", "shorting_items", "track_width", "annular_width", "hole_clearance", "hole_to_hole", "copper_edge_clearance", "via_dangling",
                "track_dangling", "padstack", "invalid_outline", "unconnected_items", "items_not_allowed", "drill_out_of_range", "micro_via_drill_out_of_range",
                "solder_mask_bridge", "starved_thermal", "zones_intersect", "isolated_copper"}


def netlist_parity(b):
    """The flow has no .kicad_sch (the schematic is SKiDL code and the netlist the contract), so schematic parity is checked against the netlist: every
    component reference, its footprint, and every (ref, pin) -> net assignment must match the placed board. Returns a list of mismatch strings."""
    comps, nets = parse_netlist(NET)
    pad_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    bad = []
    refs = {}
    for fp in b.footprints:
        ref = [it.text for it in fp.graphicItems if getattr(it, "type", "") == "reference"][0]
        refs[ref] = fp
    for r in sorted(set(comps) - set(refs)):
        bad.append(f"{r} is in the netlist but not on the board")
    for r in sorted(set(refs) - set(comps)):
        if r.startswith("MH"):
            continue                                  # mounting holes are mechanical, not in the netlist
        bad.append(f"{r} is on the board but not in the netlist")
    for r, fp in refs.items():
        if r in comps and fp.libId.split(":")[1] != comps[r][1]:
            bad.append(f"{r}: footprint {fp.libId} against netlist {comps[r][1]}")
        for pad in fp.pads:
            want = pad_net.get((r, str(pad.number)))
            have = pad.net.name if pad.net and pad.net.name else None
            if want != have and str(pad.number) != "":
                bad.append(f"{r}.{pad.number}: net {have} against netlist {want}")
    return bad


def board_size_and_holes(b):
    edge = [g for g in b.graphicItems if getattr(g, "layer", "") == "Edge.Cuts"]
    xs = [g.start.X for g in edge] + [g.end.X for g in edge]
    ys = [g.start.Y for g in edge] + [g.end.Y for g in edge]
    holes = sum(1 for fp in b.footprints for pad in fp.pads if pad.type == "np_thru_hole" and pad.drill and (pad.drill.diameter or 0) >= 2.5)
    return max(xs) - min(xs), max(ys) - min(ys), holes


def dfm():
    """End-of-layout manufacturing check: kicad-cli DRC against the .kicad_pro rules + the trace-shape rule (45-degree grid, no acute joints).
    Exit status 1 when anything blocking remains. Also confirm in JLC's own DFM/placement preview at order time (WP7)."""
    from collections import Counter
    drc()
    d = json.load(open(os.path.join(OUT, "drc.json")))
    kinds = Counter(v["type"] for v in d["violations"])
    errors = Counter(v["type"] for v in d["violations"] if v.get("severity") == "error")
    blocking = {k: n for k, n in kinds.items() if k in DFM_BLOCKING}
    blocking.update(errors)
    unconn = len(d.get("unconnected_items", []))
    if unconn:
        blocking["unconnected_items"] = unconn
    off45, acute = geometry()
    if off45:
        blocking["off_45_degree_segments"] = len(off45)
    if acute:
        # user decision 2026-11-12: 45-degree Y-branches (three or more same-net segments meeting, two of them 45 degrees apart) are accepted
        # (advisory); a two-segment 45-degree V turn, a hairpin or anything sharper still blocks
        bb_ = Board.from_file(PCB)
        deg = defaultdict(int)
        for t_ in bb_.traceItems:
            if isinstance(t_, Segment):
                for p_ in (t_.start, t_.end):
                    deg[(t_.layer, t_.net, round(p_.X, 3), round(p_.Y, 3))] += 1
        ok_y = [a for a in acute if len(a[0]) == 4 and abs(a[1] - 45.0) < 0.6 and deg.get(a[0], 0) >= 3]
        hard = len(acute) - len(ok_y)
        if hard:
            blocking["acute_joints"] = hard
        acute_y45 = len(ok_y)
    else:
        acute_y45 = 0
    # decisions 2026-11-10: a malformed courtyard is a library-footprint drawing problem, not a fab stop (advisory); overlapping courtyards are a real
    # placement problem (blocking); silk over copper is clipped by the fab (advisory); planes must exist on both inner layers before fab output.
    blocking.pop("malformed_courtyard", None)
    if kinds.get("courtyards_overlap"):
        blocking["courtyards_overlap"] = kinds["courtyards_overlap"]
    b = Board.from_file(PCB)
    zone_layers = {l for z in b.zones for l in (z.layers or [])}
    missing = [l for l in ("In1.Cu", "In2.Cu") if l not in zone_layers]
    if missing:
        blocking["inner_plane_missing"] = len(missing)
    parity = netlist_parity(b)
    if parity:
        blocking["netlist_parity"] = len(parity)
        for line in parity[:10]:
            print("parity:", line)
    w_, h_, holes = board_size_and_holes(b)
    if holes < 2:
        blocking["mounting_holes_missing"] = 2 - holes   # at least two non-plated holes of 2.5 mm or more (G2 positions)
    advisory = {k: n for k, n in kinds.items() if k not in blocking}
    if acute_y45:
        advisory["y_branch_45_accepted"] = acute_y45
    advisory["board_size"] = f"{w_:.0f} x {h_:.0f} mm against the cheap 4-layer tier (50 x 50 mm, kb/fab_ordering_notes.md): the price tier is the user's decision"
    if not any("FID" in (getattr(fp, "libId", "") or "").upper() for fp in b.footprints):
        advisory["no_assembly_fiducials"] = 1
    print("DFM blocking:", blocking or "none")
    print("DFM advisory:", advisory or "none")
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "place"
    if cmd == "place":
        place(float(sys.argv[2]) if len(sys.argv) > 2 else 100.0, float(sys.argv[3]) if len(sys.argv) > 3 else 80.0)
    elif cmd == "route":
        route(float(sys.argv[2]) if len(sys.argv) > 2 else 8)
    elif cmd == "fixacute":
        bb = Board.from_file(PCB)
        fix_acute(bb)
        bb.to_file(PCB)
    elif cmd == "silk":
        bb = Board.from_file(PCB)
        clean_silk(bb)
        bb.to_file(PCB)
    elif cmd == "holes":
        bb = Board.from_file(PCB)
        add_mounting_holes(bb)
        bb.to_file(PCB)
    elif cmd == "rules":
        write_rules()
    elif cmd == "sync":
        bb = Board.from_file(PCB)
        sync_library_fields(bb)
        bb.to_file(PCB)
    elif cmd == "drc":
        drc()
    elif cmd == "dfm":
        dfm()
    elif cmd == "geometry":
        geometry(verbose="-v" in sys.argv)
