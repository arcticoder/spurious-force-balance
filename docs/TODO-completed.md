# TODO — completed

Dated entries, newest first.

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
