# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Printing window Thursday 2026-11-12, 7:45 pm, 75 minutes.** Print session per `~/Code/sysadmin/wsl/docs/print-session-runbook.md`. At 7:45 pm plug the K1 in and switch it on (the black spool is already loaded, about 1 kg) and tell me; I run the checks and start the print only when you ask. File: `balance_p1a_post_np_bars_np_pn.gcode` (post np with its bar and the pn bar, 54 min, 43 g, no supports), about 60 min with start-up. Visual checks, clock times given at the start. Expected finish about 8:50 pm; the window ends at 9:00 pm.

The 2026-11-11 session is finished. Left to print after this window: posts pn and pp with the pp bar (73 min, 61 g), two calibration riders (13 min, 3 g), the base (4 h 41 min).

## Ready to build now — parts on hand

2. [ ] **Later print windows** (after task 1): the three files above in the order given; settings in [print_requirements.md](print_requirements.md) section 6. Fastener positions: [img/fasteners.jxl](img/fasteners.jxl); steps: [assembly.md](assembly.md). Photo of everything printed so far: [img/printed_parts_2026-11-11.jxl](img/printed_parts_2026-11-11.jxl).

3. [ ] **Choose the enclosure walls: six clear acrylic sheets, or printed wall frames with small windows.** Acrylic: six 2 mm 150 x 250 sheets, about C$49 by your cart figure, no printing. Printed: eight PLA wall halves (the bed takes 124 x 150 each), about 250 g and an estimated 16 hours of printing (13 or more 75-minute windows), plus four clear 100 x 100 x 2 mm windows whose price I have not checked. My recommendation is the acrylic; reply with the choice and I rework or leave the CAD.
4. [ ] **Show me the Dremel cutoff wheels:** a photo of the Dremel's model label and the cutoff wheels (diameter and thickness, from the packet or measured with the calipers once their cell arrives). A wheel up to about 1.2 mm thick fits the saw guide's 1.4 mm kerf slot unchanged, which would replace the hacksaw blades for the brass rod cut.

5. [ ] **Decide on the 45-degree Y-branch joints on the main board.** Thirteen of the seventeen have a leg shorter than 0.7 mm and cannot be rewritten without new copper conflicts. Accept them as the one exception to the no-acute-angle rule (the empty wedge is 45 degrees and under 0.7 mm deep; JLC's etching handles that, and their DFM preview shows it), or require re-routes that may leave connections unrouted? My recommendation is to accept them.

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed; expect it in a few weeks. Logged in `lab/docs/orders.md`.
