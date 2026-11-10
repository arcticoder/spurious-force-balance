# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Place the AliExpress balance order today** (the 2026-10-30 parcel was the last one in transit, so nothing is coming from China). Add to one cart: SR44 or LR44 button cells, 1.55 V, 11.6 x 5.4 mm, a pack of 5-10 (the calipers arrived without one; the head-hole check waits on it); 50 M3 flat 304 washers, 3.2 x 7 mm (the screws in the base nuts need them); 7 clear acrylic sheets, 2 mm, 150 x 250 mm (enclosure panels); 2 JST-SH 2-pin cables with flying leads, 100-150 mm (sensor leads); a calibration weight set, 1 mg-500 mg, accuracy class stated in the listing (torque calibration); and the hand tools the inventory lacks: junior hacksaw, flat needle file, craft knife, steel ruler (the strip and ballast cuts). Send me the listing links and prices before you pay so I can log the order; one order per day, so this is the only order today.
2. **Take the four printed parts off the plate once the bed is cool** and check each: the gap gauge (1 mm thick) and the saw-guide base are the ones to look at for warping or a lifted corner; tell me if any is damaged. Then switch the printer off or leave it on for tomorrow's 1.5 h window and tell me which.
3. **Check the new thin M3 nuts with a disc magnet** and tell me if any is pulled (stainless 304 should not be).

## Ready to build now — parts on hand

1. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Printed so far: `head`, `elec_bracket`, `fixture_saw_guide_plate`, the four `encl_shelf_*` and `vane_holder` (plate 1, 2026-11-08) and `sensor_bracket`, `damper_holder`, `fixture_gap_gauge`, `fixture_saw_guide_base` (2026-11-09, 74 min). Still to print: `gantry` (Wednesday), the four `encl_post_*`, `fixture_strip_guide` and `base`. Where the screws and nuts go on the head and on `elec_bracket`: [img/fasteners.jxl](img/fasteners.jxl). Steps: [assembly.md](assembly.md).
       The prototype check (A5) runs on the fab-assembled main board and sensor heads, not on breadboards; the order decision comes to you once I have the files and a cost picture.

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12. Nothing more to do; the review emails are no longer needed.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09, packaged and waiting for the carrier's pickup, tracking YT2631300701884014.
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09, tracking YT2631200708882856. The Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: parked (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: nothing in transit until task 1 is placed.
