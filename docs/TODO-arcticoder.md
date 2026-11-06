# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Place the `clamp_ground` order on a day after the `elec_board` order** (one JLC order per day): say so in the next chat and I set up the page in the app (the page resets after each upload and a stale session stalls the save to cart): `clamp_ground_gerbers.zip`, 19 x 17 mm, Single PCB, 5 pieces, 1.2 mm, HASL with lead, Confirm Production file No, Remove Mark, calculated **C$2.92**. Check the thickness reads 1.2 mm, save to cart, pick the cheap postal tier, and tell me the total. No coupon applies.
2. **Place the `clamp_plate` order** (the day after `clamp_ground`): `clamp_plate_gerbers.zip`, 16 x 14 mm, same settings, calculated **C$3.06** (deburring C$0.28); two plates per balance, five boards arrive.
3. **Decide on the early sensor-head order** (the three small sensor-head boards, about 13 parts; not the 169-part main board, which is not ordered; optional; its New User SMT coupon, C$13.99, ends 2026-11-25): upload `hardware/instrument/heads_panel/out/heads_panel_gerbers.zip` with `bom.csv` and `cpl.csv`
   using [heads_panel/ORDER.md](../hardware/instrument/heads_panel/ORDER.md), read the Standard-assembly total and tell me whether to go on; answer "Confirm Production File" and "Confirm Parts Placement" emails within 48 h.
   It also needs one 4-pin JST-SH cable (both ends, 100-150 mm) in the AliExpress cart. Skip it if the quote is more than you want to spend before the balance is built.
4. **Check the arrived balance materials** (stainless sheet, copper pads, brass rod, foam tape, copper foil tape; bags in `lab/docs/inventory.md`): hold a disc magnet to the sheet, the pads and the rod (none should be pulled; the pads' listing says "Carbide"), measure the rod's length with the calipers (listed 100 mm) and its diameter (10 mm), put the items in a new labelled bag `BALANCE MATERIALS` (the sheet flat in a card envelope), and tell me the results; the nuts and screws from earlier orders still have no recorded bag.

## Next order — AliExpress: what is left for the balance

The JLC boards are on their way, so this checkout is open: one order with whatever the lab list needs (the washers come from here, not JLCMC). None of them has a shipping fee in the cart; hold the cart if one shows.

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

The JLCPCB `elec_board` order (5 boards, placed 2026-11-05, $3.60 USD) and the arm order (5 FR4 boards, 1.2 mm, placed with the JLCONE $8 PCB coupon, in JLC's review); answer any "Confirm Production File" or parts-placement email within 48 h. When it ships, add the parcel to the plan in `docs/fabrication.md`.

The AliExpress order placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers. Check the nuts are non-magnetic on arrival.
