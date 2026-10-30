# Session handoff — written 2026-10-30 (replace at each handoff; do not append)

## What this chat did (details in `kb/easyeda_spark_notes.md`)

- Pictures are lossless `.jxl` now (7 files `git mv`'d; generators call `tools/to_jxl.py`); `*.jxl` and `*.eprj2` are Git LFS-tracked in this repo, `*.jxl` also in `lab` (`.gitattributes`). The user will not commit until `TODO-arcticoder.md` says so.
- easyeda-mcp-pro works: Node 24.22.1 via nvm on PATH, server entry in `~/.claude.json` (Claude Code) and the VS Code `mcp.json` (key `servers`), `TOOL_PROFILE=full` (needed to create PCB geometry), bridge connected to EasyEDA Pro (native Linux install). The tools are `mcp__easyeda-mcp-pro__*`; `easyeda_health_check` first.
- The spurious-force-balance redesign is **being rebuilt natively in EasyEDA Pro** (a KiCad/SKiDL design does not qualify for EasyEDA Spark; the user will not register or submit until the EasyEDA design exists, so nothing may be claimed before that). Project file `hardware/easyeda/spurious-force-balance.eprj2`, project UUID in the notes. Done: four mechanical boards drawn and DRC-clean (`arm`, `clamp_plate`, `clamp_ground`, `elec_board`); sensor heads `sensor_head_1` and `sensor_head_2` have valid schematics and their components were imported into the PCBs (unplaced, no board outline or routing yet).

## Waiting on the user (`docs/TODO-arcticoder.md`)

The arm order payment and the small-board JLC quote (unchanged from before, with the coupons ending 2026-11-25/26), optional sensor-head PCBA order, AliExpress lines, the printing and build; plus the item that says when to commit.

## Next agent tasks, in order (`docs/TODO-agent.md`)

0. Update (later in 2026-10-30): head 1 now has outline, autorouted signals and a filled top GND pour; its bottom pour and 6 GND connection errors remain (rebuild guard needs a server restart; recipe in `kb/easyeda_spark_notes.md`). The user was asked to restart the server. Head 2 and everything below are unchanged.
1. Sensor heads in EasyEDA: outline (26 x 17 mm, `heads_panel/build_panel.py` has the geometry), place the imported parts (MMC5983MA LGA, TMP117 WSON, JST-SH, caps), route, ground pour, DRC; move head 2's capacitor out of the title block; recheck head 2's `valid:false` warning. Then the panel (76 x 70 mm rails, tooling holes, fiducials, mouse bites) in the project's Panel1.
2. Silkscreen labels on the four mechanical boards.
3. The instrument main-board schematic (50 JLC parts, `schematic/main_board.py` is the source of the nets) and board, the same way; then OSHWLab text and the Spark registration answers (`docs/spark_application.md` is a draft; Spark registration closes 2026-11-30).
Imports need the user's click (Design > Import Changes from Schematic, Alt+I, in the PCB tab): write each needed click as a step in `TODO-arcticoder.md`.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm (torsion balances in pictures are shorter): the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote; the EasyEDA arm would then be redrawn.

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user; do not commit unless told.

## Read first

Both `docs/kb/README.md` files, `kb/easyeda_spark_notes.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, `docs/plan.md`, `docs/fabrication.md`; then `lab/docs/kb/jlc_account_and_quotes.md`.
