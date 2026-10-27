"""
params.py — single source of truth for the force-balance design (`FORCEBAL`).

Both the analytic model (`model.py`, `tools/force_noise_budget.py`) and the CAD
script (`balance.py`) read these numbers, so a mechanical change shows up in
the noise prediction and the PCB's mounting geometry together. SI units unless
the name says otherwise.

Provenance tags: [pub] taken from a published paper (named in the comment),
[ds] a data sheet, [design] a choice made here, [assume] an assumption that
the A5 prototype check measures instead of trusting.
"""

import math

KB = 1.380649e-23  # J/K
Q_E = 1.602176634e-19  # C
G_ACC = 9.80665  # m/s^2
T_K = 295.0  # room temperature

# --- the balance: a horizontal arm on a taut stainless-steel strip [design] ---
ARM_HALF_LENGTH = 0.100  # pivot to the end mass / flag / device mount; l in the model
# The arm is an FR4 board standing on edge (its faces face +-y), so a face of it is the moving electrode and its edge is the flag. Positions
# along it scale with ARM_HALF_LENGTH (a 0.075 m arm is the fallback if the long board's quote is dear).
ARM_HEIGHT = 60e-3  # m, board height: the centre of mass hangs about half of it below the strip's lower end (tilt = offset / hang)
ARM_TOP_Z = 80e-3  # m, the arm board's top edge and the lower end of the strip's free length
BOARD_T = 1.2e-3  # m, thickness of every mechanical board (weight scales with it; JLC offers 1.0, 1.2 and 1.6 mm [verify])
FR4_DENSITY = 1.85e3  # kg/m^3
FR4_TG_C = 130.0  # deg C, glass transition of standard FR4 [verify on the order page; high-Tg is a menu option]
# electrode centre, then the vane: fractions of the arm on the 200 mm baseline; on a short arm they keep their footprints apart instead
PLATE_X = 0.8 * ARM_HALF_LENGTH if ARM_HALF_LENGTH > 0.09 else ARM_HALF_LENGTH - 26e-3  # m
VANE_X = min(0.55 * ARM_HALF_LENGTH, PLATE_X - 21.5e-3)  # m, where the damper vane sits along the arm
# mass and inertia of the whole moving assembly come from the CAD (balance.py prints them; the
# smoke test fails if these two numbers drift more than 3% from it) [design]
MOVING_MASS = 0.0515  # kg
MOVING_INERTIA = 2.472e-4  # kg*m^2 about the pivot axis
STRIP_WIDTH = 4.0e-3  # m; stainless shim stock
STRIP_THICKNESS = 50e-6  # m
STRIP_LENGTH = 30e-3  # m, free length between the two clamps
STRIP_SHEAR_MODULUS = 77e9  # Pa, 304/316 stainless [assume: typical handbook value, shim lot unknown]
STRIP_YIELD_PA = 200e6  # Pa, conservative for annealed 304 [assume]
FLAG_AT = ARM_HALF_LENGTH  # the optical flag sits at the arm end

# --- masses on the arm must be non-magnetic: brass, not steel [design]. A steel slug of the ballast's size would carry an
# induced moment of about 2e-4 A*m^2 in the Earth's field (m = V B / (N mu0), N about 0.3), above the 1e-4 stray allowance.
BRASS_DENSITY = 8.5e-3  # g/mm^3 (C360 brass; rod listings say H59/H62/C36000)

# --- damping: copper vane on the arm moving between fixed N42 discs [design] ---
# the same non-contact eddy-current damper as Soni & Roy [pub]: no power, no
# permanent magnet on the moving arm (the magnets are fixed to the base).
# The vane is VANE_PADS uncut 20 x 20 x 0.3 mm copper pads stacked (touching, so they act as one sheet): damping goes with
# total thickness, so a second pad doubles it and a pad can be added or removed on the bench.
PAD_T = 0.3e-3  # m, one copper pad (listing: 20 x 20 x 0.3 mm)
VANE_PADS = 1
VANE_THICKNESS = VANE_PADS * PAD_T  # m
VANE_SIZE = (20e-3, 20e-3)  # m, the pad as it arrives (x along the arm, y along the swing)
# the discs are radially magnetized (poles on the curved sides, per the listing): they stand on edge, axes along x, one pair
# of discs above and one below the vane, each disc's N-S diameter vertical, discs of a pair side by side with opposite poles
MAGNET_GAP = 1.4e-3  # m, from the vane's mid-plane to the nearest disc surface (>= 1 mm clearance to a 2-pad stack)
MAGNET_X = (VANE_X - 4e-3, VANE_X + 4e-3)  # m, disc centres along the arm (about the vane's centre)
MAGNET_Y = 20.5e-3  # m, disc centres across the swing
MAGNET_LIP = 0.6e-3  # m, the retaining lip over an axial disc's face (axial layout only): the discs' effective gap is MAGNET_GAP + this
MAGNET_MAGNETIZATION = "axial"  # twist test 2026-10-26: free turning, no preferred angle = poles on the flat faces, so the discs lie flat facing the vane ("diametric" if a detent is found)
DAMPING_RATIO = 0.40  # zeta assumed by the noise budget: what eddy_damping_field() gives for one pad (two pads: 0.81; the axial layout gives 0.43 / 0.86)

