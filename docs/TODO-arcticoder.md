# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Review and place the `elec_board` order** (first of three, one order at a time): the JLCONE app's quote page is set up and not saved or submitted: `elec_board_gerbers.zip`, 24 x 34 mm, Single PCB, 1 design, 5 pieces, FR-4, 1.2 mm, green, HASL (with lead), Confirm Production file No, Remove Mark, calculated **C$2.92** (Special Offer C$2.79 + deburring C$0.14). Check the thickness still reads 1.2 mm, save to cart, pick the cheap postal tier at payment (the default UPS line is C$37.41), and tell me the order total. No coupon applies.
2. **Place the `clamp_ground` order** (a later day; the page resets after each upload, so say so and I set it up in the app): `clamp_ground_gerbers.zip`, 19 x 17 mm, same settings, calculated **C$2.92**.
3. **Place the `clamp_plate` order** (a later day): `clamp_plate_gerbers.zip`, 16 x 14 mm, same settings, calculated **C$3.06** (deburring C$0.28); it carries two plates per balance and five boards arrive.
4. **Decide on the early sensor-head order** (the three small sensor-head boards, about 13 parts; not the 169-part main board, which is not ordered; optional; its New User SMT coupon, C$13.99, ends 2026-11-25): upload `hardware/instrument/heads_panel/out/heads_panel_gerbers.zip` with `bom.csv` and `cpl.csv`
   using [heads_panel/ORDER.md](../hardware/instrument/heads_panel/ORDER.md), read the Standard-assembly total and tell me whether to go on; answer "Confirm Production File" and "Confirm Parts Placement" emails within 48 h.
   It also needs one 4-pin JST-SH cable (both ends, 100-150 mm) in the AliExpress cart. Skip it if the quote is more than you want to spend before the balance is built.
5. **JLCMC fasteners:** (the app's Mechatronic Parts link did not open inside it, so I could not check) check whether M3 stainless (304/A2) flat washers are listed, at what price and shipping, since two coupons (C$13.99 each) apply to that service (the nuts are bought: see En route).

6. **After the `elec_board` order, make the JLCONE app larger** (the 13% scale did not apply: your shell still resolved `jlcone` to `/usr/bin/jlcone`): run `hash -r` or open a new terminal, check `type jlcone` shows `~/.local/bin/jlcone`, then relaunch with `jlcone --remote-debugging-port=9222`; do not relaunch before the order is placed, because the quote page's upload is lost on a restart.

## Next order — AliExpress: what is left for the balance

Hold these until the JLC boards are on their way, then one checkout, with whatever the lab list needs. None of them has a shipping fee in the cart; hold the cart if one shows.

- **Clear acrylic, 2 mm, 150 × 250 mm, 7 sheets**: four walls, two lid pieces and a spare, used uncut.
- **M3 flat washers, 304 stainless, 3.2 mm inner and 7 mm outer diameter, 50 pieces** (20 are used).
- **JST-SH 1.0 mm 2-pin cable, flying leads on one end, 100 to 150 mm, 2 pieces**: carries the plate voltage from the fab board to the balance (the leads thread through the board's holes; no soldering).
- **Calibration weights, 1 mg to 500 mg** (an analytical-balance weight set): turns plate voltage into an absolute force. Pick a class stated in the listing.
- **If not already owned** (none are in the inventory): a junior hacksaw, a flat needle file, a craft knife and a steel ruler, for the brass ballast and the 4 mm stainless strip.

## Ready to build now — parts on hand

1. [ ] **Print the balance's frame** (`hardware/balance/cad/*.stl`, PLA, 3 walls, about 30% infill, 0.2 mm layers): `base`, `gantry` (lay it on its side), `head`, `sensor_bracket`, `elec_bracket`,
       `vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the four jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
       `damper_holder` is the flat-disc version (the twist test of 2026-10-26 found the discs magnetized through the flat faces). The arm, clamp plates and electrode board come as fab boards, not prints.
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).
       Steps: [assembly.md](assembly.md).

## En route

The JLCPCB arm order (5 FR4 boards, 1.2 mm) placed 2026-11-04 with the JLCONE $8 PCB coupon, in JLC's review; answer any "Confirm Production File" or parts-placement email within 48 h. When it ships, add the parcel to the plan in `docs/fabrication.md`.

The AliExpress order placed 2026-10-24: the 0.05 mm 304 stainless sheet, the 3 mm × 10 m foam tape (0.3 mm thick), the 20 × 20 × 0.3 mm copper pads (5), the 10 mm × 1 m copper foil tape and the
10 × 100 mm brass rod. Check the pads are non-magnetic on arrival (a disc magnet should not pull them).

The AliExpress order placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers. Check the nuts are non-magnetic on arrival.
