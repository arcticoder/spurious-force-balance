# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Printer set-up on the balcony, tonight when you have time (no fixed time).** Power the K1 on, then tell me when it is ready and the print window in hours. I'll name the spindle to load (red, grey, or a sealed white or black). Check that the nozzle-side filament sensor reads "no filament" with nothing loaded before a real print.
2. **Adjust the riser vents** when I ask during a print.

## Ready to build now — parts on hand

1. [ ] **Print the balance's frame** (`hardware/balance/cad/*.stl`; settings are in `hardware/balance/cad/balance.3mf`, which you have set at 3 walls and 30% infill; the values and reasons are in [print_requirements.md](print_requirements.md) section 6). Reslice in Orca first, check the nut and hole fits on the first parts, and give me the `vane_holder` mass. Filament: the Hyper PLA spools in `lab/docs/inventory.md`; you choose the colour. `base`, `gantry`, `head`, `sensor_bracket`, `elec_bracket`,
       `vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the four jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
       `damper_holder` is the flat-disc version (the twist test of 2026-10-26 found the discs magnetized through the flat faces). The arm, clamp plates and electrode board come as fab boards, not prints.
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).
       Steps: [assembly.md](assembly.md).

## En route

JLCPCB: `elec_board` (5 boards, placed 2026-11-05, $3.60 USD) is In Production after approval; the arm order (5 FR4 boards, 1.2 mm, JLCONE $8 PCB coupon) still shows Paid, waiting on JLC's review of the production-file email that went to the spam folder and was resent 2026-11-06. Answer any "Confirm Production File" or parts-placement email within 48 h and check the spam folder for JLC mail. When a parcel ships, add it to the plan in `docs/fabrication.md`.

AliExpress, placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers, estimated delivery 2026-11-15. Check the nuts are non-magnetic on arrival.
