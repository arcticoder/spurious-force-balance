# KB: main-board layout pipeline (WP5), started 2026-11-08

Audience: future LLM sessions. The user's direction (2026-11-08): fab-assembled electronics, no hand-built stage; the layout does not wait on A5 (the breadboards `lockin_amplifier` and `optical_shadow_readout` in `lab` are no longer prerequisites; the board's digital lock-in and optical front end replace them).

## Pipeline (all in `hardware/instrument/layout/mainboard.py`, run with `~/.venvs/lab-hw/bin/python`)

1. `mainboard.py place [W H]` builds `layout/out/main_board.kicad_pcb` (kiutils) from `schematic/out/main_board.net` (164 parts, 111 nets) and `lib/jlc.pretty`: four copper layers, nets on pads, connectors fixed at the edges (USB-C bottom, six 4-pin JST-SH top, four 2-pin JST-SH left, five 2.54 mm headers right), the rest placed by a damped force-directed pass (signal nets pull, power nets weakly, each capacitor toward the IC sharing its power net) then a repulsion-only legalisation with jitter. Deterministic. 110 x 90 mm gives 0 overlaps (parts are about 21% of the area).
2. `mainboard.py route` writes a Specctra DSN (own writer, no pcbnew), runs the bundled Freerouting 2.5.0 (`~/tools/freerouting/freerouting-2.5.0-linux-x64/bin/freerouting -de .dsn -do .ses -mp 8`) and imports the SES back as segments and vias (`import_ses`). A full run takes about 9 minutes (fanout 40 s, eight passes); the SES is written only at the end, so the `-do` file does not exist while it runs (the wrapper's 10-minute limit killed one run; run Freerouting directly in the background and wait for its exit).
3. DRC: `kicad-cli pcb drc --format json --severity-all --output out/drc.json out/main_board.kicad_pcb`.

## Result of the first run (110 x 90 mm, 0.2 mm tracks, 0.15 mm clearance, 0.6/0.3 vias)

415 nets to route, 9 left unrouted, DRC: 3 clearance, 6 tracks under 0.15 mm (0.10-0.12 mm pieces), 8 dangling vias, 2 annular-width, 2 padstack, 2 malformed courtyards (library footprints), 199 silk overlaps and 199 silk-over-copper (silk comes from the easyeda2kicad footprints; clean up before the fab outputs), 164 `lib_footprint_issues` (harmless, footprints are not from a library table). Not a fabricable board yet. Not yet done: ground planes on the inner layers (all four layers are used for routing), wider power tracks, USB differential pair, analog/digital partition checks, mounting holes, connector orientation (rotations were guessed: 0 on top, 90 left/right), silk and refdes, the 4-layer stackup/finish settings, and the visual review (WP6).

## Gotchas

- KiCad 9.0.9's Python `pcbnew` segfaults headless on `LoadBoard` and `BOARD.SetCopperLayerCount` raises a type error, so `ExportSpecctraDSN`/`ImportSpecctraSES` are unusable; kiutils plus the own DSN/SES code replaces them.
- `Footprint.description` from the easyeda2kicad libraries can contain newlines and colons; `kicad-cli` then fails with "Failed to load board". `mainboard.py` blanks it. When a board will not load, bisect by footprint (write one footprint at a time and run `kicad-cli pcb drc`).
- `kicad-cli pcb drc` takes its clearance from the `.kicad_pro` `net_settings.classes[Default]` next to the board, not from `board.design_settings.rules`; with the default 0.2 mm it reported 502 false clearance errors against a 0.15 mm route.
- kiutils writes pad angles as given: footprint rotation must be added to each pad's angle for connectors rotated by 90.
- DSN: unit um, y up (KiCad's y is down), one `component` block per image name, all parts on the front side.
