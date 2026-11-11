# TODO — agent (Claude-facing)

> Finished items: dated entries in `TODO-completed.md`. Waiting on the user's build or on A5: `TODO-BLOCKED.md`. Later work: `TODO-backlog.md`. The user's list: `TODO-arcticoder.md`.
> Background that used to sit here is in `kb/`: layout direction and board rules (`main_board_layout_notes.md`), printing state and staged orders (`printing_state.md`), standing rules (`project_workflow_notes.md`).

Work that needs no hands, eyes or purchasing decision from the user. Open items only; finished ones move to `TODO-completed.md`, long notes to `kb/`. When an item is startable and nothing blocks it, I start it without being asked. **[user]** marks an item that ends in something only the user can do: I do my part, then put a one-line task on `TODO-arcticoder.md` (one order per day, today's actions only).

## Open items

### Main-board layout (WP5-WP7; KiCad is the design source; no hand-built electronics; rules in `kb/main_board_layout_notes.md`)
- [ ] WP5: close the 9 unrouted connections, draw In1 ground / In2 power planes, silk cleanup, connector rotations, mounting holes, DRC clean; then `mainboard.py dfm`, WP6 render review, WP7 fab outputs (detail in `TODO-BLOCKED.md`). The order and its cost are the user's call (JLC quotes: ask for numbers only).
- [ ] Rules vs JLC's 4-layer table (`kb/pcb_toolchain_notes.md`): the 6 `track_width` errors come from our 0.15 mm floor (JLC allows 0.09); decide the floor; raise pad-hole-to-hole to 0.45 mm; annular 0.15 is JLC's absolute minimum; find why the router writes tracks under the 0.2 mm class width.
- [ ] Library hits: Q3's `TO-252-2_...-CW` is "not found" though the file is in `jlc.pretty`; 64 `lib_footprint_mismatch` probably come from `place()` emptying `description`/`models`. Test: keep both, re-place (deterministic), re-route (8.5 min), re-run DRC. The `jlc.3dshapes` folder does not exist, so WP6 has no bodies: decide whether to generate them.
- [ ] `dfm()` gate decisions: do `silk_over_copper` (199) and `courtyards_overlap`/`malformed_courtyard` block; add schematic parity, inner-zone-filled check, board size vs the JLC price tier, mounting holes, fiducials?
- [ ] `geometry()`: arcs and vias are skipped, pad-entry angles unchecked; decide the policy for the 7 Y-branch wedges (all 45 degrees): re-route or post-process (branch leaves at 90 degrees then bends) or accept Y-branches.
- [ ] First-pass defect checklist: 9 unconnected, 3 clearance, 6 track-width, 8 dangling vias, 2 annular, 2 padstack, 2 malformed courtyards, 1 courtyard overlap, 7 acute joints, planes undrawn.
- [ ] `schematic/out/*.net` `(lib ...)` lines hold absolute paths (SKiDL): find the option or post-process in `generate.py`.

### Printer and bench
- [ ] K1 total print hours over SSH: at the 2026-11-11 power-on, read-only `find /usr/data /userdata -name '*.json' -o -name '*.cfg'` and `grep -il time`, `/usr/data/creality/`; if the figure is there record the path and parsing in the wsl K1 note and drop the touchscreen task, else say so once.
- [ ] K1 Wi-Fi dropouts (twice on 2026-11-09, once 90 s into a print): at the next connection collect Moonraker `machine/system_info` network block, signal level, `klippy.log`/`moonraker.log` near the drop times. **[user]** if signal strength is the cause, a touchscreen signal reading with the balcony door as during a print.
- [ ] Bed-mesh direction (front +1.14 mm, back -0.28 mm as read): confirm the row order against Klipper's `bed_mesh` convention before saying which end is low. **[user]** a bed-screw or shim step only if the 1.4 mm range is real.
- [ ] Hot-nozzle-over-plate (2026-11-09): write a fixed load sequence in the wsl K1 note (park front-left, Z raised, before any heat) and check `START_PRINT` never leaves the nozzle over the plate.
- [ ] Print sessions: name `print-session-runbook.md` in the user's task each time; check each G-code's header, mass and preview before submitting; the base (4 h 41 min, 177 g) does not fit a 4 h window.

### Shipping and orders
- [ ] JLC consolidation research, read-only through the app: combining packages or orders, shipping coupons, the discount line on the Y4/Y5 orders, cost per kg band for 0.3-1 kg parcels; write exact page and date in `lab/docs/kb/jlc_account_and_quotes.md`. No cart saves. **[user]** if a combine step needs clicks.
- [ ] Standing: watch for deals and log coupons with expiry; keep a JLC or AliExpress parcel in transit; stage the next AliExpress order here (craft knife, steel ruler, flat file if the needle files are round, acrylic windows only after the enclosure design is agreed).

### Design work
- [ ] **Printed calibration rider** (CadQuery, PLA): hangs on the strip, notches at 1, 2, 5, 10, 20, 30 mm radius for the 1 g weight, a seat for 1-5 cm filament pieces at the end; uses `params.py` flag/arm geometry; add to `print_requirements.md` and `assembly.md`; slice for the next free window. Route is in `procedures.md` B.1.
- [ ] **Enclosure rework for cheaper acrylic** (six 2 mm 150 x 250 sheets cost about C$49): printed PLA wall frames with clear 100 x 100 x 2 mm or 50 x 50 x 2 windows; keep the enclosure the air-current control (tile joints), bed 220 x 220 (a 248 x 150 wall needs two pieces), a view in for alignment only. Compare cost, update `params.py` `PANEL_STOCK`, CadQuery parts, `assembly.md`, `fabrication.md`, re-run `smoke_test.py`. No acrylic in orders until the user agrees.
- [ ] **Printed junior hacksaw frame** for the 150 x 6 x 0.4 mm blades (tensioning screw, PLA) for the one brass-rod cut; reference Printables 133487 (licence/login: a login means a download task for the user); fall-back a blade with taped handle.
