# TODO — agent (Claude-facing)

Work that needs no hands, eyes or purchasing decision from the user: writing files, models, simulations and
documents for this experiment. The user's own list is [TODO-arcticoder.md](TODO-arcticoder.md); finished
items move to [TODO-completed.md](TODO-completed.md) (dated entries). The list conventions are in the `lab`
repo's [todo_list_conventions](https://github.com/arcticoder/lab/blob/main/docs/kb/todo_list_conventions.md).
This repo split out of `lab` on 2026-10-23; Parts A and D came with it (path fixes only). Part F (2026-10-24) comes first; Part D is done; then Part A's WP4 (schematic) onward, and A5 once the user has built the balance.

---

## Part F — licenses, the magnet test, the placed order, and a fabrication review (Opus 5.5 for Sonnet 5.5, 2026-10-24; do this first)

The user replied on five points. F1–F3 are bookkeeping. F4 is the real work: the user prints PLA only at home (fumes from ABS,
PETG and nylon rule the others out) and asked whether any part is better made by a fab service (JLCPCB's PCBs, JLC3DP, JLCCNC,
others) than bought on AliExpress and cut by hand. The question is weighed by material plus time cost against the risk that a
hand-made part adds noise or error to the experiment. Opus did the analysis below and made the decisions; Sonnet carries them
out. Work top to bottom.

### F1 — Licenses: CERN-OHL-P v2 for hardware, MIT for code, in this repo and in `lab`

- [ ] In both repos, add `LICENSE` (MIT, "Copyright (c) 2026 Arcticoder") and `LICENSE-HARDWARE` (the CERN-OHL-P v2 text,
      fetched verbatim from `https://ohwr.org/cern_ohl_p_v2.txt`; check the first lines read "CERN Open Hardware Licence Version 2 -
      Permissive"). GitHub's license detection reads `LICENSE`, so the repo badge will say MIT; the README carries the split.
- [ ] README "License" section in both, saying which files fall under which license:
      - **MIT:** code, meaning `*.py`, MicroPython `main.py`/`diagnose_*.py`, `tools/`.
      - **CERN-OHL-P-2.0:** hardware sources and their documentation, meaning CadQuery sources' outputs (STL, STEP), KiCad files,
        SPICE netlists, BOMs/parts tables, breadboard guides, assembly and build docs.
      - CadQuery `.py` files are code (MIT) whose output is hardware (CERN-OHL-P). Say so in one line.
- [ ] Remove "Pick a license" from this repo's TODO-arcticoder. Note the decision in `TODO-completed.md` in both repos.
      Commit and push both (the user asked for licenses in both; push `lab` only with its own pending changes reviewed first:
      `git -C ../lab status`).

### F2 — Magnet test: the phone result is inconclusive; replace it with a test that needs no phone

What the user saw: the needle moved a little as the disc turned and settled back. The disc couldn't come closer than 2–3 cm,
because it stuck to steel inside the phone. The compass sensor's position in a Pixel 9 is unknown. Reading it:
- At 3 cm from the sensor, a 6 × 3 mm N42 disc (0.089 A·m²) makes about 0.3–0.7 mT, ten times the Earth's field. A diametric
  disc turned there would drag the needle all the way round.
- At 10 cm it makes about 10–20 µT, below the Earth's field: a small wobble either way.
- So the result says only that the sensor was far from the disc. It doesn't tell axial from diametric.
- Compass apps also smooth their readings. A strong magnet near the phone can leave a hard-iron offset, so if the compass misbehaves
  afterwards, the user recalibrates it with the figure-of-eight motion. Nothing is damaged.

- [ ] TODO-arcticoder "What I need from you", replacing the compass item:
      - **Twist test.** Stack two discs flat face to flat face and hold the bottom one. Turn the top one about the common axis.
        If it springs back to one angle (a detent once per turn), they're magnetized across the diameter. If it turns freely with no
        preferred angle, they're axial (an axial pair is symmetric about the axis, so there's no torque).
      - **Nut check, to confirm.** Touch a black carbon-steel M3 nut to the disc. Axial: it jumps to the centre of a flat face.
        Diametric: it's pulled to two opposite points on the curved side.
      - The user answers with one word: "detent" or "free".
- [ ] Make the CAD ready for either answer. Add an axial layout to the damper holder (flat discs facing the vane, pockets with a
      retaining lip, the same 1.4 mm to the vane mid-plane), selected by `MAGNET_MAGNETIZATION`. `model.eddy_damping_field()`
      already handles both. The smoke test checks ζ for whichever layout is selected.

