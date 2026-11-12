# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. [ ] **Confirm the calibration physics correction.** A vertical-axis balance cannot be calibrated with hanging weights (they tilt it, not twist it); [procedures.md](procedures.md) B.1 and [plan.md](plan.md) now use added inertia (masses at +r and -r, period change). The calibration rider cannot be designed until you confirm or reject this. No purchase is affected: the 1 g weight, the 0.1 g scale and the PLA filament serve both methods; the pair at +r and -r needs two equal masses, so one 1 g weight plus a filament piece trimmed to the same mass on the scale works, or a second 1 g weight can ride on a later AliExpress order.

The 2026-11-11 printing session is finished. Remaining plates (the posts and their bars, base 4 h 41 min) wait for a longer window.

## Ready to build now — parts on hand

2. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Next (everything but the posts and the base is printed; the photo of 2026-11-12 shows post nn complete with its bar): `balance_p1_posts_np_pn_pp_bars.gcode` (three posts and three bars, flat, no supports, 2 h 4 min, 104 g), then `base` (4 h 41 min, 177 g). Fastener positions: [img/fasteners.jxl](img/fasteners.jxl); steps: [assembly.md](assembly.md).

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: the balance order of 2026-11-10 (cells, JST-SH cable, hacksaw blades, washers, scale, 1 g weight, needle files) is placed; expect it in a few weeks. Logged in `lab/docs/orders.md`.
