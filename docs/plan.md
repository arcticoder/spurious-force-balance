# Research instrument plan — a fab-assembled force balance

Status: gates G1–G3, requirements (WP1), candidate parts (WP2) and the analog block simulations (WP3) done
2026-10-22 (G1 confirmed 2026-10-23); no schematic, layout or order yet; layout waits on the A5 prototype check. The task list that drives this is
[TODO-agent.md](TODO-agent.md) Part A; the scope decision is recorded in
[circuit_lifecycle_and_repo_scope](https://github.com/arcticoder/lab/blob/main/docs/kb/circuit_lifecycle_and_repo_scope.md) in the `lab` repo.

The aim is one instrument that can support a publishable measurement, built from a printed
balance and JLCPCB-assembled electronics, not a set of single-circuit boards. Constraints that
shape everything: no hand soldering (the fab places every electronic part), only parts from the
fab's own library (nothing mailed in; the through-hole parts on the bench are not in the design),
one consolidated order, USB power, nothing above the repo's 50 V DC / 30 V AC line.

---

## G1 — the measurement goal (confirmed 2026-10-23)

> **Quantify, on an open, fully SMT-assembled, low-cost torsion balance operating in air, the spurious
> forces that dominate small-force and thrust measurements — the Lorentz force of supply-lead currents
> in the ambient magnetic field, and the thermal and convective forces of a dissipating device — as
> functions of current, lead geometry and dissipated power, with the balance's force noise floor,
> calibration constant and drift fully characterized.** Instrument claim: resolves forces to ≤ 0.4 nN
> (5σ on a 20 nN term) in a 1000 s measurement at a parts cost under $X (filled from the final BOM).

Why this question: the published small-thrust experiments agree that current-carrying leads and
heat are the usual false positives. The Duif paper (arXiv:1706.04999) names heat dissipated on the
balance, the Lorentz forces of DC currents and the attached power cables as the main sources of
uncertainty in microwave-cavity thrust experiments; the SpaceDrive group's balance work (Tajmar
et al.) reports, in the secondary summaries read here (the papers themselves were not), that
magnetic interaction of power cables with the Earth's field was the dominant artifact. An open
instrument that sizes those terms as a function of current and geometry is a contribution
whether or not anything anomalous is ever found, and it is answerable at the sensitivity G3
predicts: for leads of length L carrying current I across a horizontal field B, F = B I L:

