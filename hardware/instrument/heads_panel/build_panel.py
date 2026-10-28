"""
build_panel.py — the sensor-head panel for a JLC Standard-PCBA order (Part N).

    ~/.venvs/lab-hw/bin/python hardware/instrument/heads_panel/build_panel.py

One 76 x 70 mm panel (Standard assembly needs at least 70 x 70 mm with edge rails): two sensor-head-1 boards (TMP117 + MMC5983MA) and two sensor-head-2 boards (TMP117 only), each 26 x 17 mm,
tab-routed with mouse bites inside a 5 mm rail with three tooling holes and three fiducials. The parts and nets come from the SKiDL descriptions in ../schematic/heads.py (one source of truth);
placement is by hand below; routing is Freerouting; both faces get a ground pour. Outputs in out/: the KiCad board, DRC report, Gerbers + drill (zip), BOM and CPL in JLC's format, a render.
Assumptions to check in JLC's DFM / placement preview (the order asks for "Confirm Production File"): the rail and tooling-hole sizes, the mouse-bite pattern, and the part rotations in the CPL
(the CPL uses the footprint orientation as placed; JLC's library may expect others, as for any EasyEDA-sourced footprint).
"""

import builtins
import csv
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "schematic"))
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ.setdefault("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")

import pcbnew  # noqa: E402

LIB = os.path.join(HERE, "..", "lib", "jlc.pretty")
OUT = os.path.join(HERE, "out")
FREEROUTING = os.path.expanduser("~/tools/freerouting/freerouting-2.5.0-linux-x64/bin/freerouting")
MM = pcbnew.FromMM

PANEL_W, PANEL_H = 76.0, 70.0
BW, BH = 26.0, 17.0  # one head board
GAP = 2.0  # routed slot between a board and the waste
TAB = 3.0  # tab width, with mouse bites across it
# board origins (top-left) in the panel: two columns, two rows
ORIGINS = {"H1a": (11.0, 8.0), "H1b": (39.0, 8.0), "H2a": (11.0, 38.0), "H2b": (39.0, 38.0)}
KIND = {"H1a": "sensor_head_1", "H1b": "sensor_head_1", "H2a": "sensor_head_2", "H2b": "sensor_head_2"}

# local placement per part, by (kind, role): (x, y, rotation degrees)  [role = the part's "Role" field]
PLACE = {
    "sensor_head_1": {"sensor head cable": (7.0, 13.2, 0), "head temperature": (14.5, 6.0, 0), "magnetic field at the device mount": (21.5, 6.5, 0)},
    "sensor_head_2": {"sensor head cable": (7.0, 13.2, 0), "head temperature": (14.5, 6.0, 0)},
}
# passives: placed in order of appearance for each kind (positions list), by LCSC number
PASSIVES = {
    "sensor_head_1": {14663: [(14.5, 10.0, 0), (23.5, 11.2, 0)], 15849: [(19.5, 11.2, 0)], 15850: [(21.5, 14.5, 0)]},  # 100n x2, 1u, 10u
    "sensor_head_2": {14663: [(14.5, 10.0, 0)]},
}


def vec(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def harvest(builder):
    """Run a SKiDL head builder and return [(ref, lcsc, footprint, role, [(pad number, net name or None)])] for the real parts."""
    builder()
    out = []
    for p in builtins.default_circuit.parts:
        lcsc = p.fields.get("LCSC")
        if not lcsc or lcsc == "C0":
            continue
        pins = [(str(pin.num), pin.net.name if pin.net is not None and len([q for q in pin.net.pins if q.part is not None]) > 1 else None) for pin in p.pins]
        out.append((p.ref, int(lcsc[1:]), p.footprint, p.fields.get("Role", ""), pins))
    return out


def edge_line(board, x0, y0, x1, y1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(vec(x0, y0))
    s.SetEnd(vec(x1, y1))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.1))
    board.Add(s)


def npth(board, x, y, d, ref="H"):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.Reference().SetVisible(False)
    fp.SetPosition(vec(x, y))
    pad = pcbnew.PAD(fp)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(vec(d, d))
    pad.SetDrillSize(vec(d, d))
    pad.SetLayerSet(pcbnew.LSET.AllCuMask())
    pad.SetPosition(vec(x, y))
    fp.Add(pad)
    board.Add(fp)


def fiducial(board, x, y, ref):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.Reference().SetVisible(False)
    fp.SetPosition(vec(x, y))
    pad = pcbnew.PAD(fp)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(vec(1.0, 1.0))
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.F_Mask)
    pad.SetLayerSet(ls)
    pad.SetLocalSolderMaskMargin(MM(0.5))
    pad.SetPosition(vec(x, y))
    fp.Add(pad)
    board.Add(fp)


