# Session handoff — written 2026-11-01, end of chat 5 (replace at each handoff; do not append)

**Where chat 5 ended:** the user dropped the EasyEDA/Spark route and went back to KiCad. Everything EasyEDA is shelved (banners on `kb/easyeda_spark_notes.md`, `kb/easyeda_validation.md`, `docs/spark_application.md`; completed entry in `TODO-completed.md`). The KiCad/SKiDL design, the mechanical-board Gerbers and the sensor-head panel were never touched and are the order files. Do not offer to resume EasyEDA or Spark registration.

## State

- KiCad: main board and head boards exist as SKiDL netlists (`hardware/instrument/schematic/out/*.net`), 50 JLC parts; the four mechanical boards and `heads_panel` are KiCad with Gerbers (`hardware/balance/boards/fab/`, `hardware/instrument/heads_panel/out/`).
- Main-board layout (WP5) is KiCad work that waits on A5 (the prototype noise measurement) and the go/no-go (`TODO-BLOCKED.md`). Lessons from the EasyEDA attempt that carry over: the 164-part main board did not route at 106.7 x 87.6 mm with the part spacing used; leave room around the RP2040 (QFN-56, 0.4 mm pitch) and its decoupling, put the SPARE header nets on a deliberate layer, and expect about 117 x 97 mm unless the spare headers shrink. `tools/floorplan_main_board.py` (env `FP_SCALE`, `FP_MARGIN`) is a placement starting point from EasyEDA data, not KiCad.
- Shelved tools kept in `tools/`: `patch_easyeda_autoroute_jobs.py` (the user's EasyEDA install is still patched; `--revert` restores the stock files if wanted), `validate_easyeda.py`, `floorplan_main_board.py`, `route_open_nets.py` (generic offline two-layer maze router over pad/track/via dumps, usable with KiCad data by writing a loader).
- `hardware/easyeda/spurious-force-balance.eprj2` (Git LFS) is modified and unneeded; the user decides whether to commit or drop it.
- GitHub About: description and topics were returned to the KiCad wording (topics `easyeda`, `oshwlab` removed).

## Next agent tasks

Nothing startable without the user or the board (`TODO-agent.md`). Watch for: the arm decision and panel Gerbers (J4), the early sensor-head order's upload checks, A5's results into the model, then WP5 in KiCad.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm: the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). Nothing else is en route; the JLC arm and small-board orders and the AliExpress balance list wait on the user (`TODO-arcticoder.md`, coupons end 2026-11-25/26).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo; `TODO-arcticoder.md` holds only separately numbered tasks for the user, and any task given in chat is also written there.

## Read first

Both `docs/kb/README.md` files, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`; then `lab/docs/kb/jlc_account_and_quotes.md` if a JLC question comes up.
