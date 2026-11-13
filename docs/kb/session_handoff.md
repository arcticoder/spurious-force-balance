# Session handoff — chat 13 final, 2026-11-12 18:45 (replace at each handoff; do not append)

## State

- **Printing (K1-FA35, 192.168.1.70):** printed so far: plate 1 (head, saw_guide_plate in 4 pieces, elec_bracket, 4 shelves, vane_holder), small plate (sensor_bracket, damper_holder, gap gauge, saw_guide_base), gantry, post nn with its bar, strip guide (inventory parsed from the user's photo `docs/img/printed_parts_2026-11-11.jxl`: nothing to reprint). Left: posts np, pn, pp, three bars, two calibration riders, base. Files in `~/.orcaslicer-mcp/gcode/` (all 225/220 C, bed 60, 3 walls, 30 %, no supports): `balance_p1a_post_np_bars_np_pn.gcode` (54 min, 43 g, **tonight**), `balance_p1b_posts_pn_pp_bar_pp.gcode` (73 min, 61 g, needs about 85 min), `balance_p5_cal_riders_x2.gcode` (13 min, 3 g), `balance_p2_base.gcode` (4 h 41 min, 177 g). **Tonight (Thu 2026-11-12):** window from 8:15 pm, 75 min; prep done at 18:40 (runbook A + read-only B: K1 reachable and cold, Orca fork answering, header checked); the black 1 kg spool is loaded; nothing heats or prints until the user asks in that message; follow `~/Code/sysadmin/wsl/docs/print-session-runbook.md` (fast start in `kb/printing_state.md`; first-layer look about 8-10 min after start, one mid-print look, finish about 9:20). Details: `kb/printing_state.md`.
- **Orca gotchas learned:** deleting an object that has two instances crashed OrcaSlicer and lost the unsaved project (the "balance" print preset lived only in the project); relaunch with `flatpak run com.orcaslicer.OrcaSlicer` (Remote API comes up on 13130). After a reopen check temperatures with `get_config` (225/220, bed 60) before slicing. The agent cannot enable Remote API itself.
- **Enclosure (decision pending, user task 3):** printed walls proposed (`hardware/balance/enclosure_printed.py`, preview `docs/img/enclosure_printed_preview.jxl`, numbers in `kb/balance_design_notes.md` and `kb/printing_state.md`); the user prefers printing, asked about colours (yes, per plate), infill (no help in 2 mm plates; thinner plates help), wording (walls, not windows), preview (made). Waits on yes/no for printed walls and for the optional clear window.
- **Brass rod cut:** the user owns a Dremel 3000 with a reinforced cut-off wheel (31 mm x 1.0 mm); fits the saw guide's 1.4 mm slot; the hacksaw frame is dropped. A printed chop stand (nose ring, hinged arm, wheel guard, rod clamp) waits on the user's nose-thread measurement (task 4). Inventory: `lab/docs/inventory.md` Tools.
- **Calibration:** physics correction confirmed by the user 2026-11-11 (added inertia, pair at +r/-r, radii 20-80 mm); `fixture_cal_rider` (x2) designed and sliced; the user prefers a second 1 g weight (staged in `TODO-backlog.md` for the next AliExpress order, C$2.48 listing).
- **Main board (WP5-WP7):** layout done to the DFM gate on 2026-11-12: 415/415 routed, `mainboard.py dfm` no blocking item, In1 GND plane only (the In2 pour failed in three variants), 120 x 90 mm, one board (user's choice), 45-degree Y-branches accepted (user). Fab files in `hardware/instrument/fab/` (Gerbers with the plane filled, BOM 46 lines / 164 parts, CPL, `ORDER.md`). Waits on the user: JLC placement-preview check (rotations, polarity) and the price-tier decision (a 105 x 80 mm re-run is possible). Read `kb/main_board_layout_notes.md` (last section), `kb/main_board_assessment.md`, `hardware/instrument/layout/SPEC.md`. pcbnew works under `/usr/bin/python3` (3.14), not in the venv (3.12): `kb/pcb_toolchain_notes.md`.
- **JLC orders:** arm placed 2026-11-03 (In Production, factory estimate 2026-11-12, last read 2026-11-10); elec_board and clamp_ground Shipped; clamp_plate cancelled (shipping), combining parcels is explored (research in `TODO-BLOCKED.md`, needs the JLCONE app on port 9222). Coupons: `lab/docs/jlc/coupons.md` (New User SMT C$13.93 and PCB coupons end 2026-11-25/26). AliExpress order of 2026-11-10 in transit (`lab/docs/orders.md`); on arrival inventory it with bags and run the head-hole check once the calipers have a cell.
- **Other pending checks (printer on):** K1 total print hours over SSH, Wi-Fi dropout logs, `START_PRINT` macro check (all in `TODO-BLOCKED.md`). Bed mesh: front is the low end by about 1.4 mm (Klipper convention checked; wsl K1 note).

## Files that carry the state

`docs/TODO-arcticoder.md` (user tasks 1-4: tonight's window, later windows, enclosure choice, Dremel thread), `docs/TODO-agent.md` (empty, 0 lines), `docs/TODO-BLOCKED.md` (everything waiting), `docs/TODO-backlog.md` (staged order, standing duties), `docs/TODO-completed.md` (dated entries, newest first).

## Standing rules (see `kb/project_workflow_notes.md`)

TODO-agent.md must reach 0 lines every chat: do startable work, move only truly blocked items to TODO-BLOCKED.md with the exact condition. Never append to `docs/history.md` (the user pastes the full chat summary there) and never use it as a source. Never commit (the user commits everything). No quotes of the user or tone descriptions in files or chat. No tracking numbers. Never state a JLC price that is not from the user, a capture or a page read through the app. Only say I did something the transcript shows. One order per day, the user's list holds only today's actions. No hand-built electronics. Never offer EasyEDA/Spark. Printing and heating only on the user's explicit request in that message; clock-time visual checks (no camera, no hearing). Keep the build queue and parcels in transit stocked.

## Context block for the next chat (paste this)

    I'm building a small experimental-physics lab across two repos, both open in this workspace.
    - lab (github.com/arcticoder/lab): reusable bench instruments (Pico/RP2040 circuits, SPICE, breadboard
      guides, pass/fail smoke tests), the shared parts inventory and order ledger (docs/inventory.md,
      docs/orders.md), my filament stock and tools (including a Dremel 3000), and my JLC account notes
      (docs/jlc/, docs/kb/jlc_account_and_quotes.md).
    - spurious-force-balance (github.com/arcticoder/spurious-force-balance): an open, low-cost torsion balance
      that quantifies spurious forces in small-thrust measurements. Printable mechanics (CadQuery), FR4 fab
      boards, a force-noise model, and a JLCPCB-assembled RP2040 main board (KiCad 9, SKiDL, ngspice,
      MicroPython tested on the host). KiCad/SKiDL is the design source (EasyEDA/Spark dropped for good).
      State (2026-11-12 evening): the main board is laid out to the DFM gate (415/415 routed, one board,
      In1 ground plane only, 45-degree Y-branches accepted) with fab files in hardware/instrument/fab/; I still
      have to check rotations in JLC's placement preview and decide the board size against the price tier.
      The calibration uses added inertia (confirmed). The enclosure may be printed instead of acrylic (my
      decision pending, preview in docs/img/). The Dremel stand waits on my nose-thread measurement.
      Ordering: arm In Production (last read 2026-11-10), elec_board and clamp_ground shipped, clamp_plate
      cancelled; the AliExpress order of 2026-11-10 is in transit; a second 1 g weight is staged for the next order.
    - Printing: K1-FA35 on my balcony, door shut, no camera, I cannot hear it: give clock-time visual checks.
      Printed: plate 1, small plate, gantry, post nn with its bar, strip guide. Left: posts np/pn/pp, three
      bars, two calibration riders, base; files and times in docs/kb/printing_state.md. Nothing prints or heats
      without my explicit request in that message. Follow ~/Code/sysadmin/wsl/docs/print-session-runbook.md.
    Constraints: no hand soldering; fab boards use only JLC's machine-placed SMT parts; USB power, under
    50 V DC / 30 V AC; PLA only; AliExpress for stock parts (no single-item shipping fees), JLC
    PCB/PCBA/3DP/CNC when fabrication beats buying; design to stock sizes. I'm in Canada, JLC prices are CAD.
    JLC pages can be read through my JLCONE app with --remote-debugging-port=9222 (recipe in
    lab/docs/kb/jlc_account_and_quotes.md): read-only; never call JLC's API, never touch cookies, never Submit,
    Save to cart or pay; I place at most one order per day. Never put tracking numbers in chat or files. Only say
    you did something if the transcript shows it. Don't append to docs/history.md and don't use it as a source.
    Don't commit anything: I stage and commit after each chat. Pictures are lossless .jxl.
    Workflow: docs/TODO-agent.md must be empty (0 lines) each chat: do startable items, move truly blocked ones
    to TODO-BLOCKED.md. My hands-on tasks are numbered in docs/TODO-arcticoder.md. Keep docs/kb/*.md (LLM-only)
    current. Don't quote me or describe how I said things.
    Start by reading docs/kb/README.md and docs/kb/session_handoff.md in spurious-force-balance, then
    lab/docs/kb/README.md and lab/docs/kb/jlc_account_and_quotes.md, then docs/TODO-arcticoder.md and
    docs/TODO-BLOCKED.md, and my feedback below.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, `docs/kb/printing_state.md`, `docs/kb/main_board_layout_notes.md` (last section), `docs/TODO-arcticoder.md`, `docs/TODO-BLOCKED.md`, `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md` and `~/Code/sysadmin/wsl/docs/print-session-runbook.md`.
