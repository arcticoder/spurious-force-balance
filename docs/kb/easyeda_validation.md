# EasyEDA offline validation layer (2026-11-01)

Purpose: a second, tool-independent check of the EasyEDA project, runnable by any LLM or CI job without MCP access to EasyEDA. The user's rule: run it at every milestone, i.e. before telling them to commit `hardware/easyeda/spurious-force-balance.eprj2`, and report the result in `TODO-arcticoder.md`.

## What runs
- `python3 tools/validate_easyeda.py [project.epro2] [--json report.json] [--strict] [-v] [--board NAME]` (standard library only). Default input: the newest `.epro2` in `hardware/easyeda/exports/`, else the newest `hardware/easyeda/*_backup/*.epro2` (EasyEDA writes those itself; the folder is gitignored).
- It reads the `.epru` inside the `.epro2` (a zip): one JSON record per line (`header||payload|`), documents DEVICE (LCSC number `Supplier Part`, library prefix `Designator: "C?"`, `Value`), FOOTPRINT (pad numbers), PCB (COMPONENT, ATTR Designator/Device/Footprint, PAD_NET pad to net, NET, VIA, POLY...). The netlist is the PCB's pad-to-net table, so it is only as current as the last "Import Changes from Schematic".
- Checks: NAME-* (designators and net names), CONN-* (pads without a net unless the board's SKiDL netlist `hardware/instrument/schematic/out/<board>.net` leaves them open on purpose; single-pad nets), PULL-* (I2C pull-ups on boards with the RP2040 master; reset/enable/run/boot/CS nets need a driver or bias; USB-C CC 5.1 k to ground), FLOAT-* (input pins by electrical type from `hardware/instrument/lib/jlc.kicad_sym`: unconnected, or on a net with no driver or bias), SKIDL-* (every net's (LCSC, pin) multiset and part counts against `<board>.net`), BOM-* (assembled parts without LCSC number; the ADC crystal stand-in C9002/C9900177807 for C21900468), NATIVE-* (EasyEDA's own ERC/DRC, see below).
- Exit code 1 on any ERROR; `--strict` also on WARN.

## ERC and DRC are EasyEDA-native and cannot run offline
An agent with MCP access records them in `hardware/easyeda/exports/native_checks.json` at each milestone (`wip:true` downgrades a still-unrouted board to WARN): PCB: `PCB_Drc.check(true,false,true)` through `easyeda_api_call` with that PCB focused (`DMT_EditorControl.openDocument(pcbUuid)` first); an empty result list is clean; schematic: `easyeda_erc_run` (scope focused) and `easyeda_schematic_validate_netlist`. Record counts, the date, and the project save time. The validator only reads this file; it warns when a board has no entry.

## Getting the export (EasyEDA's file-export tools do not work through the bridge)
`easyeda_export_netlist`, `easyeda_bom_export` and `easyeda_pcb_export_route_context` all answer "Bridge did not return data" on this build (the underlying API returns a `File` object the bridge cannot serialize), and `.eprj2` (SQLite) keeps documents in compressed history blobs. So the `.epro2` comes from the user: EasyEDA Pro File > Export > project file (`.epro2`), saved as `hardware/easyeda/exports/spurious-force-balance.epro2` (menu name unverified; EasyEDA's own backups in `*_backup/` have the same format). Ask for it as a step in `TODO-arcticoder.md` at each milestone, together with the `.eprj2` commit.

## Milestone routine (agent)
1. Save the project, run ERC/DRC per board through MCP and update `native_checks.json`.
2. Ask the user for the fresh `.epro2` export (step in `TODO-arcticoder.md`).
3. `python3 tools/validate_easyeda.py -v --json hardware/easyeda/exports/validation_report.json`; fix ERRORs or explain them; record the result line in `TODO-arcticoder.md` next to the commit request.

## Known state
- Tested on the 2026-10-30 backup (arm, clamp_plate, clamp_ground, elec_board, sensor_head_1, sensor_head_2): 0 errors. The main board is not in that export yet; its first run is pending the user's export (expect: many NATIVE-3 WARN while unrouted, BOM-2 for the crystal, and whatever the netlist cross-check finds).
- EasyEDA numbers designators itself (RP2040 = U4), so the SKiDL cross-check matches on (LCSC, pin) per net name, not on designators.
