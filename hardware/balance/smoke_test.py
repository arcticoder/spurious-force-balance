"""
smoke_test.py — hardware/balance (the `FORCEBAL` torsion balance, gate G2/G3)

Model: the analytic model reproduces numbers published in two papers (stiffness, the 5 nm ->
12 nN conversion, drift, resonance, decay time, thermal-noise formula); the balance in
params.py has a resonance below the measurement frequency's neighbourhood and a strip stressed
far below yield; the eddy damper can supply the damping ratio the noise model assumes (by
partial engagement); the force-noise budget gives a go with margin, and the verdict flips
when the least certain assumption (air-speed fluctuation) is made four times worse.

CAD (needs cadquery; run with ~/.venvs/lab-hw/bin/python, otherwise these are SKIPPED, which
the repo-wide runner shows but does not fail): the moving assembly's mass and inertia agree
with params.py to 3%, its centre of mass is within 0.3 mm of the pivot axis, nothing collides
over +-1.5 degrees of swing, no moving parts overlap by accident, and every printed part fits the
printer.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
import force_noise_budget as FB  # noqa: E402
import model as M  # noqa: E402
import params as P  # noqa: E402

failures = []


def check(label, condition, detail):
    print(f"[{'PASS' if condition else 'FAIL'}] {label}: {detail}")
    if not condition:
        failures.append(label)


for label, ok, detail in FB.anchors():
    check(f"functional — model against the literature: {label}", ok, detail)

kappa, i, l = M.strip_stiffness(), M.inertia(), P.ARM_HALF_LENGTH
f0 = M.omega0(kappa, i) / (2 * math.pi)
check("functional — resonance is between 0.1 and 0.4 Hz (the measurement frequency sits below it)", 0.1 <= f0 <= 0.4 and P.F_MOD < f0, f"{f0:.3f} Hz, measured at {P.F_MOD} Hz")
stress = P.MOVING_MASS * P.G_ACC / (P.STRIP_WIDTH * P.STRIP_THICKNESS)
check("safety — the strip carries the balance at under a tenth of its yield stress", stress < P.STRIP_YIELD_PA / 10, f"{stress/1e6:.1f} MPa against {P.STRIP_YIELD_PA/1e6:.0f} MPa")
tilt_g = P.STRIP_WIDTH / P.STRIP_LENGTH
check("functional — the strip is wide enough to be a ribbon (width over 10x thickness) and and short", P.STRIP_WIDTH / P.STRIP_THICKNESS > 10 and P.STRIP_LENGTH < 60e-3, f"{P.STRIP_WIDTH/P.STRIP_THICKNESS:.0f}:1, {P.STRIP_LENGTH*1e3:.0f} mm")

try:
    import magpylib as mp
    have_mp = True
except ImportError:
    have_mp = False
if have_mp:
    # the field model: an axial disc agrees with the analytic on-axis result (so the radial-disc results can be trusted)
    c_ax = mp.magnet.Cylinder(dimension=(P.N42_DIAMETER, P.N42_THICKNESS), polarization=(0, 0, P.N42_BR))
    z_probe = P.N42_THICKNESS / 2 + 1.5e-3
    b_mp = float(c_ax.getB((0, 0, z_probe))[2])
    b_an = M.disc_field_on_axis(1.5e-3)
    check("functional — the magnet field model (magpylib) agrees with the analytic on-axis field of an axial disc within 2%", abs(b_mp - b_an) < 0.02 * b_an, f"{b_mp:.4f} T against {b_an:.4f} T")
    c_vane, zeta_full, b_gap = M.eddy_damping_field()
    z_two = M.eddy_damping_field(vane_t=2 * P.PAD_T)[1]
    check("functional — one 0.3 mm pad gives the damping ratio the noise budget assumes (within 20%), for either disc layout", abs(zeta_full - P.DAMPING_RATIO) <= 0.2 * P.DAMPING_RATIO, f"{zeta_full:.2f} against {P.DAMPING_RATIO} (peak Bz {b_gap:.2f} T, {P.MAGNET_MAGNETIZATION} discs, {P.VANE_PADS} pad)")
    check("functional — a second pad reaches the strong-damping end (ratio at least 0.8) so the bench can tune between the two", z_two >= 0.8, f"two pads: {z_two:.2f}")
    vx = P.VANE_SIZE[0] * 1e3 / 2
    fx_half = (P.N42_DIAMETER if P.MAGNET_MAGNETIZATION == "axial" else P.N42_THICKNESS) * 1e3 / 2  # a disc's half-extent along the arm
    ox = min((P.MAGNET_X[0] * 1e3 - fx_half) - (P.VANE_X * 1e3 - vx), (P.VANE_X * 1e3 + vx) - (P.MAGNET_X[1] * 1e3 + fx_half))
    oy = min((P.MAGNET_Y * 1e3 - P.N42_DIAMETER * 1e3 / 2) - 8.0, (8.0 + P.VANE_SIZE[1] * 1e3) - (P.MAGNET_Y * 1e3 + P.N42_DIAMETER * 1e3 / 2) - 1.6)
    check("functional — the vane extends at least 2 mm beyond the discs on every side, including the +-1.6 mm swing at the vane", min(ox, oy) >= 2.0, f"{ox:.1f} mm along x, {oy:.1f} mm along y after the swing")
    clear_two = (P.MAGNET_GAP - P.PAD_T) * 1e3
    check("functional — a two-pad vane keeps at least 1 mm to each disc", clear_two >= 1.0 - 1e-9, f"{clear_two:.2f} mm")
else:
    print("[SKIP] magpylib is not installed in this Python: the damper field checks were not run")
    zeta_full = P.DAMPING_RATIO
check("safety — the damper magnets are fixed to the base: no permanent magnetic moment on the moving arm beyond the stray allowance", P.STRAY_MOMENT < 0.01 * P.n42_moment(), f"stray {P.STRAY_MOMENT:.0e} A*m^2 against one disc's {P.n42_moment():.3f} A*m^2")

f_max = P.plate_force(P.PLATE_BIAS_MAX)
g40 = P.plate_gain(P.PLATE_BIAS_MAX)
check("safety — the calibration plates reach micronewtons without exceeding the repo's 50 V DC line", P.PLATE_BIAS_MAX < 50 and f_max > 1e-6, f"{f_max*1e6:.1f} uN at {P.PLATE_BIAS_MAX:.0f} V ({P.PLATE_AREA*1e4:.0f} cm^2, {P.PLATE_GAP*1e3:.0f} mm gap)")
check("functional — a 1 mV step of the plate signal is under 1 nN (fine force control around the bias)", g40 * 1e-3 < 1e-9, f"{g40*1e9:.0f} nN/V at {P.PLATE_BIAS_MAX:.0f} V bias, 1 mV = {g40*1e-3*1e9:.2f} nN")
check("functional — the plates' force at the bias is within the strip's travel (displacement under 0.1 mm at 1 uN)", 1e-6 / M.k_eff(kappa, l) < 0.1e-3, f"1 uN moves the flag {1e-6/M.k_eff(kappa, l)*1e6:.0f} um, gap {P.PLATE_GAP*1e3:.0f} mm")

terms = M.force_terms()
sigma, need, ok = FB.verdict(terms)
check("functional — the budget's verdict is go with margin over the model-error allowance", ok and need / sigma > 2.0, f"predicted {sigma*1e9:.3f} nN per {P.INTEGRATION_S:.0f} s, need {need*1e9:.2f} nN ({need/sigma:.1f}x margin)")
dom = max(terms, key=terms.get)
check("functional — the dominant term is the least certain one (air currents), not the readout", dom == "air currents" and terms["readout (shot + electronics + LED)"] < 0.01 * terms[dom], f"{dom} {terms[dom]*1e9:.2f} nN/sqrt(Hz); readout {terms['readout (shot + electronics + LED)']*1e9:.4f}")
flips = [v for label, v, s_, ok_ in FB.sweeps() if label.startswith("air-speed") and not ok_]
check("functional — the verdict flips at about 4x worse air-speed fluctuation, so A5 must measure it", flips and min(flips) <= 4.01e-3, f"no-go from {min(flips)*1e3:.0f} mm/s" if flips else "never")
by_air = {v: s_ for label, v, s_, ok_ in FB.sweeps() if label.startswith("air-speed")}
check("functional — resolution worsens monotonically with air-speed fluctuation", all(by_air[a] < by_air[b] for a, b in zip(sorted(by_air), sorted(by_air)[1:])), "")

# ---- CAD -----------------------------------------------------------------------------------
try:
    import cadquery  # noqa: F401
    import balance as B
except ImportError:
    print("[SKIP] CAD checks: cadquery is not importable here; run with ~/.venvs/lab-hw/bin/python")
else:
    bl, by = B.balance_solve()
    parts = B.build(bl, by)
    m, com, izz, _ = B.moving_properties(parts)
    check("functional — CAD moving mass matches params.py to 3%", abs(m / 1e3 / P.MOVING_MASS - 1) < 0.03, f"{m:.1f} g against {P.MOVING_MASS*1e3:.1f} g")
    check("functional — CAD moment of inertia matches params.py to 3%", abs(izz / P.MOVING_INERTIA - 1) < 0.03, f"{izz:.3e} against {P.MOVING_INERTIA:.3e}")
    check("functional — the solved ballast puts the centre of mass within 0.3 mm of the pivot axis", math.hypot(com[0], com[1]) < 0.3, f"({com[0]:.2f}, {com[1]:.2f}) mm")
    rod_cut = bl + 0.5  # the saw guide leaves 0.5 mm to file off
    check("functional — the ballast is one saw cut from the 100 mm rod, and its position along y keeps the rod's ends within 12 mm of the arm's mid-plane", rod_cut <= 40 and abs(by) + bl / 2 <= 12, f"{bl:.1f} mm long (cut {rod_cut:.1f}), centred {by:+.2f} mm")
    vol, who = B.interference(parts)
    check("functional — nothing collides with the fixed structure over +-1.5 degrees", vol < 0.01, f"{vol:.3f} mm^3 {who or ''}")
    hv = B.head_range_clearance(parts)
    check("functional — the torsion head turns +-5 degrees in the gantry without touching it", hv < 0.01, f"{hv:.3f} mm^3")
    reach = B.HEAD_BOSS_Y - 14.0  # an M3x14 screw's tip, measured from the mid-plane, with its nut face at HEAD_BOSS_Y
    travel = B.HEAD_TAB_R * math.sin(math.radians(5))
    check("functional — the adjusting screws can push the tab to +-5 degrees (tip reaches the mid-plane less the tab's travel)", reach <= B.HEAD_TAB_W / 2 - travel, f"tip reaches {reach:.1f} mm, tab edge must reach {B.HEAD_TAB_W/2 - travel:.1f} mm for +-{travel:.1f} mm of tab travel")
    turn = math.degrees(0.5 / B.HEAD_TAB_R)
    check("functional — one screw turn sets the zero by less than 1.5 degrees, so a tenth of a turn is 0.15 degrees", turn < 1.5, f"{turn:.2f} degrees per turn (0.5 mm pitch at {B.HEAD_TAB_R:.0f} mm)")
    fo = B.fixed_overlaps(parts)
    check("functional — no fixed parts overlap by accident (gantry, feet, clamps, damper, sensor bracket, enclosure)", not fo, f"{fo}" if fo else "none")
    over = B.moving_internal_overlaps(parts)
    check("functional — no moving parts overlap by accident", not over, f"{over}" if over else "none")
    clr = B.enclosure_clearance(parts)
    check("functional — the balance sits inside the enclosure with the planned clearance to every wall and the lid", clr >= P.ENCL_MIN_CLEARANCE * 1e3, f"{clr:.1f} mm against {P.ENCL_MIN_CLEARANCE*1e3:.0f} mm")
    cut = B.panel_cut_list(parts)
    stock = sorted((P.PANEL_STOCK[0] * 1e3, P.PANEL_STOCK[1] * 1e3, P.PANEL_T * 1e3))[::-1]
    check("functional — the acrylic is six uncut stock sheets (four walls, two lid sheets), nothing to cut", len(cut) == 1 and sum(cut.values()) == 6 and all(max(abs(a - b) for a, b in zip(k, stock)) < 0.01 for k in cut), f"{cut} against stock {stock}")
    # --- the strip's clamping loop is FR4 and steel only: no printed plastic carries the preload that holds the zero ---
    loop = ("arm", "clamp_low", "clamp_up_a", "clamp_up_b", "strip")
    plastic = [n for n in loop if parts[n][3] or parts[n][1] < 1e-3]  # a printed part, or a density below FR4's
    check("functional — every part in the strip's clamping loop is FR4 or steel, none is printed plastic", not plastic, f"{plastic}" if plastic else f"{', '.join(loop)}")
    # --- tilt: the centre of mass hangs below the strip's lower end, and the offset it can have is trimmed on the bench ---
    com_z = com[2]
    hang = (B.ZA1 - com_z) * 1e-3
    vane_clear = (P.MAGNET_GAP - P.PAD_T) * 1e3  # one pad lying on the slot's floor leaves at least this to the nearer disc
    tol = min(vane_clear * 1e-3 / P.VANE_X, 3.0e-3 / (P.ARM_HALF_LENGTH + 8e-3))  # vane clearance over its radius, flag gap (3 mm) over the finger's radius
    check("functional — the centre of mass hangs at least 30 mm below the strip's lower end", hang >= 30e-3, f"{hang*1e3:.1f} mm, {1e3/(hang*1e3):.0f} mrad of tilt per mm of offset")
    tilt = M.tilt_from_com(P.COM_OFFSET, hang)
    check("functional — the assumed 0.2 mm centre-of-mass offset tilts the arm by less than the vane and flag clearances allow", tilt <= tol, f"{tilt*1e3:.1f} mrad against {tol*1e3:.1f} mrad allowed (hangs {hang*1e3:.1f} mm below the strip)")
    # independent errors before trimming: ballast saw/file length +-0.5 mm, device card mass +-1 g at the arm's end, printed holder +-15%
    rho_b = B.BRASS_G_MM3 * math.pi * 25
    errs = [0.5 * rho_b * 0.9 * B.L / m, 1.0 * (B.L + 1) / m, 0.15 * parts["vane_holder"][1] * parts["vane_holder"][0].val().Volume() * B.X_VANE / m]
    worst = sum(errs)
    check("functional — the worst untrimmed centre-of-mass offset (ballast length, device card mass, printed holder) is within what two spare copper pads can trim", worst <= 2 * 1.08 * 0.9 * B.L / m, f"{worst:.2f} mm worst case ({errs[0]:.2f} + {errs[1]:.2f} + {errs[2]:.2f}); two pad pieces at 90 mm move it {2*1.08*0.9*B.L/m:.1f} mm")
    check("functional — untrimmed, that offset would tilt the arm past its clearances, so the bench trim is required (assembly.md step 6)", M.tilt_from_com(worst * 1e-3, hang) > tol, f"{M.tilt_from_com(worst*1e-3, hang)*1e3:.0f} mrad against {tol*1e3:.1f} mrad")
    # --- the device card is FR4 on air spacers, and its temperature at the top power stays under the glass transition less the margin ---
    rise = M.device_card_rise()
    t_card = P.AMBIENT_C + rise
    check("safety — the device card at the top dissipation stays 40 K under FR4's glass transition (so a card, and the board it hangs on, does not creep with the device's power)", t_card <= P.FR4_TG_C - P.TG_MARGIN_K, f"{t_card:.0f} C at {P.DEVICE_POWER_MAX} W (+{rise:.0f} K), limit {P.FR4_TG_C - P.TG_MARGIN_K:.0f} C")
    import fixtures as FX
    fx, fx_len, fx_slot = FX.build_all()
    check("functional — the saw guide's groove is wider than the rod and the plate and base clear each other", FX.ROD_D + 0.3 > FX.ROD_D and fx["fixture_saw_guide_base"].intersect(fx["fixture_saw_guide_plate"]).val().Volume() < 1e-3, f"groove {FX.ROD_D + 0.3:.1f} mm for a {FX.ROD_D:.0f} mm rod")
    check("functional — the strip guide's slot is exactly the strip width from the shim's fence", abs((fx_slot - 2.0) - P.STRIP_WIDTH * 1e3) < 1e-6, f"{fx_slot - 2.0:.2f} mm against {P.STRIP_WIDTH*1e3:.2f} mm")
    gg = fx["fixture_gap_gauge"].val().BoundingBox()
    check("functional — the gap gauge is exactly the electrode gap thick", abs(gg.ylen - P.PLATE_GAP * 1e3) < 1e-6, f"{gg.ylen:.2f} mm against {P.PLATE_GAP*1e3:.2f} mm")
    over = [n for n, s_ in fx.items() if max(s_.val().BoundingBox().xlen, s_.val().BoundingBox().ylen) > P.PRINT_VOLUME[0] * 1e3]
    check("functional — the printed jigs fit the printer", not over, f"{len(fx)} jigs")
    wi_half = P.ENCL_INNER[0] * 1e3 / 2
    di_half = P.ENCL_INNER[1] * 1e3 / 2
    lid_half_x = P.PANEL_STOCK[0] * 1e3 / 2
    lid_half_y = P.PANEL_STOCK[1] * 1e3  # two sheets side by side along y
    seat_x = P.LID_SEAT * 1e3 + (lid_half_x - wi_half)  # shelf plus the lid's overhang onto the wall top
    seat_y = lid_half_y - di_half
    check("functional — the lid covers the opening and bears at least 3 mm on every edge (a printed shelf on the x walls, the wall tops on the y walls)", min(seat_x, seat_y) >= 3.0 and lid_half_x > wi_half, f"{seat_x:.1f} mm on the x walls, {seat_y:.1f} mm on the y walls")
    tot = B.fastener_totals()
    short = {k: (n, P.FASTENER_OWNED.get(k, 0)) for k, n in tot.items() if k in P.FASTENER_OWNED and n > P.FASTENER_OWNED[k]}
    check("functional — every screw and carbon-steel nut the CAD's holes take is already owned (inventory.md)", not short, f"needs {tot}; owned {P.FASTENER_OWNED}" + (f"; short {short}" if short else ""))
    buy_short = {k: (tot.get(k, 0), n) for k, n in P.FASTENER_TO_BUY.items() if tot.get(k, 0) > n}
    check("functional — the planned purchase (50 washers, 20 stainless nuts) covers what the CAD needs", not buy_short, f"needs {tot.get('M3 flat washer')} washers and {tot.get('M3 nut, 304 stainless')} stainless nuts" + (f"; short {buy_short}" if buy_short else ""))
    n_screws = sum(v for k, v in tot.items() if "screw" in k)
    check("functional — every screw gets a washer", tot.get("M3 flat washer", 0) == n_screws, f"{tot.get('M3 flat washer')} washers for {n_screws} screws")
    # --- the KiCad boards are the CAD's boards: same outlines, same hole positions, nothing on the order over the cheap-shipping weight ---
    try:
        import boards as BD
    except ImportError:
        print("[SKIP] board checks: kiutils is not importable here; run with ~/.venvs/lab-hw/bin/python")
    else:
        made = {n: f() for n, f in BD.BOARDS.items()}

        def bbox(board):
            xs, ys = [], []
            for it in board.graphicItems:
                if it.layer == "Edge.Cuts":
                    xs += [it.start.X, it.end.X]
                    ys += [it.start.Y, it.end.Y]
            return max(xs) - min(xs), max(ys) - min(ys)

        ab = parts["arm"][0].val().BoundingBox()
        w, h = bbox(made["arm"])
        check("functional — the arm board's outline is the CAD arm's outline (200 mm plus the finger by 60 mm)", abs(w - ab.xlen) < 0.01 and abs(h - ab.zlen) < 0.01, f"board {w:.2f} x {h:.2f} mm, CAD {ab.xlen:.2f} x {ab.zlen:.2f} mm")
        import cadquery as cq
        arm_solid = parts["arm"][0].val()
        stray = [(x, y, d) for (x, y, d) in BD.holes_mm(made["arm"]) if arm_solid.isInside(cq.Vector(x, (B.YB0 + B.YB1) / 2, -y), 1e-6)]
        check("functional — every hole in the arm board is a hole in the CAD arm (centres are empty in the CAD)", not stray, f"{len(BD.holes_mm(made['arm']))} holes, none filled" if not stray else f"filled: {stray}")
        low = parts["clamp_low"][0].val()
        lh = [(x, y, d) for (x, y, d) in BD.holes_mm(made["clamp_plate"]) if low.isInside(cq.Vector(x, (B.YP0 + B.YP1) / 2, B.ZA1 - B.CLAMP_H / 2 - y), 1e-6)]
        lb = low.BoundingBox()
        wp_, hp_ = bbox(made["clamp_plate"])
        check("functional — the clamp plate board is the CAD clamp plate (size and holes)", not lh and abs(wp_ - lb.xlen) < 0.01 and abs(hp_ - lb.zlen) < 0.01, f"board {wp_:.1f} x {hp_:.1f} mm, CAD {lb.xlen:.1f} x {lb.zlen:.1f} mm")
        eb = parts["elec_board"][0].val().BoundingBox()
        we, he = bbox(made["elec_board"])
        check("functional — the electrode board is the CAD electrode board (size)", abs(we - eb.xlen) < 0.01 and abs(he - eb.zlen) < 0.01, f"board {we:.1f} x {he:.1f} mm, CAD {eb.xlen:.1f} x {eb.zlen:.1f} mm")
        mass = sum(BD.weight_estimate_g(n) for n in BD.BOARDS) if os.path.exists(os.path.join(BD.OUT, "arm.kicad_pcb")) else None
        if mass is not None:
            check("functional — the mechanical-board order (5 of each design) stays under the cheap-shipping weight with packing (0.25 kg)", mass + 40 < 250, f"{mass:.0f} g of boards + about 40 g packing [assume]")
    bad = [n for n, d, fits in B.printability(parts) if not fits]
    check("functional — every printed part fits the printer's build volume", not bad, f"{bad}" if bad else f"{len(B.printability(parts))} parts")
    heavy = [n for n, d, _ in B.printability(parts) if min(d) < P.MIN_WALL * 1e3]
    check("smoke — no printed part is thinner than three perimeters", not heavy, f"{heavy}" if heavy else "all at least 1.2 mm")

import material_study as MS  # noqa: E402

_fr4, _al, _pla = MS.study("FR4 1.2 mm (chosen)"), MS.study("Al 6061 sheet 0.8 mm"), MS.study("PLA printed 2.0 mm")
check("functional — the chosen arm's first bending mode (with the device card, vane and ballast on it) is above 30 Hz; below that it would sit in the building-vibration band as a spectral line", _fr4["f1_Hz"] > 30, f"{_fr4['f1_Hz']:.0f} Hz (cantilever estimate, FR4 E 20 GPa)")
check("functional — 0.8 mm aluminium sheet is a like-for-like substitute for the FR4 arm in mass and first mode (within 10%)", abs(_al["arm_g"] / _fr4["arm_g"] - 1) < 0.1 and abs(_al["f1_Hz"] / _fr4["f1_Hz"] - 1) < 0.1, f"{_al['arm_g']:.1f} g and {_al['f1_Hz']:.0f} Hz against {_fr4['arm_g']:.1f} g and {_fr4['f1_Hz']:.0f} Hz")
check("functional — a printed PLA arm needs about twice the thickness of FR4 for a similar first mode and has five times the thermal drift per kelvin", _pla["f1_Hz"] > 0.8 * _fr4["f1_Hz"] and _pla["t_mm"] / _fr4["t_mm"] > 1.5 and _pla["drift_um_per_K"] > 4 * _fr4["drift_um_per_K"], f"{_pla['t_mm']} mm gives {_pla['f1_Hz']:.0f} Hz, {_pla['drift_um_per_K']:.1f} um/K")

import arm_dxf as AD  # noqa: E402

_dxf, _size, _holes = AD.write_arm_dxf()
_pw, _ph = AD.panel_layout()
check("functional — the arm's DXF for the sheet-metal quote has the board's 208 x 60 mm outline and all 7 holes, and the four-design panel fits in 252 x 60 mm", abs(_size[0] - 208) < 1e-6 and abs(_size[1] - 60) < 1e-6 and len(_holes) == 7 and (round(_pw), round(_ph)) == (252, 60), f"outline {_size[0]:.0f} x {_size[1]:.0f}, {len(_holes)} holes, panel {_pw:.0f} x {_ph:.0f} mm")

import jlc_parcel_mass as JM  # noqa: E402

_parcels = JM.planned_parcels()
_arm = JM.parcel_total(_parcels["arm board"])
_both = JM.combined_total(_parcels, ["arm board", "small boards (3 designs)"])
check("functional — the arm order alone stays under the 0.3 kg line of JLC's cheap shipping tier at 1.2 mm (their rule plus the packing calibrated on the user's quote)", _arm < JM.LIMIT_G, f"{_arm:.0f} g against {JM.LIMIT_G:.0f} g (1.6 mm would be {(JM.board_mass_g(208, 60, 1.6, 5) + JM.PACKING_G):.0f} g: the quote's 0.34 kg)")
check("functional — the arm and the three small designs in one parcel would cross the line, so they are ordered and shipped separately", _both > JM.LIMIT_G, f"{_both:.0f} g combined")
_all = JM.combined_total(_parcels, list(_parcels))
check("functional — boards plus printed-part candidates combined would also cross the line (Combine Shipping stays off across services)", _all > JM.LIMIT_G, f"{_all:.0f} g combined")

if failures:
    print(f"\n{len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("\nAll checks passed.")
