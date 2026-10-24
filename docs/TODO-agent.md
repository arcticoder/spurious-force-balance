# TODO — agent (Claude-facing)

Work that needs no hands, eyes or purchasing decision from the user: writing files, models, simulations and
documents for this experiment. The user's own list is [TODO-arcticoder.md](TODO-arcticoder.md); finished
items move to [TODO-completed.md](TODO-completed.md) (dated entries). The list conventions are in the `lab`
repo's [todo_list_conventions](https://github.com/arcticoder/lab/blob/main/docs/kb/todo_list_conventions.md).
This repo split out of `lab` on 2026-10-23; Parts A and D below came with it (path fixes only). Part D comes first.

---

## Part D — balance materials review, 2026-10-23 (Opus 5.5 for Sonnet 5.5)

The user put five lines in the AliExpress cart, offered pre-sized acrylic stock or printed clear PETG in
place of custom-cut acrylic, and asked which lines can be checked out. Evaluated here; the user was given the
checkout answer in chat (summarized in D7). Work top to bottom; D1 and D2 change the CAD, so rerun
`hardware/balance/balance.py`, `render.py`, `smoke_test.py` (venv Python) and `tools/force_noise_budget.py`
after them. Standing rule from this review: **design to stock sizes** (whole sheets, standard pads and rods)
instead of asking for custom cuts.

### D1 — Enclosure: redesign around uncut 2 mm acrylic, 150 × 250 mm

Decision: acrylic, not PETG. Reasons (record them in `plan.md`'s A2/enclosure text,
paraphrased): the optical readout (IR LED, photodiode, flag) is all inside the box, so panel clarity only
matters for looking in, not for the measurement; the current 240 × 160 mm walls and the 266 mm lid are larger
than the K1's 220 × 220 mm bed, so printed panels would each need a seam; solid PETG panels would take about a
kilogram of filament the user doesn't have. The user offered 2 mm sheets at 150 × 200, 150 × 250, 100 × 150,
100 × 100, 80 × 80 mm and 1 mm sheets at 100 × 150, 150 × 200, 150 × 250, 200 × 300, 200 × 200 mm. Use **2 mm
at 150 × 250 mm** (1 mm over 250 mm is flexible and would drum).

Checked against the current CAD (bounding boxes, 2026-10-23): the balance's top is the gantry at z = 132 mm;
the base is ±109 mm; the arm is ±100 mm in x and ±14 mm in y; the sensor bracket reaches x = −108 mm and the
damper holder y = 54 mm. So:

- [ ] **Walls:** four uncut 150 × 250 × 2 mm sheets, long edge horizontal, standing on the table, ends held in
      vertical slots in the four corner posts. With 5 mm of each end in a slot, the clear span between post
      faces stays 240 mm (clearance to the base edge stays 11 mm). Wall height 150 mm leaves 18 mm above the
      gantry.
- [ ] **Lid:** two uncut sheets side by side, long edges along x: 250 × 300 mm of cover over a roughly
      244 × 244 mm opening. They rest on the wall tops and the post tops; their meeting seam sits on a
      printed centre rib spanning the box (a 250 mm bar fits the bed diagonally; check with `printability`).
      Make the posts and rib carry the lid level; check the lid's bearing on the wall tops along x (only
      about 3 mm a side), and add a printed ledge on the posts if that is too little.
- [ ] **Seal:** the user's cart has 0.3 mm double-sided PE foam tape, 3 mm wide, 10 m (D6). It doesn't
      compress like a gasket, so use it as a shim: strips on both faces of each wall's vertical edges inside the
      slots. New parameter `SEAL_T = 0.3e-3`; slot width `PANEL_T + 2*SEAL_T + 0.2 mm`. Strips on the wall tops
      and the rib seal the lid. The lid stays removable: tape on the wall tops keeps its liner side up, or
      the lid is taped down only for a run (pick one and write it into the assembly steps). Estimate the tape
      length (about 4 m of the 10 m) and print it. If A5 measures air-current noise above the model's
      assumption, a compressible EVA gasket becomes the next step (put that in the Deferred section, not now).
- [ ] `params.py`: `PANEL_T = 2e-3`, `PANEL_STOCK = (250e-3, 150e-3)`, `SEAL_T`; replace the fixed
      `ENCL_INNER` with values derived from the stock. `balance.py`: posts 150 mm tall, the lid replaced by two
      stock panels plus the printed rib, `panel_cut_list()` returning stock counts.
