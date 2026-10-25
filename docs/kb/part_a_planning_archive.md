# Archive: Part A planning and the finished Parts D, F, G, H (moved out of TODO-agent.md on 2026-10-24)

Audience: future LLM sessions. This is the verbatim planning text of the instrument project (hard constraints, gates G1-G3, environment and metrology plan,
architecture, toolchain) and the notes of finished Parts D, F, G and H. The open work is in `docs/TODO-agent.md`; dated outcomes are in `docs/TODO-completed.md`;
the current state of each topic is in the other notes of this folder. Unchecked boxes below are historical: WP1-WP4 and G1-G3 were completed (see TODO-completed.md).

## Part H — live JLC/LCSC part lookups (done 2026-10-24; details in TODO-completed.md)

The `jlc` CLI (`@jlcpcb/cli` 0.5.0, chosen over the MCP server) is installed; `parts.py --live` is the pre-order check (usage and quirks in `kb/pcb_toolchain_notes.md`). Decision from H5: **the electronics
order uses Standard PCBA**, because the magnetometer (C404329) and accelerometer (C189624) are Standard-only; `parts.py` records the accepted exception and the fallbacks. Run `parts.py --live` again
before WP7 (stock and PCBA flags change).

---

## Parts F and G — fabrication review, licenses, knowledge base (done 2026-10-24; details in TODO-completed.md)

What a later session needs to remember:
- The balance is now an FR4 arm board on edge with FR4 clamp plates and a fixed electrode board (JLC mechanical order, four designs), a torsion head, printed fixed frame, a 0.5 W device-card cap; decisions and numbers in
  `fabrication.md` and `kb/balance_design_notes.md`. The twist test on the discs is pending (`MAGNET_MAGNETIZATION`, default diametric; the axial layout is in the CAD too).
- JLC ordering rules and this repo's order plan: `kb/fab_ordering_notes.md`. Two JLC shipments (mechanical now, electronics after A5). The arm board's quote is the one thing to watch (about $60 / 0.29 kg).
- `kb/session_handoff.md` has the current state and the next three tasks; replace it at each handoff.

---

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
- WP1 (requirements, pin map, USB power budget), WP2 (50 JLC-stocked parts, all machine-placed SMT, 27 extended) and
  WP3 (TIA, LED sink, device-current sink, plate driver in ngspice) are done: `hardware/instrument/`. WP3 caught an 8.6%
  plate-driver overshoot and a wrong shunt value in the BOM.
- **WP4 (schematic) done as checked netlists, 2026-10-24** (`hardware/instrument/schematic/`, details in `kb/instrument_electronics_notes.md`): the main board and four head boards
  as SKiDL, symbols/footprints from `easyeda2kicad` for all 50 parts, `schematic_test.py` in the smoke tests (pin accounting, data-sheet nets, footprint pads, BOM equality, design numbers).
  It followed the RP2040 hardware design guide and the ADS131A04 data sheet, and caught four defects (200 mA ferrite bead on a 390 mA rail, a non-reference RP2040 crystal, 25 V capacitors on the 24 V boost,
  a DAC that cannot reach the simulated 4.096 V).

- [ ] **WP4b — a real ERC and the sheets.** (1) Add per-IC electrical pin types from the data sheets (RP2040, ADS131A04, LP5907, MT3608, op-amps, switches) to the generated library, then make
  `kicad-cli sch erc` pass with PWR_FLAGs on the supply nets; (2) split `main_board.build()` into `@subcircuit` blocks (power/USB, RP2040, ADC, analog drivers, motors/connectors) so that
  `generate_schematic` produces hierarchical sheets for the main board (it does not finish flat) and make the sensor-head-1 sheet route; (3) write the ERC result into the smoke test.
- [ ] **WP4c — verify the stand-in symbols.** Polarity and pin names against the data sheets for VBPW34S, IR26-21C, SS14, KT-0603R, USBLC6-2SC6, the SM02B/SM04B tab pins, and the TS-1187A pad pairs;
  the 3X016384UP crystal's pinout and pad size against the 12 MHz crystal's footprint used as a stand-in (EasyEDA has no entry, C21900468). Fix `main_board.py`/`heads.py`, rerun the test.
- [ ] **WP4d — ripple and the DAC range.** Simulate the 24 V boost output ripple at the plate through the 51 ohm / 4.7 uF filter (ngspice, MT3608 behavioral switch) and rerun the plate driver with a 3.3 V
  DAC limit (about 18.8 V); put the ripple into the force-noise budget if it matters above 0.2 Hz (it should not).
- WP5 (layout) and WP7 (order) wait on A5 per the plan's own rule.

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

