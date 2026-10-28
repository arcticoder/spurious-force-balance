# Session handoff — written 2026-10-24 (replace at each handoff; do not append)

## State at the end of the last chat

Done:
- The split from `lab` into this repo (2026-10-23), licenses (MIT + CERN-OHL-P v2) in both repos, G1-G3, WP1-WP3 (requirements, 50 JLC parts, analog simulations), Part H (live JLC lookups with the `jlc` CLI; `parts.py --live`; the electronics order is Standard PCBA), WP4 (the schematic as checked netlists: main board and four heads, `hardware/instrument/schematic/`).
- The mechanical redesign (Part F): an FR4 arm board on edge, FR4 clamp plates and fixed electrode as JLC boards, a torsion head, a 32 mm centre-of-mass hang, an FR4 device card with a 0.5 W cap, a
  field-modelled eddy damper (diametric and axial layouts), stock-size acrylic enclosure, cutting jigs. Gerbers and a DRC-clean KiCad file exist for four board designs in `hardware/balance/boards/fab/`
  (settings in `ORDER.md`). All smoke tests pass (`~/.venvs/lab-hw/bin/python tools/run_all_smoke_tests.py`); the force-noise verdict is unchanged: 0.108 nN, conditional GO (`python3 tools/force_noise_budget.py`).
- Knowledge bases of both repos brought up to date; the user's chat transcript on JLC shipping was ingested into `fab_ordering_notes.md` and deleted.

In progress / not started: WP9 and WP11 (see TODO-agent.md); WP4e sheets, WP10 and the experiment analysis are in the backlog; the firmware drivers (ADS131A04, MCP4728, sensors, lock-in, USB protocol, logger and analysis) are done and host-tested, the rest of WP8 waits for the board, WP5-WP11, A5 (the prototype noise measurement). The WP4 work is left uncommitted for the user to commit (standing instruction: the user commits).

## Waiting on the user

1. (Done 2026-10-26: the twist test found the N42 discs magnetized through the flat faces; `MAGNET_MAGNETIZATION` is now "axial", the CAD and `damper_holder` were regenerated and all checks pass.)
2. The JLC mechanical-board order: the user reads the quote (estimate $70-140 with shipping; ask before changing the design if the arm board alone is over about $60 or the parcel over 0.29 kg) and places it.
3. The remaining AliExpress lines (acrylic, 304 washers and nuts, JST-SH cable, weights, tools) after the JLC order is placed; the five items ordered 2026-10-24 are en route.
4. Printing the PLA frame (`docs/TODO-arcticoder.md` item 1) and building the balance (`docs/assembly.md`).
5. In `lab`: build the lock-in (`signal_conditioning/lockin_amplifier`) and the optical readout (`optical_shadow_readout`); the A5 prototype check needs both.

## Next agent tasks, in order

Nothing is startable without the user or the board (see `docs/TODO-agent.md`).
1. When the user returns quotes (`TODO-arcticoder.md` items 1-4): Part J4 in `TODO-BLOCKED.md` (arm material decision; the panel Gerbers if the panel quote wins; update `ORDER.md`). If the user orders the sensor-head panel, check the placement preview notes against `heads_panel/ORDER.md`.
2. When the user returns the CNC and HDI captures (`lab/docs/jlc/`): Part K and J2 with real CNC options; the A5 results into `params.py` and the budget; then WP5-WP7 if the verdict stays GO.
3. When a board exists: `bringup_adc.py`, `bringup_sensors.py`, the scripted analog bring-up, the device-side `main.py`, PIO and DMA (`TODO-BLOCKED.md`).

Coupon deadlines (2026-11-25 for most new-user coupons) are in `lab/docs/jlc/coupons.md`; the order plan is in `docs/fabrication.md`.

## Read first

Both `docs/kb/README.md` files, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, `docs/plan.md`, `docs/fabrication.md`, `docs/assembly.md`; then `lab/docs/TODO-arcticoder.md`.
