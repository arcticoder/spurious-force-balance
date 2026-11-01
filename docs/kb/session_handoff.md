# Session handoff — written 2026-10-31 (evening) (replace at each handoff; do not append)

## State of the EasyEDA redesign (details and recipes in `kb/easyeda_spark_notes.md`)

Project `hardware/easyeda/spurious-force-balance.eprj2` (UUID in the notes; profile `full`; Node 24.22.1; bridge connected through EasyEDA Pro's Advanced > MCP Bridge > Connect, which must be repeated after the computer sleeps).

| Board (PCB uuid) | State |
|---|---|
| `arm` 7bc3367e1c2d2364, `clamp_plate` 3ddf518a3b25253b, `clamp_ground` a1c4bc42816028ee, `elec_board` 05dc52ccb60a9ca9 | drawn, silkscreen done, DRC clean |
| `sensor_head_1` 6b230bf28446d8f9, `sensor_head_2` 868eebde0c888e1b | outlined, autorouted, GND pours on both layers, DRC clean |
| `main_board` 85757acc0463db9b (Board7, schematic page a173bbce992e5a91) | schematic complete and validated (164 parts, 111 nets, no floating pins, ERC 0 errors / 57 warnings); imported into the PCB by the user (164 components); **unplaced and unrouted** (DRC: 519 connection errors + 1 clearance) |
| `panel1` | parked: the API has no panel-content calls and the user could not paste boards into it; the order files are the KiCad panel Gerbers in `hardware/instrument/heads_panel/out/` |

The committed `.eprj2` already holds the four mechanical boards and head 1 (the user commits it at milestones only).

## Offline validation layer (new)

`tools/validate_easyeda.py` (standard library only) checks the EasyEDA project from live PCB netlists (`--netlists hardware/easyeda/exports/netlists`, pulled through `easyeda_api_call` `PCB_Net.getNetlist`; no user export needed; recipe in `kb/easyeda_validation.md`) or from an `.epro2`. Checks: naming, pads without nets, I2C pull-ups, control-pin bias, floating inputs (pin types from `hardware/instrument/lib/jlc.kicad_sym`), a cross-check against the SKiDL netlist, BOM numbers, and `exports/native_checks.json`. First main-board run (2026-10-31) found that the **main_board PCB is stale**: imported before the TLV9062 unit-B designators were fixed, so pads 5-7 of U14/U15 have no nets (the schematic is correct). Alt+I said "no changes", so U14/U15 were deleted from the PCB; the user redoes Alt+I to re-add them (item 0 of `TODO-arcticoder.md`). After that, re-pull the netlists and expect 0 errors except the crystal stand-in warning.

## Next agent tasks, in order (`docs/TODO-agent.md`)

1. Main board PCB: wait for the user's re-import, re-pull and validate the live netlists; no placement was done yet (164 parts at `easyeda_pcb_modify_component` one call each, or compute positions in a scratch script first; the sync leaves parts in a spaced grid, 2 layers, no stackup change possible via API); then outline (size from `docs/plan.md`), floorplan by function (power entry and boost on one edge, USB-C, RP2040 with its crystal and flash, the 4-channel ADC with its analog supplies away from the boost converter, op-amp/LED drive, connectors on the edges), place with `easyeda_pcb_modify_component`, autoroute with GND ignored (`easyeda_pcb_autoroute`), create GND pours on both layers, ask the user to rebuild copper in Copper Manager, autoroute GND, DRC to 0, re-run the validator, then tell the user the `.eprj2` is ready to commit. A 164-part 2-layer board may need to be 4 layers or hand-routed in places: check `easyeda_board_stackup` first.
2. Main-board loose ends: the ADC crystal U13 has the C9002 stand-in's LCSC fields (set C21900468 / 3X016384UP and check pads); the schematic page is a spaced grid, not presentable (tidy it before the OSHWLab upload); the TLV9062 unit B symbols are U14/U15 (second halves of chips U14/U15).
3. OSHWLab text and the Spark registration answers (`docs/spark_application.md` is a draft); registration closes 2026-11-30 and the user registers only after the EasyEDA design really exists.

## Gotchas learnt (all in `kb/easyeda_spark_notes.md`)

Keep the working tab focused (`DMT_EditorControl.openDocument(uuid)` first; lost focus looks like timeouts or "failed to get pins"); chunk big nets at 6 pins per `connect_pins_by_net`; use primitive ids not designators; EasyEDA numbers designators itself; `easyeda_pcb_rebuild_copper` locks after a failed read-back (persisted in `~/.easyeda-mcp-pro/easyeda-mcp-pro.sqlite`; do not edit it): the user rebuilds copper from the UI; `easyeda_pcb_add_text` fails (use `PCB_PrimitiveString.create`); bottom silk under top copper is invisible in the combined view.

## Open question from the user, still unanswered in the repo

Why the arm is 208 mm (torsion balances in pictures are shorter): the noise budget barely depends on arm length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper and needs rework; it could fit JLC's cheap 100 x 100 mm tier. If the user wants it shorter, parametrize `ARM_HALF_LENGTH` first and requote; the EasyEDA arm would then be redrawn.

## Supply chain

An AliExpress order of 2026-10-30 is en route: 20 M3 thin (DIN439) 304 stainless nuts and digital calipers (`lab/docs/orders.md`). Nothing else is en route; the JLC arm and small-board orders and the AliExpress balance list wait on the user (`TODO-arcticoder.md`, coupons end 2026-11-25/26).

## Standing rules (see `kb/project_workflow_notes.md`)

Never state a JLC price that is not in the user's words or captures; do not edit or mine `docs/history.md`; do not quote the user or describe how they said things; never commit (the user stages and commits everything after each chat; only flag `.eprj2` milestones in `TODO-arcticoder.md`).

## Read first

Both `docs/kb/README.md` files, `kb/easyeda_spark_notes.md`, `kb/easyeda_validation.md`, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`; then `lab/docs/kb/jlc_account_and_quotes.md` if a JLC question comes up.

## Reminders moved out of TODO-arcticoder.md (2026-11-01)
The EasyEDA bridge drops after computer sleep (user: Advanced > MCP Bridge > Connect; keep the PCB tab focused). Spark registration closes 2026-11-30 and waits for the finished EasyEDA design. Next `.eprj2` milestone to ask the user to commit: main board placed, routed, DRC-clean, validator clean, `native_checks.json` refreshed. `PCB_Document.startAutoLayout` returned nothing and moved no parts (2026-11-01; EasyEDA not busy afterwards, API calls work again).
