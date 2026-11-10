# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Place the AliExpress balance order** (cart reviewed 2026-11-10; nothing is in transit from China until it is placed). Keep in the cart: the LR44 5-pack (C$2.85), the 2-pin JST-SH 10 cm cable 5-pack (C$1.04), the 6-inch 24T mini hacksaw blades (C$1.92), M3 x 7 x 0.5 mm flat washers (3.2 mm is the hole, not the thickness), a 1 g calibration weight (C$2.47) and the 0.1 g digital scale (C$3.97). Take the acrylic sheets out of this order (the enclosure design is being reworked around small clear windows; see `TODO-agent.md`). The needle file, craft knife and steel ruler are not in the cart yet; they go in the next order. Send me the washer listing line and the cart total before you pay so I can log the order.
2. **Take the four printed parts off the plate once the bed is cool** and check each: the gap gauge (1 mm thick) and the saw-guide base are the ones to look at for warping or a lifted corner; tell me if any is damaged. Then switch the printer off or leave it on for today's 1.5 h window (Tuesday) and tell me which.
3. **Check the new thin M3 nuts with a disc magnet** and tell me if any is pulled (stainless 304 should not be).
4. **Read the printer's total print hours on its touchscreen** the next time it is on, and tell me the figure (the touchscreen counter is the true one; Moonraker only counts jobs since it was installed).

## Ready to build now — parts on hand

1. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Printed so far: `head`, `elec_bracket`, `fixture_saw_guide_plate`, the four `encl_shelf_*` and `vane_holder` (plate 1, 2026-11-08) and `sensor_bracket`, `damper_holder`, `fixture_gap_gauge`, `fixture_saw_guide_base` (2026-11-09, 74 min). Still to print: `gantry` (Wednesday), the four `encl_post_*`, `fixture_strip_guide` and `base`. Where the screws and nuts go on the head and on `elec_bracket`: [img/fasteners.jxl](img/fasteners.jxl). Steps: [assembly.md](assembly.md).
       The prototype check (A5) runs on the fab-assembled main board and sensor heads, not on breadboards; the order decision comes to you once I have the files and a cost picture.

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12. Nothing more to do; the review emails are no longer needed.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09, packaged and waiting for the carrier's pickup (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app). The Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: nothing in transit until task 1 is placed.
