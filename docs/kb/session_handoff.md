# Session handoff — written 2026-10-24 (replace at each handoff; do not append)

## State at the end of the last chat

Done:
- The split from `lab` into this repo (2026-10-23), licenses (MIT + CERN-OHL-P v2) in both repos, G1-G3, WP1-WP3 (requirements, 50 JLC parts, analog simulations), Part H (live JLC lookups with the `jlc` CLI; `parts.py --live`; the electronics order is Standard PCBA), WP4 (the schematic as checked netlists: main board and four heads, `hardware/instrument/schematic/`).
- The mechanical redesign (Part F): an FR4 arm board on edge, FR4 clamp plates and fixed electrode as JLC boards, a torsion head, a 32 mm centre-of-mass hang, an FR4 device card with a 0.5 W cap, a
  field-modelled eddy damper (diametric and axial layouts), stock-size acrylic enclosure, cutting jigs. Gerbers and a DRC-clean KiCad file exist for four board designs in `hardware/balance/boards/fab/`
  (settings in `ORDER.md`). All smoke tests pass (`~/.venvs/lab-hw/bin/python tools/run_all_smoke_tests.py`); the force-noise verdict is unchanged: 0.108 nN, conditional GO (`python3 tools/force_noise_budget.py`).
- Knowledge bases of both repos brought up to date; the user's chat transcript on JLC shipping was ingested into `fab_ordering_notes.md` and deleted.

In progress / not started: WP4b-WP4d (a meaningful ERC and sheets, stand-in symbol checks, boost ripple; see TODO-agent.md), WP5-WP11, A5 (the prototype noise measurement). The WP4 work is left uncommitted for the user to commit (standing instruction: the user commits).

## Waiting on the user

1. The twist test on the N42 discs ("detent" = magnetized across the diameter, the default; "free" = through the flat faces): it decides which `damper_holder` is printed. If "free", set `MAGNET_MAGNETIZATION = "axial"` in `hardware/balance/params.py`, rerun `balance.py`, `boards.py`.
2. The JLC mechanical-board order: the user reads the quote (estimate $70-140 with shipping; ask before changing the design if the arm board alone is over about $60 or the parcel over 0.29 kg) and places it.
3. The remaining AliExpress lines (acrylic, 304 washers and nuts, JST-SH cable, weights, tools) after the JLC order is placed; the five items ordered 2026-10-24 are en route.
4. Printing the PLA frame (`docs/TODO-arcticoder.md` item 1) and building the balance (`docs/assembly.md`).
5. In `lab`: build the lock-in (`signal_conditioning/lockin_amplifier`) and the optical readout (`optical_shadow_readout`); the A5 prototype check needs both.

## Next three agent tasks, in order

1. If the twist test says "free": switch to the axial layout, regenerate everything, rerun all checks. Otherwise: nothing here.
2. WP4b-WP4d in `docs/TODO-agent.md`: pin types and `kicad-cli sch erc`, hierarchical sheets, verify the stand-in symbols (polarity, the ADC crystal footprint), boost ripple and the DAC's 3.3 V ceiling.
3. Ingest the A5 results when the user has them: the measured noise spectrum, the optical photocurrent (Rf), the trim procedure's real numbers; update `params.py` and rerun the budget; then WP5-WP7 if the verdict stays GO.

## Read first

Both `docs/kb/README.md` files, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, `docs/plan.md`, `docs/fabrication.md`, `docs/assembly.md`; then `lab/docs/TODO-arcticoder.md`.