### F3 — The order: five lines placed 2026-10-24

The user placed the AliExpress order for the 0.05 mm 304 stainless sheet, the foam tape (3 mm × 10 m × 0.3 mm), the copper pads
(20 × 20 × 0.3 mm, 5), the copper foil tape (10 mm × 1 m) and the brass rod (10 × 100 mm).
- [ ] `lab/docs/orders.md`: move the five entries from "In cart" to an ordered section dated 2026-10-24.
      `lab/docs/inventory.md` "On Order": one row each (bag to assign on arrival).
- [ ] This repo's TODO-arcticoder: an "En route" section (after the actionable sections, per lab's conventions) listing the five.
      Remove them from "Next order".

### F4 — Fabrication review: what to make, buy or print, and the design gaps the review found

Write the decision record as `docs/fabrication.md` (for a reader of the repo, not chat style). It holds a per-part table (function,
what it does to the measurement, current method, failure mode, options, cost and time estimates, decision) and the reasoning
below. Cost figures not read from a live quote page are marked "[estimate; verify on the quote page]". Sonnet can't open JLC's
interactive quote pages, so the user confirms totals before ordering.

**F4.1 — Design gaps found by this review (true whatever the fabrication route; fix them in the redesign):**

1. **No zero adjustment (a torsion head).** The 1 mm electrode gap at 80 mm allows only ±0.4° of arm rotation, and the flag and
   vane need the arm near its design angle. A strip clamped by hand will sit some degrees off. Every torsion balance carries a
   rotatable fibre head for this.
   - Add a torsion head at the top clamp: ±5° of range, about 0.05° resolution, lockable.
   - Suggested form: a disc turned by an M3 screw pushing a 40 mm lever against a spring (a printed flexure, or a rubber band
     hooked on two posts). It's locked by two screws clamping it to the gantry beam through arc slots, with metal (washer)
     faces at the lock.
   - Smoke test: the range covers ±5°; one screw turn (0.5 mm pitch over a 40 mm lever, about 0.7°) is under 1°, so finer
     setting is a fraction of a turn.
   - Assembly step: set the zero by centring the flag before the plates are brought within 5 mm (the fixed plate's bracket gets a
     slot so it slides in after zeroing).
2. **A dissipating device can't sit on PLA.** G1's device cards dissipate up to about 0.9 W (300 mA in 10 Ω) on the arm. A 20 ×
   30 mm card in still air (about 10 W/m²K on both faces) warms by about 80 K/W, so 0.2 W is about +17 K and 0.9 W about +75 K.
   PLA softens around 55–60 °C, so a PLA mount near the card creeps, synchronously with the device's power. That is exactly the
   thermal term the experiment measures, so the instrument would add its own artifact.
   - The device mount and the arm near it must be FR4 (glass transition 130 °C or more; JLC sells higher-Tg FR4, 155/170
     [verify]).
   - The DUT card must stand off the arm on a short thermal break.
   - Add a check that the card's estimated temperature at the planned top power stays 40 K under the mount's Tg. If it doesn't,
     cap the power in `params.py` and in the plan's G1 table.
3. **Self-tapping screws into PLA in the torsion path.** Both strip clamps' half-a screws thread into PLA pilot holes, and PLA creeps
   under the bolt preload. As the joints relax, the clamps rotate a little, and that is zero drift with no signature. Every joint
   between the strip and the arm, and between the strip and the gantry, becomes a through-bolt with a nut and washers.
   Clamping faces are metal or FR4, never PLA.
4. **Centre-of-mass tilt.** It is 66 mrad per mm of offset, against 16 mrad of clearance, so the centre of mass has to sit within
   about 0.1 mm of the axis. The ±15% mass uncertainty of printed parts is the main source. Two levers:
   - Make the moving parts from materials with known density in a symmetric layout (F4.2), so a uniform density error moves
     nothing.
   - Lower the centre of mass relative to the strip's lower end (hang 15 mm today; tilt = offset / hang). Aim for 30 mm or more,
     by hanging the heavy parts low (ballast and device card below the arm plane) and putting the clamp high on the arm.
   - Report the new mrad-per-mm figure and check it against the clearances in the smoke test.

