"""
balance.py — CadQuery model of the torsion balance (`FORCEBAL`), G2.

    ~/.venvs/lab-hw/bin/python hardware/balance/balance.py

Builds every part in millimetres from `params.py`, computes the moving assembly's mass and moment of
inertia and compares them with the model's, checks that nothing collides over the arm's swing, that every
printed part fits the printer, that the balance sits inside the enclosure with room to spare, derives the
fastener list from the holes it cuts, and exports STL files (one per part) and a STEP assembly to
`hardware/balance/cad/`. The FR4 boards are fabricated by JLCPCB (see `boards.py`, which writes their KiCad
files from the same numbers); only the fixed frame and the vane holder are printed, in PLA.

Layout (z up, the pivot axis is the z axis, the strip hangs on it):
  The arm is an FR4 board standing on edge in the x-z plane (faces toward +-y), 60 mm tall, hung from its top
  edge by a 50 um stainless strip clamped flat to the board's +y face by a small FR4 plate (the arm's copper
  pad under the plate grounds the strip). A face of the board carries the moving calibration electrode, its
  end finger is the flag crossing the optical bracket, a brass rod through a hole in it is the ballast (sliding
  it along y trims the lean), the damper's copper pad lies on a printed holder on its +y face, and the device
  card is bolted to its -y face on spacers. Because the board hangs 30 mm below the strip's lower end, the arm
  tilts only 33 mrad per mm of centre-of-mass offset (a printed 20 mm arm was 66).
  The strip's top end is clamped between two FR4 plates hung in a printed carrier (the torsion head), a 30 mm
  disc turning in a bore of the printed gantry; two M3 screws push its lever tab, which sets the zero to +-5
  degrees. A printed frame with six uncut acrylic sheets encloses it all.
"""

import math
import os

import cadquery as cq

import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cad")

MM = 1e3
L = P.ARM_HALF_LENGTH * MM
PLA_G_MM3 = 1.24e-3
INFILL = 0.6  # fraction of the solid's mass for a printed part (walls + 30% gyroid)
CU_G_MM3, STEEL_G_MM3, ND_G_MM3, ACRYLIC_G_MM3 = 8.96e-3, 7.93e-3, 7.5e-3, 1.18e-3
BRASS_G_MM3 = P.BRASS_DENSITY
FR4_G_MM3 = P.FR4_DENSITY * 1e-6  # kg/m^3 -> g/mm^3

# board and strip stack (y): arm board | strip | clamp plate, the strip centred on the axis
T_STRIP = P.STRIP_THICKNESS * MM
W_STRIP = P.STRIP_WIDTH * MM
BT = P.BOARD_T * MM
YB0, YB1 = -T_STRIP / 2 - BT, -T_STRIP / 2  # the arm board
YP0, YP1 = T_STRIP / 2, T_STRIP / 2 + BT  # a clamp plate on the +y side
ZA1 = P.ARM_TOP_Z * MM  # the arm board's top edge
ZA0 = ZA1 - P.ARM_HEIGHT * MM
CLAMP_H = 14.0  # height of each strip clamp plate
Z_STRIP0 = ZA1 - CLAMP_H  # the strip's lower end
Z_UP0 = ZA1 + P.STRIP_LENGTH * MM  # the upper clamp plates' bottom edge; the strip's free length is ZA1..Z_UP0
Z_UP1 = Z_UP0 + CLAMP_H
Z_V = 50.0  # height of the damper vane and the flag, mm
X_PLATE = P.PLATE_X * MM
X_VANE = P.VANE_X * MM
X_BALLAST, Z_BALLAST = -0.9 * L, ZA0 + 14.0
X_BOLT_DUT = L - 3.0
VANE_T = P.VANE_THICKNESS * MM
M3_CLEAR, M3_PILOT, M3_HEAD = 3.4, 2.6, 6.2
NUT_DIA, NUT_DEPTH = 6.35, 2.6  # M3 nut, 5.5 mm across flats (6.35 circumscribed), pocket depth
FOOT_Z0, FOOT_Z1 = 6.0, 10.0  # flange of each foot, on top of the 6 mm base
BASE_HALF = 109.0  # base plate is 218 x 218 mm (the K1 prints 220 x 220)
Z_BEAM0, Z_BEAM1 = 118.0, 138.0  # the gantry's cross beam; the torsion head sits in it
HEAD_BOSS_Y = 14.0  # half-width of the head's lever extension: an M3x14 adjusting screw's tip reaches the tab's mid-plane from here
HEAD_TAB_R, HEAD_TAB_W = 26.0, 6.0  # the lever tab's reach and width