# --- readout: a flag crossing an LED-to-photodiode gap, lock-in demodulated ---
LED_PHOTOCURRENT = 100e-6  # A at mid-flag, 20 mA LED [ds estimate: IR26-21C 4.25 mW/sr x 0.09 sr x ~0.5 / VBPW34S 0.67 A/W (50 uA at 1 mW/cm2 on 7.5 mm2), halved by the flag; A5 measures the real number]
BEAM_EDGE_WIDTH = 1.4e-3  # m, the LED's 20 degree beam at 4 mm: 2 x 4 mm x tan(10 deg) [ds, IR26-21C view angle]
TIA_RF = 10e3  # ohm [design: 100 uA + ambient stays inside the ADC's +/-2.44 V]
ADC_NOISE_V = 80e-9  # V/sqrt(Hz) input-referred [ds: ADS131A04 Table 1, 5.01 uVrms at 8 kSPS, gain 1, 3.3 V analog supply, 2.442 V reference = 79 nV/rtHz]
LED_RIN = 1e-6  # 1/sqrt(Hz) relative intensity noise of the DAC-driven LED [assume]
RIN_REJECTION = 30.0  # ratiometric (reference photodiode) rejection of LED intensity noise [design]

# --- environment; every value here is [assume] and is measured in A5 ---------
TILT_NOISE_RAD = 1e-7  # rad/sqrt(Hz) of floor tilt at F_REF
SEISMIC_ACC = 1e-6  # m/s^2/sqrt(Hz) of floor acceleration at F_REF
COM_OFFSET = 0.2e-3  # m, centre-of-mass offset from the pivot axis after balancing
# Printed-part masses read from the slicer (g), by part name. A real print differs from the CAD estimate (infill, walls) by +-15%,
# which moves the centre of mass by about +-1 mm; entering the slicer's figure replaces the density estimate for that part.
PRINTED_MASS_G = {}  # only the PLA parts that move (the vane holder) are left; the boards' mass follows from their thickness
AIR_AREA = 2e-3  # m^2, projected area the air can push on (flag, device mount)
AIR_SPEED_RMS = 1.0e-3  # m/s mean flow inside the draught shield
AIR_SPEED_FLUCT = 1.0e-3  # m/s fluctuation, at F_REF, per sqrt(Hz) of bandwidth
TEMP_NOISE = 1e-3  # K/sqrt(Hz) inside the enclosure at F_REF
ARM_EXPANSION = 14e-6  # 1/K, FR4 in the board's plane [assume: handbook range 12-16 ppm/K]
PLA_EXPANSION = 70e-6  # 1/K, printed PLA [assume]
FRAME_PATH = 0.10  # m, PLA between the strip's top clamp and the sensor bracket (gantry leg, base, bracket): its drift moves the flag against the sensor [assume]
B_NOISE = 10e-9  # T/sqrt(Hz) of ambient magnetic field noise at F_REF
STRAY_MOMENT = 1e-4  # A*m^2 residual moment of screws and leads on the moving arm [assume]
F_REF = 0.1  # Hz, where the environmental densities above apply
SPECTRAL_SLOPE = 1.0  # environmental density scales as (F_REF / f)^slope

# --- the measurement ------------------------------------------------------------
F_MOD = 0.05  # Hz, the device-under-test is switched at this frequency
INTEGRATION_S = 1000.0  # s of data per force estimate