**F4.2 — Decisions (Opus's call, made on the criteria the user set; record them in `fabrication.md` and `plan.md`):**

| Part | Decision | Why |
|---|---|---|
| Arm, with the flag and the moving electrode | **FR4 PCB from JLCPCB**, 1.6 mm (or 2.0 mm [verify the options]), black solder mask, ENIG finish, no components. One board, symmetric about the axis. | In-plane CTE about 14 ppm/K against PLA's 70 (the budget's arm-expansion term already sweeps 70→23→1 ppm/K). Tg 130 °C+ (gap 2). Density known (FR4 about 1.85 g/cm³, board thickness ±10% scales a symmetric arm uniformly, so the centre of mass doesn't move; gap 4). The routed edge is a straight flag edge. Copper pours on both faces under black mask make the flag opaque (bare FR4 passes IR, so this matters). The moving electrode is an ENIG pad, and a trace runs to the strip clamp's pad, so the foil route and its 0.3 g asymmetric mass go away. Machined to about ±0.1–0.2 mm with no user labour. |
| Strip clamp plates (top and bottom, four pieces) | **FR4 PCB** small boards (or one panel of them) with ENIG clamping pads. | FR4 doesn't creep like PLA (gap 3). The ENIG pad gives the strip's electrical contact, so the ground path is copper and clamp pressure, not tape adhesive. |
| Fixed electrode | **FR4 PCB**: ENIG pad 20 × 8 mm with a grounded guard ring (a Kelvin guard: it pins the field edge, so the effective area is the pad's) and a plated M3 hole as the wire terminal (wire under a washer, no solder). | The calibration plates are the instrument's absolute force reference. Copper tape on a PLA face has uncertain flatness (±0.1 mm over 20 mm is ±10% of the gap, ±20% of the force), adhesive at the edges and oxidizing copper (patch potentials). A PCB pad is flat, gold-faced and has a defined area. Also evaluate (as a note in `plan.md`, not a design change yet) measuring the plates' capacitance on the fab board, which gives F = ½V² dC/dx (the electrostatic force-balance method). Check the JLC library for a CDC part (AD7746, FDC1004) and record stock and price. |
| Device-card mount (thermal break) | **FR4 PCB** standoff tab, part of the arm or a small board. | Gap 2. |
| Base, gantry, sensor bracket, damper holder, electrode bracket, enclosure posts and shelves, jigs | **Keep PLA on the K1.** | Fixed parts: their thermal motion is slow, and the lock-in at 0.05 Hz rejects it (0.31 nN/K of apparent force from 100 mm of PLA at 70 ppm/K, times 1 mK/√Hz, is far under the air-current term; record this number). The torsion-path joints become through-bolts (gap 3). The damper holder carries the magnets' attraction: compute it with magpylib's force function (check the version supports it) and check the cradle lips' stress against a long-term PLA creep allowance (about 5 MPa [assume, cite a source if one is found]); thicken them if needed. |
| Enclosure | **Acrylic from AliExpress (stock 2 mm, 150 × 250 mm, 7 sheets)**, as designed. | Already cut-free and cheap. Fab'd acrylic adds nothing. |
| Ballast | Decide after the FR4 arm is designed (its mass changes). In order of preference: (a) a standard brass part, used whole, if one fits the mass and keeps the centre of mass low (brass M3 standoffs, nuts or washers stacked on a 304 screw: count the stack height against the hang, gap 4); (b) one saw cut from the rod already ordered, with the saw guide (needs a junior hacksaw and a file, about $5–8 on AliExpress, tools the user keeps); (c) a JLCCNC brass part, only if a JLC mechanical order is happening anyway and its marginal cost is under (b)'s tools. | The trim absorbs a ±0.2 mm hand-cut error (±1% of the ballast's mass), so precision isn't the deciding factor; cost and labour are. |
| Torsion strip | **Hand-cut from the ordered sheet with the printed guide**, as designed. | κ is calibrated from the measured period, so a ±0.2 mm width error doesn't matter. Edge quality affects anelastic loss (drift, 1/f noise). A5 measures the quality factor and drift. Fallback, if A5 shows a low Q or creep: photo-etched strip (stress-free, burr-free edges; find a service, and check whether JLC's laser-cut stainless stencils come in 0.05 mm [verify; they are likely 0.08–0.2 mm, which would need a narrower strip for the same κ ∝ w t³]). Record the fallback; don't act on it. |
| Vane | **The ordered copper pad, uncut.** | Already right. |
| Copper foil tape (ordered) | Becomes trim material and a spare ground strap. | The FR4 parts make it unnecessary for the plates. |
| JLC3DP / JLCCNC parts | **None for now.** | No part left on PLA needs a non-PLA print or a machined part once the above is done. Revisit only if a PLA part fails a creep, stress or tolerance check (the damper lips, the torsion head). JLC3DP's SLA and MJF are the first choices then, since the user can't print those materials at home. |