FASTENERS = []  # (kind, where) appended as holes are cut


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_z(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def cyl_x(y, z, x0, x1, d):
    return cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0).translate((x0, y, z))


def cyl_y(x, z, y0, y1, d):
    return cq.Workplane("XZ").circle(d / 2).extrude(-(y1 - y0)).translate((x, y0, z))


def ring_y(x, z, y0, y1, od, idia):
    return cyl_y(x, z, y0, y1, od).cut(cyl_y(x, z, y0 - 1, y1 + 1, idia))


def nut_pocket_z(x, y, z_top, depth=NUT_DEPTH):
    return cq.Workplane("XY").polygon(6, NUT_DIA).extrude(depth).translate((x, y, z_top - depth))


def nut_pocket_y(x, z, y_face, direction, depth=NUT_DEPTH):
    """Hex pocket in a face normal to y; direction +1 cuts toward +y from y_face, -1 toward -y."""
    return cq.Workplane("XZ").polygon(6, NUT_DIA).extrude(-depth * direction).translate((x, y_face, z))


def screw_set(x, z, y_base, direction, length, nut_spans, label, kind):
    """The moving or fixed hardware of one bolt as one solid: head (5.5 x 2 mm) on a washer (7 x 0.5) at y_base,
    a 3 mm shank of `length` toward `direction`, and a nut ring (6 x 3 mm) for each (y0, y1) in nut_spans. Appends to FASTENERS."""
    head = cyl_y(x, z, *sorted((y_base - direction * 2.0, y_base)), 5.5)
    wash = ring_y(x, z, *sorted((y_base, y_base + direction * 0.5)), 7.0, 3.2)
    shank = cyl_y(x, z, *sorted((y_base + direction * 0.5, y_base + direction * length)), 3.0)
    solid = head.union(wash).union(shank)
    for y0, y1 in nut_spans:
        solid = solid.union(ring_y(x, z, y0, y1, 5.5, 3.0))
    FASTENERS.append((f"M3x{int(length)} pan head screw", label))
    FASTENERS.append(("M3 flat washer", label))
    for _ in nut_spans:
        FASTENERS.append((kind, label))
    return solid


def with_foot(part, x0, x1, y0, y1, hole_xy, base_holes, label, slack=False):
    """Add a flanged foot under a fixed part: flange y0..y1, one M3 screw at each hole. Normally from below through the base into a nut
    captured in a hex pocket in the flange's top face. With slack=True the screw goes down from above through a 6.6 mm hole in the flange
    (+-1.6 mm of play, for aligning the part) into a nut captured in the base's underside."""
    part = part.union(box(x0, x1, y0, y1, FOOT_Z0, FOOT_Z1))
    for (hx, hy) in hole_xy:
        if slack:
            part = part.cut(cyl_z(hx, hy, FOOT_Z0 - 0.1, FOOT_Z1 + 0.1, 6.6))
            base_holes.append((hx, hy, "nut_below"))
            FASTENERS.append(("M3x14 pan head screw", f"{label}: from above through the flange into a nut in the base"))
            FASTENERS.append(("M3 nut", f"{label}: captured in the base's underside"))
        else:
            part = part.cut(cyl_z(hx, hy, FOOT_Z0 - 0.1, FOOT_Z1 + 0.1, M3_CLEAR)).cut(nut_pocket_z(hx, hy, FOOT_Z1))
            base_holes.append((hx, hy, None))
            FASTENERS.append(("M3x12 pan head screw", f"{label}: from below through the base into the foot"))
            FASTENERS.append(("M3 nut", f"{label}: captured in the foot"))
        FASTENERS.append(("M3 flat washer", f"{label}: under the screw head"))
    return part


