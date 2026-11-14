# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [x] **Safety glasses for the brass cut:** in your AliExpress cart (SCVCN photochromic cycling glasses, C$3.48, listing 1005010228786764). Not yet placed; when the order is placed, I log it in `lab/docs/orders.md`. No dust mask is being bought.
2. [ ] **Print windows (reserved by you 2026-11-13).** Saturday 2026-11-14, 07:30-10:00: post pp's L (47.6 min, 26.3 g); sliced and ready (`balance_p7_post_pp_L_20261113.gcode`, bed 60, header checked). A second file is ready to follow it on the black spool (`balance_p8_wall_strips_x4_20261113.gcode`: the four wall strips, 65.6 min, 29.1 g, bed 60). Pp L plus start-up (about 12 min) plus the strips (about 68 min, fast start) ends about 2 h 10 min after you start, inside the window. Optional: skip the strips if the window runs short; the strip orientation has some bridging and two of them touch the bed on only 71 % of the footprint, so look at the first layer of that print (I give the clock time). Plug the printer in and switch it on before the window; the first print after a power-on uses the normal start (runbook section E). Sunday 2026-11-15, 16:30-18:30: next window, no file assigned yet. Saturday 2026-11-21, 07:30-12:30: the base (4 h 41 min), sliced on 2026-11-20. Then the enclosure plates (`kb/balance_design_notes.md`). Photo of everything printed so far: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).
3. [ ] **Cut the ballast from the brass rod with the hacksaw (after the glasses, the blades and the printed handle).** Saw a 15 mm piece in the printed saw guide (`docs/assembly.md`, Ballast section): the guide leaves 0.5 mm to file off. The blades (from the 2026-11-10 parcel, in transit; tell me when it lands) have no handle, so I designed a printed pad-saw handle that clamps the blade's end under a cover with four M3 x 14 screws and rides in the guide's slot (`fixture_hacksaw_handle_body` and `_cover`, 130 x 24 x 22 mm and 62 x 24 x 6 mm). It is my own design, not the Printables one (the blades are 6 x 0.4 mm and their hole positions are unknown; if you still want the Printables frame, send the link and I check its fit to these blades). It is sliced for the Sunday 2026-11-15 window once the model is Sonnet. Wear the glasses for the whole cut. No mask is needed for a hand hacksaw cut: the chips are coarse. The only fine dust is from filing the sawn face, which is a small exposure; keep filing short, wipe the filings up with a damp cloth rather than blowing them away, and wash your hands after (brass can contain lead). Then file the sawn face to the length `balance.py` prints (15.1 mm with the CAD's numbers) and check it passes through the arm board's 10.2 mm hole.
4. [ ] **Main-board checks in JLC's own placement preview, when you start that order** (I remind you then; `hardware/instrument/fab/ORDER.md`): connector directions, LED polarity, crystal pin 1, the ESD array and SOT-23 rotations; and decide the board size against the price tier (120 x 90 mm, or about 105 x 80 mm with a placement re-run). The preview is JLCPCB's check of the fab files; an extra review of the layout by another model before ordering is optional (I can prepare a review packet if you want one).

## En route

JLCPCB (last read in the JLCONE app 2026-11-10; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production in the last read (2026-11-10); the user reports it has since shipped (not yet confirmed in the app).
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed and in transit; expect it in a few weeks. Logged in `lab/docs/orders.md`.