- [ ] Smoke test: every acrylic panel is an uncut stock sheet (the cut list is exactly six 250 × 150 × 2 mm
      sheets); every printed enclosure part fits the bed; clearance ≥ `ENCL_MIN_CLEARANCE` to the walls and to the
      lid underside; the lid covers the opening in both axes with bearing ≥ 3 mm on every edge.
- [ ] Order line: **7 sheets** (6 plus a spare) of clear 2 mm acrylic, 150 × 250 mm.

### D2 — Damper: the owned N42 discs are magnetized radially; remodel, re-orient, choose the vane thickness

Found in this review, not by the user: the damper uses the ten N42 D6 × 3 mm discs, and both the listing
and `inventory.md` say they are **radially** magnetized (poles on the curved sides). In the CAD the discs are
flat-face to the vane, and `model.disc_field_on_axis()`/`eddy_damping_estimate()` assume **axial**
magnetization, so the damping estimate (ζ ≈ 0.6 at full engagement, 0.3 mm vane) doesn't apply to these
magnets. With radial magnetization, flat-face mounting puts the field mostly in the vane's plane, and eddy
damping goes with the field *through* the vane.

- [ ] Add `magpylib` to `~/.venvs/lab-hw` (record its version in `hardware/README.md`). Cross-check it against
      `disc_field_on_axis()` for an axial disc (it must agree), then model the D6 × 3 mm discs with
      diametric magnetization.
- [ ] Re-orient the discs in the CAD: on edge (axis horizontal), one above and one below the vane, each with
      its N–S diameter vertical, so a curved pole faces the vane; opposite poles face each other across the gap.
      Mounting: printed cradles that let each disc turn freely about its own axis, so the two discs line up by
      attraction during assembly, then fix them (the 0.3 mm double-sided tape, or a printed cap). Write those
      steps into the assembly text.
- [ ] Damping estimate from the modelled field: c = σ t ∫ B⊥² dA over the vane, keeping the existing
      factor-of-two caveat. Also evaluate two discs per side, side by side with alternating poles (ten are owned),
      which raises the field gradient and damping.
- [ ] Choose the vane: the copper pad listing sells **20 × 20 mm at 0.3, 0.5, 0.8 and 1.0 mm** (D6 has the URL).
      Damping can be lowered on the bench (partial engagement, a wider gap) but not raised past full engagement.
      So the full-engagement ζ must be ≥ 0.6 (target 0.5); choose the thinnest variant that meets it, and the
      magnet arrangement too if no single pair is enough. The user has been told to add the 1.0 mm variant
      next to the 0.3 mm one, so both will arrive. Keep ≥ 1 mm of clearance between the vane and each magnet.
- [ ] Vane size 20 × 20 mm (was 20 × 22): it is the pad uncut. At full engagement keep about 2 mm of vane
      beyond the magnets' footprint on every side (eddy currents need the return path); move the damper
      holder in y if needed. Attach the vane to its holder with the 0.3 mm double-sided tape (it is uncut, so
      there is nothing to drill). Re-solve the ballast.