def build(ballast_len=10.0, ballast_y=0.0):
    """All parts. ballast_len and ballast_y (mm) are solved by balance_solve() so the moving assembly's centre of mass sits on the pivot
    axis: the length balances x, the rod's position along y balances the lean."""
    FASTENERS.clear()
    parts = {}  # name -> (solid, density g/mm3, moving, printed)
    base_holes = []

    def add(name, wp, density, moving, printed=False):
        if printed and name in P.PRINTED_MASS_G:  # the slicer's figure beats the infill estimate
            density = P.PRINTED_MASS_G[name] / wp.val().Volume()
        parts[name] = (wp, density, moving, printed)

    pla = PLA_G_MM3 * INFILL

    # ---- the moving assembly: the arm board and what hangs on it --------------------------------------------------
    arm = box(-L, L, YB0, YB1, ZA0, ZA1).union(box(-L - 8, -L, YB0, YB1, Z_V - 4, Z_V + 4))  # the finger is the flag
    for x in (-5.0, 5.0):  # strip clamp bolts
        arm = arm.cut(cyl_y(x, ZA1 - CLAMP_H / 2, YB0 - 1, YB1 + 1, M3_CLEAR))
    arm = arm.cut(cyl_y(X_BALLAST, Z_BALLAST, YB0 - 1, YB1 + 1, 10.2))  # ballast rod hole
    for x in (X_VANE - 3, X_VANE + 3):  # vane holder bolts, below the vane's slot
        arm = arm.cut(cyl_y(x, Z_V - 4.5, YB0 - 1, YB1 + 1, M3_CLEAR))
    for dz in (-6.0, 6.0):  # device card bolts
        arm = arm.cut(cyl_y(X_BOLT_DUT, Z_V + dz, YB0 - 1, YB1 + 1, M3_CLEAR))
    add("arm", arm, FR4_G_MM3, True)
    # the strip and the lower clamp plate: the strip lies on the arm board's +y face under the plate
    add("strip", box(-W_STRIP / 2, W_STRIP / 2, -T_STRIP / 2, T_STRIP / 2, Z_STRIP0, Z_UP1), STEEL_G_MM3, True)
    low = box(-8, 8, YP0, YP1, Z_STRIP0, ZA1)
    for x in (-5.0, 5.0):
        low = low.cut(cyl_y(x, ZA1 - CLAMP_H / 2, YP0 - 1, YP1 + 1, M3_CLEAR))
    add("clamp_low", low, FR4_G_MM3, True)
    hw = None
    for x in (-5.0, 5.0):  # head and washer on the plate's +y face, nut (304 stainless: it moves) on the board's -y face
        s_ = screw_set(x, ZA1 - CLAMP_H / 2, YP1 + 0.5, -1, 10.0, [(YB0 - 2.4, YB0)], "lower strip clamp bolt", "M3 nut, 304 stainless")
        hw = s_ if hw is None else hw.union(s_)
    add("hw_clamp_low", hw, STEEL_G_MM3, True)
    # ballast: a brass rod along y through the arm board's hole, its position along y trimmed to level the arm
    add("ballast", cyl_y(X_BALLAST, Z_BALLAST, ballast_y - ballast_len / 2, ballast_y + ballast_len / 2, 10.0), BRASS_G_MM3, True)
    # damper vane: one uncut 20 x 20 mm copper pad (or two stacked) lying in the slot of a printed holder bolted to the board's +y face
    vx0, vx1 = X_VANE - P.VANE_SIZE[0] * MM / 2, X_VANE + P.VANE_SIZE[0] * MM / 2
    vy0, vy1 = 8.0, 8.0 + P.VANE_SIZE[1] * MM
    vane_box = box(vx0, vx1, vy0, vy1, Z_V - VANE_T / 2, Z_V + VANE_T / 2)
    holder_y1 = 12.0
    holder = box(X_VANE - 6, X_VANE + 6, YB1, holder_y1, Z_V - 9, Z_V + 3)
    holder = holder.cut(box(vx0 - 0.2, vx1 + 0.2, vy0 - 0.2, holder_y1 + 0.1, Z_V - 0.4, Z_V + 0.4))  # the vane slot: room for two pads
    hw = None
    for x in (X_VANE - 3, X_VANE + 3):
        holder = holder.cut(cyl_y(x, Z_V - 4.5, YB1 - 0.1, holder_y1 + 0.1, M3_CLEAR)).cut(nut_pocket_y(x, Z_V - 4.5, holder_y1, -1))
        s_ = screw_set(x, Z_V - 4.5, YB0 - 0.5, 1, 14.0, [(holder_y1 - NUT_DEPTH, holder_y1)], "vane holder bolt", "M3 nut, 304 stainless")
        hw = s_ if hw is None else hw.union(s_)
    add("vane_holder", holder, pla, True, True)
    add("hw_holder", hw, STEEL_G_MM3, True)
    add("vane", vane_box, CU_G_MM3, True)
    # device card: 16 x 24 FR4 on two stacked 304 nuts per bolt (a 4.8 mm air gap to the arm board), 2 g with the device
    card_y0, card_y1 = YB0 - 4.8 - 1.6, YB0 - 4.8
    card = box(L - 12, L + 4, card_y0, card_y1, Z_V - 12, Z_V + 12)
    hw = None
    for dz in (-6.0, 6.0):
        s_ = screw_set(X_BOLT_DUT, Z_V + dz, card_y0 - 0.5, 1, 14.0, [(YB0 - 2.4, YB0), (YB0 - 4.8, YB0 - 2.4), (YB1, YB1 + 2.4)], "device card bolt", "M3 nut, 304 stainless")
        card = card.cut(cyl_y(X_BOLT_DUT, Z_V + dz, card_y0 - 1, card_y1 + 1, M3_CLEAR))
        hw = s_ if hw is None else hw.union(s_)
    add("dut_card", card, 2.0 / card.val().Volume(), True)  # 2 g with the resistor and header [assume]
    add("hw_dut", hw, STEEL_G_MM3, True)

    # ---- the fixed structure --------------------------------------------------------------------------------
    # gantry: two legs, a cross beam, and a boss holding the torsion head's bore, one printed piece; the legs stand on feet
    gantry = box(-6, 6, 39, 51, 6, Z_BEAM1).union(box(-6, 6, -51, -39, 6, Z_BEAM1)).union(box(-8, 8, -51, 51, Z_BEAM0, Z_BEAM1))
    gantry = gantry.union(box(-19, 19, -19, 19, Z_BEAM0, Z_BEAM1)).union(box(19, 31, -HEAD_BOSS_Y, HEAD_BOSS_Y, Z_BEAM0, Z_BEAM1))
    gantry = gantry.cut(cyl_z(0, 0, 128, Z_BEAM1 + 1, 30.4)).cut(cyl_z(0, 0, Z_BEAM0 - 1, 129, 28.0))  # head bore above a ledge, carrier hole below
    gantry = gantry.cut(box(12, 28, -8, 8, 128, Z_BEAM1 + 1))  # pocket for the lever tab: +-8 mm, room for the head's +-5 degrees
    for sy in (1, -1):  # two push-push adjusting screws on the +x extension, tips reaching the tab; nuts captured in the outer faces
        gantry = gantry.cut(cyl_y(24, 133, *sorted((sy * 7.9, sy * (HEAD_BOSS_Y + 0.1))), M3_CLEAR)).cut(nut_pocket_y(24, 133, sy * HEAD_BOSS_Y, -sy))
        FASTENERS.append(("M3x14 pan head screw", "torsion head adjusting screw"))
        FASTENERS.append(("M3 nut", "torsion head adjusting screw, captured in the gantry"))
        FASTENERS.append(("M3 flat washer", "torsion head adjusting screw"))
    gantry = with_foot(gantry, -16, 16, 39, 51, [(-11, 45), (11, 45)], base_holes, "gantry leg +y")
    gantry = with_foot(gantry, -16, 16, -51, -39, [(-11, -45), (11, -45)], base_holes, "gantry leg -y")
    add("gantry", gantry, pla, False, True)
    # the torsion head: a disc in the bore, a carrier block hanging below it holding the upper clamp plates, and the lever tab
    head = cyl_z(0, 0, 128, 136, 30.0).union(box(10, HEAD_TAB_R, -HEAD_TAB_W / 2, HEAD_TAB_W / 2, 128, 136)).union(box(-10, 10, -8, 8, Z_UP0 - 2.0, 128))
    head = head.cut(box(-9.5, 9.5, -4.0, 4.6, Z_UP0 - 3.0, Z_UP1 + 1.0))  # slot for the plate stack, open at the bottom
    head = head.cut(box(-9.5, 9.5, -4.0, 4.6, Z_UP0 - 3.0, Z_UP1 + 1.0))
    for x in (-5.0, 5.0):
        head = head.cut(cyl_y(x, (Z_UP0 + Z_UP1) / 2, -9, -3.9, M3_CLEAR))  # the bolts' tips hang in the -y wall
    add("head", head, pla, False, True)
    for name, (y0, y1) in (("clamp_up_a", (YB0, YB1)), ("clamp_up_b", (YP0, YP1))):
        plate = box(-8, 8, y0, y1, Z_UP0, Z_UP1)
        if name == "clamp_up_b":
            plate = plate.union(box(3, 9, y0, y1, Z_UP0 - 5, Z_UP0))  # a tab with a 1.6 mm plated hole for the ground wire, clear of the strip
            plate = plate.cut(cyl_y(6, Z_UP0 - 2.5, y0 - 1, y1 + 1, 1.6))
        for x in (-5.0, 5.0):
            plate = plate.cut(cyl_y(x, (Z_UP0 + Z_UP1) / 2, y0 - 1, y1 + 1, M3_CLEAR))
        add(name, plate, FR4_G_MM3, False)
    for x in (-5.0, 5.0):  # head + washer on the +y plate, nut on the -y plate: the preload loop is the two plates and the strip
        FASTENERS.append(("M3x10 pan head screw", "upper strip clamp bolt"))
        FASTENERS.append(("M3 flat washer", "upper strip clamp bolt"))
        FASTENERS.append(("M3 nut", "upper strip clamp bolt (carbon steel is fine: it does not move)"))

    # sensor bracket: a column and two prongs 3 mm either side of the flag finger, boards for the LED and photodiode on the tips
    bx0, bx1 = -L - 12, -L - 2
    bracket = box(bx0, bx1, 36, 44, 6, Z_V + 12).union(box(bx0, bx1, -3.5, 44, Z_V - 4 - 3 - 3, Z_V - 4 - 3)).union(box(bx0, bx1, -3.5, 44, Z_V + 4 + 3, Z_V + 4 + 3 + 3))
    bracket = with_foot(bracket, bx0, bx1, 26, 54, [(0.5 * (bx0 + bx1), 31), (0.5 * (bx0 + bx1), 49)], base_holes, "sensor_bracket")
    add("sensor_bracket", bracket, pla, False, True)

    # damper: four N42 discs on edge (two above the vane, two below) in cradles whose windows hold them in; one printed holder
    axial = P.MAGNET_MAGNETIZATION == "axial"
    gz = (P.MAGNET_GAP + (P.MAGNET_LIP if axial else 0.0)) * MM  # vane mid-plane to the nearest disc surface
    dd = P.N42_DIAMETER * MM
    dh = P.N42_THICKNESS * MM
    my = P.MAGNET_Y * MM
    mxs = [x * MM for x in P.MAGNET_X]
    zl, zu = (Z_V - (gz + dh / 2), Z_V + (gz + dh / 2)) if axial else (Z_V - (gz + dd / 2), Z_V + (gz + dd / 2))  # disc centre heights
    dhold = box(X_VANE - 8, X_VANE + 8, 36, 44, 6, Z_V + 12)
    if axial:
        # flat discs facing the vane, each in a round pocket open at its far face (a tape cap holds it) with a 0.6 mm lip round a 4.6 mm window
        lip_t = P.MAGNET_LIP * MM
        low_slab = box(X_VANE - 8, X_VANE + 8, my - 4.0, 44, zl - dh / 2 - 4.0, Z_V - gz + lip_t)
        up_slab = box(X_VANE - 8, X_VANE + 8, my - 4.0, 44, Z_V + gz - lip_t, zu + dh / 2 + 4.0)
        for xc in mxs:
            low_slab = low_slab.cut(cyl_z(xc, my, zl - dh / 2 - 5, Z_V - gz, dd + 0.2)).cut(cyl_z(xc, my, Z_V - gz - 0.01, Z_V - gz + lip_t + 1, 4.6))
            up_slab = up_slab.cut(cyl_z(xc, my, Z_V + gz, zu + dh / 2 + 5, dd + 0.2)).cut(cyl_z(xc, my, Z_V + gz - lip_t - 1, Z_V + gz + 0.01, 4.6))
    else:
        # four discs on edge in cradles whose windows hold them in (a 4.5 mm window in the bore's wall holds a 6 mm disc)
        lip = math.sqrt((dd / 2 + 0.1) ** 2 - 2.25**2)
        low_slab = box(X_VANE - 8, X_VANE + 8, my - 4.0, 44, zl - 5.5, zl + lip)
        up_slab = box(X_VANE - 8, X_VANE + 8, my - 4.0, 44, zu - lip, zu + 5.5)
        for xc in mxs:
            low_slab = low_slab.cut(cyl_x(my, zl, xc - dh / 2 - 0.1, xc + dh / 2 + 4, dd + 0.2))
            up_slab = up_slab.cut(cyl_x(my, zu, xc - dh / 2 - 0.1, xc + dh / 2 + 4, dd + 0.2))
            low_slab = low_slab.cut(box(xc - dh / 2 - 0.1, xc + dh / 2 + 4, my - 2.25, my + 2.25, zl, zl + lip + 1))
            up_slab = up_slab.cut(box(xc - dh / 2 - 0.1, xc + dh / 2 + 4, my - 2.25, my + 2.25, zu - lip - 1, zu))
    dhold = dhold.union(low_slab).union(up_slab)
    dhold = with_foot(dhold, X_VANE - 8, X_VANE + 8, 26, 54, [(X_VANE, 31), (X_VANE, 49)], base_holes, "damper_holder")
    add("damper_holder", dhold, pla, False, True)
    for i, xc in enumerate(mxs):
        for tag, zc in (("low", zl), ("up", zu)):
            add(f"magnet_{tag}_{i}", cyl_z(xc, my, zc - dh / 2, zc + dh / 2, dd) if axial else cyl_x(my, zc, xc - dh / 2, xc + dh / 2, dd), ND_G_MM3, False)

    # the fixed calibration electrode: an FR4 board 1.0 mm from the arm board's +y face, taped to a printed bracket whose feet slide on
    # oversize holes (so the gap is set after the head has zeroed the arm)
    eb0 = YB1 + P.PLATE_GAP * MM  # the board's front (pad) face
    ebx0, ebx1 = X_PLATE - 12, X_PLATE + 12
    ez0, ez1 = Z_V - 12, Z_V + 12
    eboard = box(ebx0, ebx1, eb0, eb0 + BT, ez0, ez1 + 10)  # 10 mm of tab above the bracket for the two wire holes
    for x in (X_PLATE - 6, X_PLATE + 6):
        eboard = eboard.cut(cyl_y(x, ez1 + 5, eb0 - 1, eb0 + BT + 1, 1.6))
    add("elec_board", eboard, FR4_G_MM3, False)
    ebr = box(ebx0 - 2, ebx1 + 2, eb0 + BT, eb0 + BT + 8, 6, ez1).union(box(ebx0 - 2, ebx0, eb0, eb0 + BT, ez0 - 1, ez1)).union(box(ebx1, ebx1 + 2, eb0, eb0 + BT, ez0 - 1, ez1))
    ebr = ebr.union(box(ebx0 - 2, ebx1 + 2, eb0, eb0 + BT, ez0 - 1.5, ez0))  # shelf under the board
    ebr = with_foot(ebr, ebx0 - 2, ebx1 + 2, eb0 + BT, eb0 + BT + 18, [(X_PLATE - 8, eb0 + BT + 9), (X_PLATE + 8, eb0 + BT + 9)], base_holes, "electrode bracket", slack=True)
    add("elec_bracket", ebr, pla, False, True)

    # the base, with a clearance hole under every foot (and a nut pocket in its underside where a foot's screw comes from above)
    base = box(-BASE_HALF, BASE_HALF, -BASE_HALF, BASE_HALF, 0, 6)
    for (hx, hy, kind) in base_holes:
        base = base.cut(cyl_z(hx, hy, -0.1, 6.1, M3_CLEAR))
        if kind == "nut_below":
            base = base.cut(nut_pocket_z(hx, hy, NUT_DEPTH))
    add("base", base, pla, False, True)

    # ---- enclosure: four corner posts with slots, four identical pinwheel walls (uncut stock sheets), a two-sheet lid ----
    wi, di, hi = (v * MM for v in P.ENCL_INNER)
    t = P.PANEL_T * MM
    slot_clear = 2 * P.SEAL_T * MM + 0.2  # total slack across the wall: the foam shim on both faces plus 0.2 mm
    hx, hy = wi / 2, di / 2
    panels = {
        "panel_py": box(-hx, hx + t, hy, hy + t, 0, hi),
        "panel_px": box(hx, hx + t, -hy - t, hy, 0, hi),
        "panel_ny": box(-hx - t, hx, -hy - t, -hy, 0, hi),
        "panel_nx": box(-hx - t, -hx, -hy, hy + t, 0, hi),
    }
    lid_x = P.PANEL_STOCK[0] * MM / 2
    lid_w = P.PANEL_STOCK[1] * MM
    lids = {"encl_lid_a": box(-lid_x, lid_x, 0, lid_w, hi, hi + t), "encl_lid_b": box(-lid_x, lid_x, -lid_w, 0, hi, hi + t)}
    pw = P.ENCL_POST * MM
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = sx * (hx + t / 2), sy * (hy + t / 2)
            post = box(cx - pw / 2, cx + pw / 2, cy - pw / 2, cy + pw / 2, 0, hi)
            for pn, pnl in panels.items():
                bb = pnl.val().BoundingBox()
                grown = box(bb.xmin - slot_clear / 2, bb.xmax + slot_clear / 2, bb.ymin - slot_clear / 2, bb.ymax + slot_clear / 2, bb.zmin - 1, bb.zmax + 1)
                post = post.cut(grown)
            add(f"encl_post_{'p' if sx > 0 else 'n'}{'p' if sy > 0 else 'n'}", post, pla, False, True)
    seat = P.LID_SEAT * MM
    for sx in (1, -1):
        for k, (y0, y1) in enumerate(((-(hy - 10 + 1), -1.0), (1.0, hy - 10 + 1))):
            xa, xb = (hx - seat, hx) if sx > 0 else (-hx, -hx + seat)
            add(f"encl_shelf_{'p' if sx > 0 else 'n'}x_{k}", box(xa, xb, y0, y1, hi - 6, hi), pla, False, True)
    for pn, pnl in panels.items():
        add(pn, pnl, ACRYLIC_G_MM3, False, False)
    for ln, lid in lids.items():
        add(ln, lid, ACRYLIC_G_MM3, False, False)
    return parts