**F4.3 — Order logistics (a decision for the user, put to them in one line):**
- **Two JLC orders.** A mechanical-boards order now (unassembled FR4: arm, clamp plates, fixed electrode, device-card tab), and the
  electronics order after A5, as planned.
  - Reason: A5 should measure the mechanics the experiment will use. A PLA prototype measured at A5 and then rebuilt in FR4 would
    leave A5's drift and thermal results not transferring.
  - Cost: one extra JLC shipment [estimate shipping and the board cost from JLC's published pricing; verify].
  - Unassembled boards have no setup or extended-part fees.
  - Note the panel rule: different designs on one board usually cost extra; compare that with separate small boards.
  - Check whether JLC ships PCB, 3D-print and CNC items in one parcel if any non-PCB part is added [verify].
- **AliExpress:** hold the remaining lines (washers, 304 nuts, JST-SH cable, weights, tools) until the redesign fixes the fastener
  list. The fastener counts will change with through-bolts and the torsion head; M3×16/20 may be needed, so check what the owned
  10/12/14 mm screws cover. Then it's one AliExpress order with no single-item fees. The acrylic doesn't change and can go in that
  same order.
- **Printing:** tell the user to hold all printing until the redesign lands. The fixed parts' geometry moves with the FR4 arm (gantry
  height, bracket positions).

