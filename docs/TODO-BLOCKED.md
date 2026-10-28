# TODO — agent, blocked

> Open items are in `docs/TODO-agent.md`; finished items in `docs/TODO-completed.md`.

These wait on the user's balance build (see `TODO-arcticoder.md`) or on the A5 result.

## Written procedures that need data or hardware to finish
- [ ] `hardware/instrument/firmware/bringup_analog.py`: scripted `[PASS]`/`[FAIL]` versions of the LED-sink, plate-driver, device-current and motor steps of `docs/bringup.md` section 4 (needs the board; the checks and limits are in that section).
- [ ] The slow-demodulation analysis script for the measurement campaign (`docs/procedures.md` section C, step 6): demodulate the logged deflection at the modulation frequency and report force per ampere or per watt with uncertainties; write it with the first real data.
- [ ] Fill the paper skeleton (`docs/paper/main.tex`): every `\todo{}` is a measurement or a figure; the results sections wait on A5 and the campaign.

## Part J4 — the arm's material decision (waits on the user's quotes)
- [ ] When the user has read the arm quotes (1.2 mm and 1.0 mm FR4, the four-design panel probe from `boards/fab/ORDER.md`) and, if made, the JLCCNC sheet-metal capture (upload `boards/fab/arm_cnc.dxf`): fill the
      numbers into `docs/fabrication.md` ("Material and process"), apply its decision rule (keep FR4 unless an aluminium arm is cheaper by more than the redesign and the eddy-current and insulation points pass), build the
      panel Gerbers if the panel quote wins, and update `ORDER.md`.

## A5 — prototype noise measurement (needs the printed balance, the lock-in and the optical readout)
- [ ] Test the mechanics and the optical readout's displacement sensitivity on the bench: the printed/FR4 balance, the breadboard optical readout and lock-in (`optical_shadow_readout`), the Pico.
      Compare the measured resonance, Q and displacement noise, the optical photocurrent (Rf) and the trim procedure's real numbers with G2/G3; update `params.py`, rerun `tools/force_noise_budget.py`.
      A disagreement over a factor of a few sends the design back to G2/G3, not to the fab.

## WP8 remainder — needs the main board (after WP7) to test
- [ ] Device-side `hardware/instrument/firmware/main.py`: acquisition loop on DRDY, lock-in per period (`lockin.py`), sensor polling at 1 Hz, `protocol.py` packets over USB CDC (a 32-frame ADC packet every 4 ms), the safe
      start order (DAC 0 V, gates off, boost off, then enable) and a watchdog that turns the LED gates, device current and boost off if the host stops talking.
- [ ] LED modulation by PIO (a square wave on `LED1_MOD`/`LED2_MOD`, 1 kHz = 4 ADC samples on, 4 off at 8 kSPS, locked to the ADC frame count) and the DRDY-driven ADC read by PIO + DMA
      (`lab` `docs/kb/rp2040_performance_notes.md`); port `lockin.py` to viper with 16-bit input (`in_shift` 8) and compare it with the Python reference on the same samples.
- [ ] Run `bringup_adc.py` and `bringup_sensors.py` on the board and record where the real chips differ from the fakes (the lists of unverified assumptions are in the KB); verify the LIS2DW12 register values against
      ST's data sheet first (the download was blocked).

## After A5, if the verdict stays GO
- [ ] WP5 — Layout: RP2040 per the reference layout, ADC per its data sheet, analog/digital partition (the plate driver and LED sinks are the noisiest blocks), decoupling, USB pair, mounting holes and
      connector positions from G2, silkscreen pin names; DRC clean against JLC's rules.
- [ ] WP5 panel rule (Part M, 2026-10-27): Standard PCBA needs at least 70 x 70 mm with edge rails drawn in the design and has a stencil per order; the sensor and optical heads go on the main board's panel (panel by
      customer, V-cut or mouse bites, rails), not as separate small boards; recompute the electronics parcel mass by JLC's rule (`tools/jlc_parcel_mass.py`: panel rectangle x thickness; the PCBA packaging options add weight).
      H5 stands: the main board is probably over 70 x 70 mm anyway, so Standard costs the setup and stencil, not a layout constraint.
- [ ] WP6 — Visual review from `kicad-cli pcb render` images and a written checklist.
- [ ] WP7 precheck — in JLC's placement preview confirm the parts the schematic could not verify from a data sheet: KT-0603R LED polarity (footprint marks conflict), the ADC crystal C21900468's pad numbering (a stand-in symbol is used), USBLC6-2SC6 pin 1 position, the SM02B/SM04B mounting tabs (pins 3-4 and 5-6 are wired to GND), the TS-1187A pad pairs; and the VBPW34S/IR26-21C rotation (anode/cathode sides per the Vishay and Everlight drawings).
- [ ] WP7 — Fabrication outputs in `hardware/instrument/fab/`: Gerbers + drill, BOM and CPL in JLC's format (rotations checked against JLC's placement preview), an order-settings README (Standard PCBA,
      layers, thickness, finish, quantity minimums checked at the time); run `parts.py --live` first.
