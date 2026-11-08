# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Decide on `clamp_plate` (JLC cart Y6, C$3.10 goods, not paid).** The analysis is done. Weight is not the cause: the parcel is 0.14 kg, the same as elec_board and clamp_ground, which shipped on Global Standard Direct Line for about C$2.13 (US$1.50) on 2026-11-05 and 2026-11-06. The same line now reads C$8.14 (about US$5.77). The arm's order page (Y3, 2026-11-03) shows the Global line at US$7.75 for 0.28 kg, so the rise is in JLC's rate, not in the parcel. The likely cause is a rate change or the end of a promotional rate; JLC's pages do not say which, and support can confirm it.
   Status (2026-11-08): the cart line is gone. The Y6 and later Y7 clamp_plate orders both show Order Cancelled on the account's orders page, so nothing is in production. The New User PCB coupon took $3 off at the payment step but reverted to C$11.24 at the summary. The other coupons cannot reduce the Global line: each covers only its own service's goods, and the shipping coupon needs shipping over C$21.15, which the Global line never reaches. The only coupon route left is a carrier whose charge sits between C$21.15 and C$22.24 for this parcel. Tell me whether to re-add clamp_plate to the cart so the carrier prices can be read, or to pay C$8.14, or to wait for JLC support.
2. **Printer set-up on the balcony.** Reconvene at 13:30 (the user's availability). Then power the K1 on, and tell me when it is ready and the print window in hours. I'll name the spindle to load (red, grey, or a sealed white or black). Check that the nozzle-side filament sensor reads "no filament" with nothing loaded before a real print.
3. **Adjust the riser vents** when I ask during a print.

## Ready to build now — parts on hand

1. [ ] **Print the balance's frame** (`hardware/balance/cad/*.stl`; settings are in `hardware/balance/cad/balance.3mf`, which you have set at 3 walls and 30% infill; the values and reasons are in [print_requirements.md](print_requirements.md) section 6). Reslice in Orca first, check the nut and hole fits on the first parts, and give me the `vane_holder` mass. Filament: the Hyper PLA spools in `lab/docs/inventory.md`; you choose the colour. `base`, `gantry`, `head`, `sensor_bracket`, `elec_bracket`,
       `vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the four jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
       `damper_holder` is the flat-disc version (the twist test of 2026-10-26 found the discs magnetized through the flat faces). The arm, clamp plates and electrode board come as fab boards, not prints.
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).
       Steps: [assembly.md](assembly.md).

## En route

JLCPCB: `elec_board` (5 boards, placed 2026-11-05, $3.60 USD) is In Production after approval; the arm order (5 FR4 boards, 1.2 mm, JLCONE $8 PCB coupon) still shows Paid, waiting on JLC's review of the production-file email that went to the spam folder and was resent 2026-11-06. Answer any "Confirm Production File" or parts-placement email within 48 h and check the spam folder for JLC mail. When a parcel ships, add it to the plan in `docs/fabrication.md`.

AliExpress, placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers, estimated delivery 2026-11-15. Check the nuts are non-magnetic on arrival.