# --- the claim the instrument is meant to support (G1) -------------------------
CLAIM_FORCE_N = 20e-9  # smallest spurious-force term to size, at 5 sigma
CLAIM_SIGMAS = 5.0
MODEL_ERROR_FACTOR = 10.0  # allowance for the [assume] terms being wrong

# --- electrostatic calibration / disturbance-injection plates [design] -----------
# A fixed plate on the base faces a plate on the arm (grounded through the stainless strip: no lead,
# no magnetic moment). Force F = eps0 A V^2 / (2 d^2); a DC bias V_b with a small signal dV gives the
# linear force 2 * (eps0 A / (2 d^2)) * V_b * dV. All voltages stay under the repo's 50 V DC line.
PLATE_AREA = 16e-4 * 0.5  # m^2: 20 mm x 8 mm overlap of the two plates
PLATE_GAP = 1.0e-3  # m
PLATE_RADIUS = PLATE_X  # m, where the plates act on the arm (their lever arm)
PLATE_BIAS_MAX = 40.0  # V
EPS0 = 8.8541878128e-12

# --- N42 disc (the damper magnet and a candidate calibration part) --------------
N42_BR = 1.32  # T, nominal for N42 [assume: strength untested, listing's report is for another size]
N42_DIAMETER = 6e-3
N42_THICKNESS = 3e-3

# --- enclosure: a printed frame with drop-in acrylic panels (the air-current term is the budget's largest) [design] ---
# Sized to uncut stock: 2 mm clear acrylic, 150 x 250 mm sheets (a size sold ready-made). Four identical walls in a pinwheel give an
# inner span of stock length - thickness; two more sheets side by side are the lid.
PANEL_T = 2e-3  # acrylic thickness bought; the frame's slots are PANEL_T + 2*SEAL_T + 0.2 mm, so a thickness change is one number
PANEL_STOCK = (250e-3, 150e-3)  # m, the sheet as sold (long side, short side)
SEAL_T = 0.3e-3  # m, double-sided PE foam tape used as a shim on both faces of each wall inside its slot
ENCL_INNER = (PANEL_STOCK[0] - PANEL_T, PANEL_STOCK[0] - PANEL_T, PANEL_STOCK[1])  # clear volume, m
LID_SEAT = 6e-3  # m, bearing of the lid on a printed shelf along each x wall (the lid sheets are 250 mm long, the opening 248)
ENCL_POST = 20e-3  # corner post cross-section, m
ENCL_MIN_CLEARANCE = 10e-3  # nearest moving or fixed balance part to a panel

# --- fasteners: what the CAD's holes take, and what is already owned (inventory.md) ---
FASTENER_OWNED = {"M3 nut": 55, "M3x10 pan head screw": 50, "M3x12 pan head screw": 50, "M3x14 pan head screw": 50}

# --- printing -------------------------------------------------------------------
FASTENER_TO_BUY = {"M3 nut, 304 stainless": 20, "M3 flat washer": 50}  # the planned AliExpress lines (not yet ordered)
PRINT_VOLUME = (220e-3, 220e-3, 250e-3)  # Creality K1 build volume [assume; check the manual]
MIN_WALL = 1.2e-3  # m, 3 perimeters at 0.4mm


def plate_force(v_total):
    """Electrostatic force (N) of the plate pair at voltage v_total across it."""
    return EPS0 * PLATE_AREA * v_total**2 / (2 * PLATE_GAP**2)


def plate_gain(v_bias):
    """Small-signal force per volt (N/V) around a DC bias."""
    return EPS0 * PLATE_AREA * v_bias / PLATE_GAP**2


def n42_moment():
    """Magnetic moment of one disc, A*m^2 (m = Br V / mu0)."""
    v = math.pi * (N42_DIAMETER / 2) ** 2 * N42_THICKNESS
    return N42_BR * v / (4e-7 * math.pi)

# --- the device under test and its heat [assume: still air, 10 W/m^2/K from both faces of a 16 x 24 mm card] ---
DEVICE_POWER_MAX = 0.5  # W, the top dissipation of a device card: 0.9 W (300 mA through 10 ohm) would put the card 117 K up, past FR4's glass transition less 40 K; 0.5 W is 224 mA through 10 ohm
DEVICE_CARD_AREA = 2 * 16e-3 * 24e-3  # m^2, both faces
HEAT_H = 10.0  # W/m^2/K
AMBIENT_C = 22.0
TG_MARGIN_K = 40.0  # the board that carries the card must stay this far below its glass transition
