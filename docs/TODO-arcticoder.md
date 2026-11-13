# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Printing window Thursday 2026-11-12, from 8:15 pm, 75 minutes.** Runbook: `~/Code/sysadmin/wsl/docs/print-session-runbook.md` (prep steps done at 6:40 pm). The black 1 kg spool is already loaded (the sensor sees filament; the job needs 43 g): nothing to swap unless you changed it. At 8:15 pm switch the K1 on if it is off, make sure the plate is clear, and tell me; nothing heats until you ask in that message. File `balance_p1a_post_np_bars_np_pn.gcode` (post np with its bar and the pn bar, no supports, 54 min, 43 g, about 60 min with start-up). Look at the first layer at about 8:35 pm and once at about 8:55 pm (clock times follow the actual start); expected finish about 9:20 pm.

The 2026-11-11 session is finished. Left to print after this window: posts pn and pp with the pp bar (73 min, 61 g), two calibration riders (13 min, 3 g), the base (4 h 41 min).

## Ready to build now — parts on hand

2. [ ] **Later print windows** (after task 1): the three files above in the order given; settings in [print_requirements.md](print_requirements.md) section 6. Fastener positions: [img/fasteners.jxl](img/fasteners.jxl); steps: [assembly.md](assembly.md). Photo of everything printed so far: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).

3. [ ] **Decide the printed enclosure walls** (preview: [img/enclosure_printed_preview.jxl](img/enclosure_printed_preview.jxl)). Proposal: walls and lid printed as plates (a 250 mm wall is a 148 mm and a 100 mm plate joined by a printed strip), grey walls, red lid, black joining strips, and optionally one clear 100 x 150 x 2 mm acrylic window in the front wall. Plates 1.2 mm thick with a 2 mm rim where they slide into the posts: about 7-8 hours of printing in about eight sessions and about 300 g of PLA; full 2 mm plates would take about 11 hours and 440 g (estimates from a slice with the standard preset). Reply: printed yes or no, and window yes or no.
4. [ ] **Measure the Dremel's nose thread:** unscrew the nose cap and measure the threaded end's outside diameter with the printed calipers, and count the threads over 10 mm. I design a printed chop stand that screws onto it (arm, hinge, wheel guard, rod clamp) once I have these two numbers. Also tell me whether you have safety glasses and a dust mask; cutting brass with the abrasive wheel needs both.



## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed; expect it in a few weeks. Logged in `lab/docs/orders.md`.