def outline_with_tabs(board, x0, y0, w, h):
    """The board's outline, open for one tab on each of the left and right sides (centred), with mouse bites across each tab."""
    mid = y0 + h / 2
    a, b = mid - TAB / 2, mid + TAB / 2
    edge_line(board, x0, y0, x0 + w, y0)
    edge_line(board, x0, y0 + h, x0 + w, y0 + h)
    for x in (x0, x0 + w):
        edge_line(board, x, y0, x, a)
        edge_line(board, x, b, x, y0 + h)
        for k in range(4):  # mouse bites: 0.5 mm holes at 0.8 mm pitch across the tab, centred on the board edge
            npth(board, x, mid - 1.2 + 0.8 * k, 0.5, "MB")


def build():
    os.makedirs(OUT, exist_ok=True)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(MM(1.6))
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(MM(0.25))
    nc.SetClearance(MM(0.2))
    nc.SetViaDiameter(MM(0.6))
    nc.SetViaDrill(MM(0.3))

    # panel frame
    for (x0, y0, x1, y1) in ((0, 0, PANEL_W, 0), (PANEL_W, 0, PANEL_W, PANEL_H), (PANEL_W, PANEL_H, 0, PANEL_H), (0, PANEL_H, 0, 0)):
        edge_line(board, x0, y0, x1, y1)
    for i, (x, y) in enumerate(((2.5, 2.5), (PANEL_W - 2.5, 2.5), (2.5, PANEL_H - 2.5))):
        npth(board, x, y, 2.0, "TH%d" % (i + 1))
    for i, (x, y) in enumerate(((8.0, 2.5), (PANEL_W - 8.0, 2.5), (PANEL_W - 8.0, PANEL_H - 2.5))):
        fiducial(board, x, y, "FID%d" % (i + 1))

    netinfo = {}

    def net(name):
        if name not in netinfo:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            netinfo[name] = ni
        return netinfo[name]

    data = {k: harvest(getattr(__import__("heads"), k)) for k in set(KIND.values())}
    bom = {}  # (lcsc, footprint) -> [designators]
    cpl = []
    n_ref = {"U": 0, "C": 0, "J": 0}
    for inst, (ox, oy) in ORIGINS.items():
        kind = KIND[inst]
        seen = {}
        for ref, lcsc, fpname, role, pins in data[kind]:
            if role in PLACE[kind]:
                x, y, rot = PLACE[kind][role]
            else:
                k = seen.get(lcsc, 0)
                seen[lcsc] = k + 1
                x, y, rot = PASSIVES[kind][lcsc][k]
            lib, name = fpname.split(":")
            fp = pcbnew.FootprintLoad(LIB, name)
            letter = "J" if lcsc == 160404 else "U" if lcsc in (699536, 404329) else "C"  # connector, ICs, capacitors
            n_ref[letter] += 1
            des = "%s%d" % (letter, n_ref[letter])
            fp.SetReference(des)
            fp.SetValue(name)
            fp.Reference().SetVisible(False)  # the 0603 parts are too small for silkscreen text; the designators stay in the BOM and CPL
            fp.Value().SetVisible(False)
            fp.SetPosition(vec(ox + x, oy + y))
            fp.SetOrientationDegrees(rot)
            for pad in fp.Pads():
                for num, nname in pins:
                    if pad.GetNumber() == num and nname:
                        pad.SetNet(net("%s/%s" % (inst, nname)))
            board.Add(fp)
            bom.setdefault((lcsc, name), []).append(des)
            cpl.append((des, ox + x, oy + y, "Top", rot))
        # silkscreen label
        t = pcbnew.PCB_TEXT(board)
        t.SetText("%s %s" % (inst, kind.replace("sensor_head_", "head ")))
        t.SetPosition(vec(ox + BW / 2, oy + BH - 1.0))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(vec(0.9, 0.9))
        board.Add(t)

    path = os.path.join(OUT, "heads_panel.kicad_pcb")
    board.Save(path)
    return board, path, bom, cpl, netinfo


