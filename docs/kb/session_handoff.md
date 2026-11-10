# Session handoff — written 2026-11-10, chat 11 (replace at each handoff; do not append)

**Chat 11 (2026-11-10):** the 2026-11-09 evening print (`balance_plate0_small`: sensor_bracket, damper_holder, fixture_gap_gauge, fixture_saw_guide_base; 74 min, 31.7 g, black spool) finished; the user inspects the parts. All remaining plates were then sliced ahead and saved as G-code (see Printing). A print-session runbook was written (`~/Code/sysadmin/wsl/docs/print-session-runbook.md`). The audit of the last 10 commits is in `TODO-agent.md` (notes only, nothing actioned). User corrections: never put tracking numbers in chat or files; I did read the JLC order pages through the app's debug port (transcript confirms the navigations and the arm's In Production steps), but the tab was left on a different page and I did not say so; Moonraker's print-hour total undercounts (the touchscreen read 131 h on 2026-08-06), so the 300 h self-test is judged from the touchscreen.

## State

- **JLC orders:** arm placed 2026-11-03 (In Production since 2026-11-08, factory estimate 2026-11-12); elec_board placed 2026-11-05 (Shipped 2026-11-09); clamp_ground placed 2026-11-06, order Y5 (Shipped 2026-11-08); tracking numbers only in the JLC app. clamp_plate (Y6/Y7) was cancelled by the user because shipping would not come down (C$8.14 on the Global Standard Direct Line for 0.14 kg; list rate US$5.77; the earlier cheap rate was a -US$4.27 discount line). The user is exploring combining parcels to cut shipping for it and other items: research item in `TODO-agent.md`; keep watching for deals. Coupons: `lab/docs/jlc/coupons.md` (New User SMT C$13.93 and PCB coupons end 2026-11-25/26).
- **AliExpress:** nothing in transit. The user built a cart on 2026-11-10 (LR44 5-pack, JST-SH 2-pin cable 5-pack, hacksaw blades 10 pcs, M3 x 7 x 0.5 washers, plus my suggested 1 g weight and 0.1 g scale); acrylic was taken out pending the enclosure rework; file/knife/ruler go in the next order. Log it when the user sends the total.
- **Main board (WP5):** `kb/main_board_layout_notes.md` (pipeline `hardware/instrument/layout/mainboard.py`, commands `place|route|drc|geometry|dfm`; 164 parts, 4 layers; first run 9 of 415 connections unrouted, 3 clearance errors, 7 acute joints). Next: close the 9, draw the In1/In2 planes, silk cleanup, connector rotations, mounting holes, DRC clean, `mainboard.py dfm`, WP6 review, WP7 fab outputs. The audit items on `mainboard.py` (stale DRC data, fail-open DFM list, geometry gaps) are in `TODO-agent.md`.
- **Printing:** printed: plate 1 (2026-11-08) and the small plate (2026-11-09). Pre-sliced G-code in `~/.orcaslicer-mcp/gcode/` at the section-6 settings: post nn 1 h 13 min 37 g; strip guide 35 min 14 g; three posts 3 h 34 min 110 g; gantry 3 h 16 min 70 g; base 4 h 41 min 177 g (the last two differ from the older 3 h 58 min / 3 h 25 min figures; check them in the preview). Windows: Tue 11-10 1.5 h (strip guide, or one post with no margin), Wed 11-11 4 h (three posts or the gantry). Process: the runbook. Print hours: Moonraker 2.85 h after the last print; touchscreen total unknown, 131 h on 2026-08-06; the user was asked for the current figure. The K1's Wi-Fi dropped twice on 2026-11-09 (not understood). Bed-mesh direction unconfirmed.
- **Parts:** thin nuts (magnet check pending) and calipers (need an LR44 cell) arrived 2026-11-09; the head-hole check waits on the cell. No finer scale (asked once; the user may find one). Calibration route without a mg weight set is a task in `TODO-agent.md` (cut copper-wire lengths of known mass per metre, or a 1 g weight at a short radius).

## Next agent tasks

1. Start the next startable item in `TODO-agent.md` without being asked: WP5 layout, then the audit checks, the calibration route, the enclosure/acrylic rework, the shipping research.
2. Printing sessions: follow the runbook; heater and print only on the user's explicit request in that message.
3. Log the AliExpress order when the user reports it; keep a parcel always in transit; stage the next order (one per day).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words, captures or a page read through the app; never put tracking numbers in chat or files; say only what the transcript shows I did; do not edit or mine `docs/history.md` unless asked to read named lines; do not quote the user or describe how they said things; never commit in these repos; `TODO-arcticoder.md` holds only separately numbered tasks for the user's hands; TODO-agent.md is mine, I start startable items myself; no hand-built electronics (fab-assembled boards only).

