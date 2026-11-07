# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Place the `clamp_ground` order**: the page is set up in the JLCONE app (uploaded `clamp_ground_gerbers.zip`, 17 x 19 mm, Single PCB, 5 pieces, 1.2 mm, HASL with lead, Confirm Production File No, Remove Mark, calculated **C$2.96** with the edge-rounding line). Do not reload or navigate the tab. Save to cart, pick the cheap postal tier, and tell me the total.
2. **Check the arrived balance materials** (stainless sheet roll, copper pads, brass rod, foam tape, copper foil tape; bags in `lab/docs/inventory.md`): hold a disc magnet to the sheet, the pads and the rod (none should be pulled; the pads' listing says "Carbide"), measure the rod's diameter (10 mm) and length (listed 100 mm) with the printed calipers (the digital ones are en route), put everything in the labelled bag `BALANCE MATERIALS` (the roll goes in loosely, no flattening or folding), and tell me the results; the nuts and screws from earlier orders still have no recorded bag.

## Ready to build now — parts on hand

1. [ ] **Print the balance's frame** (`hardware/balance/cad/*.stl`, PLA, 3 walls, about 30% infill, 0.2 mm layers): `base`, `gantry` (lay it on its side), `head`, `sensor_bracket`, `elec_bracket`,
       `vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the four jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
       `damper_holder` is the flat-disc version (the twist test of 2026-10-26 found the discs magnetized through the flat faces). The arm, clamp plates and electrode board come as fab boards, not prints.
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).
       Steps: [assembly.md](assembly.md).

## En route

JLCPCB: `elec_board` (5 boards, placed 2026-11-05, $3.60 USD) is In Production after approval; the arm order (5 FR4 boards, 1.2 mm, JLCONE $8 PCB coupon) still shows Paid, waiting on JLC's review of the production-file email that went to the spam folder and was resent 2026-11-06. Answer any "Confirm Production File" or parts-placement email within 48 h and check the spam folder for JLC mail. When a parcel ships, add it to the plan in `docs/fabrication.md`.

AliExpress, placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers, estimated delivery 2026-11-15. Check the nuts are non-magnetic on arrival.