def import_ses(board, ses):
    """Add Freerouting's wires and vias to the board. pcbnew.ImportSpecctraSES returns False on this board without a message, so the session file is read directly
    (resolution um 10: coordinates are in units of 0.1 um; y is KiCad's, already negative-down in the DSN's frame, so it is negated)."""
    import re

    text = open(ses).read()
    text = text[text.index("(network_out"):]
    unit = lambda v: int(v) * 100  # 0.1 um -> nm  # noqa: E731
    layers = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    n_tracks = n_vias = 0
    for m in re.finditer(r'\(net "([^"]+)"(.*?)\n      \)', text, re.S):
        name, body = m.group(1), m.group(2)
        ni = board.FindNet(name)
        for w in re.finditer(r'\(path (\S+) (\d+)\s+([-\d\s]+)\)', body):
            layer, width, nums = w.group(1), int(w.group(2)), list(map(int, w.group(3).split()))
            pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(unit(x0), -unit(y0)))
                t.SetEnd(pcbnew.VECTOR2I(unit(x1), -unit(y1)))
                t.SetWidth(unit(width))
                t.SetLayer(layers[layer])
                t.SetNet(ni)
                board.Add(t)
                n_tracks += 1
        for v in re.finditer(r'\(via "[^"]*" (-?\d+) (-?\d+)', body):
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(unit(int(v.group(1))), -unit(int(v.group(2)))))
            via.SetWidth(MM(0.6))
            via.SetDrill(MM(0.3))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(ni)
            board.Add(via)
            n_vias += 1
    print("imported %d track segments and %d vias" % (n_tracks, n_vias))


def route(path):
    dsn = os.path.join(OUT, "heads_panel.dsn")
    ses = os.path.join(OUT, "heads_panel.ses")
    board = pcbnew.LoadBoard(path)
    pcbnew.ExportSpecctraDSN(board, dsn)
    subprocess.run([FREEROUTING, "-de", dsn, "-do", ses, "-mp", "20"], check=True, capture_output=True, timeout=600)
    board = pcbnew.LoadBoard(path)
    import_ses(board, ses)
    return board


def add_outlines(board):
    """The tab-routed board outlines and mouse bites, added after routing (the router needs the single closed panel frame)."""
    for ox, oy in ORIGINS.values():
        outline_with_tabs(board, ox, oy, BW, BH)


def pours(board):
    """A ground pour on both faces inside each board outline (inset 0.5 mm), on that board's GND net."""
    nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByName().values()} if hasattr(board.GetNetInfo(), "NetsByName") else {}
    for inst, (ox, oy) in ORIGINS.items():
        gnd = board.FindNet("%s/GND" % inst)
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = pcbnew.ZONE(board)
            z.SetLayer(layer)
            z.SetNet(gnd)
            z.SetLocalClearance(MM(0.25))
            z.SetMinThickness(MM(0.2))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            o = z.Outline()
            o.NewOutline()
            for x, y in ((ox + 0.5, oy + 0.5), (ox + BW - 0.5, oy + 0.5), (ox + BW - 0.5, oy + BH - 0.5), (ox + 0.5, oy + BH - 0.5)):
                o.Append(MM(x), MM(y))
            board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def exports(path, bom, cpl):
    # BOM and CPL in JLC's column names
    with open(os.path.join(OUT, "bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (lcsc, name), des in sorted(bom.items(), key=lambda kv: kv[1][0]):
            w.writerow([name, ",".join(des), name, "C%d" % lcsc])
    with open(os.path.join(OUT, "cpl.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for des, x, y, layer, rot in cpl:
            w.writerow([des, "%.3fmm" % x, "%.3fmm" % -y, layer, "%d" % rot])  # JLC's Y is up; KiCad's is down
    g = os.path.join(OUT, "gerbers")
    os.makedirs(g, exist_ok=True)
    subprocess.run(["kicad-cli", "pcb", "export", "gerbers", "--output", g + "/", "--layers", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts", path], check=True, capture_output=True)
    subprocess.run(["kicad-cli", "pcb", "export", "drill", "--output", g + "/", "--format", "excellon", "--drill-origin", "absolute", "--excellon-separate-th", path], check=True, capture_output=True)
    z = os.path.join(OUT, "heads_panel_gerbers.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(g)):
            zf.write(os.path.join(g, fn), fn)
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--output", os.path.join(OUT, "drc.json"), path], check=False, capture_output=True)
    subprocess.run(["kicad-cli", "pcb", "render", "--output", os.path.join(OUT, "heads_panel.png"), "--side", "top", "--width", "1400", "--height", "1300", path], check=False, capture_output=True)
    return z


def main():
    board, path, bom, cpl, netinfo = build()
    board = route(path)
    add_outlines(board)
    pours(board)
    board.Save(path)
    z = exports(path, bom, cpl)
    print("wrote", os.path.relpath(path, HERE), "and", os.path.relpath(z, HERE))


if __name__ == "__main__":
    main()