def balance_solve():
    """Ballast length and position along y (mm) that put the moving centre of mass on the z axis. The rod hangs at a fixed x, so its length
    balances the x moment of everything else and its y position cancels the y moment: no search over rebuilt solids is needed."""
    bl, by = 10.0, 0.0
    rho_b = BRASS_G_MM3 * math.pi * 25  # g per mm of rod, diameter 10
    for _ in range(3):
        parts = build(bl, by)
        mx = my = 0.0
        for name, (wp, rho, moving, _) in parts.items():
            if not moving or name == "ballast":
                continue
            s_ = wp.val()
            m = s_.Volume() * rho
            c = s_.Center()
            mx += m * c.x
            my += m * c.y
        bl = mx / (rho_b * -X_BALLAST)
        by = -my / (rho_b * bl)
    return bl, by


def moving_properties(parts):
    """Mass (g), centre of mass (mm) and moment of inertia about the z axis (kg*m^2) of the moving assembly."""
    m_tot = 0.0
    cx = cy = cz = 0.0
    props = []
    for name, (wp, rho, moving, _) in parts.items():
        if not moving:
            continue
        s = wp.val()
        v = s.Volume()
        c = s.Center()
        m = v * rho
        icom = cq.Shape.matrixOfInertia(s)  # per unit density, about the part's own centre of mass
        izz = (icom[2][2] * rho + m * (c.x**2 + c.y**2)) * 1e-9  # g*mm^2 -> kg*m^2
        props.append((name, m, izz))
        m_tot += m
        cx += m * c.x
        cy += m * c.y
        cz += m * c.z
    return m_tot, (cx / m_tot, cy / m_tot, cz / m_tot), sum(p[2] for p in props), props


