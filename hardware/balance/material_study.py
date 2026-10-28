"""
material_study.py — the arm's material and thickness compared (Part J1): mass, moment of inertia, first bending mode, thermal drift, electrodes.

    python3 hardware/balance/material_study.py

The arm hangs on edge (faces toward +-y): the pendulum swings in the thin direction, so the arm bends in the direction where its stiffness is E h t^3 / 12. It is clamped at the
centre, so each half is a cantilever of length L = ARM_HALF_LENGTH; the first mode comes from Rayleigh's quotient with the static tip-load shape phi(x) = (3 L x^2 - x^3) / (2 L^3),
which is exact for a point load and within a few percent for the lumped masses used here:  k = 3 E I / L^3,  m_eff = integral(mu phi^2) + sum(M_i phi(x_i)^2),  f = sqrt(k / m_eff) / 2 pi.
The masses carried on each half are the CAD's (balance.py output of 2026-10-26: device card and its hardware, vane and holder on the +x half; the ballast on the -x half): estimates of
where they sit, not a CAD modal analysis. Material properties are handbook values, not measured: FR4 E 20 GPa (JLC's TG135 laminate, in-plane, glass-cloth direction), 6061 aluminium 69 GPa,
PLA 3.5 GPa (FDM, along the layers). Creep and moisture are listed, not modelled.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402

# name: (E GPa, density g/cm^3, thickness mm, CTE ppm/K, carries electrodes?, note)
CANDIDATES = {
    "FR4 1.2 mm (chosen)": (20.0, 1.85, 1.2, 14.0, True, "ENIG pads and guard on the board itself; flat to about 0.1 mm; low creep"),
    "FR4 1.6 mm": (20.0, 1.85, 1.6, 14.0, True, "JLC's default thickness: +33% mass, about +40% first-mode frequency"),
    "FR4 1.0 mm": (20.0, 1.85, 1.0, 14.0, True, "JLC offers 1.0 mm; 0.1 mm tolerance band is +-10% at 1.0 mm and over"),
    "FR4 0.8 mm": (20.0, 1.85, 0.8, 14.0, True, ""),
    "FR4 0.4 mm": (20.0, 1.85, 0.4, 14.0, True, "mass falls to a third; the first mode falls into the building-vibration band"),
    "Al 6061 sheet 0.8 mm": (69.0, 2.70, 0.8, 23.0, False, "conductive: the arm is the grounded electrode; no pads or guard; CNC or laser cut, one piece"),
    "Al 6061 sheet 1.0 mm": (69.0, 2.70, 1.0, 23.0, False, ""),
    "PLA printed 2.0 mm": (3.5, 1.24, 2.0, 68.0, False, "creeps under steady load, absorbs moisture, warps over 208 mm; electrodes would be foil"),
    "PLA printed 3.0 mm": (3.5, 1.24, 3.0, 68.0, False, ""),
}

HOLE_FILL = 26.48 / (208 * 60 * 1.2 * 1.85e-3)  # the CAD arm's mass against the solid bounding board (holes and the finger's shape)
# lumped masses on each half: (position along the half in m, mass in kg): CAD masses, positions estimated
PLUS_X = [(0.095, 6.41e-3), (P.VANE_X, 5.30e-3)]  # device card with its hardware; vane, its holder and hardware
MINUS_X = [(0.090, 10.07e-3)]  # the brass ballast


def phi(x, L):
    return (3 * L * x * x - x ** 3) / (2 * L ** 3)


def study(name):
    E, rho, t, cte, electrodes, note = CANDIDATES[name]
    L = P.ARM_HALF_LENGTH
    h = P.ARM_HEIGHT
    t_m = t * 1e-3
    mu = rho * 1e3 * h * t_m * HOLE_FILL  # kg per metre of one half
    EI = E * 1e9 * h * t_m ** 3 / 12
    k = 3 * EI / L ** 3
    out = {}
    for side, masses in (("+x", PLUS_X), ("-x", MINUS_X)):
        m_eff = mu * L * 0.2357 + sum(m * phi(x, L) ** 2 for x, m in masses)  # integral of mu phi^2 dx = 33/140 mu L
        out[side] = math.sqrt(k / m_eff) / (2 * math.pi)
    arm_mass_g = mu * 2 * L * 1e3 + 0.0
    inertia = mu * 2 * L * (2 * L) ** 2 / 12  # uniform strip about its centre
    return {"E_GPa": E, "t_mm": t, "arm_g": arm_mass_g, "arm_I": inertia, "f1_plus_Hz": out["+x"], "f1_minus_Hz": out["-x"], "f1_Hz": min(out.values()),
            "drift_um_per_K": cte * 1e-6 * L * 1e6, "electrodes": electrodes, "note": note}


def main():
    print("%-24s %7s %9s %8s %8s %8s %9s  %s" % ("candidate", "arm g", "I x1e-5", "f1 +x", "f1 -x", "drift", "electrodes", "note"))
    for name in CANDIDATES:
        s = study(name)
        print("%-24s %7.1f %9.2f %7.0fHz %7.0fHz %5.1f um/K %9s  %s" % (name, s["arm_g"], s["arm_I"] * 1e5, s["f1_plus_Hz"], s["f1_minus_Hz"], s["drift_um_per_K"], "board" if s["electrodes"] else "extra", s["note"]))
    print("CAD arm (FR4 1.2 mm, with its holes): 26.5 g, 8.84e-5 kg m^2 about z; the uniform-strip inertia above is the bare board without the finger and holes")


if __name__ == "__main__":
    main()
