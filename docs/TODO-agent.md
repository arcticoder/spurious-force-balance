# TODO — agent (Claude-facing)

Work that needs no hands, eyes or purchasing decision from the user: writing files, models, simulations and
documents for this experiment. The user's own list is [TODO-arcticoder.md](TODO-arcticoder.md); finished
items move to [TODO-completed.md](TODO-completed.md) (dated entries). The list conventions are in the `lab`
repo's [todo_list_conventions](https://github.com/arcticoder/lab/blob/main/docs/kb/todo_list_conventions.md).
This repo split out of `lab` on 2026-10-23; Parts A and D came with it (path fixes only). Parts F and G (2026-10-24) are done; Part D is done. Next: Part H (live JLC part checks), then Part A's WP4 (schematic) onward, and A5 once the user has built the balance.

---

## Part H — live JLC/LCSC part lookups from the terminal (H1–H4 done 2026-10-24; H5 open, do before WP4)

**Why.** WP2's 48 parts were checked against the jlcparts snapshot of 2026-10-22 (`~/jlcparts/cache.sqlite3`), which goes stale and has no
Economic-versus-Standard PCBA flag. WP4 fixes part numbers and WP7 orders them, so a session needs live stock, basic/extended, PCBA type and
price tiers for any LCSC number. JLCONE (the desktop app) has no CLI, API or MCP server; community tools fill the gap.

**Decision: the CLI `@jlcpcb/cli`, not the MCP server.** Both are the same unofficial project (github.com/l3wi/jlc-cli, v0.5.0, 2026-09-28;
not affiliated with JLCPCB) and query the same backend, so nothing is lost. The CLI wins because:
- a session already has Bash; an MCP server only loads at session start, needs a config change and a restart, and adds its tool schemas to
  every session in every workspace repo;
- `jlc info C<n> --json` can be scripted into a repo check that anyone can rerun (the end user too), which an MCP tool call cannot;
- the MCP can still be added later with one line (`claude mcp add jlc -- npx -y @jlcpcb/mcp@0.5.0`) if interactive browsing turns out useful.

Traps found while checking: the package name `jlc-mcp` in the MCP's own README returns 404 on npm (the real package is `@jlcpcb/mcp`, whose
binary is named `jlc-mcp`); a third package, `jlcpcb-mcp` (Eyalm321), is unrelated and not chosen. Pin the version; do not use `@latest`.

- [x] **H1 — install and probe.** `npm install -g @jlcpcb/cli@0.5.0` (node 22.15 under nvm in `~/.nvm`, so no sudo). Check `jlc --version`,
  then `jlc info C2040 --json` (RP2040) and `jlc info C882747 --json` (ADS131A04). Record the JSON field names actually returned (stock,
  library type, `pcba_type`, price tiers, package, datasheet URL). Check whether `jlc search "<q>" --in-stock --basic-only` prints plain rows
  when stdout is not a TTY or opens the Ink TUI and hangs; if it hangs, use `info` only and note it. If the install or a lookup fails
  (JLC changed its web endpoints), record the error and fall back to the snapshot; do not try other packages without a note here first.
- [x] **H2 — a live BOM check.** Add `--live` to `hardware/instrument/parts.py` (through a small function in `hardware/tools/jlc_query.py`
  that runs `jlc info C<n> --json` via `subprocess`, with a timeout and a clear error if `jlc` is missing). For each BOM row print snapshot
  versus live stock, basic/extended, PCBA type and the unit price at the order quantity; flag (a) any part out of stock or with stock under
  ten times the quantity for one order, (b) any "Standard only" part, since one forces the whole board onto Standard PCBA (cost goes into
  `kb/fab_ordering_notes.md`), (c) any part that moved basic to extended. Do not add it to `run_all_smoke_tests.py` (network-dependent);
  document the command in `parts.md`'s header and in `docs/fabrication.md` as the pre-order check for WP7. Fix or replace flagged parts
  before WP4 starts, rerunning `parts.py --write`.
- [x] **H3 — symbols/footprints: compare, do not switch yet.** WP4's plan uses `easyeda2kicad`. Run `jlc install C882747 --project
  <scratch dir> --yes` (never the global library) and compare the footprint's pads and the symbol's pin names against `easyeda2kicad`'s output
  for the same part. Adopt `jlc install` for WP4 only if it is clearly better (its README claims built-in KiCad footprints for 2-terminal R/C/L
  and a `library_fix` path for pin corrections); write the outcome either way.
- [x] **H4 — knowledge base.** `kb/pcb_toolchain_notes.md`: the tool, the pinned version, the JSON fields, the TTY behavior, the npm-name trap,
  and that it is unofficial and can break when JLC changes its site. `kb/project_workflow_notes.md` "Tools available": add `jlc`. Move H1–H4 to
  `TODO-completed.md` with a short dated entry when H5 is closed.
- [ ] **H5 — settle the two Standard-PCBA-only parts** (found by H2: the LIS2DW12 accelerometer C189624 and the MMC5983MA magnetometer C404329; every
  other part is Economic-compatible and in stock). Standard assembly costs about $17 more in setup and is the two-sided service (`kb/fab_ordering_notes.md`).
  Options: (a) the accelerometer: C50385411, an MSKSEMI LIS2DW12TR-MS in the same LGA-12 package, Economic-compatible, $0.49, 11.6k in stock; read its datasheet for
  register and pinout compatibility with ST's LIS2DW12 before adopting it, since an unverified second source is a risk to a measurement instrument, although this sensor
  only logs floor motion and tilt; (b) the magnetometer sits on the head boards, which are separate small boards: decide whether they are ordered as their own Standard
  assembly or the sensor is dropped from the head (no Economic 3-axis magnetometer turned up in searches of `jlc search --economic-only` for "magnetometer", "MMC5983MA", "QMC5883L",
  "LIS3MDL"; the ICM-20948 is Economic but costs $20). Also settle whether the main board needs parts on both sides (that alone forces Standard). Write the decision into `parts.py`, rerun
  `parts.py --live` until it reports 0 flagged (or the flags are explained in the BOM comment), and `parts.py --write`.

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

