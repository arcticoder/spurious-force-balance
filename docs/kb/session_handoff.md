# Session handoff — written 2026-11-01 (replace at each handoff; do not append)

**Latest (end of chat 3): job API patch live and working (see the last bullets of easyeda_spark_notes.md); main_board DRC at the end: 41 clearance + 24 connection errors (6 GND, 18 signal); waiting for the user's DRC panel detail (TODO-arcticoder item 1), then fix clearance errors, hand-route/re-place the signal nets, DRC, milestone routine. Older note: (chat 2; autorouter crawled twice, see easyeda_spark_notes.md last bullet; GND route re-sent after EasyEDA restart, state unknown):** user's Copper Manager rebuild worked (`PCB_PrimitivePoured.getAll`: GND_top 369 fills, GND_bot 15). DRC then: 118 connection errors (98 GND, 22 signal on the same 11 nets as before, so the second signal pass added nothing). A GND-only autoroute (`keep`) was started and timed out the bridge as usual; it runs inside EasyEDA, the user restarted EasyEDA after it crawled; the job-API/router patch (`tools/patch_easyeda_autoroute_jobs.py`) is the way forward (`TODO-arcticoder.md` item 1 asks for one more restart). Next: re-run `PCB_Drc.check(true,false,true)` (the result lists errors as `[MaxDepth]` strings with per-net counts: use the counts), then a signal autoroute for the 11 nets, hand-route the rest (`PCB_PrimitiveLine.create` / `easyeda_pcb_add_track`, `easyeda_pcb_add_via`).

## State of the EasyEDA redesign (recipes and gotchas in `kb/easyeda_spark_notes.md`)

Project `hardware/easyeda/spurious-force-balance.eprj2` (UUID in the notes; profile `full`; Node 24.22.1). Bridge: EasyEDA Pro Advanced > MCP Bridge > Connect (auto-reconnect is on; it still drops after sleep or a restart of EasyEDA).

| Board (PCB uuid) | State |
|---|---|
| `arm` 7bc3367e1c2d2364, `clamp_plate` 3ddf518a3b25253b, `clamp_ground` a1c4bc42816028ee, `elec_board` 05dc52ccb60a9ca9 | drawn, silkscreen done, DRC clean |
| `sensor_head_1` 6b230bf28446d8f9, `sensor_head_2` 868eebde0c888e1b | routed, GND pours, DRC clean |
| `main_board` 85757acc0463db9b (schematic page a173bbce992e5a91) | schematic and PCB netlist agree (164 parts; validator 0 errors); outline 106.7 x 87.6 mm (x -100..4100, y -3300..150 mil); **placed** by `tools/floorplan_main_board.py` (all 164 parts, DRC placement-clean); signals autorouted in two passes (second pass log: "nets completion 90.09%, add tracks 9, vias 2"); **GND pours GND_top (id 6a590aab3806d515, layer 1) and GND_bot (deb152eb4908f417, layer 2) created at the end of this session but not yet filled**: the user rebuilds copper in Copper Manager (item 0 of `TODO-arcticoder.md`) |
| `panel1` | parked (no panel-content API); order files are the KiCad panel Gerbers in `hardware/instrument/heads_panel/out/` |

The committed `.eprj2` holds the four mechanical boards and head 1 only. The main board is NOT at a commit milestone.

## Next agent tasks, in order (`docs/TODO-agent.md`)

1. Main board routing: after the user's Copper Manager rebuild, run `easyeda_drc_run` (output is 60 KB; save-to-file then count with python: rules, nets), then a GND autoroute (`routingNets:["GND"]`, `existingPrimitiveMode:"keep"`) for pads enclosed by traces, and a signal pass (`routingNets:[...]` for the nets DRC still lists) if signals remain. The autorouter times out the bridge at 15 s but keeps running in EasyEDA (a progress percentage shows; the log line "Auto routing completed" marks the end; the user reports it): never start a second run while one is going. Aim for DRC 0; hand-route or move parts (`easyeda_pcb_place_batch`, `easyeda_pcb_modify_component`) for what the router leaves.
2. Milestone routine (`kb/easyeda_validation.md`): refresh `hardware/easyeda/exports/native_checks.json` (main_board no longer `wip` once routed), pull live netlists (`PCB_Net.getNetlist` through `api_call`, write `exports/netlists/<board>.json`), run `python3 tools/validate_easyeda.py --netlists hardware/easyeda/exports/netlists -v`, report in `TODO-arcticoder.md`, then ask the user to commit the `.eprj2`. No user export is needed.
3. Connector orientation: JST SM0xB and USB-C orientation was inferred from pad geometry (signal pads inward, tabs outward); ask the user to check the 3D view once routed.
4. Main-board loose ends: ADC crystal U13 carries the C9002 stand-in's LCSC fields (set C21900468 / 3X016384UP, check pad numbering); the schematic page is a spaced grid (tidy before the OSHWLab upload); board size could shrink after routing (Standard assembly needs at least 70 x 70 mm).
5. OSHWLab text and the Spark registration answers (`docs/spark_application.md` is a draft); registration closes 2026-11-30; the user registers only after the EasyEDA design exists.

## What changed this session (details in the notes)

- Validator now reads live netlists (`--netlists`), found the stale main-board import; cause was the second units of the TLV9062 (`AddIntoPcb` false); fixed by setting it true on the unit-B symbols (U14, U15) plus the user's Alt+I.
- MCP server: `easyeda_pcb_modify_component` was broken upstream (no project id); fixed and `easyeda_pcb_place_batch` added in the user's fork `arcticoder/easyeda-mcp-pro` (branch `fix/pcb-component-project-id`, upstream PR https://github.com/oaslananka/easyeda-mcp-pro/pull/811). `~/.claude.json` runs the fork's `dist/index.js` (rebuild with Node 24.22.1 `npx tsc -p tsconfig.build.json` after changes; the `pnpm` shim for `verify:fast` is in the notes). Upstream may merge; keep using the fork until then.
- Floorplan tooling: `tools/floorplan_main_board.py` (inputs `exports/main_board_parts.json`, output `exports/main_board_placement.json`; regenerate the inputs from `PCB_PrimitiveComponent.getAll` + `PCB_PrimitivePad.getAll` if the schematic is re-imported and ids change).
- EasyEDA's own `PCB_Document.autoLayout` is non-deterministic and was abandoned.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm (torsion balances in pictures are shorter): the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote; the EasyEDA arm would then be redrawn.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). Nothing else is en route; the JLC arm and small-board orders and the AliExpress balance list wait on the user (`TODO-arcticoder.md`, coupons end 2026-11-25/26).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo (the user stages and commits everything after each chat; only flag `.eprj2` milestones in `TODO-arcticoder.md`); `TODO-arcticoder.md` holds only separately numbered tasks for the user (no notes to self), and any task given in chat is also written there.

## Read first

Both `docs/kb/README.md` files, `kb/easyeda_spark_notes.md`, `kb/easyeda_validation.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`; then `lab/docs/kb/jlc_account_and_quotes.md` if a JLC question comes up.
