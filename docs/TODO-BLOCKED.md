# TODO — agent, blocked

> Open items are in `docs/TODO-agent.md`; finished items in `docs/TODO-completed.md`.

These wait on the user's balance build (see `TODO-arcticoder.md`) or on the assembled board. The main board is no longer waiting on A5 (user's direction of 2026-11-08: fab-assembled electronics, no breadboards); the WP5-WP7 items below are open work, listed in `TODO-agent.md`.

## Shipping research (needs the JLCONE app on the debug port)
- [ ] JLC consolidation research, read-only through the app: combining packages or orders, shipping coupons, the discount line on the Y4/Y5 orders, cost per kg band for 0.3-1 kg parcels; write exact page and date in `lab/docs/kb/jlc_account_and_quotes.md`. No cart saves. Blocked: the app was not running with `--remote-debugging-port=9222` on 2026-11-11 (port closed). Start when the user launches it that way; a combine step that needs clicks becomes a user task then.
- [ ] Re-read the JLC order states (arm, elec_board, clamp_ground; last read 2026-11-10; the arm's factory estimate of 2026-11-12 has passed). Blocked on the app's route: on 2026-11-13 the port was open, but a direct navigation to the orders URL bounced back to the Black Friday events page. Next session with port 9222 open: reach the orders list from the account menu, read the status steps as plain text, write the dated states to `lab/docs/kb/jlc_account_and_quotes.md`, and no tracking numbers in any file.

## Design work waiting on the user
- [ ] Printed enclosure (decided 2026-11-12: printed walls and lid, 1.2 mm plates with a 2 mm rim, no window; model `hardware/balance/enclosure_printed.py`, plan and estimates `kb/balance_design_notes.md`): print after the frame (posts, bars, base); slice each window-sized file the day before its window (runbook step A1), grey walls, red lid, black strips; update `assembly.md` and `fabrication.md` text from acrylic to printed when the first plate is printed (the CAD, params and smoke test already say printed).
- [ ] Slice the printed hacksaw handle (`fixture_hacksaw_handle_body` 130 x 24 x 22 mm and `_cover` 62 x 24 x 6 mm, from `hardware/balance/cad/`, print as modelled, no supports, 3 walls, 30 %, settings in `kb/printing_state.md`) for the Sunday 2026-11-15 16:30-18:30 window. Condition: the session runs on Sonnet (user's rule: no slicing on Haiku) and it is before that window; check the print time fits 2 h with start-up.
- [ ] Re-slice the base for the Saturday 2026-11-21 07:30-12:30 window: condition is the date 2026-11-20. The existing `balance_p2_base.gcode` (4 h 41 min, 177 g) predates the flow cap; check its START_PRINT bed temperature (60, not 55) and speeds, or re-slice with the settings in `kb/printing_state.md` (2026-11-13 entry).

## `clamp_plate` JLC order: cancelled by the user on 2026-11-08 because its shipping would not come down; combining parcels to cut per-item shipping is being explored
- [ ] Revisit when a new coupon covers the order's shipping, or when the Global Standard Direct Line for a 0.14 kg parcel falls back toward US$1.50 (C$2.13) on a fresh quote. Then re-add the Gerber set (`clamp_plate_gerbers.zip`, 16 x 14 mm, 1.2 mm, HASL with lead, Single PCB, 5 pieces) to the cart and read the total; the user approves and pays. Shipping was C$8.14 (Y6, 2026-11-08); the order pages (2026-11-09) show that is the list rate (US$5.77 for 0.14 kg) and that the cheap earlier shipping on Y4/Y5 was a discount line of -US$4.27 on the order, so look for a discount covering shipping in the cart; the Y6 and Y7 orders were cancelled by the user because the shipping price would not go down. Combining several packages to cut shipping for this item and others is being explored (research item in `TODO-agent.md`); this is not a permanent shelving. It cannot join the clamp_ground order (Y5 was placed 2026-11-06 and is in production); the user's wish to cut per-item shipping means it should go into the next JLC order, even if that parcel passes 0.3 kg. The user accepts the four spare boards as waste and will not pay a shipping premium for them.

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

## Main board: layout done 2026-11-12, waits on the user's JLC steps
- [ ] WP6/WP7 precheck in JLC's placement preview (user, when the main-board order is started): connector directions, LED polarity, crystal pin 1, ESD and SOT-23 rotations; fix any in `place()` or `fab()` and regenerate (`mainboard.py fab`). Files: `hardware/instrument/fab/` (`ORDER.md`). The order itself follows the one-order-per-day rule; the quote page is set up only when the user says the previous order is placed.
- [ ] Board size against JLC's price tier (120 x 90 mm; the right-middle area is empty, so a 105 x 80 mm board is possible if the quote warrants a re-run of placement): the user's decision after the quote.

