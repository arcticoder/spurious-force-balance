# TODO — arcticoder

Things that need your hands, eyes or a purchasing decision for this experiment: ordering, printing, assembling, bench checks. File-creation work is not here; it is in
[TODO-agent.md](TODO-agent.md). The parts ledger is shared with the [`lab`](https://github.com/arcticoder/lab) repo (its `docs/inventory.md` and `docs/orders.md`), and the AliExpress
cart is one checkout across both repos. Done items move to [TODO-completed.md](TODO-completed.md).

---

## What I need from you

0. **Commit when you are ready** (I will not commit): both repos have staged changes: pictures converted to `.jxl` with LFS, the EasyEDA project (`hardware/easyeda/*.eprj2`, LFS), the new `tools/to_jxl.py`, the kb and TODO files,. `lab` already has its `.gitattributes` commit and only a staged kb note; commit it, then this repo; push only after `git lfs ls-files` lists the `.jxl` and `.eprj2` files. Save in EasyEDA Pro first (I saved at the end of this session). No other action is waiting on you for the EasyEDA work: the schematic imports for both sensor heads are done and the next agent task is placement and routing. Registering for Spark waits until the boards are redone in EasyEDA Pro (draft answers: [spark_application.md](spark_application.md)); registration closes 2026-11-30.
1. **Pay for the arm order** (FR4 1.2 mm, green, HASL, 5 pieces: C$7.86 after the coupon; check that the thickness still reads 1.2 mm at payment: it reverts to 1.6 mm and the shipping then jumps to C$12.05). Its JLCONE $8 PCB coupon ends 2026-11-26.
2. **Quote and order the three small designs separately** (`clamp_ground`, `elec_board`, `clamp_plate` zips; 1.2 mm, HASL; a second coupon, e.g. New User PCB, ends 11-25): do not add them to the arm's order or use Combine Shipping (the arm's parcel is 294 g of the 300 g line). Tell me the three lines' prices.
3. **Coupon dates:** in the JLC account, note the expiry date of each coupon whose list entry says only "valid for 30 days" or "60 days" (the dollar-off-$40/$50 3D-printing, material, FDM and nylon ones), and the claim date if shown.
4. **Optional now (the aluminium arm is shelved): JLCCNC sheet-metal quote page** (I can only see the upload box; the options appear after a file is uploaded): make `lab/docs/jlc/cnc_sheet_metal_quote_ui.md` the way you did the other two. Use any STEP/DXF (I will export the arm for it later:
   Part J3). Also useful: the HDI option on the PCB quote (thicknesses, layer counts, price for 5 pieces of the arm) as `lab/docs/jlc/hdi_quote_ui.md`.
5. **Decide on the early sensor-head order** (optional; its New User SMT coupon, C$13.99, ends 2026-11-25): upload `hardware/instrument/heads_panel/out/heads_panel_gerbers.zip` with `bom.csv` and `cpl.csv`
   using [heads_panel/ORDER.md](../hardware/instrument/heads_panel/ORDER.md), read the Standard-assembly total and tell me whether to go on; answer "Confirm Production File" and "Confirm Parts Placement" emails within 48 h.
   It also needs one 4-pin JST-SH cable (both ends, 100-150 mm) in the AliExpress cart. Skip it if the quote is more than you want to spend before the balance is built.
6. **JLCMC fasteners:** check whether M3 stainless (304/A2) hex nuts and flat washers are listed, at what price and shipping, since two coupons (C$13.99 each) apply to that service.

## Next orders — JLC mechanical boards (two orders)

Settings are in [ORDER.md](../hardware/balance/boards/fab/ORDER.md): 1.2 mm (the page reverts to 1.6 mm: check it), green, HASL, 5 pieces each, no Combine Shipping, the cheap postal tier. Unassembled boards: no setup or extended-part fees.
(a) The arm alone: quoted C$7.86 after the coupon, shipping C$2.10. (b) The three small designs: not quoted yet. Together about C$10-25 [estimate for (b)]; the old $70-140 estimate was wrong.

## Next order — AliExpress: what is left for the balance

Hold these until the JLC boards are on their way, then one checkout, with whatever the lab list needs. None of them has a shipping fee in the cart; hold the cart if one shows.

- **Clear acrylic, 2 mm, 150 × 250 mm, 7 sheets**: four walls, two lid pieces and a spare, used uncut.
- **M3 flat washers, 304 stainless, 3.2 mm inner and 7 mm outer diameter, 50 pieces** (20 are used).
- **M3 hex nuts, 304 stainless, 20 pieces** (10 are used, all on the moving arm and the vane holder).
- **JST-SH 1.0 mm 2-pin cable, flying leads on one end, 100 to 150 mm, 2 pieces**: carries the plate voltage from the fab board to the balance (the leads thread through the board's holes; no soldering).
- **Calibration weights, 1 mg to 500 mg** (an analytical-balance weight set): turns plate voltage into an absolute force. Pick a class stated in the listing.
- **If not already owned** (none are in the inventory): a junior hacksaw, a flat needle file, a craft knife and a steel ruler, for the brass ballast and the 4 mm stainless strip.

## Ready to build now — parts on hand

1. [ ] **Print the balance's frame** (`hardware/balance/cad/*.stl`, PLA, 3 walls, about 30% infill, 0.2 mm layers): `base`, `gantry` (lay it on its side), `head`, `sensor_bracket`, `elec_bracket`,
       `vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the four jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
       `damper_holder` is the flat-disc version (the twist test of 2026-10-26 found the discs magnetized through the flat faces). The arm, clamp plates and electrode board come as fab boards, not prints.
       The prototype check (A5) needs the lock-in and the optical readout from `lab` built first (`signal_conditioning/lockin_amplifier`, `signal_conditioning/optical_shadow_readout`).
       Steps: [assembly.md](assembly.md).

## En route

The AliExpress order placed 2026-10-24: the 0.05 mm 304 stainless sheet, the 3 mm × 10 m foam tape (0.3 mm thick), the 20 × 20 × 0.3 mm copper pads (5), the 10 mm × 1 m copper foil tape and the
10 × 100 mm brass rod. Check the pads are non-magnetic on arrival (a disc magnet should not pull them).
