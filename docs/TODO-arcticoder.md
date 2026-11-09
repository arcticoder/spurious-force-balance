# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Tell me when the calipers arrive (due 2026-11-15).** Then I will give you the head-hole measurement steps (the CAD has 3.4 mm holes; the earlier reading was about 4.5 x 5.0 mm with printed calipers). Nothing waits on it.

## Ready to build now — parts on hand

1. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Printed so far: `head`, `elec_bracket`, `fixture_saw_guide_plate`, the four `encl_shelf_*` and `vane_holder` (plate 1, 2026-11-08, all whole). Still to print: `gantry` (Wednesday), the four `encl_post_*`, `sensor_bracket`, `damper_holder`, the other fixtures, and `base`. Where the screws and nuts go on the head and on `elec_bracket`: [img/fasteners.jxl](img/fasteners.jxl). Steps: [assembly.md](assembly.md).
       The prototype check (A5) runs on the fab-assembled main board and sensor heads, not on breadboards; the order decision comes to you once I have the files and a cost picture.

## En route

JLCPCB: `elec_board` (5 boards, placed 2026-11-05, $3.60 USD) is In Production after approval; the arm order (5 FR4 boards, 1.2 mm, JLCONE $8 PCB coupon) still shows Paid; you emailed JLC again on 2026-11-08 (the @duck.com address may be dropping their mail), waiting on JLC's review of the production-file email that went to the spam folder and was resent 2026-11-06. Answer any "Confirm Production File" or parts-placement email within 48 h and check the spam folder for JLC mail. When a parcel ships, add it to the plan in `docs/fabrication.md`.

AliExpress, placed 2026-10-30: 20 M3 thin (DIN439) 304 stainless hex nuts (10 are used; thinner than a standard nut, so they sit loosely in the captured pockets) and digital calipers, estimated delivery 2026-11-15. Check the nuts are non-magnetic on arrival.