def _disjoint(ba, bb):
    return ba.xmax < bb.xmin or ba.xmin > bb.xmax or ba.ymax < bb.ymin or ba.ymin > bb.ymax or ba.zmax < bb.zmin or ba.zmin > bb.zmax


def interference(parts, angles_deg=(-1.5, 0, 1.5), skip_pairs=(("arm", "elec_board"), ("arm", "elec_bracket"), ("hw_dut", "elec_bracket")),
                 narrow=(("arm", "elec_board", 0.4), ("arm", "elec_bracket", 0.4), ("hw_dut", "elec_bracket", 0.4))):
    """Largest overlap volume (mm^3) between any moving part and any fixed part over the arm's swing. The head and upper clamp plates are
    fixed here; their own +-5 degree range is checked separately. Only parts that are close are tested pairwise (a bounding-box prefilter)."""
    worst = (0.0, None)
    fixed = [(n, p[0].val()) for n, p in parts.items() if not p[2]]
    for ang in angles_deg:
        for n, (wp, _, moving, _) in parts.items():
            if not moving or n == "strip":
                continue
            s = wp.val().rotate((0, 0, 0), (0, 0, 1), ang)
            bb = s.BoundingBox()
            for fn, fs in fixed:
                if (n, fn) in skip_pairs:
                    continue
                if _disjoint(bb, fs.BoundingBox()):
                    continue
                vol = s.intersect(fs).Volume()
                if vol > worst[0]:
                    worst = (vol, (n, fn, ang))
    # the electrode pair has a 1 mm gap, so its swing limit is narrower than the rest
    for a, b, lim in narrow:
        for ang in (-lim, lim):
            s = parts[a][0].val().rotate((0, 0, 0), (0, 0, 1), ang)
            vol = s.intersect(parts[b][0].val()).Volume()
            if vol > worst[0]:
                worst = (vol, (a, b, ang))
    return worst


