# KB: the torsion balance — design findings, numbers, and the checks that guard them

Audience: future LLM sessions. State of 2026-10-24. Everything is in `hardware/balance/` (`params.py` holds the numbers, `balance.py` the CAD, `boards.py` the FR4 boards, `fixtures.py` the
printed jigs, `smoke_test.py` the checks, `model.py` + `tools/force_noise_budget.py` the physics). User-facing build steps: `docs/assembly.md`; the fabrication decisions: `docs/fabrication.md`.

## What it is

A torsion balance whose arm swings in a horizontal plane: a 200 x 60 x 1.2 mm FR4 board stands on edge and hangs from its top edge by a taut 4 mm x 50 um x 30 mm stainless strip. Goal (G1, confirmed
2026-10-23): quantify, on an open low-cost balance in air, the spurious forces that dominate small-thrust measurements: the Lorentz force of supply-lead currents in the ambient field and the
thermal and convective forces of a dissipating device, with the noise floor, calibration constant and drift characterized; claim: resolve 0.4 nN or better (5 sigma on 20 nN) in 1000 s.

## Numbers (from `params.py`/`model.py`; rerun `python3 tools/force_noise_budget.py`)

- Torsion constant 450 uN*m/rad (thin strip plus the tension term), moving mass 51.5 g, inertia 2.47e-4 kg*m^2, resonance 0.215 Hz, k_eff = kappa/l^2 = 0.045 N/m (1 uN moves the flag 22 um).
- Measured at 0.05 Hz with a lock-in; one 1000 s measurement resolves 0.108 nN (1 sigma): conditional GO. Terms (nN/sqrt(Hz)): air currents 4.80 (assumed 1 mm/s fluctuation; the verdict flips at 4 mm/s),
  PLA frame to sensor 0.63, floor acceleration 0.21 and tilt 0.20 through a 0.2 mm centre-of-mass offset, FR4 arm expansion 0.13, damper Brownian 0.021, stray magnetic 0.020, readout 0.006 (146 pm/sqrt(Hz)).
- Anchors the model reproduces (checked in `force_noise_budget.py anchors()`): Soni & Roy, Rev. Sci. Instrum. 84, 095103 (2013) torsion constant, 5 nm to 0.012 uN, 1.5 um drift to 3.6 uN; the
  cryogenic balance of arXiv:2206.02890 (resonance 7.05 mHz, decay 16.7 to 24.6 days, Eq. 1 thermal torque).
- Arm length barely moves the resolution (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length), but shortening is not free: the damper weakens to zeta 0.10 per pad at 75 mm.

## Findings that shaped the design (each is guarded by a smoke check)

1. **No permanent magnet on the arm.** One N42 6 x 3 mm disc is 0.089 A*m^2: about 7 nN/sqrt(Hz) of field-noise force. Masses on the arm are brass, 304 stainless or plastic; steel would carry an induced moment above the allowed 1e-4 A*m^2.
2. **Damper.** The ten N42 discs are radially magnetized (poles on the curved side) per the listing; the user's phone-compass test was inconclusive (see handoff), so the CAD holds both layouts
   (`MAGNET_MAGNETIZATION`). Eddy damping is c = sigma t integral(Bz^2 dA) over the vane [assume low magnetic Reynolds number; good to about a factor of two] with the magpylib field; the earlier
   analytic estimate (on-axis field uniform over the disc) overstated damping about 1.6x. One 20 x 20 x 0.3 mm copper pad gives zeta 0.40 (diametric, four discs on edge, 1.4 mm to the vane
   mid-plane); two pads 0.81; the axial layout 0.43 / 0.86. Pads stack to tune. Damping rises with (vane radius / arm length)^2.
3. **Centre-of-mass tilt.** The arm tilts by (centre-of-mass offset) / (hang below the strip's lower end). The printed 20 mm arm hung 15 mm (66 mrad per mm); the 60 mm board hangs 32 mm (31 mrad
   per mm). Clearances (vane to disc 1.1 mm over 55 mm, flag to prong 3 mm over 108 mm) allow about 20 mrad, so offset must be trimmed below about 0.6 mm; the budget assumes 0.2 mm. Untrimmed errors reach
   about 2.7 mm worst case (ballast length +-0.5 mm: 0.58; device card +-1 g: 1.96; printed holder +-15%: 0.16), so a bench trim is required: spare copper pads on the board's face (1.9 mm each at the
   end) and sliding the ballast rod along y.
