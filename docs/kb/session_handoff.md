# Session handoff — written 2026-11-01, end of chat 5 (replace at each handoff; do not append)

**Where chat 5 ended (updated after the restart: 68 GND stitching vias placed with `createMany`; DRC now 0 clearance errors after deleting one via, 63 connection errors: 39 GND, 24 on the nine signal nets, all around U4 and the spare-header run; project saved 2026-11-02T02:15Z):** `main_board` was re-floorplanned with more room (`FP_SCALE=1.1 FP_MARGIN=40`, outline 117.3 x 96.8 mm), signals re-routed, GND pours recreated; DRC 0 clearance errors, 114 connection errors (90 GND pads that the pours do not reach, 24 on nine open signal nets: XIN, DVDD_1V1, DUT_EN, MON_5V, LED1_MOD, LED2_MOD, I2C_SDA, I2C_SCL, SPARE_A/G/H). The project was saved before asking the user to restart EasyEDA. The patcher gained `PCB_PrimitiveVia.createMany` / `PCB_PrimitiveLine.createMany` (applied to the install, `node --check` clean; loads at the restart). Details and lessons: `kb/easyeda_spark_notes.md`, last bullet.

## Next agent tasks, in order (`docs/TODO-agent.md`)

1. (Added late in chat 5: `tools/route_open_nets.py` exists; the nine open nets cannot be added to the current U4 fan-out, only absurd detours exist, so rip up and re-route U4's nets deliberately; see the last bullets of `kb/easyeda_spark_notes.md`. `PCB_Drc.checkCompact` loads after the user's restart, `TODO-arcticoder.md` item 1.) Open the board (`DMT_EditorControl.openDocument("85757acc0463db9b")`; the MCP bridge reconnects after sleep/restart). `createMany` for vias and lines is live. Remaining GND: about 22 pads with no overlap-via spot (need a short track plus via, try 6 mil clearance, or a nudged neighbour part) and about 10 vias stranded in pour fragments (move next to a pad with a track); pour ids 473110e174a939f3 and 0311cc6a827b5195; the pad list is in the last bullet of `kb/easyeda_spark_notes.md`.
2. Hand-route the nine open signal nets with `PCB_PrimitiveLine.createMany` (and bottom-layer vias); the pairs and positions come from the DRC detail. Do not run the autorouter on GND again.
3. DRC 0, then the milestone routine (`kb/easyeda_validation.md`): refresh `native_checks.json`, pull live netlists, run the validator, ask the user to commit the `.eprj2`; connector orientation check in 3D; ADC crystal LCSC fields; OSHWLab text and Spark answers (registration closes 2026-11-30).
4. The board is now 117.3 x 96.8 mm (was 106.7 x 87.6): the JLC cost effect is unknown; ask the user for a JLC quote of the main board only when the layout is final.
5. Upstream: the fork `~/Code/typescript/easyeda-mcp-pro` is older than upstream main (PRs #813, #816 merged); switch when convenient. The user declined a `BRIDGE_TIMEOUT_MS` change: do not offer it again.

## Standing state

Board uuids and the other boards are unchanged from chat 4 (`arm` 7bc3367e1c2d2364, `clamp_plate` 3ddf518a3b25253b, `clamp_ground` a1c4bc42816028ee, `elec_board` 05dc52ccb60a9ca9, `sensor_head_1` 6b230bf28446d8f9, `sensor_head_2` 868eebde0c888e1b; main_board 85757acc0463db9b, schematic page a173bbce992e5a91). The committed `.eprj2` holds the four mechanical boards and head 1 only; the main board is NOT at a commit milestone. Placement files: `hardware/easyeda/exports/main_board_placement.json` now holds the 1.1/40 placement (the old one is reproduced with `FP_SCALE=1.0 FP_MARGIN=28`).

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm: the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote; the EasyEDA arm would then be redrawn.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). Nothing else is en route; the JLC arm and small-board orders and the AliExpress balance list wait on the user (`TODO-arcticoder.md`, coupons end 2026-11-25/26).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo (the user stages and commits everything after each chat; only flag `.eprj2` milestones in `TODO-arcticoder.md`); `TODO-arcticoder.md` holds only separately numbered tasks for the user (no notes to self), and any task given in chat is also written there.

## Read first

Both `docs/kb/README.md` files, `kb/easyeda_spark_notes.md`, `kb/easyeda_validation.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`; then `lab/docs/kb/jlc_account_and_quotes.md` if a JLC question comes up.