def head_range_clearance(parts, deg=5.0):
    """Overlap volume (mm^3) between the torsion head (rotated +-deg, with the clamp plates it carries) and the gantry."""
    worst = 0.0
    for ang in (-deg, deg):
        for n in ("head",):
            s = parts[n][0].val().rotate((0, 0, 0), (0, 0, 1), ang)
            worst = max(worst, s.intersect(parts["gantry"][0].val()).Volume())
    return worst


def fixed_overlaps(parts):
    """Overlap volumes between fixed parts that are not meant to merge."""
    names = [n for n, p in parts.items() if not p[2]]
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            va, vb = parts[a][0].val(), parts[b][0].val()
            if _disjoint(va.BoundingBox(), vb.BoundingBox()):
                continue
            vol = va.intersect(vb).Volume()
            if vol > 1e-3:
                bad.append((a, b, round(vol, 3)))
    return bad


def moving_internal_overlaps(parts):
    """Overlap volumes between moving parts that are not meant to merge."""
    names = [n for n, p in parts.items() if p[2]]
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            va = parts[a][0].val()
            vb = parts[b][0].val()
            if _disjoint(va.BoundingBox(), vb.BoundingBox()):
                continue
            vol = va.intersect(vb).Volume()
            if vol > 1e-3:
                bad.append((a, b, vol))
    return bad


