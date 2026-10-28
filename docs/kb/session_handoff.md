# Session handoff — written 2026-10-28 (replace at each handoff; do not append)

## State at the end of the last chat

Done (details in `docs/TODO-completed.md`):
- Split from `lab`, licenses (MIT + CERN-OHL-P v2), G1-G3 (0.108 nN per 1000 s, conditional GO), WP1-WP4: requirements, 50 JLC parts, analog simulations, the schematic as checked netlists (`hardware/instrument/schematic/`).
- Mechanics: FR4 arm board on edge, FR4 clamp plates and fixed electrode as JLC boards, printed frame, torsion head, eddy damper. **The N42 discs are magnetized through the flat faces** (twist test 2026-10-26): `MAGNET_MAGNETIZATION = "axial"`, CAD regenerated, all checks pass.
- Firmware layer, host-tested only (never run on a board): ADS131A04 and MCP4728 drivers, TMP117/MMC5983MA/LIS2DW12 drivers, fixed-point lock-in, USB protocol, logger and analysis, bring-up scripts (`hardware/instrument/firmware`, `host`); the lists of assumptions only silicon can confirm are in `kb/instrument_electronics_notes.md`.
- JLC work: `lab/docs/jlc/coupons.md`, `tools/jlc_parcel_mass.py`, `hardware/balance/material_study.py`, `arm_dxf.py`, `ORDER.md` as a field-by-field recipe, the sensor-head PCBA panel (`hardware/instrument/heads_panel/`, DRC clean, BOM/CPL, optional order), the bring-up and experiment procedures (`docs/bringup.md`, `docs/procedures.md`), the paper skeleton (`docs/paper/`), and a labelled picture of the apparatus (`docs/img/apparatus.png`, from `hardware/balance/render_labeled.py`).
- The arm order was **quoted by the user on 2026-10-28: FR4 1.2 mm, green, HASL, 5 pieces, C$14.17 + C$2.10 shipping, C$7.86 after the coupon**; the FR4 arm and HASL are decided (the aluminium arm is shelved).

## Waiting on the user (`docs/TODO-arcticoder.md`)

1. Pay for the arm order (check the thickness field reads 1.2 mm: it reverts to 1.6 mm, 0.34 kg, shipping C$12.05). Coupon ends 2026-11-26.
2. Quote and order the three small boards separately (the arm's parcel is 294 g of the 300 g line by JLC's rule with its packing); they were not quoted yet.
3. Optional: the sensor-head panel order (New User SMT coupon ends 2026-11-25), coupon dates for the 30/60-day coupons, the CNC and HDI quote-page captures, JLCMC fasteners, the remaining AliExpress lines (acrylic, 304 washers and nuts, JST-SH cables, weights, tools).
4. Print the PLA frame (the `damper_holder` is the flat-disc version now) and build the balance (`docs/assembly.md`); in `lab`, build the lock-in and the optical readout for the A5 prototype check.

## Open question raised by the user, not answered in the repo

The user looked at pictures of torsion balances and none has a 21 cm arm. The arm is 208 mm because of its layout (electrode at 80 mm, vane/damper at 55 mm, device card at 100 mm, ballast, flag) and because the noise budget hardly depends on its length (0.108 / 0.109 / 0.112 nN at 100 / 75 / 50 mm half-length, `fabrication.md`); a shorter arm weakens the damper (0.10 per pad at 75 mm) and needs a rework, and it could fit JLC's cheap 100 x 100 mm board tier. If the user wants a shorter arm, that is the first task: parametrize `ARM_HALF_LENGTH` (params.py), rerun `balance.py`, `boards.py`, the smoke tests, the damper and electrode positions, and requote.

## Next agent tasks, in order

Nothing is startable without the user or the board (`docs/TODO-agent.md`).
1. The user's answer on the arm length (above), then the small-board quote into `ORDER.md` and the order plan (`docs/fabrication.md`).
2. Placement-preview notes for the sensor-head panel if the user orders it (`heads_panel/ORDER.md`); the A5 results into `params.py` and the budget; then WP5-WP7 (`TODO-BLOCKED.md`; Standard PCBA needs 70 x 70 mm with rails).
3. When a board exists: the bring-up scripts, `bringup_analog.py`, the device-side `main.py`, PIO/DMA, verify the LIS2DW12 against ST's data sheet (`TODO-BLOCKED.md`).

Do not ask the user to click through JLC pages for numbers you can compute, and never state a JLC price that is not in their captures: the quote pages cannot be read from here (`kb/fab_ordering_notes.md`). `docs/history.md` is the user's chat transcript: do not edit it.

## Read first

Both `docs/kb/README.md` files, this repo's `docs/TODO-arcticoder.md` and `docs/TODO-agent.md`, `docs/plan.md`, `docs/fabrication.md`, `docs/assembly.md`; then `lab/docs/kb/jlc_account_and_quotes.md` and `lab/docs/TODO-arcticoder.md`.