**F4.4 — The redesign (Sonnet's work after writing `fabrication.md`):**
- [ ] `hardware/balance/`:
  - The arm as a 2D board outline plus thickness (from `params.py`), with copper features: electrode pad, ground trace, flag pour,
    clamp pads.
  - Clamp plates, fixed electrode board and device tab as boards.
  - The torsion head, through-bolted joints, lowered centre of mass.
  - Re-solve the ballast; rerun every check: collisions over the swing (with the torsion head's range), tilt per mm, ζ, enclosure,
    fasteners against owned stock, printability.
- [ ] Board outputs:
  - Generate each mechanical board as a KiCad PCB (outline on Edge.Cuts, pads and pours, plated M3 holes) with `kiutils` from the
    same CadQuery numbers, so the CAD and the boards can't disagree.
  - `kicad-cli pcb drc` clean against JLC's published rules (min drill, annular ring, copper-to-edge).
  - Gerbers and drill in `hardware/balance/boards/fab/`, an order note per board (thickness, finish, mask colour, quantity 5).
  - A render with `kicad-cli pcb render`.
  - Smoke test: board outline equals the CAD's outline; holes match the CAD's bolt positions to 0.01 mm.
- [ ] Mass model: FR4 1.85 g/cm³ and 35 µm copper per layer (1 oz) for the boards. The slicer-mass step stays only for printed
      moving parts, if any are left.
- [ ] Update `docs/assembly.md`, `plan.md` (G2 table, design decisions, the metrology section's plate description, the
      artifacts list), the README status, and this repo's TODO-arcticoder:
      - the JLC mechanical order as a "Next order" entry with board list and estimated cost;
      - the revised AliExpress list;
      - the print list (fixed parts only);
      - the hold notice.
- [ ] Commit and push this repo when the checks pass.

### F5 — Memory (Sonnet, after F4)

- [ ] A user-preference memory: home printing is PLA only (fumes rule out ABS, PETG and nylon). Fab services (JLC PCB as structure,
      JLC3DP, JLCCNC) are in scope when they beat buying and hand-cutting on cost, time or measurement risk. Link
      `feedback_design_to_stock_sizes`.

## Part D — balance materials review (done 2026-10-23; details in TODO-completed.md)

D1–D7 are finished and recorded. Standing rule from the review: **design to stock sizes**. What a later session needs to remember:

- The enclosure is six uncut 2 mm, 150 × 250 mm acrylic sheets (four pinwheel walls, inner span 248 mm; a two-sheet lid on printed shelves).
- The damper uses four radially magnetized N42 discs standing on edge, modelled with magpylib; one 0.3 mm copper pad gives ζ 0.45, two give 0.90
  (so the 1.0 mm pad is not needed). If the user's compass check says the discs are axial, set `MAGNET_MAGNETIZATION = "axial"` (the cradles
  would then need a rework: they are built for edge-on discs).
- Centre-of-mass offset tilts the arm 66 mrad per mm (it hangs 15 mm below the strip), against about 16 mrad of clearance; slicer masses in
  `PRINTED_MASS_G` and a bench trim are required. A y-trim seat does not exist (y errors should be small); add one if A5 needs it.
- The `lab` repo's ledger lists the cart items; checkout is the user's. Update `inventory.md` "On Order" when they say it is checked out.
- Open for WP4 and later: the plate driver's JST-SH output cable and where the strip ground returns on the board (one GND pin).

---

### Part A — a fabricated, fully assembled research instrument (JLCPCB)

**What changed.** The user stops hand soldering (header bridges again on the
ADS1115 on 2026-10-22; the braid stuck instead of wicking) and wants boards
designed in KiCad, analog blocks validated in ngspice (KiCad's simulator is
ngspice; LTspice is optional), and manufacturing files exported for a fully
assembled JLCPCB order. The result must be an instrument that can support a
publishable (arXiv-level) experimental study, not a set of one-circuit boards.

**Progress, 2026-10-22 (Sonnet 5.5 session; details in `docs/plan.md`):**
- A0 done (scope note in `kb/circuit_lifecycle_and_repo_scope.md`, memory updated).
- G1 proposed, awaiting the user's one-line confirmation. G2 done as a first cut: `hardware/balance/`
  (parametric CadQuery model, analytic model, render, smoke test; mass, inertia and centre of mass solved
  from the CAD; no collisions over the swing). G3 done: `tools/force_noise_budget.py` reproduces six
  published numbers, predicts 0.11 nN (1σ, 1000 s, in air), conditional GO; air currents decide it (flips
  at 4 mm/s fluctuation).
- Findings that change this plan: **no permanent magnet on the arm** (an N42 disc is 7 nN/√Hz of field
  noise; the damper magnets are fixed to the base) so the coil calibration below is replaced by
  **electrostatic plates** (grounded through the strip, no lead, no moment), transferred to absolute force
  with weights or wire riders; the readout (5 pN/√Hz) is far below the environment, so the electronics need
  not be exotic. Lead current is limited by USB to about 0.4 A.
- A4 toolchain done (KiCad 7 + venv with SKiDL, kiutils, easyeda2kicad, CadQuery; Freerouting 2.5.0; JLC parts
  snapshot); KiCad was upgraded to 9.0.9 on 2026-10-23, so `kicad-cli sch erc` / `pcb drc` / `pcb render` are available.
- A5 (prototype before layout) needs the user: the print, the materials order, the lock-in and optical readout.
- WP1 (requirements, pin map, USB power budget), WP2 (48 JLC-stocked parts, all machine-placed SMT, 25 extended) and
  WP3 (TIA, LED sink, device-current sink, plate driver in ngspice) are done: `hardware/instrument/`. WP3 caught an 8.6%
  plate-driver overshoot and a wrong shunt value in the BOM. **Next: WP4 (schematic).** It needs: the Raspberry Pi RP2040
  hardware design reference (fetch from datasheets.raspberrypi.com and follow it for the crystal, flash and USB), the ADS131A04's
  pin table and input network (datasheet pages on AVSS/VNCP and the reference), symbols and footprints from `easyeda2kicad` by
  LCSC number, and a SKiDL description with connectivity checks (every IC pin accounted for). ERC is `kicad-cli sch erc` (KiCad 9.0.9) plus a pin-table test. WP5 (layout) and WP7 (order) wait on A5
  per the plan's own rule.

**Hard constraints:**
- **All electronic parts are SMT parts sourced and placed by JLCPCB** from its own
  library. The user does not mail parts to the fab, so the through-hole parts on
  hand (49E/SS49E, PT334-6C, MF52AT, 5mm LEDs, leaded piezo) are not part of the
  design; their roles go to JLC-stocked SMT equivalents (for example a SOT-23
  linear Hall sensor, an SMD photodiode, 0603 NTCs, an SMD LED or IR emitter, a
  MEMS accelerometer). Purely mechanical items that need no soldering (the N42
  discs as a calibration target, the coin motors' flying leads into a
  fab-assembled screw terminal) may still be used where they fit, but nothing
  depends on them.
- **No soldering by the user.** Sensor heads are separate small JLC-assembled SMT
  boards joined to the main board by cables (check what pre-crimped cable JLC or an
  AliExpress cart in the same order window can supply, so nothing needs crimping).
- **One consolidated order** (shipping paid once), USB-powered, everything under the
  repo's 50V DC / 30V AC line.
- **No schematic, parts table or layout before the three gates in A1 pass.**

#### A0. Record the scope change (first, small)

- [ ] Update `kb/circuit_lifecycle_and_repo_scope.md` and the memory
      `lab_circuit_ephemeral_and_repo_scope` (no quotes): the repo now aims at a
      fabricated research instrument for a publishable study; breadboard builds
      become validation steps; ranking for this work may use research value.
      Feedback memories: the user does no more hand soldering, and fab orders use
      only the fab's own SMT parts (no customer-supplied parts).

#### A1. Three gates before any electronics design

These define the scientific value; the electronics only implement them. Results go
in `docs/plan.md` (user-facing), with the calculations in a
script (`tools/force_noise_budget.py`, pass/fail smoke test like the circuits).

- [ ] **G1 — Measurement goal (one paragraph, then the user confirms it).** State
      the claim the instrument supports if it meets its predicted performance. A
      bare "build an instrument" goal is not enough; the question must be specific
      and answerable at the achievable sensitivity. Recommended default to propose:
      *quantify the spurious-force mechanisms that have produced false positives in
      the small-thrust literature (current in the device's power leads interacting
      with the ambient and geomagnetic field, ohmic heating and thermal expansion,
      convection) on an open, low-cost, fully SMT-assembled balance, with the
      power-feed geometry and current as the controlled variables*, alongside the
      instrument claim (for example: an open µN-scale force balance with
      characterized vibrational, thermal and magnetic couplings at a parts cost
      under $X). The cited literature in `spacetime_circuits_dependency.md` is where
      those mechanisms are documented; cite the specific papers. Fill in $X and the
      force scale from G3, not before.
- [ ] **G2 — First mechanical design, with a model.** The mechanics are the
      experiment, so this comes before the PCB. A concrete design (OpenSCAD or
      CadQuery source in the repo, printable on the K1): balance type (beam on a
      knife edge or flexure, or a torsion pendulum on a fibre or flexure pivot), arm
      lengths, pivot stiffness (flexure geometry and material), mass and moment of
      inertia, resonant frequency and Q, the displacement-to-force conversion, the
      calibration actuator's position and lever arm, sensor locations (optical
      readout at the arm's end, accelerometer on the base, field and temperature
      sensors near the device under test), and the isolation concept (a printed
      or bought passive stage; what `VIBISO` becomes). An analytic model at
      minimum (spring constant, resonance, thermal-expansion paths of PLA versus
      a stiffer material, the magnetic coupling geometry of the calibration
      coil); FEA where the analytic model is doubtful. The PCB's mounting holes,
      head-board sizes and connector positions are then set by this design.
