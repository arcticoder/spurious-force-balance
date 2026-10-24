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
   magnetized across its diameter (what the listing says); no swing means through its flat faces.

## Next order — AliExpress: materials for the balance

Already in the cart: the 0.05 mm 304 stainless sheet, 3 mm × 10 m foam tape, 20 × 20 × 0.3 mm copper pads,
10 mm × 1 m copper foil tape, 10 × 100 mm brass rod. Add the lines below, check the total, and hold the cart
if any line shows a shipping fee. The screws and carbon-steel nuts on hand cover the printed balance.

- **Copper pads, 20 × 20 × 1.0 mm** (the same listing as the 0.3 mm ones): the damper vane may need the
  thicker piece, and damping can be lowered on the bench but not raised.
- **Clear acrylic, 2 mm, 150 × 250 mm, 7 sheets**: four walls and two lid pieces, uncut, and a spare.
- **M3 flat washers, 304 stainless, 3.2 mm inner and 7 mm outer diameter, 50 pieces**.
- **M3 hex nuts, 304 stainless, 20 pieces**: the lower strip clamp rides on the moving arm, so its nuts
  have to be non-magnetic.
- **Calibration weights, 1 mg to 500 mg** (an analytical-balance weight set): turns plate voltage into an
  absolute force. Pick a class stated in the listing.
- **If not already owned** (none are in the inventory): a junior hacksaw, a flat needle file, a craft knife
  and a steel ruler, for the brass ballast and the 4 mm stainless strip.

## Ready to build now

1. [ ] **Print the balance** (`hardware/balance/cad/*.stl`, PLA, 3 walls, about 30% infill): `arm`, `base`,
       `gantry`, `top_clamp_a/b`, `low_clamp_a/b`, `vane_holder`, `elec_arm`, `elec_fixed`, `damper_holder`,
       `sensor_bracket`, `flag`, the four `encl_post_*` posts (0.2 mm layers; `flag` may be better cut from
       card). The part list will change when the Part D enclosure and damper work lands; wait for that
       before printing. The strip, vane, ballast, acrylic and washers come with the materials order.
       The prototype check (A5) needs the lock-in and the optical readout from `lab`
       (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`) built first.
