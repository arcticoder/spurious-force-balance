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
Order of promotion: (1) `clamp_ground` placed 2026-11-06; (2) `clamp_plate` is on the user's list now: `clamp_plate_gerbers.zip`, 16 x 14 mm, same settings as `clamp_ground`, deburring line included, two plates per balance; (3) the AliExpress balance list: 7 clear acrylic sheets (2 mm, 150 x 250 mm), 50 M3 flat 304 washers (3.2 x 7 mm), 2 JST-SH 2-pin cables with flying leads (100-150 mm), a calibration weight set (1 mg-500 mg, class stated), and the hand tools not in the inventory (junior hacksaw, flat needle file, craft knife, steel ruler); (4) optionally the sensor-head panel (about 13 parts; New User SMT coupon ends 2026-11-25) with a 4-pin JST-SH cable, if the user wants it before the balance is built.
Because AliExpress shipping is slow, promote the AliExpress list as soon as `clamp_plate` is placed, not after.

### Printing from the MCP servers (agent-run; needs the user's explicit go in the message)
The orcaslicer and 3d-printer MCP servers give direct control of Orca and the K1 (`lab/docs/inventory.md` filament section; the wsl workspace's KB has the connection notes). Not started: no printer heating or print start without the user's explicit request. Open for the balance frame: reslice `balance.3mf` in Orca and check the Hyper PLA profile; a pause-and-swap plan for the white spool if the print needs more than its remaining filament (user to be present for spool loading and the riser vents).

