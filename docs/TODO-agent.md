# TODO — agent (Claude-facing)

> Finished items are recorded as dated entries in `docs/TODO-completed.md`.
> Items waiting on the user's build or on A5 are in `docs/TODO-BLOCKED.md`.
> Later work is in `docs/TODO-backlog.md`.
> The finished Parts D, F, G, H and the original Part A planning text are archived in `docs/kb/part_a_planning_archive.md`.
> The user's own list is `docs/TODO-arcticoder.md`. List conventions: the `lab` repo's `docs/kb/todo_list_conventions.md`.

Work that needs no hands, eyes or purchasing decision from the user. Keep this file to open items only: when one is finished, move a dated one-paragraph entry to
`TODO-completed.md` and delete it here; put long notes in `docs/kb/`.

---

## Open Items

### KiCad is the design source (the EasyEDA/Spark route was dropped 2026-11-01)
No EasyEDA or Spark work is open: the native redesign, its MCP tooling, `tools/validate_easyeda.py` and the notes are shelved (`kb/easyeda_spark_notes.md` header). The KiCad/SKiDL netlists, the four mechanical boards, the sensor-head panel and its Gerbers are the order files. Open KiCad work: WP5 main-board layout waits on A5 (`TODO-BLOCKED.md`); WP4e sheet rendering is in `TODO-backlog.md`.
Nothing is startable without the user or the board. Waiting on the user: the JLC quotes and the sensor-head order decision (`TODO-arcticoder.md`), which feed Part J4 in `TODO-BLOCKED.md`; waiting on the board: the rest of WP8 and the
bring-up. The next work when something arrives: the arm decision and panel Gerbers (J4), the early sensor-head order's file upload checks, or A5's results into the model.

### Staged orders (one order per day; promote to `TODO-arcticoder.md` only when the order before it is placed and I can set the next page up)
Order of promotion: (1) `clamp_ground` placed 2026-11-06; (2) `clamp_plate` is parked in `TODO-BLOCKED.md` (the user declined the current shipping price on 2026-11-08; it returns when a coupon or a lower shipping price makes it worth ordering); (3) the AliExpress balance list: 7 clear acrylic sheets (2 mm, 150 x 250 mm), 50 M3 flat 304 washers (3.2 x 7 mm), 2 JST-SH 2-pin cables with flying leads (100-150 mm), a calibration weight set (1 mg-500 mg, class stated), and the hand tools not in the inventory (junior hacksaw, flat needle file, craft knife, steel ruler); (4) optionally the sensor-head panel (about 13 parts; New User SMT coupon ends 2026-11-25) with a 4-pin JST-SH cable, if the user wants it before the balance is built.
Because AliExpress shipping is slow, promote the AliExpress list as soon as `clamp_plate` is placed, not after.

### Printing from the MCP servers (agent-run; no print or heater without the user's explicit request)
Direct control: the orcaslicer and 3d-printer MCP servers drive Orca and the K1 (connection notes in `~/Code/sysadmin/wsl/docs/kb`). The 3MF is a source for settings and per-part overrides, not required to print. State (2026-11-08): plate 1 (head, saw guide plate, elec_bracket, four shelves, vane_holder) is printed (1 h 37 min, black Hyper PLA). The Orca project (unsaved; this build cannot save projects) has four plates: 0 (nine parts, about 4 h), 1 (printed), 2 (gantry, 3 h 58 min), 3 (base, 3 h 25 min), all sliced at the settings of `print_requirements.md` section 6 except plate 0, which was sliced earlier at the wrong settings and needs a re-slice. User's windows: Mon 2026-11-09 2.5 h, Tue 11-10 1.5 h, Wed 11-11 4 h (gantry, 3 h 58 min). The K1's START_PRINT levels the bed itself on every print; no separate levelling run is needed. Next: split the plates to fit each window (the four 150 mm `encl_post_*` are most of plate 0; the base can be split or run over two sessions), re-slice, verify the G-code header (225/60 C) and send it with `upload_gcode print=true material=PLA`, then watch it with a Monitor on `print_stats`. Heater and print start need the user's explicit request each time. `params.py` now carries the sliced `vane_holder` mass (0.93 g); the user has only a kitchen scale, so no weighing is planned (the trim in assembly.md section 7 absorbs the difference). K1 notes: `~/Code/sysadmin/wsl/docs/kb/apps/k1-moonraker.md`.
