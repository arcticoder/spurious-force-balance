# Session handoff — chat 13 final, 2026-11-13 00:00 (replace at each handoff; do not append)

## State

- **Printing (K1-FA35, 192.168.1.70):** printed: plate 1, small plate, gantry, posts nn, np and pn with bars np/pn/nn and the pp bar, strip guide, two calibration riders (`fixture_cal_rider`). The user inspects tonight's parts (task 1). Left: post pp (L, about 32 min; new G-code needed), the base (`balance_p2_base.gcode`, 4 h 41 min, 177 g), then the enclosure plates. All files in `~/.orcaslicer-mcp/gcode/` are 225/220 C, 3 walls, 30 %, no supports; slice each file the day before its window. Details, the fast-start failure (a full `START_PRINT` is needed once per Klipper boot) and the Orca gotchas: `kb/printing_state.md`, `~/Code/sysadmin/wsl/docs/print-session-runbook.md` (section E), wsl K1 note (2026-11-12 findings: SSH read-only route, no hour counter on the printer, Wi-Fi -62 dBm).
- **Enclosure: DECIDED printed** (1.2 mm plates with a 2 mm rim, lid tiles 2 mm, no window): `hardware/balance/enclosure_printed.py`, `params.ENCL_PRINTED`, smoke test updated, plan and estimates (about 10 h, 320 g, about 9 windows, grey walls, red lid, black strips) in `kb/balance_design_notes.md`; `assembly.md`/`fabrication.md` wording still says acrylic until the first plate is printed.
- **Brass ballast:** a 15 mm cut from the 10 x 100 mm rod (about 10 g) goes in a 10.2 mm hole in the arm board (arm already in production). The user found a 10 g stainless weight at C$2.92; it fits only if its diameter is 10 mm or less (task 5). The Dremel 3000 (cut-off wheel 31 x 1.0 mm) stand is planned (housing thread 3/4 in - 12 UN, photo `docs/img/dremel_nose_threads.jxl`) but blocked on safety glasses and a dust mask (task 3); the hacksaw guide is the fallback.
- **Calibration:** added inertia, confirmed; riders printed; a second 1 g weight is staged for the next AliExpress order (`TODO-backlog.md`).
- **Main board (WP5-WP7):** layout done to the DFM gate (415/415 routed, `mainboard.py dfm` no blocking item, In1 GND plane only, 120 x 90 mm, one board, 45-degree Y-branches accepted); fab files in `hardware/instrument/fab/` (Gerbers with the plane filled, BOM 46 lines, CPL, `ORDER.md`). Waits on the user: JLC placement-preview check and the price-tier/board-size decision (task 4; remind them when the order starts; an extra model review is optional). Read `kb/main_board_layout_notes.md` (last section), `kb/main_board_assessment.md`, `hardware/instrument/layout/SPEC.md`. pcbnew works only under `/usr/bin/python3` (3.14), not the venv (3.12).
- **JLC:** arm placed 2026-11-03 (In Production, estimate 2026-11-12, last read 2026-11-10), elec_board and clamp_ground shipped, clamp_plate cancelled. Coupons (19 unused, ledger `lab/docs/jlc/coupons.md`): four Black Friday warm-up coupons claimed 2026-11-12, valid to 2026-11-27 (PCBA, PCBA parts, shipping, prototype); New User coupons expire 2026-11-25/26. The app was driven through its debug port for messages and campaign pages (recipe in `lab/docs/kb/jlc_account_and_quotes.md`); the campaign page's "updated Terms" dialog is the user's to accept. JLC shipping-consolidation research still open (`TODO-BLOCKED.md`). AliExpress order of 2026-11-10 in transit.
- **Lab repo:** `docs/inventory.md` has the Dremel 3000 and its accessories; coupons and JLC notes updated.

## Files that carry the state

`docs/TODO-arcticoder.md` (user tasks 1-5), `docs/TODO-agent.md` (empty, 0 lines), `docs/TODO-BLOCKED.md`, `docs/TODO-backlog.md` (staged AliExpress order: second 1 g weight, craft knife, steel ruler, safety glasses, dust masks), `docs/TODO-completed.md` (newest first).

## Standing rules (see `kb/project_workflow_notes.md`)

