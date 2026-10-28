# Experiment procedures

Three procedures in the order they are done: A5, the prototype check before anything is ordered for layout; the calibration; and the measurement campaign that supports the claim in `docs/plan.md` (G1). Each step names the data
to record and the command that analyzes it. Run `docs/bringup.md` first on any electronics. Keep a test log (one text file per day: date, what was done, every number, every surprise); the analysis scripts read the CSV
files the logger writes (`host/logger.py --out runNNN`), and each run is named by a running number plus what it was (`run012_decay`).

Numbers from the model that the measurements are compared with (`tools/force_noise_budget.py`, `hardware/balance/params.py`): strip stiffness 4.5e-4 N m/rad; moving inertia 2.47e-4 kg m^2; undamped resonance 0.215 Hz
(4.66 s); damping ratio 0.40 with one 0.3 mm copper pad (damped period about 5.1 s) and 0.86 with two; predicted force noise 0.11 nN per 1000 s lock-in measurement (1 sigma), dominated by air currents (4.8 nN/rtHz at 0.05 Hz).

## A. The A5 prototype check (the balance, the lab breadboard optical readout and lock-in, the Pico)

Goal: find out whether the model's resonance, damping, optical sensitivity and noise are right before electronics are laid out. A disagreement beyond a factor of a few goes back to the model (G2/G3), not to the fab.
Setup: the balance built and trimmed (`docs/assembly.md` section 7), the enclosure on, lid on, the breadboard `optical_shadow_readout` and `lockin_amplifier` from the `lab` repo powered, the Pico logging the lock-in output (or the ADS131A04
when it exists). Nothing touches the table; leave the room.

