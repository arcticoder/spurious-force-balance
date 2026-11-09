# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Measure the head's two holes with the calipers once they arrive (due 2026-11-15), or tell me again how you measured them.** The CAD has 3.4 mm holes in the head's -y wall (the upper clamp bolts' tips hang in them; no nut) and your ruler reading was about 4.5 x 5.0 mm. If the calipers also read well over 3.5 mm I will check the slice for hole growth; the fit is not critical, so nothing waits on it.
2. **Block Wednesday morning (2026-11-11, 4 h) for the gantry.** Monday's 2.5 h goes to the plate-0 parts that fit, Tuesday's 1.5 h to the first half of the base. I will tell you which file is loaded before each run; you start it by telling me to.

## Ready to build now — parts on hand

1. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Printed so far: `head`, `elec_bracket`, `fixture_saw_guide_plate`, the four `encl_shelf_*` and `vane_holder` (plate 1, 2026-11-08, all whole). Still to print: `gantry` (Wednesday), the four `encl_post_*`, `sensor_bracket`, `damper_holder`, the other fixtures, and `base`. Where the screws and nuts go on the head and on `elec_bracket`: [img/fasteners.jxl](img/fasteners.jxl). Steps: [assembly.md](assembly.md).
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).

## En route

JLCPCB: `elec_board` (5 boards, placed 2026-11-05, $3.60 USD) is In Production after approval; the arm order (5 FR4 boards, 1.2 mm, JLCONE $8 PCB coupon) still shows Paid, waiting on JLC's review of the production-file email that went to the spam folder and was resent 2026-11-06. Answer any "Confirm Production File" or parts-placement email within 48 h and check the spam folder for JLC mail. When a parcel ships, add it to the plan in `docs/fabrication.md`.

AliExpress, placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers, estimated delivery 2026-11-15. Check the nuts are non-magnetic on arrival.
