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
- [ ] Enclosure rework for cheaper acrylic: waits on the user's choice (`TODO-arcticoder.md`, task 3). If printed wall frames with small windows are chosen: PLA wall halves 124 x 150 (the bed takes 220), clear 100 x 100 x 2 mm windows, update `params.py` `PANEL_STOCK`, the CadQuery parts, `assembly.md`, `fabrication.md`, re-run `smoke_test.py`. No acrylic goes in an order until then.
- [ ] Hacksaw route: the printed junior hacksaw frame (Printables 133487) is dropped for now because the user owns a Dremel with cutoff wheels; waits on their photo or the wheel's thickness (`TODO-arcticoder.md`, task 4). The saw guide's kerf slot is 1.4 mm: a wheel up to about 1.2 mm thick works in it unchanged; a thicker wheel needs `KERF` raised in `fixtures.py`.

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

## Main board WP5 finish (state 2026-11-11 evening; waits on the running In2-plane route)
- [ ] The route with the In2 3V3_D plane (`mainboard.py route 58`, started about 20:40 on 2026-11-11, log `layout/out/route_in2_b.log`; a 35-minute try wrote no SES) decides the rest. When it ends: if an SES was written, `import_ses` already ran `sync`, mounting holes, silk policy and both planes; run `mainboard.py drc`, `geometry`, `dfm`, record the numbers in `kb/main_board_layout_notes.md`. If no SES again: the board file is the fallback-routed state of 2026-11-10 (In1 GND plane only, In2 carries signals; a copy is in the scratchpad only), the In2 plane is dropped for this board size (say so in the notes and relax `inner_plane_missing` in `dfm` to In1 only, with the reason), and the closing steps below run on that state.
- [ ] Closing steps on whichever state results: 3 unrouted connections, 3 clearance errors, the USB-C VBUS via touching the GND pad A1B12 (a real short: re-route or move the via), 3 courtyard overlaps around L4 (C49, R18, C3: nudge those parts and re-route locally), 2 dangling vias and 2 dangling tracks, 7 silk-over-copper, 3 silk-to-edge. The tools are in `mainboard.py` (`sync`, `holes`, `silk`, `fixacute`, `rules`, `drc`, `geometry`, `dfm`).
- [ ] Acute joints: 17 Y-branches with 45 degrees between legs; `fix_acute` rewrites the 4 whose shorter leg is 0.72 mm or more, the other 13 have shorter legs. Waits on the user's choice (`TODO-arcticoder.md`, task 5).
- [ ] Connector rotations: the library does not say which way each JST-SH or header faces; check them in JLC's placement preview with the WP7 precheck below (a user step), then fix in `place()`.
- [ ] `jlc.3dshapes` does not exist, so WP6 renders show no part bodies; decided not to generate them (JLC's placement preview is the body check; WP6 reviews copper, silk and outline).

## Main board (WP5-WP7), open work: layout now, not after A5
- [ ] WP5 rules (user, 2026-11-09): layer count by need (2 simple, 4-6 with dedicated ground and power planes when noise needs them; this board is 4 with planes still to draw: In1 ground, In2 power, signals on F/B); 45-degree or rounded copper only, no acute angles (`mainboard.py geometry`: 0 off-grid segments, 7 acute joints in the first pass); end with `mainboard.py dfm` (DRC + shape gate) and JLC's own DFM/placement preview.
- [ ] WP5 — Layout: RP2040 per the reference layout, ADC per its data sheet, analog/digital partition (the plate driver and LED sinks are the noisiest blocks), decoupling, USB pair, mounting holes and
      connector positions from G2, silkscreen pin names; DRC clean against JLC's rules.
- [ ] WP5 panel rule (Part M, 2026-10-27): Standard PCBA needs at least 70 x 70 mm with edge rails drawn in the design and has a stencil per order; the sensor and optical heads go on the main board's panel (panel by
      customer, V-cut or mouse bites, rails), not as separate small boards; recompute the electronics parcel mass by JLC's rule (`tools/jlc_parcel_mass.py`: panel rectangle x thickness; the PCBA packaging options add weight).
      H5 stands: the main board is probably over 70 x 70 mm anyway, so Standard costs the setup and stencil, not a layout constraint.
- [ ] WP6 — Visual review from `kicad-cli pcb render` images and a written checklist.
- [ ] WP7 precheck — in JLC's placement preview confirm the parts the schematic could not verify from a data sheet: KT-0603R LED polarity (footprint marks conflict), the ADC crystal C21900468's pad numbering (a stand-in symbol is used), USBLC6-2SC6 pin 1 position, the SM02B/SM04B mounting tabs (pins 3-4 and 5-6 are wired to GND), the TS-1187A pad pairs; and the VBPW34S/IR26-21C rotation (anode/cathode sides per the Vishay and Everlight drawings).
- [ ] WP7 — Fabrication outputs in `hardware/instrument/fab/`: Gerbers + drill, BOM and CPL in JLC's format (rotations checked against JLC's placement preview), an order-settings README (Standard PCBA,
      layers, thickness, finish, quantity minimums checked at the time); run `parts.py --live` first.
