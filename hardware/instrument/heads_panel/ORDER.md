# Sensor-head panel — JLCPCB Standard PCBA quote recipe (Part N, 2026-10-27)

What: one 76 x 70 mm panel with two sensor-head-1 boards (TMP117 + MMC5983MA) and two sensor-head-2 boards (TMP117), 26 x 17 mm each, tab-routed with mouse bites in a 5 mm rail with three tooling
holes and three fiducials. Standard assembly needs at least 70 x 70 mm with edge rails [quote-page capture, `lab/docs/jlc/pcba_quote_ui.md`]; this panel meets it. Files in `out/`:
`heads_panel_gerbers.zip`, `bom.csv`, `cpl.csv`, `drc.json`, `heads_panel.png`, `heads_panel.kicad_pcb` (rebuild: `~/.venvs/lab-hw/bin/python hardware/instrument/heads_panel/build_panel.py`).
Why now (optional): the heads do not depend on the A5 result; the New User SMT coupon (C$13.99) ends 2026-11-25; it exercises JLC's assembly flow and puts the magnetometer and temperature drivers on real hardware
before the main board. One panel carries 2 + 2 heads: 4 TMP117, 2 MMC5983MA. **It is the user's decision after reading the quote.**

## Fields (Standard PCB/PCBA quote, PCBA toggle on)

| Field | Choice | Why |
|---|---|---|
| Base Material / Layers | FR-4, 2 | |
| Dimensions | 76 x 70 mm | the panel |
| PCB Qty | 5 panels (the preset minimum) | 5 panels = 10 + 10 heads of the two kinds |
| Different Design | 2 | head 1 and head 2 |
| Delivery Format | **Panel by Customer** | the panel is drawn here (tabs, mouse bites, rails) |
| PCB Thickness | 1.6 mm | the default; 76 x 70 x 1.6 mm = 15.7 g, 79 g for 5 |
| Color / Silkscreen | Green / White | fastest; nothing optical here |
| Surface Finish | **ENIG** | the MMC5983MA is an LGA with 0.5 mm pitch: HASL is "less suited to fine pitch". ENIG's nickel is slightly magnetic; the offset it adds is removed by the SET/RESET procedure the driver uses |
| Outer copper, via covering, via size | 1 oz, Tented, 0.3 mm / (0.4/0.45) | the router used 0.3 mm vias with 0.6 mm pads |
| Board Outline Tolerance | +-0.2 mm (Regular) | |
| Confirm Production File | **Yes** | see the assumptions below |
| Mark on PCB | Remove Mark | |
| PCB Assembly | **On; PCBA Type Standard; Assembly Side Top; PCBA Qty 2** (two panels: 4 head-1 and 4 head-2 boards) | two panels are enough for bring-up; more can follow |
| Confirm Parts Placement | **Yes** | check the rotations in JLC's preview (below) |
| Stencil | Order together with PCB | Standard assembly processes the stencil per order |
| Depanel Boards & Edge Rail Before Delivery | No | the user breaks the mouse bites |
| Nitrogen reflow, Flying probe, Function test, Cardboard / ESD packaging | No | the packaging options add weight and cost |
| Assembly Remark | "Sensor head panel. Magnetometer U2/U4 (MMC5983MA, C404329) and TMP117 (C699536) are Standard-only parts. Please confirm placement and rotation of the LGA and WSON parts." | |

Files to upload: the Gerber zip, then `bom.csv` and `cpl.csv`. Parts, all JLC-stocked: C404329 MMC5983MA x2, C699536 TMP117 x4, C160404 JST-SH 4-pin x4, C14663 100 nF x6, C15849 1 uF x2, C15850 10 uF x2.
Extended parts: C404329, C699536, C160404 (3 x about US$3 loading fee [community]); the passives are basic. Parts cost about US$9.4 per panel at the 5-piece snapshot prices (`parts.py` snapshot), so the quote is
dominated by the Standard setup, the stencil and the extended-part fees: read it before deciding.

## Coupon

One coupon per checkout: **New User SMT (C$13.99, ends 2026-11-25)**. The stencil coupon (C$9.80, ends 12-25) cannot be stacked in the same checkout; it is unused unless a later order also needs a stencil.

## Cable

Each head connects to the Pico or the main board with a 4-pin JST-SH cable (pins: 3V3_D, GND, SDA, SCL): a 4-pin JST-SH 1.0 mm cable with connectors on both ends, 100-150 mm, for the AliExpress cart.
For bring-up on the bench the heads need only a Pico and `firmware/bringup_sensors.py` (I2C0: GP4 SDA, GP5 SCL, 400 kHz, pull-ups are on the main board: add two 2.2 kohm resistors to 3V3 on a breadboard).

## What was checked, and what was assumed

- Routing: Freerouting, 0 unrouted; both faces carry a ground pour; `kicad-cli pcb drc`: 0 unconnected, no clearance errors. KiCad reports 16 "malformed outline" errors because the tab gaps leave each board outline open on purpose
  (the panel is milled along the lines; JLC panels by customer are drawn this way [assume]); the other messages are silkscreen-clipped-by-mask and pour-island warnings.
- Assumed, to confirm in JLC's DFM and placement preview (hence "Confirm Production File" and "Confirm Parts Placement"): the 5 mm rail, 2 mm tooling holes and 1 mm fiducials, the 2 mm routed gap and 3 mm tabs with four 0.5 mm
  bites at 0.8 mm pitch, and the part rotations in `cpl.csv`, which use each footprint as drawn (EasyEDA-sourced footprints often need a rotation or mirror in JLC's library: the preview shows it).
- Not done: JLC's own DFM; the symbols' polarity (no polarized parts here); the MMC5983MA's 10 uF reservoir capacitor is a 0805 X5R (25 V part at 3.3 V).
