# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Printing window Thursday 2026-11-12, from 8:15 pm, 75 minutes.** Runbook: `~/Code/sysadmin/wsl/docs/print-session-runbook.md` (prep steps done at 6:40 pm). The black 1 kg spool is already loaded (the sensor sees filament; the job needs 43 g): nothing to swap unless you changed it. At 8:15 pm switch the K1 on if it is off, make sure the plate is clear, and tell me; nothing heats until you ask in that message. File `balance_p1a_post_np_bars_np_pn.gcode` (post np with its bar and the pn bar, no supports, 54 min, 43 g, about 60 min with start-up). Started 7:42 pm; first layer looked good; expected finish about 8:45 pm. A second file follows (`balance_p6_post_pn_bar_pp_riders_x2.gcode`: post pn, pp bar, two calibration riders, 51 min, 38 g) after you clear the plate and say go.

The 2026-11-11 session is finished. Left to print after this window: posts pn and pp with the pp bar (73 min, 61 g), two calibration riders (13 min, 3 g), the base (4 h 41 min).

## Ready to build now — parts on hand

2. [ ] **Later print windows** (after task 1): the three files above in the order given; settings in [print_requirements.md](print_requirements.md) section 6. Fastener positions: [img/fasteners.jxl](img/fasteners.jxl); steps: [assembly.md](assembly.md). Photo of everything printed so far: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).

3. [ ] **Safety gear for abrasive cutting (AliExpress order).** You own no safety glasses or dust mask, and the Dremel wheel throws hot grit and brass dust (it can contain lead). Pick one listing each and tell me the links so I add them to the next cart: clear polycarbonate safety glasses marked ANSI Z87.1 or EN 166 (anti-fog optional), and a pack of FFP2 or KN95 masks whose listing shows an EN 149 or GB 2626 test report. My search found no AliExpress listings, so I cannot name candidates; certification claims on AliExpress are often unverifiable, so choose a seller that shows the certificate. Until they arrive, no abrasive wheel on brass: the hacksaw in the saw guide (blades are in the 2026-11-10 parcel) needs no grit but still wear glasses when filing.
4. [ ] **Main-board checks in JLC's own placement preview, when you start that order** (I remind you then; `hardware/instrument/fab/ORDER.md`): connector directions, LED polarity, crystal pin 1, the ESD array and SOT-23 rotations; and decide the board size against the price tier (120 x 90 mm, or about 105 x 80 mm with a placement re-run). The preview is JLCPCB's check of the fab files; an extra review of the layout by another model before ordering is optional (I can prepare a review packet if you want one).



## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed; expect it in a few weeks. Logged in `lab/docs/orders.md`.
