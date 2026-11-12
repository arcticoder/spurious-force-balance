# TODO — agent, blocked

> Open items are in `docs/TODO-agent.md`; finished items in `docs/TODO-completed.md`.

These wait on the user's balance build (see `TODO-arcticoder.md`) or on the assembled board. The main board is no longer waiting on A5 (user's direction of 2026-11-08: fab-assembled electronics, no breadboards); the WP5-WP7 items below are open work, listed in `TODO-agent.md`.

## Printer and bench (the K1 is off unless the user has it on; startable at the next power-on, 2026-11-12 7:45 pm session)
- [ ] K1 total print hours over SSH: read-only `find /usr/data /userdata -name '*.json' -o -name '*.cfg'`, `grep -il time`, `/usr/data/creality/`; if the figure is there, record the path and parsing in the wsl K1 note and drop the touchscreen task; if not, say so once. Needs the printer on.
- [ ] K1 Wi-Fi dropouts: collect Moonraker `machine/system_info`, signal level, `klippy.log`/`moonraker.log` near the 2026-11-11 times (7:19-7:50 cluster, 8:52 drop; log in `kb/printing_state.md`). Needs the printer on. A touchscreen signal reading is a user task only if the log points to signal strength.
- [ ] `START_PRINT` check: read the macro from the printer's config over Moonraker and confirm it never leaves the nozzle over the plate while heating (the fixed load sequence is already in the wsl K1 note and the runbook step 10). Needs the printer on.

## Shipping research (needs the JLCONE app on the debug port)
- [ ] JLC consolidation research, read-only through the app: combining packages or orders, shipping coupons, the discount line on the Y4/Y5 orders, cost per kg band for 0.3-1 kg parcels; write exact page and date in `lab/docs/kb/jlc_account_and_quotes.md`. No cart saves. Blocked: the app was not running with `--remote-debugging-port=9222` on 2026-11-11 (port closed). Start when the user launches it that way; a combine step that needs clicks becomes a user task then.

## Design work waiting on the user
- [ ] Printed enclosure: waits on the user's decision (`TODO-arcticoder.md`, task 3). If printed: add a 2 mm rim (6 mm wide) on the slot edges of 1.2 mm plates in `enclosure_printed.py`, slice each plate per window, move the parts into `balance.py` in place of the acrylic panels, update `params.py` (`PANEL_STOCK`), `assembly.md`, `fabrication.md`, `print_requirements.md`, re-run `smoke_test.py`; the window sheet (100 x 150 x 2 mm) joins the next AliExpress order if wanted.
- [ ] Dremel chop stand for the brass-rod cut (replaces the hacksaw frame; the user owns a Dremel 3000 with a reinforced 31 x 1.0 mm cut-off wheel): waits on the nose-thread measurement (`TODO-arcticoder.md`, task 4; sources say 3/4 in x 12 TPI on related models, unconfirmed for the 3000). Design: a printed threaded nose ring (print a short test ring first), an arm hinged on an M3 screw so the wheel plunges straight down in the kerf plane, a half guard over the top of the wheel, and a rod clamp derived from the saw guide with the plate cut away around the kerf (reach below the mandrel head is about 12 mm, so the 10 mm rod needs an open kerf, or a cut from two sides with the rod turned 180 degrees). The 1.0 mm wheel fits the existing 1.4 mm kerf slot. Safety in `procedures`/`assembly`: glasses, mask, outdoors, brass dust may contain lead.

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

