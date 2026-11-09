# TODO — agent, blocked

> Open items are in `docs/TODO-agent.md`; finished items in `docs/TODO-completed.md`.

These wait on the user's balance build (see `TODO-arcticoder.md`) or on the assembled board. The main board is no longer waiting on A5 (user's direction of 2026-11-08: fab-assembled electronics, no breadboards); the WP5-WP7 items below are open work, listed in `TODO-agent.md`.

## Parked: `clamp_plate` JLC order (decided 2026-11-08 by the user: not at the current shipping price)
- [ ] Revisit when a new coupon covers the order's shipping, or when the Global Standard Direct Line for a 0.14 kg parcel falls back toward US$1.50 (C$2.13) on a fresh quote. Then re-add the Gerber set (`clamp_plate_gerbers.zip`, 16 x 14 mm, 1.2 mm, HASL with lead, Single PCB, 5 pieces) to the cart and read the total; the user approves and pays. Shipping was C$8.14 (Y6, 2026-11-08); the Y6 and Y7 orders were cancelled by the user. The user accepts the four spare boards as waste and will not pay a shipping premium for them.

## Written procedures that need data or hardware to finish
- [ ] `hardware/instrument/firmware/bringup_analog.py`: scripted `[PASS]`/`[FAIL]` versions of the LED-sink, plate-driver, device-current and motor steps of `docs/bringup.md` section 4 (needs the board; the checks and limits are in that section).
- [ ] The slow-demodulation analysis script for the measurement campaign (`docs/procedures.md` section C, step 6): demodulate the logged deflection at the modulation frequency and report force per ampere or per watt with uncertainties; write it with the first real data.
- [ ] Fill the paper skeleton (`docs/paper/main.tex`): every `\todo{}` is a measurement or a figure; the results sections wait on A5 and the campaign.

## A5 — prototype noise measurement (needs the printed balance and the assembled main board with the sensor heads)
- [ ] Test the mechanics and the optical readout's displacement sensitivity on the bench: the printed/FR4 balance, the assembled main board (its optical readout and digital lock-in) and the sensor heads.
      Compare the measured resonance, Q and displacement noise, the optical photocurrent (Rf) and the trim procedure's real numbers with G2/G3; update `params.py`, rerun `tools/force_noise_budget.py`.
      A disagreement over a factor of a few sends the design back to G2/G3, not to the fab.

## WP8 remainder — needs the main board (after WP7) to test
- [ ] Device-side `hardware/instrument/firmware/main.py`: acquisition loop on DRDY, lock-in per period (`lockin.py`), sensor polling at 1 Hz, `protocol.py` packets over USB CDC (a 32-frame ADC packet every 4 ms), the safe
      start order (DAC 0 V, gates off, boost off, then enable) and a watchdog that turns the LED gates, device current and boost off if the host stops talking.
- [ ] LED modulation by PIO (a square wave on `LED1_MOD`/`LED2_MOD`, 1 kHz = 4 ADC samples on, 4 off at 8 kSPS, locked to the ADC frame count) and the DRDY-driven ADC read by PIO + DMA
      (`lab` `docs/kb/rp2040_performance_notes.md`); port `lockin.py` to viper with 16-bit input (`in_shift` 8) and compare it with the Python reference on the same samples.
- [ ] Run `bringup_adc.py` and `bringup_sensors.py` on the board and record where the real chips differ from the fakes (the lists of unverified assumptions are in the KB); verify the LIS2DW12 register values against
      ST's data sheet first (the download was blocked).

## Main board (WP5-WP7), open work: layout now, not after A5
- [ ] WP5 — Layout: RP2040 per the reference layout, ADC per its data sheet, analog/digital partition (the plate driver and LED sinks are the noisiest blocks), decoupling, USB pair, mounting holes and
      connector positions from G2, silkscreen pin names; DRC clean against JLC's rules.
- [ ] WP5 panel rule (Part M, 2026-10-27): Standard PCBA needs at least 70 x 70 mm with edge rails drawn in the design and has a stencil per order; the sensor and optical heads go on the main board's panel (panel by
      customer, V-cut or mouse bites, rails), not as separate small boards; recompute the electronics parcel mass by JLC's rule (`tools/jlc_parcel_mass.py`: panel rectangle x thickness; the PCBA packaging options add weight).
      H5 stands: the main board is probably over 70 x 70 mm anyway, so Standard costs the setup and stencil, not a layout constraint.
- [ ] WP6 — Visual review from `kicad-cli pcb render` images and a written checklist.
- [ ] WP7 precheck — in JLC's placement preview confirm the parts the schematic could not verify from a data sheet: KT-0603R LED polarity (footprint marks conflict), the ADC crystal C21900468's pad numbering (a stand-in symbol is used), USBLC6-2SC6 pin 1 position, the SM02B/SM04B mounting tabs (pins 3-4 and 5-6 are wired to GND), the TS-1187A pad pairs; and the VBPW34S/IR26-21C rotation (anode/cathode sides per the Vishay and Everlight drawings).
- [ ] WP7 — Fabrication outputs in `hardware/instrument/fab/`: Gerbers + drill, BOM and CPL in JLC's format (rotations checked against JLC's placement preview), an order-settings README (Standard PCBA,
      layers, thickness, finish, quantity minimums checked at the time); run `parts.py --live` first.
