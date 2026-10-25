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

### WP8 — firmware and host software (startable: the pin map is fixed in `pins.py`)
- [ ] Bring-up scripts per block with `[PASS]`/`[FAIL]` lines (ADS131A04 over SPI0 with the charge pump enabled, MCP4728, TMP117/LIS2DW12/MMC5983MA, LED gating, plate and device-current setting);
      fixed-point digital lock-in; ADC by PIO + DMA (`lab` `docs/kb/rp2040_performance_notes.md`); USB streaming to a host-side Python logger (timestamped CSV or HDF5); analysis scripts that
      produce the noise spectra, calibration and coupling coefficients with uncertainties. Start with the bring-up scripts and the register map from the data sheets, tested on the host with a fake SPI.
