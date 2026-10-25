# TODO — completed

Dated entries, newest first.

- 2026-10-24 — WP4, the schematic (as checked netlists): SKiDL descriptions of the main board and four head boards in `hardware/instrument/schematic/`, symbols and footprints for all 50 BOM parts in `hardware/instrument/lib/`; `schematic_test.py` (in the smoke tests) checks pin accounting, data-sheet nets, symbol pins against footprint pads, BOM equality with `parts.py` and design numbers. Reading the RP2040 hardware design guide and the ADS131A04 data sheet against the BOM changed it: the exact Raspberry Pi crystal (ABM8-272-T3), 2 A ferrite beads on the 5 V rail (the 600 ohm bead is rated 200 mA), 50 V capacitors on the 24 V boost; the extended-part budget went from 25 to 27. Open: WP4b-WP4d in TODO-agent.md.

- 2026-10-24 — Part H (H1–H4), live JLC lookups: `@jlcpcb/cli` 0.5.0 installed globally under nvm (chosen over the MCP server); `hardware/tools/jlc_query.py live()` and `parts.py --live` check the
  48-part BOM against JLC's live stock, library type and PCBA type (about 80 s, sequential because JLC answers 429 to bursts); it flagged two Standard-PCBA-only parts (H5 open); `jlc install` compared with
  `easyeda2kicad` on the ADS131A04: same pins and pads, so WP4 keeps `easyeda2kicad`. Notes in `kb/pcb_toolchain_notes.md`.
  H5: the two Standard-PCBA-only sensors are kept and the electronics order goes on Standard assembly (about $17 more setup, two-sided placement allowed); the MSKSEMI LIS2DW12 clone was rejected for lack of a datasheet and a spec mismatch; `parts.py --live` now reports 0 flagged.
- 2026-10-24 — Parts F and G: licenses (MIT + CERN-OHL-P v2) in both repos; the user's JLC-shipping chat ingested into `docs/kb/fab_ordering_notes.md` (checked against JLC's Combine Shipping page, capabilities page,
  OSH Park docs) and deleted; fabrication review in `docs/fabrication.md`: the arm, clamp plates and fixed electrode become FR4 boards for JLC (KiCad files, DRC clean, Gerbers and `ORDER.md` in
  `hardware/balance/boards/fab/`), a torsion head, FR4 device card with a 0.5 W cap, a clamping loop with no printed plastic, the centre of mass hanging 32 mm below the strip (31 mrad per mm), a field-modelled
  damper in two layouts, a gap gauge; plan, assembly steps and README rewritten; the five AliExpress items ordered 2026-10-24 recorded in `lab`; both knowledge bases updated with a handoff note.

- 2026-10-23 — Part D, balance materials review: enclosure redesigned for uncut 2 mm 150 × 250 mm acrylic (pinwheel walls, two-sheet lid,
  printed shelves, foam-tape-shimmed slots); damper rebuilt for radially magnetized discs on edge with a field model (magpylib, cross-checked
  to 0.01% against the analytic axial field), 20 × 20 mm vane of one or two 0.3 mm pads; saw guide for the ballast and strip-cutting guide;
  trim seats and `PRINTED_MASS_G` after finding that centre-of-mass offset tilts the arm 66 mrad per mm; foil path for the plate electrodes
  with a terminal on the fixed plate; `docs/assembly.md`. Smoke tests: 2 run, 0 failed; the force-noise verdict is unchanged (0.108 nN).
- 2026-10-23 — Split out of `lab` into this repo, with the experiment's history kept (G1–G3, WP1–WP3,
  the balance CAD and model, the instrument parts and simulations).
