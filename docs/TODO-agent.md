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

### EasyEDA Pro conversion and Spark submission (the bridge is connected on the user's side; the EasyEDA MCP tools were not loaded in the session that wrote this, so check ToolSearch for `easyeda` first)
- [ ] Redo the designs natively in EasyEDA Pro through the MCP tools (a KiCad/SKiDL design does not qualify for Spark, so an import alone is not enough; use the KiCad files as the reference for geometry, nets and parts, and build the EasyEDA project from them) (the four balance boards in `hardware/balance/boards/*.kicad_pcb`, `heads_panel.kicad_pcb`, and the `.kicad_sch` from `hardware/instrument/schematic/out/`), through the MCP tools or EasyEDA Pro's own KiCad import; fix what the importer loses (outline, drills, stackup, LCSC part numbers); run DRC; compare with the KiCad DRC results; one project with the boards as separate PCBs.
- [ ] Write the OSHWLab submission text and the Spark sponsorship application from what the pages show once the user is logged in (the official Spark pages are JS-rendered and could not be read from a session; `kb/easyeda_spark_notes.md` has what is known). Registration closes 2026-11-30.
Nothing is startable without the user or the board. Waiting on the user: the JLC quotes and the sensor-head order decision (`TODO-arcticoder.md`), which feed Part J4 in `TODO-BLOCKED.md`; waiting on the board: the rest of WP8 and the
bring-up. The next work when something arrives: the arm decision and panel Gerbers (J4), the early sensor-head order's file upload checks, or A5's results into the model.