| I | L | B (assumed 20 µT, measured by the board's magnetometer) | F |
|---|---|---------|---|
| 10 mA | 50 mm | 20 µT | 10 nN |
| 100 mA | 50 mm | 20 µT | 100 nN |
| 300 mA (the USB-powered limit; 1 A needs a bench supply) | 50 mm | 20 µT | 300 nN |

The claim is sized to a 20 nN term at 5σ (see G3). Controlled variables: current (0.05–1 A,
scaling check F ∝ I), lead orientation (a 90° rotation should null a Lorentz term), lead
geometry (straight, twisted pair, coaxial return), and dissipated power with the current held
fixed (heater resistor on the device mount).

## G2 — the mechanical design (first cut, with a model)

Source: `hardware/balance/` (`params.py` is the single source of numbers, `model.py` the analytic
model, `balance.py` the CadQuery model, `render.py` the picture, `smoke_test.py` the checks). Run
the CAD with `~/.venvs/lab-hw/bin/python hardware/balance/balance.py`; STL files for each part
are exported to `hardware/balance/cad/` (printable on the K1: the largest part is 200 × 32 × 28 mm).

| Item | Value |
|------|-------|
| Type | Torsion balance: a horizontal arm on a taut stainless strip (4 mm × 50 µm × 30 mm), ±100 mm |
| Torsion constant | 448 µN·m/rad (thin-strip formula plus the ribbon's tension term) |
| Moving mass / inertia | 46.7 g / 2.83 × 10⁻⁴ kg·m² (from the CAD; the printed parts' slicer masses replace its density estimate) |
| Resonance | 0.200 Hz (period 5.0 s) |
| Stiffness at the arm end | 0.0448 N/m: 1 µN moves the flag 22 µm (the Soni & Roy stand, below, is 54× stiffer) |
| Measurement frequency | 0.05 Hz (the device under test is switched at this rate; the readout is lock-in demodulated) |
| Damping | A 20 × 20 mm copper vane on the arm (one uncut 0.3 mm pad, or two stacked) between four N42 discs **fixed** to the base (eddy-current damper, as in Soni & Roy). The discs are radially magnetized, so they stand on edge in printed cradles, two above and two below the vane, 1.4 mm from its mid-plane. The field is modelled with magpylib (checked against the analytic on-axis field of an axial disc to 0.01%) and integrated over the vane: one pad gives a damping ratio of 0.45 (what the budget assumes), two pads 0.90 [first-order estimate, good to about a factor of two]. The earlier analytic estimate overstated damping about 1.6× because it took the on-axis field as uniform over the disc |
| Displacement readout | Flag on the arm crossing an LED-to-photodiode gap in a C-bracket (LED board above, photodiode board below, both small fab-assembled boards) |
| Calibration and disturbance injection | Electrostatic plates (20 × 8 mm, 1 mm gap, at 80 mm), faced with copper foil tape. The moving plate is grounded through the strip, so it needs no lead wire and carries no magnetic moment: its foil tail runs along the arm and hub into the lower strip clamp, and a second foil tail leaves the top clamp under a screw washer together with the plate driver's ground wire. No joint depends on the tape's adhesive being conductive (every joint is clamped). The fixed plate has a foil tail and wire under a washer on a terminal screw in its foot. 5.7 µN at 40 V; around a 40 V bias, 283 nN per volt, so 1 mV is 0.28 nN |
| Device mount | Vertical plate at +x for a terminal block and the device's leads; a dummy brass block stands in for the device's mass |
| Balance trim | A brass ballast in the −x pocket, its hole offset in y, is solved so the centre of mass is on the axis (CAD: 0.00 mm). The arm hangs 15 mm below the strip's lower end, so each millimetre of centre-of-mass offset tilts it by 66 mrad, and the vane and flag clearances allow about 16 mrad: a ±15% error in a printed part's mass (a real print against the infill estimate) moves the centre of mass about ±1 mm and would tilt the arm past them. So the slicer's masses go into `params.py` before the final ballast is cut, and two 16 × 8 mm recesses on the arm's top face take copper-pad pieces or foil squares for the bench trim (1.06 mm of authority from two stacked pad pieces at one end) |

**Design decisions this work forced** (each from a check that failed or a number that surprised):

- *No permanent magnet on the moving arm.* One N42 6 × 3 mm disc has a moment of 0.089 A·m²;
  against 10 nT/√Hz of ambient field noise (assumed) that alone is about 7 nN/√Hz of force noise,
  more than every term except air currents. The earlier idea of calibrating with a coil acting on
  an N42 disc on the arm is dropped; the discs only damp, and they are fixed to the base.
- *Electrostatic calibration transferred from masses.* The V² law is checked against known weights
  at micronewtons (1 mg is 9.8 µN) and then used down to nanonewtons.
- *A moving-assembly collision check across the arm's swing* found the counterweight pocket
  touching the sensor bracket, the vane tip touching the damper holder, and the arm's edge touching
  the fixed electrode; each was fixed in the CAD (swing limit ±1.5°, ±0.4° at the 1 mm plate gap).
- *The first layout's centre of mass was 10.8 mm off the axis*, which would have coupled floor tilt
  into torque far above the model's assumed 0.2 mm; the ballast and counter-mass are now solved.
- *The damper magnets are radially magnetized* (poles on the curved sides, per the listing), which the first damper design
  ignored: flat-face mounting would have put the field in the vane's plane. Standing the discs on edge restores the field
  through the vane; a field model replaced the analytic estimate, and a stack of 0.3 mm pads tunes the damping (so the 1.0 mm
  pad is not needed).
- *Centre-of-mass offset tilts the arm* far more than first assumed (see "Balance trim"); this made bench trim and slicer masses part
  of the design rather than a refinement.

Parts the mechanics need that are not on hand (an AliExpress cart item list, in
`TODO-arcticoder.md`): stainless-steel shim stock, 50 µm (in the cart); copper sheet, 0.3 mm; conductive copper foil tape;
a brass rod, 10 mm diameter, for the ballast (steel would feel the damper magnets); M3 washers and 304
stainless nuts (screws and carbon-steel nuts are on hand); six uncut 2 mm acrylic sheets, 150 × 250 mm, and double-sided
foam tape; a JST-SH 1.0 mm 2-pin cable with flying leads for the plate driver; and 1 mg to 500 mg calibration weights.
The enclosure (draught shield) is decided: a printed frame with four identical 250 mm wall sheets in a pinwheel (inner span
248 mm, 150 mm tall) and a lid of two more sheets, the walls held in slots shimmed with 0.3 mm foam tape; sheet size and
thickness are `PANEL_STOCK` and `PANEL_T` in `hardware/balance/params.py`. Acrylic rather than printed clear PETG: the optics
are all inside the box, so clarity only matters for looking in; the 240+ mm panels exceed the 220 mm print bed; and solid
panels would take about a kilogram of filament. If A5 shows the air-current term above the model's assumption, a compressible gasket
is the next step.
Design to stock sizes: every piece bought is used uncut (acrylic sheets, copper pads, the brass rod's one saw cut, the
shim sheet's 4 mm strip), with printed jigs for the cuts (`hardware/balance/fixtures.py`).

## G3 — the end-to-end force-noise prediction, and the go/no-go

Source: `tools/force_noise_budget.py` (run it; `hardware/balance/smoke_test.py` checks it).
It first checks the model against published numbers, all of which pass:

| Check | Published | Model |
|-------|-----------|-------|
| Soni & Roy (RSI 84, 095103, 2013): torsion constant from I = 0.0385 kg·m², ω = 2.240 rad/s | 0.0034 N·m/deg | 0.00337 |
| their 5 nm of sensor noise | 0.012 µN | 0.0122 |
| their 1.5 µm of drift over 8 h | 3.6 µN | 3.65 |
| cryogenic torsion balance (arXiv:2206.02890): resonance of κ = 2.22 × 10⁻⁸ N·m/rad, I = 1.13 × 10⁻⁵ kg·m² | 7.05 mHz | 7.054 |
| its amplitude decay time, Q = 3.2 × 10⁴ to 4.7 × 10⁴ | 16.7 to 24.6 days | 16.7 to 24.5 |

Predicted force-noise density at the 0.05 Hz measurement frequency:

| Term | nN/√Hz | Basis |
|------|--------|-------|
| Air currents | 4.80 | assumed 1 mm/s mean flow and fluctuation inside a draught shield, 20 cm² flag |
| Temperature (arm expansion) | 0.63 | assumed 1 mK/√Hz, printed arm at 70 ppm/K |
| Floor acceleration through the centre-of-mass offset | 0.22 | assumed 10⁻⁶ m/s²/√Hz, 0.2 mm offset |
| Floor tilt through the same offset | 0.22 | assumed 10⁻⁷ rad/√Hz |
| Thermal (Brownian, eddy damper) | 0.025 | computed |
| Magnetic (stray moment × field noise) | 0.020 | assumed 10⁻⁴ A·m², 10 nT/√Hz |
| Optical readout | 0.005 | computed (123 pm/√Hz: shot 90, ADC 76, LED 33, TIA 18) |
| **Total** | **4.85** | |

One 1000 s lock-in measurement resolves **0.11 nN (1σ)**. The claim needs ≤ 0.40 nN (a 20 nN term at 5σ,
with a 10× allowance for the assumed terms), so the verdict is **GO, conditional on the assumed
environment being measured**: the margin over the allowance is 3.7×.

What decides it: air currents. The verdict flips to no-go if the air-speed fluctuation is 4 mm/s
instead of 1 mm/s; nothing else moves it. The readout, the part the circuit boards implement, is
two orders of magnitude below the environmental terms, which means the electronics need not be
exotic and the effort belongs in the enclosure, the leveling and the thermal design.

Comparison, with the caveat that a model of stationary noise is not a measured spectrum: Soni &
Roy report 5 nm of sensor noise (about 10 nN on their stiff stand), a drift of 3.6 µN over 8 h, and a
lowest measured thrust of 1.3 µN ± 20%; the SpaceDrive balance is described as designed for about
100 nN resolution in vacuum with magnetic shielding. This design is softer and quieter in its
readout, but works in air, where the real spectrum will be the test (A5).

## A2 — environment control and absolute metrology

The terms G3 ranks decide what the first build includes:

1. **Air currents (dominant).** A closed enclosure around the balance with a small, thermally quiet
   volume; the sensor boards' dissipation kept low; no fans. The first build is a printed frame
   with acetate or acrylic panels (an open decision: material and where it comes from). Vacuum is out of
   scope for the first iteration; its expected benefit is removing this term.
2. **Temperature.** Thermal mass and insulation around the balance; the board logs temperature at the
   arm's base, the flag end and the enclosure wall. A metal arm (aluminium, 23 ppm/K) instead of the
   printed one is the fallback if G3's temperature term proves larger.
3. **Magnetic field.** No permanent magnets on the arm; the board's magnetometer records the field at
   the device mount, which is also the B in G1's force law. Active compensation (a Helmholtz pair driven
   from the field sensor) is the next step if the measured field noise exceeds the assumed 10 nT/√Hz.
4. **Floor motion.** A heavy base on soft feet; the on-board accelerometer measures the floor; the
   balance is leveled and trimmed to a centre-of-mass offset of 0.2 mm or better.

Absolute scale and its uncertainty: the electrostatic plates give force from F = ε₀ A V² / (2 d²), but
the area and gap are only known to a few percent, so the scale comes from weights. Procedure: hang
calibrated weights of 1 mg to 50 mg on a known arm radius to produce 10 µN to 500 µN, read the plate
voltage that gives the same deflection, and fit F = c V²; the fit constant c then holds down to the
nanonewton range, with the lever-arm uncertainty and weight tolerance in the budget. The optical
readout's displacement scale is calibrated by moving the flag a known distance with a micrometer stage
or a printed step gauge. The calibration uncertainty and its drift over a campaign (repeat calibrations
at set intervals, temperature dependence of the strip's stiffness) get an explicit budget in the final
paper. The current shunt and the voltage DACs are checked against a reference.

## Electronics (SMT only; WP1–WP3 done, schematic next)

The full requirements, block diagram and the numbers each block is held to are in
[hardware/instrument/requirements.md](../hardware/instrument/requirements.md); the parts are in
[hardware/instrument/parts.md](../hardware/instrument/parts.md) (48 part numbers, all machine-placed SMT, all in stock at 20x
the order's need, 25 of them extended, about $24 of components per board). In outline: an RP2040 on the board, USB-C power
(500 mA budget), two low-noise 3.3 V rails, an ADS131A04 24-bit simultaneous ADC (79 nV/√Hz), a 12-bit quad DAC, a 24 V boost with
an OPA197 plate driver, a 0.3 A device-current sink, two coin-motor drivers, and heads for the optical channel, magnetic field,
temperature and floor motion.

Simulated (ngspice, behavioral op-amps from the data sheets; checks in `hardware/instrument/smoke_test.py`):

| Block | Result |
|-------|--------|
| Photodiode TIA (VBPW34S 70 pF, 10 kΩ, 1 nF) | 79.98 dB at 1 kHz, no peaking, corner 16.8 kHz |
| IR LED current sink, gated from a PIO pin | 20.00 mA at 1.02 V, zero off, edge settles in 0.2 µs, 1.08 V headroom |
| Device-current sink (AOD4184A, 1.5 nF gate, 37 S) | stable across wide corners with a 1 kΩ/10 nF compensation; 0.94 W in the MOSFET at 300 mA (52 K rise) |
| Plate driver (OPA197, gain 5.7, 24 V) | linear to 0.001%, no overshoot with a 10 pF feedback capacitor (8.6% without), peak 22.8 V |

Two things the simulations caught before layout: the first plate-driver feedback had an 8.6% overshoot, and the BOM had a 100 mΩ
shunt where the design needs 1 Ω. Not yet simulated: the ADC's input network, the boost converter's ripple, the regulators' noise.

**A rough cost picture, to be replaced by JLC's quote.** Components about $24 per board (about $120 for five). Assembly fees as
JLC's help pages and a third-party summary describe them (read through a search tool; the pages themselves returned no
fees to this session): economic assembly roughly $8 setup plus a loading fee per extended part (reported as $3, possibly cut to
$1.50 in late 2025), standard assembly about $25 setup plus a loading fee on every part, a stencil fee of $1.50 to $9, and about
$0.0017 per solder joint. The four-layer boards, the head boards and the device cards, and shipping to Canada are on top. As an
order-of-magnitude figure, one assembled order is likely in the low hundreds of dollars, most of it fixed fees: another reason
for one consolidated order and for proving the design on the breadboard balance first (A5).

## Next steps and decisions for the user

See [TODO-agent.md](TODO-agent.md) (work packages WP1–WP11) and the top of
[TODO-arcticoder.md](TODO-arcticoder.md). Decisions: a budget
ceiling for the order; whether to print the balance now (it needs the stainless strip and copper from
the next order) so A5 can measure the real noise before the boards are laid out.
