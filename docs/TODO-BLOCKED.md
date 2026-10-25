# TODO — agent, blocked

> Open items are in `docs/TODO-agent.md`; finished items in `docs/TODO-completed.md`.

These wait on the user's balance build (see `TODO-arcticoder.md`) or on the A5 result.

## A5 — prototype noise measurement (needs the printed balance, the lock-in and the optical readout)
- [ ] Test the mechanics and the optical readout's displacement sensitivity on the bench: the printed/FR4 balance, the breadboard optical readout and lock-in (`optical_shadow_readout`), the Pico.
      Compare the measured resonance, Q and displacement noise, the optical photocurrent (Rf) and the trim procedure's real numbers with G2/G3; update `params.py`, rerun `tools/force_noise_budget.py`.
      A disagreement over a factor of a few sends the design back to G2/G3, not to the fab.

## After A5, if the verdict stays GO
- [ ] WP5 — Layout: RP2040 per the reference layout, ADC per its data sheet, analog/digital partition (the plate driver and LED sinks are the noisiest blocks), decoupling, USB pair, mounting holes and
      connector positions from G2, silkscreen pin names; DRC clean against JLC's rules.
- [ ] WP6 — Visual review from `kicad-cli pcb render` images and a written checklist.
- [ ] WP7 precheck — in JLC's placement preview confirm the parts the schematic could not verify from a data sheet: KT-0603R LED polarity (footprint marks conflict), the ADC crystal C21900468's pad numbering (a stand-in symbol is used), USBLC6-2SC6 pin 1 position, the SM02B/SM04B mounting tabs (pins 3-4 and 5-6 are wired to GND), the TS-1187A pad pairs; and the VBPW34S/IR26-21C rotation (anode/cathode sides per the Vishay and Everlight drawings).
- [ ] WP7 — Fabrication outputs in `hardware/instrument/fab/`: Gerbers + drill, BOM and CPL in JLC's format (rotations checked against JLC's placement preview), an order-settings README (Standard PCBA,
      layers, thickness, finish, quantity minimums checked at the time); run `parts.py --live` first.