TODO-agent.md must be 0 lines at the end of every chat (do startable work; move only truly blocked items to TODO-BLOCKED.md with the condition). Never append to `docs/history.md` or use it as a source unless the user names lines. Never commit. No quotes of the user, no tone descriptions. No tracking numbers. Never print secrets (the printer's root password was printed once by mistake on 2026-11-12: read `.env` with `awk '$1=="KEY"{print $2}'`, never print key lines). Never state a JLC price that is not from the user, a capture or an app read. Say only what the transcript shows. One order per day. No hand-built electronics; never EasyEDA/Spark. Heat and print only on the user's explicit request in that message; clock-time visual checks only. Long jobs in the background, one change per routing run.

## Context block for the next chat (paste this)

    I'm building a small experimental-physics lab across two repos, both open in this workspace.
    - lab (github.com/arcticoder/lab): reusable bench instruments — Raspberry Pi Pico/RP2040 circuits with
      SPICE netlists, breadboard guides and pass/fail smoke tests — plus the shared parts inventory and
      order ledger (docs/inventory.md, docs/orders.md), my filament stock and tools (docs/inventory.md,
      "Filament" and "Tools", including a Dremel 3000), and my JLC account notes (docs/jlc/: coupons read from
      my account, captures and reads of JLC's quote pages, docs/kb/jlc_account_and_quotes.md).
    - spurious-force-balance (github.com/arcticoder/spurious-force-balance): the first experiment — an open,
      low-cost torsion balance that quantifies the spurious forces (supply-lead Lorentz forces, heating,
      convection) that dominate small-thrust measurements. Printable mechanics (CadQuery), FR4 fab boards for
      the arm and electrodes, a force-noise model, and JLCPCB-assembled RP2040 electronics (KiCad 9, SKiDL,
      ngspice, MicroPython firmware tested on the host). KiCad/SKiDL is the design source: I dropped the
      EasyEDA/Spark route on 2026-11-01 (shelved; never offer EasyEDA, Spark, its MCP or the validator again).
      No more hand-built electronics: the instrument is fab-assembled boards.
      State (2026-11-13): the main board (WP5) is laid out to the DFM gate: 120 x 90 mm, one board, In1 ground
      plane only, all 415 connections routed, 45-degree Y-branches accepted; fab files are in
      hardware/instrument/fab/ (Gerbers, BOM, CPL, ORDER.md). I still have to check rotations and polarity in
      JLC's own placement preview and decide the board size against the price tier (remind me when I start that
      order). The calibration uses added inertia (confirmed); the two riders are printed. The enclosure is
      decided: printed PLA plates (1.2 mm with a 2 mm rim, no window; grey walls, red lid), to print after the
      frame. The ballast is a 15 mm cut of the 10 mm brass rod unless the 10 g stainless weight I found
      (C$2.92) has a diameter of 10 mm or less. I own no safety glasses or dust mask, so the Dremel cut-off wheel
      waits for them (AliExpress; the hacksaw guide is the fallback).
      Ordering state (2026-11-13; JLC statuses last read 2026-11-10): the arm is In Production (factory estimate
      2026-11-12), elec_board and clamp_ground are shipped, clamp_plate is cancelled (shipping), and I am exploring
      combining parcels. My AliExpress order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, a 1 g
      weight, a 0.1 g scale, needle files) is in transit (lab/docs/orders.md). I claimed four JLC Black Friday
      warm-up coupons on 2026-11-12 (valid to 2026-11-27; lab/docs/jlc/coupons.md). The quote page for the next
      JLC order is set up only when I say the previous one is placed.
    - Printing: the K1-FA35 is on my balcony with the door shut and I work in the office: there is no camera and
      I cannot hear it, so give me clock-time visual checks, never audible ones. I plug it in, switch it on and
      load the filament you advise; you run heating, homing and starting only when I ask in that message.
      The agent drives OrcaSlicer and the K1 through MCP and Moonraker (wsl workspace: connection notes,
      docs/print-session-runbook.md, the K1 note). Printed so far: plate 1, the small plate, the gantry, posts
      nn/np/pn with their bars, the pp bar, the strip guide and two calibration riders. Left: post pp (about
      32 min), the base (4 h 41 min), then the enclosure plates (about 10 h in total). The first print after a
      power-on must use the normal start (see the runbook, section E).
    Constraints: no hand soldering; fab boards use only JLC's machine-placed SMT parts; USB power, under
    50 V DC / 30 V AC; PLA only on my Creality K1; AliExpress for stock parts (no single-item shipping fees),
    JLC PCB/PCBA/3DP/CNC when fabrication beats buying and cutting by hand; design to stock sizes. I'm in
    Canada and JLC prices on my account are in CAD. I will exceed JLC's 0.3 kg cheap-shipping line if that
    lowers the per-item shipping; I will not pay a shipping premium for a tiny order.
    JLC quote, message and coupon pages can be read through my JLCONE desktop app when I launch it with
    --remote-debugging-port=9222 (recipe and gotchas in lab/docs/kb/jlc_account_and_quotes.md): read-only text
    reads, a few paced clicks (I authorised Get Coupon on the campaign page once), uploads of this repo's own
    Gerber zips for quotes. Never call JLC's API, never touch the cookies, never accept terms for me, never
    Submit, Save to cart or pay: I approve and pay, and I place at most one order per day. Treat any JLC price
    not from my words, my captures or a page read through the app as an estimate. Never put parcel tracking
    numbers or secrets in chat or files. Only say you did something if the transcript shows it.
    docs/history.md is my chat transcript: never append to it (I paste the full summary myself), don't edit
    existing text, and don't use it as an analysis source unless I name lines to read. Pictures are lossless
    .jxl (keep them small); .jxl and .eprj2 are Git LFS (the .eprj2 is leftover from the dropped route; I decide
    whether to keep it). Don't commit anything in these repos: I stage and commit everything after each chat.
    Workflow: docs/TODO-agent.md is the agent's own list and must be empty (0 lines) at the end of every chat:
    do startable items, move truly blocked ones to TODO-BLOCKED.md with the exact condition (TODO-backlog.md and
    TODO-completed.md sit beside it). My hands-on tasks live in docs/TODO-arcticoder.md as separately numbered
    tasks for me only; any task or decision you give me in chat goes there too. Keep docs/kb/*.md (LLM-only
    notes) up to date with discoveries. Don't quote me or describe how I said things in files or chat. Keep an
    eye on the supply chain: always have a few AliExpress or JLC items in transit, and watch for deals.
    Start by reading docs/kb/README.md and docs/kb/session_handoff.md in spurious-force-balance, then
    lab/docs/kb/README.md and lab/docs/kb/jlc_account_and_quotes.md. Then continue from
    docs/TODO-arcticoder.md, docs/TODO-BLOCKED.md and my feedback below.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, `docs/kb/printing_state.md`, `docs/kb/main_board_layout_notes.md` (last section), `docs/TODO-arcticoder.md`, `docs/TODO-BLOCKED.md`, `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md` and `~/Code/sysadmin/wsl/docs/print-session-runbook.md` for the printer side.