- [ ] Phone-compass check for the user (one line in TODO-arcticoder's "What I need from you"): turn a disc
      about its own axis flat on a table next to a phone's compass app. A full swing of the needle means radial
      magnetization (use the new design); no change means axial (the old flat-face design stands, ζ ≈ 0.6 with
      0.3 mm). Write the CAD so either orientation is one parameter (`MAGNET_MAGNETIZATION = "diametric"`).
- [ ] Smoke test: the magpylib axial cross-check; the vane's full-engagement ζ ≥ 0.6 for the chosen
      thickness and magnetization; vane overhang ≥ 2 mm; vane-to-magnet clearance ≥ 1 mm.

### D3 — Ballast: from the 10 × 100 mm brass rod (uncut), plus trim

The rod is the shortest the listing sells. 18 mm of it is the ballast, which means one saw cut; the user's
inventory has no saw or file.

- [ ] Printed **saw guide**: a V-block with a kerf slot and an end stop at the ballast length plus 0.5 mm, for a
      junior hacksaw. Then filing to length. Add to "Next order" (D7): a junior hacksaw and a flat needle file,
      unless the user already has them (the inventory shows neither).
- [ ] **Printed-part mass uncertainty.** Find out what density `balance.py` uses for printed parts (infill,
      walls). Real prints differ by ±10–20%. Turn that range into a centre-of-mass offset and into the tilt of the
      hanging arm (it changes the plate gap, the vane gap and the flag height), and check them against the
      existing 0.3 mm centre-of-mass check. If the range is wider than that check, the bench trim has to absorb it.
      Free fix: the user reads each printed part's filament mass from the slicer (one line in
      TODO-arcticoder's print item), and `params.py` gets a table of those masses that replaces the density
      estimate.
- [ ] **Trim without new parts:** flat trim pads on the arm at both ends and both sides (in the CAD). Trim weights:
      spare 20 × 20 mm copper pads (about 1.1 g at 0.3 mm, 3.6 g at 1.0 mm) and squares of copper foil tape (about
      0.04 g per cm²). All are non-magnetic. Write a bench balancing procedure that ends with a pass/fail
      reading, using the optical readout or a level line on the arm, so the user isn't left guessing.

### D4 — Strip cutting (0.05 mm 304 sheet, 100 × 1000 mm, in the cart)

- [ ] Printed **strip-cutting guide**: two plates that clamp the shim with exactly 4.0 mm exposed, for scoring
      several passes with a craft knife along a steel edge, then snapping. Length: the 30 mm free length plus
      both clamp lengths (from the CAD). Work out what a ±0.2 mm width error does to κ (∝ w t³ plus the tension
      term); the period measurement calibrates it anyway. Mention deburring with a fine file, because edge
      kinks add anelastic loss. A craft knife and a steel ruler: one "if not owned" order line (they aren't in
      the inventory either).

### D5 — Calibration plates: copper foil tape (10 mm × 1 m, conductive acrylic adhesive, in the cart)

- [ ] Check the electrical path for both plates in the CAD and the text, with no soldering. Moving plate: the
      foil wraps the 20 × 8 mm face and runs along the arm to the lower strip clamp, where the clamp presses its
      copper face against the strip (ground through the strip and the top clamp). Fixed plate: the foil wraps its
      face and runs to an M3 screw, where a washer clamps a ring terminal or a stripped wire onto it. If the
      path needs anything not on hand (ring terminals), add it to D7's order lines.
- [ ] The listing sells single- and double-sided-conductive variants, and the user's selection reads only
      "10mm x 1M". With the clamped joints above, both variants work; a foil-to-foil overlap joint needs the
      conductive adhesive. Design so that no joint depends on the adhesive, and note that in the order record.
- [ ] Keep exposed PLA away from the electrode gap: the foil covers each facing surface and 1 mm past its
      edges. Stray charge on bare plastic near the gap is a known patch-potential term; write it into the
      plan's systematic list if it isn't there.

### D6 — Record the cart (orders.md "In cart"; paraphrase, no listing marketing text)

- [ ] Foam tape: https://www.aliexpress.com/item/1005008202477750.html, variant 10 m / black / 3 mm / 0.3 mm;
      PE foam, double-sided acrylic adhesive, 0.3 mm thick, rated 80 °C. Use: slot shim and lid seal (D1).
- [ ] Copper pads: https://www.aliexpress.com/item/1005002935282949.html, variant 20 × 20 × 0.3 mm, 5 pieces;
      the listing's spec table says "Carbide" (listing noise; the title and description say copper). Arrival
      check: non-magnetic (a disc magnet doesn't pull it). Also the 1.0 mm variant once added (D2).
- [ ] Copper foil tape: https://www.aliexpress.com/item/1005005694527982.html, variant 10 mm × 1 m; 99.98%
      copper, conductive acrylic adhesive per the listing.
- [ ] Brass rod: https://www.aliexpress.com/item/1005005771688003.html, variant 10 × 100 mm, 1 piece; length
      ±1–5 mm per the listing.
- [ ] Inventory "On Order" rows go in when the user says it's checked out, not before.

### D7 — TODO-arcticoder.md

- [ ] Remove "What I need from you" item 1 (ADS1115): the user had already shelved it. Replace it with the
      phone-compass check (D2), one line, if D2 isn't settled by then.
- [ ] "Next order": mark as in the cart the stainless sheet, foam tape, copper pads 0.3 mm, copper foil tape
      and brass rod. Still to add before checkout: copper pads 20 × 20 × 1.0 mm (same listing as the 0.3 mm);
      7 × clear acrylic 2 mm 150 × 250 mm; M3 flat washers 304, 50; M3 hex nuts 304, 20; calibration weights
      1 mg–500 mg; and, if not owned, a junior hacksaw, a flat needle file, a craft knife and a steel ruler. Then
      check out as one order. Remove the 3 mm acrylic and 3 mm foam lines.
- [ ] Print item: new part names after D1–D4 (posts 150 mm, lid rib, magnet cradles, saw guide, strip guide),
      and a request for the slicer's mass per part (D3).


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

