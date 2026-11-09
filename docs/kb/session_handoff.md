# Session handoff — written 2026-11-08, end of chat 9 (replace at each handoff; do not append)

**Where chat 9 ended:** plate 1 of the balance's printed frame is printed (whole); the K1 is off until Monday. The user's direction changed the electronics plan: fab-assembled boards only, so the main-board layout started (first routed pass done, not fabricable yet). `clamp_plate` stays parked.

## State

- **JLC orders:** arm placed 2026-11-03 (Paid, awaiting JLC's production review; the user emailed JLC again 2026-11-08, the @duck.com address may be dropping their mail); elec_board placed 2026-11-05 (In Production); clamp_ground placed 2026-11-06, order Y5 (In Production); clamp_plate parked in `TODO-BLOCKED.md` (shipping on the Global Standard Direct Line was C$8.14 for 0.14 kg against about C$2.13 earlier; the user declined it, Y6/Y7 cancelled). It cannot join Y5; it goes into the next JLC order, and the user will exceed 0.3 kg if that lowers per-item shipping (the 0.3 kg line is of little value if every parcel pays about C$8). Coupons: `lab/docs/jlc/coupons.md` (the New User SMT coupon, C$13.93, ends 2026-11-25; the PCB coupons end 2026-11-25/26).
- **Main board (WP5):** `kb/main_board_layout_notes.md` (pipeline `hardware/instrument/layout/mainboard.py`; 164 parts on 110 x 90 mm, 4 layers; first Freerouting run left 9 of 415 nets unrouted, 3 clearance errors). Next: close the 9, inner-layer ground planes, silk cleanup, connector rotations, mounting holes, DRC clean, WP6 review, then WP7 fab outputs and a cost picture for the user's budget decision. `docs/plan.md` was reconciled with the no-breadboards direction; A5 now runs on the assembled boards.
- **Printing:** plate 1 printed 2026-11-08 (head, saw guide plate, elec_bracket, four shelves, vane_holder; 1 h 37 min, black Hyper PLA, 225/60 C). Orca project has four plates (0 nine parts about 4 h and needs a re-slice at the section 6 settings; 2 gantry 3 h 58 min; 3 base 3 h 25 min), unsaved (the build cannot save projects). The user's windows: Mon 2026-11-09 2.5 h, Tue 11-10 1.5 h, Wed 11-11 4 h (gantry). All need the printer plugged in and on, filament loaded, vents closed; I split plates to fit each window, re-slice, check the G-code header, send, and monitor only on the user's explicit request. The K1 re-levels every print (START_PRINT); the bed mesh shows about 1.4 mm front-to-back tilt (not left-right), which belt tooth-skipping on the user's description of the 3-lead-screw layout could change, but the direction (which end is low) is unread; read `bed_mesh` or measure with the printer on before anything is opened. Connection notes and findings: `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md`.
- **Parts:** the user fitted two M3x14 screws into the base nuts; washers (AliExpress list) not yet arrived; calipers and thin nuts due 2026-11-15 (the user will say when; then the head-hole check: CAD 3.4 mm, the user's printed-calipers reading was 4.5 x 5.0 mm). `docs/img/fasteners.jxl` shows where the head's and `elec_bracket`'s screws go. `params.py` carries the sliced `vane_holder` mass (0.93 g); no finer scale (the user may find one; follow up once after the next print session).
- **Supply chain:** AliExpress order of 2026-10-30 in transit; the staged AliExpress balance list waits for a deal (the user's rule). Keep something always in transit.

## Next agent tasks

1. Continue WP5 (see above); it is open work, start it without being asked.
2. Printing as above, when the user reports the printer on.
3. Read the bed mesh and report which end is low once the printer is on (no heating; the user approves moving it).
4. Put `clamp_plate` into the next JLC order when one is staged; promote the AliExpress list only on a deal.

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words, captures or a page read through the app; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in these repos; `TODO-arcticoder.md` holds only separately numbered tasks for the user's hands; TODO-agent.md is mine, I start startable items myself; no hand-built electronics (fab-assembled boards only).

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
      Ordering state (2026-11-08): the arm is placed (HASL, in JLC's review); elec_board and clamp_ground are
      placed (In Production); clamp_plate is parked (shipping was C$8.14 on Global Standard Direct Line,
      previously about C$2) and goes into the next JLC order. The quote page for the next order is set up
      only when I say the previous one is placed.
    - Printing: the K1 is on my balcony; I plug it in, switch it on, load the filament you advise, keep the riser
      vents closed unless told otherwise and tell you the print window (Mon 2.5 h, Tue 1.5 h, Wed 4 h this week).
      The agent drives OrcaSlicer and the K1 through MCP (the wsl workspace has the connection notes; it is only
      for OrcaSlicer, the K1 and WSL). Nothing prints or heats without my explicit request in that message.
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
    docs/history.md is my chat transcript: don't edit it or use it as an analysis source. Pictures are lossless
    .jxl; .jxl and .eprj2 are Git LFS (the .eprj2 is leftover from the dropped route; I decide whether to keep it).
    Don't commit anything in these two repos: I stage and commit everything after each chat.
    Workflow: whichever model is running actions what needs actioning. docs/TODO-agent.md is the agent's own
    list (open items only; TODO-BLOCKED.md, TODO-backlog.md and TODO-completed.md sit beside it): start the next
    startable item without being asked. My hands-on tasks live in docs/TODO-arcticoder.md as separately numbered
    tasks for me only (no notes to yourself; any task you give me in chat goes there too); only things that truly
    need my hands (orders, bench checks, the printer set-up) go there. Keep docs/kb/*.md (LLM-only notes) up to
    date with discoveries. Don't quote me or describe how I said things in files or chat. Keep an eye on the
    supply chain: always have a few AliExpress or JLC items in transit.
    Start by reading docs/kb/README.md and docs/kb/session_handoff.md in spurious-force-balance, then
    lab/docs/kb/README.md and lab/docs/kb/jlc_account_and_quotes.md. Then continue from
    docs/TODO-agent.md and my feedback below.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, `docs/kb/main_board_layout_notes.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, and `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md` for the printer side.