- [ ] **G3 — End-to-end force-noise prediction and a go/no-go.** Chain every noise
      source to force: photodiode shot noise and LED intensity noise; TIA thermal
      and op-amp voltage/current noise; ADC noise; digital lock-in bandwidth; then
      displacement noise, through the mechanical transfer function of G2, to force
      noise in N/√Hz versus frequency. Add the environmental terms: floor
      vibration (seismic/building noise spectra from the literature, attenuated by
      the isolation concept), thermal drift (temperature spectrum × expansion
      coefficients), air currents, magnetic noise × the balance's magnetic moment.
      Compare against `tools/resolution_budget.py`'s table and against at least two
      published balances from the cited papers (take their reported noise floors
      from the papers, don't recall them). **Go/no-go:** if the predicted floor
      can't support G1's claim, change the mechanics, optics or environment (G2/A2)
      and repeat; don't proceed to parts or schematic until it does. Record the
      decision and the numbers.

#### A2. Environment control and absolute metrology (plan them; cost them)

- [ ] **Environment.** For each dominant term from G3, a control and its expected
      suppression: a closed enclosure against air currents (printed or acrylic box,
      draught shield), thermal mass and insulation with logged temperatures, a
      magnetic strategy (passive mu-metal is costly; active compensation with a
      Helmholtz pair driven by the board's coil driver, fed back from the field
      sensor, is the low-cost option; at minimum, measure and report the field),
      a heavy reference surface on soft feet, and vacuum flagged explicitly as out
      of scope for the first iteration with its expected effect stated (air damping
      and convection). Only the controls G3 shows to be necessary for G1 go into
      the first build.
- [ ] **Absolute calibration and uncertainty budget.** The coil-and-magnet actuator
      is a relative calibration; establish the absolute scale independently. Two
      candidates: (1) a known force from gravity, by tilting the balance a measured
      angle (measured with the board's accelerometer) or by placing small known
      masses; (2) the coil's force constant measured against (1), then used in-situ.
      Current measured on a precision shunt (0.1% or better, characterized against
      a reference), displacement scale from the optical readout calibrated with a
      known displacement (a micrometer stage or a printed step gauge). Write the
      uncertainty budget for the calibration constant, and for its drift over a
      measurement campaign (repeat calibration intervals, temperature dependence).

#### A3. Architecture (after the gates; verify every part before committing)

Main board, 4-layer (signal / GND / power / signal), size set by G2, plus small
SMT sensor-head boards in the same order:

- **MCU: RP2040 on the board** from Raspberry Pi's published minimal design (fetch
  their KiCad files from the "Hardware design with RP2040" document; check the
  licence): QSPI flash, 12MHz crystal, USB-C, BOOTSEL and RESET buttons, SWD pads.
  Keeps every RP2040 register address this repo's code uses (not RP2350: see
  `kb/rp2350_notes.md`). Fallback if layout risk looks too high: a Pico socket.