def enclosure_clearance(parts):
    """Smallest gap (mm) between any balance part (everything not part of the enclosure) and the enclosure's clear volume's walls."""
    wi, di, hi = (v * MM for v in P.ENCL_INNER)
    gap = 1e9
    for n, (wp, _, _, _) in parts.items():
        if n.startswith(("panel_", "encl_")):
            continue
        bb = wp.val().BoundingBox()
        gap = min(gap, wi / 2 - bb.xmax, wi / 2 + bb.xmin, di / 2 - bb.ymax, di / 2 + bb.ymin, hi - bb.zmax)
    return gap


def printability(parts):
    rows = []
    for name, (wp, _, _, printed) in parts.items():
        if not printed:
            continue
        bb = wp.val().BoundingBox()
        dims = sorted((bb.xlen, bb.ylen, bb.zlen), reverse=True)
        fits = bb.xlen <= P.PRINT_VOLUME[0] * MM and bb.ylen <= P.PRINT_VOLUME[1] * MM and bb.zlen <= P.PRINT_VOLUME[2] * MM
        rows.append((name, dims, fits))
    return rows


def fastener_totals():
    """{kind: count} from the holes the CAD cut."""
    totals = {}
    for kind, _ in FASTENERS:
        totals[kind] = totals.get(kind, 0) + 1
    return totals