1. **Zero and levelness.** Note the flag's position in its window (the optical readout's DC level, volts) with the arm trimmed and at rest: this is the baseline. Record the temperature.
2. **Photocurrent.** With the LED at 20 mA (the breadboard's LED current, written down) and the flag centred, record the photodiode current (from the TIA output and Rf). The design assumed 100 uA at mid-flag with Rf = 10 kohm (10 kV/A):
   write down the real current and the real Rf. If the current is under 30 uA or over 200 uA, Rf changes (and with it the TIA headroom on the ADC, `docs/kb/instrument_electronics_notes.md`).
3. **Optical sensitivity.** Move the flag by a known distance with the torsion head (a tenth of a turn is 0.1 degree at the flag, which is 0.17 mm at 100 mm) and read the change: volts per millimetre. Do it three times each way. This is the displacement scale.
4. **Resonance and damping.** Displace the arm by about 1 degree with the torsion head, release, record 300 s of the readout at 20 samples/s or more. Fit a damped sine (`host/analyze.py` gives the spectrum; a fit of
   f and the decay rate comes from the peaks): record f, the decay time and ζ. Compare: f 0.215 Hz undamped, ζ 0.40 with one pad; repeat with two pads (ζ 0.86). If f is off by more than 20%, the strip's thickness or the moving inertia is wrong:
   measure the strip with a micrometer and weigh the arm.
5. **Noise.** Arm at rest, enclosure closed, 3600 s of data, then compute the amplitude spectral density (`python hardware/instrument/host/analyze.py run_adc.csv --channel 1`) and the Allan deviation. Convert displacement noise to force noise
   with the stiffness and arm length: F = kappa x displacement / L^2 (kappa 4.5e-4 N m/rad, L 0.1 m: 45 nN per micrometre at the flag). Record the noise floor at 0.05 Hz and at 1 Hz, the 1 s to 1000 s Allan deviation, the slow drift per hour, and the temperature record next to it.
   Compare with 0.11 nN per 1000 s (4.8 nN/rtHz at 0.05 Hz). Note any lines (mains 50/60 Hz, building vibration, the arm's bending mode near 36 Hz) and whether they move when the room's air handling changes.
6. **Air-current test.** Repeat step 5 with the lid lifted 10 mm, then with a quiet fan across the room for 600 s: the change in the low-frequency noise tells whether air currents (the model's dominant term) behave as assumed.
7. **Decision.** Write the measured numbers beside the model's in `docs/kb/instrument_electronics_notes.md` (A5 results), update `params.py` and rerun `tools/force_noise_budget.py`. If the verdict stays GO, layout (WP5) proceeds.

## B. Calibration: force per volt on the plates, and the displacement scale

The electrostatic force F = c V^2 (c about 7.1e-10 N/V^2 from the geometry, known to a few percent) is transferred to an absolute scale by weights.
1. **Weights.** With the arm trimmed and the plate leads in place, hang a calibrated weight (1 mg to 50 mg, 10 uN to 490 uN) on a wire rider or a loop of thin wire at a measured radius (the distance from the strip's axis; measure it with the
   flag's graduations or a ruler to 0.2 mm). Record the deflection. Remove, repeat three times each weight; use at least five weights. Fit deflection against force: the compliance (rad per N m), with the uncertainty from the fit and from the weights'
   tolerance (the weight class stated in the listing) and the radius.
2. **Plates.** Drive the plate at 5 V steps from 0 to 18.8 V (DAC up to 3.3 V) and record the deflection at each (settle 60 s each, three times, both polarities: V^2 does not care about sign; a difference means a charge or an offset). Fit deflection = a V^2 + b. The ratio gives c in N/V^2 with its
   uncertainty. Check the quadratic shape (the residuals of a V^2 fit should be under 2%).
3. **Repeat** the calibration at the start and the end of every campaign day and whenever the temperature has moved by more than 2 C; the strip's stiffness changes with temperature. Log the temperature.
4. **Lock-in scale.** Drive the plates with a slow square wave (0.02 Hz, 5 V, then 10 V) and confirm the demodulated amplitude follows V^2; this checks the measurement chain that the campaign uses.

## C. The measurement campaign (G1)

The quantity: the force on the balance caused by (i) a current I through the supply leads, in the ambient field B (F = B I L), and (ii) the power dissipated by the device (thermal and convective forces), as functions of current, lead geometry
and power. The method: modulate the cause on and off slowly and read the force at the modulation frequency with a lock-in (this rejects drift and the 1/f noise).
1. **Conditions logged for every run:** date, time, operator absent, enclosure state, temperature (three TMP117 and the room), field vector (MMC5983MA), floor acceleration (LIS2DW12), lead geometry, current, polarity, device power, the plate DAC state (off), the
   calibration constant in use.
2. **Order of runs:** a baseline run (no current, 1000 s) before and after every group of conditions; conditions randomized within a day; at least five repeats of every condition on different days; one day with the lid lifted to measure the air term.
3. **Lead-current runs:** with the device card as a 10 ohm resistor on the arm (or leads only), switch `DUT_EN` on and off in a square wave at 0.025 Hz (20 s on, 20 s off) for 1000 s at 100, 200 and 300 mA, positive and negative lead orientation (swap the leads), and the three
   lead geometries (straight pair, twisted pair, coaxial return). Expected force from B I L: about 0.6 uN at 300 mA if the horizontal field is 20 uT over a 0.1 m lead: far above the 0.11 nN noise, so use the lower currents to reach the sub-nN region and look at how the signal scales with I and with the field angle.
4. **Heating runs:** current held constant (no modulation) with the dissipated power set by the card resistor, 0.1 to 0.5 W (the card is capped at 0.5 W), then off: the force steps at the thermal time constant. Record 3000 s on, 3000 s off. These runs separate heating (slow, follows temperature) from Lorentz forces (fast, follows current).
5. **Controls:** every condition with the leads unplugged from the device but the same current path on the board; the plate calibration check at the end of the day; a no-current, no-heat hour to measure the day's drift.
6. **Analysis:** convert deflection to force with the day's calibration; demodulate at the modulation frequency (`host/analyze.py` for spectra; the lock-in is in `firmware/lockin.py` for the optical carrier, and the slow demodulation is a script of its own to be written with the first data); report each coupling as a force per ampere
   (or per watt) with its uncertainty from the repeats, the calibration, the lever arm and the field reading. The claim in G1 is "forces resolved to 0.4 nN (5 sigma on a 20 nN term) in 1000 s": show the measured noise floor that supports it.
7. **Failure modes to record, not hide:** a signal that changes with the time of day, or with the enclosure lid, or that does not reverse with the current's polarity, is probably not a Lorentz force; say what it is likely to be and how it was checked.
