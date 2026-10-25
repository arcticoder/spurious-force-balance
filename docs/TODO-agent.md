# TODO — agent (Claude-facing)

> Finished items are recorded as dated entries in `docs/TODO-completed.md`.
> Items waiting on the user's build or on A5 are in `docs/TODO-BLOCKED.md`.
> Later work is in `docs/TODO-backlog.md`.
> The finished Parts D, F, G, H and the original Part A planning text are archived in `docs/kb/part_a_planning_archive.md`.
> The user's own list is `docs/TODO-arcticoder.md`. List conventions: the `lab` repo's `docs/kb/todo_list_conventions.md`.

Work that needs no hands, eyes or purchasing decision from the user. Keep this file to open items only: when one is finished, move a dated one-paragraph entry to
`TODO-completed.md` and delete it here; put long notes in `docs/kb/`.

---

## Open Items

### WP9 — bring-up and experiment procedures for the user (startable: write them against the existing drivers and `docs/assembly.md`)
- [ ] `docs/bringup.md`: the order of power-up and checks for the electronics when they arrive (USB current, rails, `bringup_sensors.py`, `bringup_adc.py`, the device-side safe-start order), each step with its expected
      [PASS] output and what a [FAIL] means, using the unverified-assumption lists in `kb/instrument_electronics_notes.md`.
- [ ] `docs/procedures.md`: the calibration sequence (electrostatic plates against weights or wire riders), the measurement campaign (durations, repeats, conditions logged: lead current, geometry, ambient field and temperature
      from the logged sensors), and the A5 prototype checks, each as numbered steps with the data to record and the analysis command (`host/analyze.py`).

### WP11 — the paper skeleton (startable)
- [ ] `docs/paper/` LaTeX skeleton: apparatus (from `balance_design_notes.md` and `fabrication.md`), the noise model against measurement (`tools/force_noise_budget.py`), calibration and its uncertainty, systematics (lead
      Lorentz force, heating, convection), the G1 result placeholders, open-source availability; sections filled from existing numbers, results left as marked placeholders.