- **Power:** USB-C 5V in (ESD protection, polyfuse), separate 3.3V regulators for
  digital and analog (low-noise LDO for analog), ferrite split, one ground plane
  with a defined star point near the ADC. G3 sets how low the analog rail's noise
  must be.
- **Precision ADC:** compare ADS131M04 (24-bit, 4 simultaneous channels, up to
  32kSa/s, SPI: fits the digital lock-in and vibration channels; read by PIO+DMA per
  `kb/rp2040_performance_notes.md`), ADS1220 (24-bit, slower) and ADS1115 (too slow
  for a kHz lock-in). G3 decides whether its noise matters. Slow housekeeping on
  the RP2040's own ADC.
- **Op-amps:** rail-to-rail CMOS parts JLC stocks (candidates: OPA2376, OPA2333,
  TLV9062, MCP6022), chosen on G3's noise numbers; simulate with the vendor's model.
- **Front ends**, all SMT, on the main board or the heads per G2's sensor
  locations:
  1. Optical readout (number of channels from G2): modulated SMD LED or IR emitter
     with a DAC-set current sink (PIO-gated), SMD photodiode, TIA and anti-alias
     filter into the ADC; demodulated in firmware (digital lock-in).
  2. Magnetic field: SMD linear Hall sensors (or a 3-axis magnetometer chip if G3
     needs better resolution) near the device under test; ratiometric amplifier with
     a DAC-set null where an analog sensor is used.
  3. Vibration: MEMS accelerometer on the base (noise density chosen from G3;
     ADXL355-class if needed) and optionally one on the beam.
  4. Temperature: 0603 NTCs or digital temperature sensors at the points G2/G3 name.
- **Actuators and stimulus:**
  1. Electrostatic plate driver (replaces the coil: see the progress note): a DAC-set op-amp stage
     on a boosted rail, 0 to about 24 V (2 µN with the G2 plates), reading its own output
     through a divider into the ADC. Active magnetic compensation, if A2 adopts it, would use a
     separate coil driver on the board, not on the arm.
  2. Disturbance injection: drivers for vibration actuators (the coin motors via a
     screw terminal, or a JLC-stocked SMD motor/buzzer if preferred) and a
     controllable heater (SMD resistor) for thermal-coupling tests.
  3. Test currents for G1's spurious-force study: a driver that passes a known
     current through a dummy load and leads of chosen geometry.
  4. Stimulus DAC: a DC-capable DAC chip is required (LED current, coil current,
     Hall null); the PIO+DMA R-2R (`signal_generator_r2r`) is optional and costs 8
     GPIOs.
- **Bring-up aids:** labelled test pads on every analog node, SWD header, status
  LEDs, spare-GPIO header, mounting holes from G2.
- **Pin budget** early: 30 GPIOs for ADC SPI, DAC, LED modulation, actuator PWMs,
  I2C, housekeeping ADC pins.

#### A4. Toolchain in WSL (verify each step and record versions)