def panel_cut_list(parts):
    """Acrylic panels to buy: {(w, h, t): count}, in mm."""
    out = {}
    for n, (wp, _, _, printed) in parts.items():
        if n.startswith(("panel_", "encl_lid")):
            bb = wp.val().BoundingBox()
            dims = sorted((round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)), reverse=True)
            out[tuple(dims)] = out.get(tuple(dims), 0) + 1
    return out


def export(parts):
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):  # drop STLs of parts that no longer exist
        if f.endswith(".stl") and not f.startswith("fixture_") and f[:-4] not in parts:
            os.remove(os.path.join(OUT, f))
    asm = cq.Assembly(name="balance")
    for name, (wp, _, moving, _) in parts.items():
        cq.exporters.export(wp, os.path.join(OUT, f"{name}.stl"))
        asm.add(wp, name=name)
    asm.save(os.path.join(OUT, "balance.step"))


def main():
    bl, by = balance_solve()
    print(f"balance: brass ballast {bl:.1f} mm long, centred {by:+.2f} mm along y")
    parts = build(bl, by)
    m, com, izz, props = moving_properties(parts)
    print(f"moving mass {m:.1f} g (params: {1e3*P.MOVING_MASS:.1f} g), centre of mass ({com[0]:.2f}, {com[1]:.2f}, {com[2]:.1f}) mm, "
          f"hangs {Z_STRIP0 + CLAMP_H - com[2]:.1f} mm below the strip's lower end")
    print(f"moment of inertia about z {izz:.3e} kg*m^2 (params {P.MOVING_INERTIA:.3e})")
    for name, mm, ii in sorted(props, key=lambda a: -a[2]):
        print(f"  {name:14s} {mm:6.2f} g  {ii:.2e} kg*m^2")
    print("worst overlap with the fixed structure over +-1.5 deg:", interference(parts))
    print("torsion head +-5 deg against the gantry (mm^3):", head_range_clearance(parts))
    print("moving-part overlaps:", moving_internal_overlaps(parts))
    print("fixed-part overlaps:", fixed_overlaps(parts))
    print(f"enclosure clearance: {enclosure_clearance(parts):.1f} mm")
    print("fasteners:", fastener_totals())
    print("acrylic cut list (w x h x t mm: count):", panel_cut_list(parts))
    for name, dims, fits in printability(parts):
        print(f"  {name:16s} {dims[0]:.0f} x {dims[1]:.0f} x {dims[2]:.0f} mm  {'fits' if fits else 'TOO BIG'}")
    export(parts)
    print("exported to", OUT)


if __name__ == "__main__":
    main()
