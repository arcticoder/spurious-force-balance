# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing,
assembling, bench checks. File-creation work is not here; it is in [TODO-agent.md](TODO-agent.md). The
parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md`
and `docs/orders.md`), and the AliExpress cart is one checkout across both repos. Done items move to
[TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Pick a license** (one line back): CERN-OHL-P for the hardware plus MIT for the code, or none (as in
   `lab`). Until you pick, the repo has no license file.
2. **Optional one-minute check, for the damper design:** turn one of the N42 discs about its own axis,
   flat on a table next to a phone's compass app. A needle that swings all the way round means the disc is
   magnetized across its diameter (what the listing says and the design assumes); no swing means through
   its flat faces, and `MAGNET_MAGNETIZATION` in `params.py` switches to the other layout.

## Next order — AliExpress: materials for the balance

Already in the cart: the 0.05 mm 304 stainless sheet, the 3 mm × 10 m foam tape, the 20 × 20 × 0.3 mm copper
pads (5), the 10 mm × 1 m copper foil tape, the 10 × 100 mm brass rod. All five can be checked out with the
lines below; none is waiting on a design change. The 1.0 mm copper pad is not needed (a second 0.3 mm pad
doubles the damping). Check the total, and hold the cart if any line shows a shipping fee. The screws and
carbon-steel nuts on hand cover the printed balance.

- **Clear acrylic, 2 mm, 150 × 250 mm, 7 sheets**: four walls, two lid pieces and a spare. Used uncut.
- **M3 flat washers, 304 stainless, 3.2 mm inner and 7 mm outer diameter, 50 pieces**.
- **M3 hex nuts, 304 stainless, 20 pieces**: the lower strip clamp rides on the moving arm, so its nuts
  have to be non-magnetic.
- **JST-SH 1.0 mm 2-pin cable, flying leads on one end, 100 to 150 mm, 2 pieces**: carries the plate voltage
  from the fab board's plate connector to the balance (the leads clamp under washers; no soldering).
- **Calibration weights, 1 mg to 500 mg** (an analytical-balance weight set): turns plate voltage into an
  absolute force. Pick a class stated in the listing.
- **If not already owned** (none are in the inventory): a junior hacksaw, a flat needle file, a craft knife
  and a steel ruler, for the brass ballast and the 4 mm stainless strip.

## Ready to build now

1. [ ] **Slice the balance's moving printed parts, then print** (full steps in [assembly.md](assembly.md) § 1). First slice
       `arm`, `low_clamp_a/b`, `vane_holder`, `flag` and `elec_arm` without printing, and send the slicer's mass in grams for
       each (or tell me and I will update `PRINTED_MASS_G`), so the arm's ballast hole and the ballast length come out right.
       Then print, PLA, 3 walls, about 30% infill, 0.2 mm layers: `arm`, `base`, `gantry`, `top_clamp_a/b`, `low_clamp_a/b`,
       `vane_holder`, `elec_arm`, `elec_fixed`, `damper_holder`, `sensor_bracket`, `flag`, the four `encl_post_*`, the four
       `encl_shelf_*`, and the jigs `fixture_saw_guide_base/plate` and `fixture_strip_guide` (`hardware/balance/cad/*.stl`; the
       `panel_*`, `encl_lid_*`, `magnet_*`, `vane`, `strip`, `ballast` and `dut_dummy` files are not printed). Largest part
       200 × 32 × 28 mm. The strip, vane, ballast, acrylic and washers wait on the materials order; the printed parts alone let you check
       fit and the sensor bracket's gap. The prototype check (A5) needs the lock-in and the optical readout from `lab`
       (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`) built first.
