# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Read three JLC quotes and the shipping table** (the mechanical order is the first order, and its New User PCB coupon, C$8.40, ends 2026-11-25; place the order by about 11-20). On the quote page:
   (a) the arm alone, 5 pieces, 208 x 60 mm, 1.2 mm, black, ENIG: price, the mass the page shows, and the shipping options with prices for Canada; (b) the same at 1.0 mm; (c) the four designs as listed in
   [ORDER.md](../hardware/balance/boards/fab/ORDER.md). If the arm alone is over about $60, or a parcel is over 0.29 kg, stop and tell me.
2. **Shipping price table** for the cheap Global Standard Direct Line tier (and the next tier up): the price the quote page shows for estimated masses of about 100 g, 200 g, 290 g and 310 g to your address (change the
   quantity or thickness of any board to move the mass). It tells me where the real cliff is for Canada and whether splitting into parcels pays.
3. **Coupon dates:** in the JLC account, note the expiry date of each coupon whose list entry says only "valid for 30 days" or "60 days" (the dollar-off-$40/$50 3D-printing, material, FDM and nylon ones), and the claim date if shown.
4. **JLCCNC sheet-metal quote page** (I can only see the upload box; the options appear after a file is uploaded): make `lab/docs/jlc/cnc_sheet_metal_quote_ui.md` the way you did the other two. Use any STEP/DXF (I will export the arm for it later:
   Part J3). Also useful: the HDI option on the PCB quote (thicknesses, layer counts, price for 5 pieces of the arm) as `lab/docs/jlc/hdi_quote_ui.md`.
5. **Decide on the early sensor-head order** (optional; its New User SMT coupon, C$13.99, ends 2026-11-25): upload `hardware/instrument/heads_panel/out/heads_panel_gerbers.zip` with `bom.csv` and `cpl.csv`
   using [heads_panel/ORDER.md](../hardware/instrument/heads_panel/ORDER.md), read the Standard-assembly total and tell me whether to go on; answer "Confirm Production File" and "Confirm Parts Placement" emails within 48 h.
   It also needs one 4-pin JST-SH cable (both ends, 100-150 mm) in the AliExpress cart. Skip it if the quote is more than you want to spend before the balance is built.
6. **JLCMC fasteners:** check whether M3 stainless (304/A2) hex nuts and flat washers are listed, at what price and shipping, since two coupons (C$13.99 each) apply to that service.

## Next order — JLC mechanical boards (four designs, one cart)

Upload the four Gerber zips from `hardware/balance/boards/fab/` and use the settings in [ORDER.md](../hardware/balance/boards/fab/ORDER.md): 1.2 mm, black mask, 5 pieces each, ENIG on
three designs, **Combine Shipping on**, a postal (not courier) tier if one is offered for Canada. Unassembled boards: no setup or extended-part fees. Estimated **$70–140 total** with shipping
[estimate; the quote page decides]. The estimated parcel mass is about 195 g with packing, under JLC's 0.3 kg line for the cheap tier [community data: see `docs/kb/fab_ordering_notes.md`].

## Next order — AliExpress: what is left for the balance

Hold these until the JLC boards are on their way, then one checkout, with whatever the lab list needs. None of them has a shipping fee in the cart; hold the cart if one shows.

- **Clear acrylic, 2 mm, 150 × 250 mm, 7 sheets**: four walls, two lid pieces and a spare, used uncut.
- **M3 flat washers, 304 stainless, 3.2 mm inner and 7 mm outer diameter, 50 pieces** (20 are used).
- **M3 hex nuts, 304 stainless, 20 pieces** (10 are used, all on the moving arm and the vane holder).
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

The AliExpress order placed 2026-10-24: the 0.05 mm 304 stainless sheet, the 3 mm × 10 m foam tape (0.3 mm thick), the 20 × 20 × 0.3 mm copper pads (5), the 10 mm × 1 m copper foil tape and the
10 × 100 mm brass rod. Check the pads are non-magnetic on arrival (a disc magnet should not pull them).
