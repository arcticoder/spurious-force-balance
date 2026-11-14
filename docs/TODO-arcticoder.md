# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Safety glasses for the brass cut (next AliExpress cart).** You own no eye protection, and the hacksaw throws brass chips. Pick one listing: clear polycarbonate (not plain acrylic or fashion lenses) wraparound glasses with side protection. A Z87.1 or EN 166 mark is not required for a hand hacksaw: those ratings are about high-speed impact from power tools, which this cut does not involve. Send me the link and I log it in `lab/docs/orders.md` and add it to the cart. No dust mask is being bought.
2. [ ] **Next print window.** Saturday 2026-11-14 from 07:30 to 10:00 is blocked in your calendar. Tell me the next window (date, start time, length). Post pp's L (about 32 min) is the next file; I slice it the day before the window you name, then the base (4 h 41 min, so a window of about 5 h with start-up), then the enclosure plates (`kb/balance_design_notes.md`). Photo of everything printed so far: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).
3. [ ] **Cut the ballast from the brass rod with the hacksaw (after the glasses arrive).** Saw a 15 mm piece in the printed saw guide (`docs/assembly.md`, Ballast section): the guide leaves 0.5 mm to file off. The cut waits on the glasses and on the hacksaw blades from the 2026-11-10 parcel (in transit; tell me when it lands). Wear the glasses for the whole cut. No mask is needed for a hand hacksaw cut: the chips are coarse. The only fine dust is from filing the sawn face, which is a small exposure; keep filing short, wipe the filings up with a damp cloth rather than blowing them away, and wash your hands after (brass can contain lead). Then file the sawn face to the length `balance.py` prints (15.1 mm with the CAD's numbers) and check it passes through the arm board's 10.2 mm hole.
4. [ ] **Main-board checks in JLC's own placement preview, when you start that order** (I remind you then; `hardware/instrument/fab/ORDER.md`): connector directions, LED polarity, crystal pin 1, the ESD array and SOT-23 rotations; and decide the board size against the price tier (120 x 90 mm, or about 105 x 80 mm with a placement re-run). The preview is JLCPCB's check of the fab files; an extra review of the layout by another model before ordering is optional (I can prepare a review packet if you want one).

## En route

JLCPCB (last read in the JLCONE app 2026-11-10; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production in the last read (2026-11-10); the user reports it has since shipped (not yet confirmed in the app).
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed and in transit; expect it in a few weeks. Logged in `lab/docs/orders.md`.