## Context block for the next chat (paste this)

    I'm building a small experimental-physics lab across two repos, both open in this workspace.
    - lab (github.com/arcticoder/lab): reusable bench instruments — Raspberry Pi Pico/RP2040 circuits with
      SPICE netlists, breadboard guides and pass/fail smoke tests — plus the shared parts inventory and
      order ledger (docs/inventory.md, docs/orders.md), my filament stock (docs/inventory.md, "Filament"),
      and my JLC account notes (docs/jlc/: coupons read from my account, captures and reads of JLC's quote
      pages, docs/kb/jlc_account_and_quotes.md).
    - spurious-force-balance (github.com/arcticoder/spurious-force-balance): the first experiment — an open,
      low-cost torsion balance that quantifies the spurious forces (supply-lead Lorentz forces, heating,
      convection) that dominate small-thrust measurements. Printable mechanics (CadQuery), FR4 fab boards for
      the arm and electrodes, a force-noise model, and JLCPCB-assembled RP2040 electronics (KiCad 9, SKiDL,
      ngspice, MicroPython firmware tested on the host). KiCad/SKiDL is the design source: I dropped the
      EasyEDA/Spark route on 2026-11-01 (shelved; never offer EasyEDA, Spark, its MCP or the validator again).
      No more hand-built electronics: the instrument is fab-assembled boards, so the main-board layout (WP5,
      KiCad, pipeline in hardware/instrument/layout/) is open work and does not wait on the prototype
      noise measurement A5, which will run on the assembled boards.
      Ordering state (2026-11-10): the arm is In Production (factory estimate 2026-11-12); elec_board and
      clamp_ground are shipped; I cancelled clamp_plate because its shipping would not come down, and I am
      exploring combining parcels to cut shipping for it and other items. My AliExpress cart (cells, JST-SH
      cable, hacksaw blades, washers, a 1 g weight, a 0.1 g scale) is being placed; nothing else is in transit.
      The quote page for the next JLC order is set up only when I say the previous one is placed.
    - Printing: the K1 is on my balcony; I plug it in, switch it on, load the filament you advise, keep the riser
      vents closed unless told otherwise and tell you the print window. The agent drives OrcaSlicer and the K1
      through MCP and Moonraker (the wsl workspace has the connection notes and the print-session runbook
      docs/print-session-runbook.md; it is only for OrcaSlicer, the K1 and WSL). Remaining plates are pre-sliced
      in ~/.orcaslicer-mcp/gcode/. Nothing prints or heats without my explicit request in that message.
    Constraints: no hand soldering; fab boards use only JLC's machine-placed SMT parts; USB power, under
    50 V DC / 30 V AC; PLA only on my Creality K1; AliExpress for stock parts (no single-item shipping fees),
    JLC PCB/PCBA/3DP/CNC when fabrication beats buying and cutting by hand; design to stock sizes. I'm in
    Canada and JLC prices on my account are in CAD. I will exceed JLC's 0.3 kg cheap-shipping line if that
    lowers the per-item shipping; I will not pay a shipping premium for a tiny order.
    JLC quote and coupon pages can be read through my JLCONE desktop app when I launch it with
    --remote-debugging-port=9222 (recipe and gotchas in lab/docs/kb/jlc_account_and_quotes.md): read-only text
    reads, a few paced mouse clicks, uploads of this repo's own Gerber zips for quotes. Never call JLC's API, never
    touch the cookies, never Submit, Save to cart or pay: I approve and pay, and I place at most one order per
    day. Treat any JLC price not from my words, my captures or a page read through the app as an estimate.
    Never put parcel tracking numbers in chat or in files. Only say you did something if the transcript shows it.
    docs/history.md is my chat transcript: don't edit it or use it as an analysis source unless I name lines to
    read. Pictures are lossless .jxl; .jxl and .eprj2 are Git LFS (the .eprj2 is leftover from the dropped route;
    I decide whether to keep it). Don't commit anything in these two repos: I stage and commit everything after
    each chat.
    Workflow: whichever model is running actions what needs actioning. docs/TODO-agent.md is the agent's own
    list (open items only; TODO-BLOCKED.md, TODO-backlog.md and TODO-completed.md sit beside it): start the next
    startable item without being asked. My hands-on tasks live in docs/TODO-arcticoder.md as separately numbered
    tasks for me only (no notes to yourself; any task you give me in chat goes there too); only things that truly
    need my hands (orders, bench checks, the printer set-up) go there. Keep docs/kb/*.md (LLM-only notes) up to
    date with discoveries. Don't quote me or describe how I said things in files or chat. Keep an eye on the
    supply chain: always have a few AliExpress or JLC items in transit, and watch for deals.
    Start by reading docs/kb/README.md and docs/kb/session_handoff.md in spurious-force-balance, then
    lab/docs/kb/README.md and lab/docs/kb/jlc_account_and_quotes.md. Then continue from
    docs/TODO-agent.md and my feedback below.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, `docs/kb/main_board_layout_notes.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md` and `~/Code/sysadmin/wsl/docs/print-session-runbook.md` for the printer side.
