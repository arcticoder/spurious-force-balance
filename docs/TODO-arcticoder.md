# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

1. **Place the AliExpress balance order** from the cart: LR44 5-pack (C$2.85), 2-pin JST-SH 10 cm cable 5-pack (C$1.04), 6-inch 24T mini hacksaw blades (C$1.92), M3 x 7 x 0.5 mm washers x100 (C$0.73), 1 g M1 weight (C$2.48), 0.1 g scale (C$3.79) and the 2-pack diamond needle files (C$1.38); the cart then clears the Choice free-shipping threshold. Tell me when it is placed.
2. **Printing session, morning of Wed 2026-11-11 (4 h, gantry):** follow [`print-session-runbook.md`](../../../sysadmin/wsl/docs/print-session-runbook.md) (in the wsl workspace) from the top. Plug the printer in and switch it on, keep the riser vents closed, and tell me the window; I check the sliced G-code before I submit it and tell you which spool to load.

## Ready to build now — parts on hand

1. [ ] **Print the rest of the balance's frame** (`hardware/balance/cad/*.stl`; settings in [print_requirements.md](print_requirements.md) section 6). Next: `gantry` (Wednesday), then the four `encl_post_*`, `fixture_strip_guide` and `base`. Fastener positions: [img/fasteners.jxl](img/fasteners.jxl); steps: [assembly.md](assembly.md).

## En route

JLCPCB (read in the JLCONE app 2026-11-09; details in `lab/docs/kb/jlc_account_and_quotes.md`):
- `arm` (5 FR4 boards, placed 2026-11-03): In Production since 2026-11-08, factory finish estimate 2026-11-12.
- `elec_board` (placed 2026-11-05): Shipped 2026-11-09 (tracking number in the JLC app).
- `clamp_ground` (placed 2026-11-06): Shipped 2026-11-08, left the Hong Kong sort facility 2026-11-09 (tracking number in the JLC app); the Global Standard Direct Line is labelled 8-12 days.
- `clamp_plate`: not ordered; shipping is being worked on (see `TODO-BLOCKED.md`).
Answer any JLC email within 48 h and check the spam folder. When a parcel lands, tell me and I add it to the plan in `docs/fabrication.md`.

AliExpress: nothing in transit until task 1 is placed.