- [ ] KiCad 8 or 9 with `kicad-cli` (`sch erc`, `pcb drc`, export of
      Gerbers/drill/positions/BOM/PDF, `pcb render` to PNG for in-session visual
      review).
- [ ] Parts data: `easyeda2kicad` (symbols/footprints/3D by LCSC number) and the
      `jlcparts` database (stock, basic versus extended; extended parts carry a
      per-part setup fee, so count them).
- [ ] Design entry: script-generated netlist (SKiDL) imported into pcbnew, or KiCad
      schematics written through a file library such as `kiutils`. Criteria: ERC
      runs, a readable PDF schematic comes out, edits are diffable.
- [ ] Routing: critical nets (USB pair, crystal, ADC inputs, reference, TIA inputs)
      placed and routed deliberately; the rest may go through Freerouting. Design
      rules from JLC's current published capabilities (fetched, not recalled).
- [ ] Simulation: ngspice with vendor op-amp models (`set ngbehavior=ps` for
      PSpice-format models); every analog block gets a netlist and a pass/fail
      `smoke_test.py`.
- [ ] Mechanics: OpenSCAD or CadQuery in the repo, with a script that exports STLs
      and computes the G2 model numbers from the same parameters.

#### A5. Prototype check before the order (de-risks iteration)

- [ ] Before committing to layout, test G2's mechanics and the optical readout's
      displacement sensitivity with what is already on the bench: a printed beam,
      the breadboard optical readout and lock-in (`optical_shadow_readout`, no
      soldering), the Pico. Compare the measured resonance, Q and displacement noise
      with the G2/G3 predictions. A disagreement over a factor of a few sends the
      design back to G2/G3, not to the fab.

#### A6. Work packages (after A1–A5, each PR-sized, in order)

- [ ] WP1 — Requirements, block diagram, pin budget, power budget (USB 500mA versus
      coil, heater and actuators), all traced to G1–G3.
- [ ] WP2 — Part selection table (`hardware/<board>/parts.md`): LCSC number,
      basic/extended, stock, price, datasheet limits at 3.3V, noise figures used in
      G3, vendor SPICE model location.
- [ ] WP3 — Simulations of each analog block with the chosen parts; check each
      against its G3 noise allocation.
- [ ] WP4 — Schematic, hierarchical by block; ERC clean; PDF committed.
- [ ] WP5 — Layout: RP2040 per the reference layout, ADC per its datasheet, analog
      and digital partition, decoupling, USB pair, mounting holes and connector
      positions from G2, silkscreen pin names; DRC clean against JLC's rules.
- [ ] WP6 — Visual review from `kicad-cli pcb render` images and a written checklist.
- [ ] WP7 — Fabrication outputs in `hardware/<board>/fab/`: Gerbers + drill, BOM and
      CPL in JLC's format (rotations checked against JLC's placement preview), and an
      order-settings README (layers, thickness, finish, assembly sides, quantity
      minimums checked at the time).
- [ ] WP8 — Firmware and host software: bring-up scripts per block with
      `[PASS]`/`[FAIL]` lines; fixed-point digital lock-in; ADC by PIO+DMA; USB
      streaming to a host-side Python logger (timestamped CSV or HDF5); analysis
      scripts that produce the G1 numbers (noise spectra, calibration, coupling
      coefficients with uncertainties).
- [ ] WP9 — Bring-up and experiment procedures for the user, including the
      calibration sequence from A2 (electrostatic plates against weights or wire riders) and the measurement campaign (durations,
      repeats, conditions logged).
- [ ] WP10 — The order: a "Next order" entry in `TODO-arcticoder.md` with the JLC
      upload steps and settings (the user gets the quote), plus off-board items
      (coil, cables, enclosure materials, calibration masses) for an AliExpress cart
      in the same window.
- [ ] WP11 — The paper: a LaTeX skeleton (`docs/paper/`) started at G1 and filled as
      results come in: apparatus (from G2/A3), noise model (G3) against measurement,
      calibration and its uncertainty (A2), systematics, the G1 result, and
      open-source availability.

#### A7. Decisions to put to the user (one line each in TODO-arcticoder, when reached)

The G1 measurement goal; the G3 go/no-go outcome; which environment controls the
first build includes (A2); a budget ceiling for the order; RP2040 on the board
versus a Pico socket; the coil's source; whether the on-hand coin motors and N42
discs are used as off-board mechanical parts.

