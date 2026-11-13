# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Inspect tonight's prints** when the bed is at about 40 C: post np with its bar and the pn bar (first print), post pn, the pp bar and the two calibration riders (second print); tell me if anything is stringy, warped or has gaps. Remove the purge strand at the rear-left corner if still on the plate.

The 2026-11-11 session is finished. Left to print after this window: posts pn and pp with the pp bar (73 min, 61 g), two calibration riders (13 min, 3 g), the base (4 h 41 min).

## Ready to build now — parts on hand

2. [ ] **Later print windows:** post pp (about 32 min) and the base (4 h 41 min), then the enclosure plates (`kb/balance_design_notes.md`); I slice each file the day before its window and name the runbook each time. Photo of everything printed on 2026-11-11: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).

3. [ ] **Safety gear for abrasive cutting (AliExpress order).** You own no safety glasses or dust mask, and the Dremel wheel throws hot grit and brass dust (it can contain lead). Pick one listing each and tell me the links so I add them to the next cart: clear polycarbonate safety glasses marked ANSI Z87.1 or EN 166 (anti-fog optional), and a pack of FFP2 or KN95 masks whose listing shows an EN 149 or GB 2626 test report. My search found no AliExpress listings, so I cannot name candidates; certification claims on AliExpress are often unverifiable, so choose a seller that shows the certificate. Until they arrive, no abrasive wheel on brass: the hacksaw in the saw guide (blades are in the 2026-11-10 parcel) needs no grit but still wear glasses when filing.
4. [ ] **Main-board checks in JLC's own placement preview, when you start that order** (I remind you then; `hardware/instrument/fab/ORDER.md`): connector directions, LED polarity, crystal pin 1, the ESD array and SOT-23 rotations; and decide the board size against the price tier (120 x 90 mm, or about 105 x 80 mm with a placement re-run). The preview is JLCPCB's check of the fab files; an extra review of the layout by another model before ordering is optional (I can prepare a review packet if you want one).



5. [ ] **Ballast alternative (your call):** send me the dimensions (diameter and height) or link of the C$2.92 10 g stainless weight. The arm's ballast hole is 10.2 mm and the arm is already in production, so the weight fits only if its diameter is 10 mm or less; then it replaces the sawn rod piece (about 10 g at 15 mm) and the cut is not needed. If it is wider, saw the rod with the hacksaw guide (the rod, blades and guide are already owned, so buying the weight adds C$2.92 and saves nothing).

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed; expect it in a few weeks. Logged in `lab/docs/orders.md`.
