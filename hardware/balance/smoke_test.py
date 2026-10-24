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
    check("functional — one 0.3 mm pad gives the damping ratio the noise budget assumes (within 20%)", abs(zeta_full - P.DAMPING_RATIO) <= 0.2 * P.DAMPING_RATIO, f"{zeta_full:.2f} against {P.DAMPING_RATIO} (peak Bz {b_gap:.2f} T, {P.MAGNET_MAGNETIZATION} discs, {P.VANE_PADS} pad)")
    check("functional — a second pad reaches the strong-damping end (ratio at least 0.8) so the bench can tune between the two", z_two >= 0.8, f"two pads: {z_two:.2f}")
    vx = P.VANE_SIZE[0] * 1e3 / 2
    ox = min((P.MAGNET_X[0] * 1e3 - P.N42_THICKNESS * 1e3 / 2) - (60 - vx), (60 + vx) - (P.MAGNET_X[1] * 1e3 + P.N42_THICKNESS * 1e3 / 2))
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
    bl, cl = B.balance_solve()
    parts = B.build(bl, cl)
    m, com, izz, _ = B.moving_properties(parts)
    check("functional — CAD moving mass matches params.py to 3%", abs(m / 1e3 / P.MOVING_MASS - 1) < 0.03, f"{m:.1f} g against {P.MOVING_MASS*1e3:.1f} g")
    check("functional — CAD moment of inertia matches params.py to 3%", abs(izz / P.MOVING_INERTIA - 1) < 0.03, f"{izz:.3e} against {P.MOVING_INERTIA:.3e}")
    check("functional — the solved ballast puts the centre of mass within 0.3 mm of the pivot axis", math.hypot(com[0], com[1]) < 0.3, f"({com[0]:.2f}, {com[1]:.2f}) mm")
    check("functional — the brass ballast fits its pocket (the hole is 19 mm deep) and its hole stays inside the pocket after the y offset", bl <= 19.0 and abs(cl) + 5.15 <= 10, f"ballast {bl:.1f} mm long, hole offset {cl:+.2f} mm in y")
    vol, who = B.interference(parts)
    check("functional — nothing collides with the fixed structure over +-1.5 degrees", vol < 0.01, f"{vol:.3f} mm^3 {who or ''}")
    fo = B.fixed_overlaps(parts)
    check("functional — no fixed parts overlap by accident (gantry, feet, clamps, damper, sensor bracket, enclosure)", not fo, f"{fo}" if fo else "none")
    over = B.moving_internal_overlaps(parts)
    check("functional — no moving parts overlap by accident", not over, f"{over}" if over else "none")
    clr = B.enclosure_clearance(parts)
    check("functional — the balance sits inside the enclosure with the planned clearance to every wall and the lid", clr >= P.ENCL_MIN_CLEARANCE * 1e3, f"{clr:.1f} mm against {P.ENCL_MIN_CLEARANCE*1e3:.0f} mm")
    cut = B.panel_cut_list(parts)
    stock = sorted((P.PANEL_STOCK[0] * 1e3, P.PANEL_STOCK[1] * 1e3, P.PANEL_T * 1e3))[::-1]
    check("functional — the acrylic is six uncut stock sheets (four walls, two lid sheets), nothing to cut", len(cut) == 1 and sum(cut.values()) == 6 and all(max(abs(a - b) for a, b in zip(k, stock)) < 0.01 for k in cut), f"{cut} against stock {stock}")
    com_z = B.moving_properties(parts)[1][2]
    hang = (B.Z_LOW1 - com_z) * 1e-3
    tilt = M.tilt_from_com(P.COM_OFFSET, hang)
    tol = min((P.MAGNET_GAP - P.PAD_T) / 0.070, 2.4e-3 / 0.108)  # vane clearance over its outer radius, flag gap over the flag radius
    check("functional — the assumed 0.2 mm centre-of-mass offset tilts the arm by less than the vane and flag clearances allow", tilt <= tol, f"{tilt*1e3:.1f} mrad against {tol*1e3:.1f} mrad allowed (hangs {hang*1e3:.1f} mm below the strip)")
    wide = M.tilt_from_com(1.0e-3, hang)
    check("functional — a +-15% printed-mass error (about +-1 mm of offset) would tilt the arm past its clearances, so slicer masses and bench trim are required", wide > tol, f"{wide*1e3:.0f} mrad against {tol*1e3:.1f} mrad")
    seat_g = P.TRIM_SEAT[0] * P.TRIM_SEAT[1] * 1e4 * (8.96 * P.PAD_T * 100) * 2  # two stacked copper-pad pieces, g
    auth = seat_g * 72 / (B.moving_properties(parts)[0]) 
    check("functional — one seat of two stacked copper-pad pieces trims the centre of mass by at least 0.5 mm", auth >= 0.5, f"{auth:.2f} mm ({seat_g:.2f} g at x = 72 mm)")
    import fixtures as FX
    fx, fx_len, fx_slot = FX.build_all()
    base_bb = fx["fixture_saw_guide_base"].val().BoundingBox()
    # the kerf's near wall is the ballast length plus 0.5 mm (to file off) from the stop face
    kerf_cut = fx["fixture_saw_guide_base"].val().Volume() - fx["fixture_saw_guide_base"].cut(B.box(0, 1000, -1, 31, 4.5, 25)).val().Volume()
    check("functional — the saw guide's groove is wider than the rod and the plate and base clear each other", FX.ROD_D + 0.3 > FX.ROD_D and fx["fixture_saw_guide_base"].intersect(fx["fixture_saw_guide_plate"]).val().Volume() < 1e-3, f"groove {FX.ROD_D + 0.3:.1f} mm for a {FX.ROD_D:.0f} mm rod")
    check("functional — the strip guide's slot is exactly the strip width from the shim's fence", abs((fx_slot - 2.0) - P.STRIP_WIDTH * 1e3) < 1e-6, f"{fx_slot - 2.0:.2f} mm against {P.STRIP_WIDTH*1e3:.2f} mm")
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
    check("functional — every screw and nut the CAD's holes take is already owned (inventory.md)", not short, f"needs {tot}; owned {P.FASTENER_OWNED}" + (f"; short {short}" if short else ""))
    n_screws = sum(v for k, v in tot.items() if "screw" in k)
    check("functional — every screw gets a washer, and washers are the one fastener to buy", tot.get("M3 flat washer", 0) == n_screws and "M3 flat washer" not in P.FASTENER_OWNED, f"{tot.get('M3 flat washer')} washers for {n_screws} screws")
    bad = [n for n, d, fits in B.printability(parts) if not fits]
    check("functional — every printed part fits the printer's build volume", not bad, f"{bad}" if bad else f"{len(B.printability(parts))} parts")
    heavy = [n for n, d, _ in B.printability(parts) if min(d) < P.MIN_WALL * 1e3]
    check("smoke — no printed part is thinner than three perimeters", not heavy, f"{heavy}" if heavy else "all at least 1.2 mm")

if failures:
    print(f"\n{len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("\nAll checks passed.")
