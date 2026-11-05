# Session handoff — written 2026-11-04, end of chat 6 (replace at each handoff; do not append)

**Where chat 6 ended:** the EasyEDA/Spark route was dropped on 2026-11-01 (shelved notes and tools, see `TODO-completed.md`); KiCad/SKiDL is the design source again. The rest of the chat was JLC ordering through the JLCONE desktop app. Do not offer EasyEDA, Spark, the MCP bridge or the validator again.

## State

- **Arm order** placed (2026-11-03 05:42 GMT+8 on JLC's clock), HASL with lead, total C$3.00 after the JLCONE $8 coupon, in JLC's review; JLC asked about the three copper areas (answered from `arm.kicad_pcb`: two bottom-only pads joined by a 0.6 mm trace, one flag pad on both faces).
- **Three small boards** (`elec_board`, `clamp_ground`, `clamp_plate` zips in `hardware/balance/boards/fab/`) go as three single-board orders (C$2.92, C$2.92, C$3.06; Special Offer holds on every upload; no coupon applies). `TODO-arcticoder.md` items 1-3, one order per day at most. The app's quote page may still hold the `elec_board` setup: it is not saved to the cart or submitted; the user approves and pays. After each order, set up the next one in the app when the user says so (the page resets after each upload).
- `small_panel_gerbers.zip` (36 x 96.5 mm, four boards on mouse-bite tabs, `boards.py` `panel_small()`) is only the fallback: Panel by Customer with 3 designs costs C$19.25.
- Coupons: the account's 15 unused coupons are the ledger in `lab/docs/jlc/coupons.md` (JLCONE PCB $5 and New User PCB need goods over C$2.79, so neither applies to Special Offer orders; New User SMT C$13.93 ends 2026-11-25 for the sensor-head panel if ordered; CNC and 3DP new-user coupons end 11-25/26 and 12-25).
- KiCad main-board layout (WP5) still waits on A5 and the go/no-go (`TODO-BLOCKED.md`); layout lessons from the EasyEDA attempt: room around the RP2040 (QFN-56, 0.4 mm pitch) and its decoupling, about 117 x 97 mm. Shelved tools in `tools/`: `patch_easyeda_autoroute_jobs.py` (the user's EasyEDA install is still patched; `--revert`), `validate_easyeda.py`, `floorplan_main_board.py`, `route_open_nets.py`.
- The user removed `easyeda-mcp-pro` and `/opt/apps/easyeda-pro/resources/app` from the workspace. `hardware/easyeda/spurious-force-balance.eprj2` (LFS) is modified and unneeded; the user decides.
- JLCONE app: `~/.local/bin/jlcone` wraps it at 13% scale, but the user's shell cached `/usr/bin/jlcone`, so it did not apply (`TODO-arcticoder.md` item 6, after the first order).

## Next agent tasks

Nothing startable that needs no user: set up the next order's page in the JLCONE app when asked (recipe in `lab/docs/kb/jlc_account_and_quotes.md`); the JLCMC M3 washer check could not be done in the app (the link opens outside it); the optional early sensor-head order and its JLC quote (`TODO-arcticoder.md` item 4); WP5 and A5 as in `TODO-BLOCKED.md`.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm: the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). The JLC arm order is in review; three small-board orders are the user's next tasks; the AliExpress balance list waits on the user (`TODO-arcticoder.md`; keep the cart fed so something is always in transit).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words, captures or a page read through the app; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo; `TODO-arcticoder.md` holds only separately numbered tasks for the user, and any task given in chat is also written there.

## Read first

Both `docs/kb/README.md` files, `lab/docs/kb/jlc_account_and_quotes.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`.