4. **Zero adjustment.** The electrodes' 1 mm gap allows only +-0.4 degrees; a hand-clamped strip sits several degrees off. A torsion head (printed disc in the gantry bore carrying the upper clamp; two M3
   push-push screws on a 26 mm lever, 1.1 degrees per turn, +-5 degrees reachable) zeroes the arm before the fixed electrode is set with a 1.00 mm gauge.
5. **No PLA in the strip's clamping loop.** Self-tapped screws in PLA relax; every clamp part is FR4 or steel, with through-bolts and nuts. A smoke check fails if a printed part enters the loop.
6. **Device heating.** A 16 x 24 mm FR4 card in still air (10 W/m^2/K) rises 65 K/0.5 W (130 K/W). FR4 Tg is about 130 C [verify at order]; the rule is card temperature at most Tg minus 40 K, so the device power is capped at
   0.5 W (224 mA through the 10 ohm card; 300 mA through 2.2 ohm is only 0.2 W). PLA near a hot device would creep with its power, the very effect being measured.
7. **Electrostatic calibration plates.** 20 x 8 mm ENIG pads, 1.0 mm gap at 80 mm; F = eps0 A V^2 / (2 d^2): 5.7 uN at 40 V; around a 40 V bias 283 nN/V (1 mV = 0.28 nN). The moving pad is grounded through the strip (no lead
   on the arm, no moment); the fixed pad sits in a grounded ENIG guard so the effective area is the pad's. The absolute scale is transferred from known weights (1 mg is 9.8 uN). The plate driver is limited to under 23 V here
   (50 V DC repo line). The gap is an effective parameter fitted in calibration.
8. **Enclosure** (the biggest noise lever): six uncut 2 mm 150 x 250 mm acrylic sheets, four identical pinwheel walls (inner span 248 mm, 150 mm tall) plus a two-sheet lid on printed shelves; slots shimmed with 0.3 mm foam tape.
   Printed clear PETG was rejected (panels exceed the 220 mm bed; the home printer is PLA only).
9. **Strip.** Hand-cut with a printed guide; stiffness is calibrated from the measured period. The quality factor and drift are measured in A5; fallback is a photo-etched strip.

## Collision/geometry checks (all in `balance.py`/`smoke_test.py`)

Nothing collides over +-1.5 degrees of arm swing (+-0.4 degrees at the electrode pair; the head +-5 degrees in the gantry); no unintended fixed or moving overlaps; enclosure clearance 12 mm
(rule: at least 10); the strip's lower clamp, upper clamp and arm board are FR4/steel; every fastener is owned except washers and stainless nuts; the board outlines and hole positions equal the CAD's.
Past defects found by these checks: counterweight pocket vs bracket, vane tip vs holder, arm edge vs fixed electrode, a nut at the vane's height, a 6.0 mm nut ring larger than a hex pocket's inscribed circle.

## Superseded (do not reintroduce)

The printed 20 mm arm, flag tab, vane holder with a copper foil route, steel ballast, 3 mm acrylic panels, a 1 mm copper vane, the 0.3 mm vane at ZETA 0.6, printed clamp halves with self-tapped
screws, and the foil-tape plates.

## Added 2026-10-28

- The magnets are axial (twist test 2026-10-26): the damper uses flat round pockets, damping 0.43 per pad (0.86 with two); `balance_design_notes` text above that mentions the on-edge cradles describes the unused diametric option.
- The arm's first bending mode with its loads is about 36 Hz (`hardware/balance/material_study.py`); FR4 stays (decided 2026-10-28 on the user's quote), thickness 1.2 mm, finish HASL.
- A labelled picture of the whole apparatus (arm 208 mm, 250 x 250 x 200 mm acrylic box) is `docs/img/apparatus.png` (`render_labeled.py`). The user asked why the arm is so long compared with pictures of torsion balances: see the open question in `session_handoff.md`.

