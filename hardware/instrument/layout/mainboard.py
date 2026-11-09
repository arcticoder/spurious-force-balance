"""
mainboard.py — WP5: the instrument main board in KiCad format, from the SKiDL netlist, without KiCad's Python API (pcbnew segfaults headless here).

    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py place [W H]   # footprints, nets, force-directed placement -> out/main_board.kicad_pcb
    ~/.venvs/lab-hw/bin/python hardware/instrument/layout/mainboard.py route         # Specctra DSN -> Freerouting -> SES -> tracks/vias in the board
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
CLEAR, TRACK, VIA_D, VIA_H = 0.15, 0.2, 0.6, 0.3


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
        fp.models = []
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
    for r in refs:
        if r not in pos:
            pos[r] = (W / 2 + rng.normal(0, 8), H / 2 + rng.normal(0, 8))
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

    def clip():
        P[:, 0] = np.clip(P[:, 0], S[:, 0] / 2 + 1.5, W - S[:, 0] / 2 - 1.5)
        P[:, 1] = np.clip(P[:, 1], S[:, 1] / 2 + 1.5, H - S[:, 1] / 2 - 1.5)

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
    b.to_file(PCB)
    json.dump({"board": {"design_settings": {"rules": {"min_clearance": CLEAR, "min_track_width": 0.15, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3,
                                                         "min_copper_edge_clearance": 0.2, "min_hole_to_hole": 0.25, "min_via_annular_width": 0.15}}}},
              open(os.path.join(OUT, "main_board.kicad_pro"), "w"), indent=1)
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
    xs = [g.start.X for g in b.graphicItems] + [g.end.X for g in b.graphicItems]
    ys = [g.start.Y for g in b.graphicItems] + [g.end.Y for g in b.graphicItems]
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
    out.append('    (class default ' + " ".join(f'"{n}"' for n in sorted(nets)) +
               f'\n      (circuit (use_via "Via[0-3]_600:300_um"))\n      (rule (width {TRACK*u:.0f}) (clearance {CLEAR*u:.0f}))\n    )')
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
    b.to_file(PCB)
    print(f"imported {nseg} segments and {nvia} vias")


def drc():
    rpt = os.path.join(OUT, "drc.json")
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--output", rpt, PCB], capture_output=True)
    d = json.load(open(rpt))
    from collections import Counter
    print("violations:", dict(Counter(v["type"] for v in d["violations"])), "| unconnected:", len(d.get("unconnected_items", [])))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "place"
    if cmd == "place":
        place(float(sys.argv[2]) if len(sys.argv) > 2 else 100.0, float(sys.argv[3]) if len(sys.argv) > 3 else 80.0)
    elif cmd == "route":
        route()
    elif cmd == "drc":
        drc()
