# TODO — agent (Claude-facing)

> Finished: `TODO-completed.md`. Waiting on something outside my control: `TODO-BLOCKED.md`. Later work: `TODO-backlog.md`. The user's list: `TODO-arcticoder.md`. Open items only; the reasoning is in `kb/main_board_assessment.md`.

### Main board: change of method (assessment 2026-11-11)
- [ ] Read the result of the In2-plane route started about 21:00 on 2026-11-11 (`layout/out/route_in2_b.log`) and record it in `kb/main_board_layout_notes.md`; do not patch that board further, whatever it shows (the method changes below).
- [ ] A. One-hour spike on the headless `pcbnew` segfault (`KICAD_CONFIG_HOME`, `xvfb-run`, a minimal board); if it loads, plan the switch to native Specctra export/import, zone fill and DRC; record either outcome in `kb/pcb_toolchain_notes.md`.
- [ ] B. Write `hardware/instrument/layout/SPEC.md` before any more routing: stackup (In1 solid GND, In2 3V3 pours plus slow signals), rules, net classes (power widths, USB pair, analog), keep-outs, mounting holes, connector edges and directions, floorplan.
- [ ] C. Replace force-directed placement with a floorplan plus per-block templates from the data sheets (RP2040 guide section 2, ADS131A04 layout, MT3608 layout); keep the DFM gate, parity, geometry, silk and hole tools.
- [ ] D. Pre-route and lock the critical nets in code (USB pair, both crystals, boost loop, power trunks), then autoroute the rest with 5-10-minute limits.
- [ ] E. In2 as 3V3 pours under their blocks with signal channels, not a solid plane; then DRC, `geometry`, `dfm`, WP6 render review.
