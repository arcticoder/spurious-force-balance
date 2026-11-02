# Session handoff — written 2026-11-01, end of chat 4 (replace at each handoff; do not append)

**Where chat 4 ended:** `main_board` DRC is 0 clearance errors and 44 connection errors (26 GND, 18 signal on 9 nets). The EasyEDA install is patched (`tools/patch_easyeda_autoroute_jobs.py`, details in `kb/easyeda_spark_notes.md`, last bullets): job-style autorouting with progress/cancel and a `router` option, full DRC detail (`PCB_Drc.checkJson`), direct copper rebuild (`PCB_PrimitivePour.rebuildCopperById`). All of it is live (the user restarted EasyEDA after the last patch). The user does not click through the app any more: code the change, then ask for a restart if a patch needs loading. No routing job is running at the handoff.

## State of the EasyEDA redesign (recipes and gotchas in `kb/easyeda_spark_notes.md`)

Project `hardware/easyeda/spurious-force-balance.eprj2` (UUID in the notes; profile `full`; Node 24.22.1). Bridge: EasyEDA Pro Advanced > MCP Bridge > Connect (auto-reconnect is on; it still drops after sleep or a restart of EasyEDA).

| Board (PCB uuid) | State |
|---|---|
| `arm` 7bc3367e1c2d2364, `clamp_plate` 3ddf518a3b25253b, `clamp_ground` a1c4bc42816028ee, `elec_board` 05dc52ccb60a9ca9 | drawn, silkscreen done, DRC clean |
| `sensor_head_1` 6b230bf28446d8f9, `sensor_head_2` 868eebde0c888e1b | routed, GND pours, DRC clean |
| `main_board` 85757acc0463db9b (schematic page a173bbce992e5a91) | schematic and PCB netlist agree (164 parts; validator 0 errors); outline 106.7 x 87.6 mm; placed by `tools/floorplan_main_board.py`; GND pours GND_top (6a590aab3806d515) and GND_bot (deb152eb4908f417) filled (rebuilt 2026-11-01 after the last router edits); routing incomplete: 26 GND connection errors (dangling stubs `(GND): e19xx/e20xx` left after I deleted 17 overlapping GND tracks/vias, plus pads U11_4, U11_10, C15_2, C14_2, C10_2, R24_2, U17_3) and 18 signal errors on LED1_MOD, 3V3_D, I2C_SCL, SPARE_A/F/G/H, USB_DP, QSPI_SD1 (two pads each; neither router connected them; SPARE_A/F/G/H run from the RP2040 area to the bottom-edge parts H1-H4) |
| `panel1` | parked (no panel-content API); order files are the KiCad panel Gerbers in `hardware/instrument/heads_panel/out/` |

The committed `.eprj2` holds the four mechanical boards and head 1 only. The main board is NOT at a commit milestone.

## Next agent tasks, in order (`docs/TODO-agent.md`)

1. Finish `main_board` routing. (a) Rebuild nothing yet; run a GND pass to completion: `PCB_Document.startAutoRouting` through `api_call` with `[{RoutingNets:["GND"],existingPrimitiveMode:"keep",router:"pangolin"}]`, poll `getAutoJobStatus(jobId)` every few minutes (the limit is now 60 minutes, a pangolin GND pass reached 60% after 13 minutes before; never `cancelAutoJob` unless it truly stalls: a cancelled pass leaves clearance-violating interim tracks), then `PCB_PrimitivePour.rebuildCopperById` for both pours, then `PCB_Drc.checkJson` (save to a file, never print it). (b) The 9 signal nets: both routers fail; route them by hand with `PCB_PrimitiveLine.create`/`easyeda_pcb_add_track` and vias (`easyeda_pcb_add_via`), choosing paths from the live primitives (an offline union-find over `PCB_Net.getAllPrimitivesByNet` data is a good checker), or move parts (`easyeda_pcb_place_batch`, now upstream) so the router can. (c) DRC 0.
2. Milestone routine (`kb/easyeda_validation.md`): refresh `hardware/easyeda/exports/native_checks.json`, pull live netlists, run `python3 tools/validate_easyeda.py --netlists hardware/easyeda/exports/netlists -v`, report in `TODO-arcticoder.md`, then ask the user to commit the `.eprj2`.
3. Connector orientation (JST SM0xB, USB-C) in the 3D view: ask the user once routed (a `TODO-arcticoder.md` item).
4. Loose ends: ADC crystal U13 carries the C9002 stand-in's LCSC fields (set C21900468 / 3X016384UP, check pad numbering); tidy the spaced-grid schematic page before the OSHWLab upload; board size could shrink after routing (Standard assembly needs at least 70 x 70 mm).
5. OSHWLab text and the Spark registration answers (`docs/spark_application.md` is a draft); registration closes 2026-11-30; the user registers only after the EasyEDA design exists.
6. Upstream: PRs #813 and #816 are merged into upstream easyeda-mcp-pro; #811 can be closed. The local fork (`~/Code/typescript/easyeda-mcp-pro`, `~/.claude.json` runs its `dist/index.js`) is older than upstream main: switch when convenient (rebuild with Node 24.22.1, session restart). The user declined a `BRIDGE_TIMEOUT_MS` change: do not offer it again.

## What changed this session (details in `kb/easyeda_spark_notes.md`, last bullets)

- Both GND pours filled (user's Copper Manager rebuild), then autorouter passes: JRouter GND 98 to 33 open connections; pangolin GND to 6 but cancelled at 60% (left 41 clearance errors); I removed the 17 overlapping GND objects the DRC detail named.
- Autorouter engines: `optimization` 1 = pangolin wasm (completion), 0 = JRouter; the new `router` option overrides it. JRouter and pangolin both stall near 50-60% on this board.
- App patching: the editor lives in `assets/pro-pcb/*/js/pcb.js`, `assets/pro-ui/*/js/ui.js`, `assets/pro-api/*/api.js` (not `app.js`); the patcher keeps `.orig` copies and `--revert` restores them; re-run it after an EasyEDA update (it refuses if an anchor string changed).
- Offline GND connectivity model (union-find over pads, tracks, vias and copper fills) was a scratchpad script only.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm (torsion balances in pictures are shorter): the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote; the EasyEDA arm would then be redrawn.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). Nothing else is en route; the JLC arm and small-board orders and the AliExpress balance list wait on the user (`TODO-arcticoder.md`, coupons end 2026-11-25/26).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit in this repo (the user stages and commits everything after each chat; only flag `.eprj2` milestones in `TODO-arcticoder.md`); `TODO-arcticoder.md` holds only separately numbered tasks for the user (no notes to self), and any task given in chat is also written there.

## Read first

Both `docs/kb/README.md` files, `kb/easyeda_spark_notes.md`, `kb/easyeda_validation.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`; then `lab/docs/kb/jlc_account_and_quotes.md` if a JLC question comes up.
