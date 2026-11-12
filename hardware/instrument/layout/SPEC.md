# Main board layout specification (written 2026-11-11/12, before further routing)

Board: 120 x 90 mm, 4 layers, 1.6 mm (confirm at order), 164 parts, 111 nets. The price tier against board size is the user's decision (the cheap 4-layer tier is 50 x 50 mm). Source of truth: the SKiDL netlist `../schematic/out/main_board.net`; this file is the layout contract; `mainboard.py` implements it.

## Stackup
| Layer | Use |
|---|---|
| F.Cu | signals and parts |
| In1.Cu | solid GND plane, nothing else (the router may place GND tracks here; the plane zone is poured after routing) |
| In2.Cu | signals plus a 3V3_D pour that flows around other nets' tracks (poured after routing) |
| B.Cu | signals |

## Rules (decided; see `kb/pcb_toolchain_notes.md`)
Track 0.2 mm default, clearance 0.15 mm, vias 0.6/0.3 mm (annular 0.15 mm, JLC's absolute minimum), DRC track floor 0.10 mm (fine-pitch neck-downs), pad-hole to pad-hole 0.45 mm (custom rule), copper to edge 0.2 mm, 45-degree bends only; 45-degree Y-branches are accepted (user, 2026-11-12), two-segment V turns and hairpins are not.

## Net classes
- Power trunks 0.4 mm: V5, VBUS, VBUS_F, V24, V24_RAW, V5_BOOST, BOOST_SW.
- Rails 0.25 mm: 3V3_A, 3V3_AR, 3V3_D, DVDD_1V1 (3V3_D also poured on In2).
- Signals 0.2 mm; USB_DP/USB_DM (and _C) routed together, short, no stubs; both crystals (XIN/XOSC_OUT and ADC_XTAL1/2) short and inside their blocks.
- GND: any layer; every GND pad gets a via to In1 near it.

## Floorplan (fractions of W x H, y down; `BLOCK_REGIONS` in `mainboard.py`)
Six 4-pin JST-SH head connectors fixed along the top edge, four 2-pin JST-SH on the left edge, five 2.54 mm headers on the right edge, USB-C bottom centre; four M3 mounting holes at the corners (3.2 mm drill, 3.8 mm keepout, moved inward only when copper is in the way).
| Block | Region | Contents |
|---|---|---|
| ADC | x 0.30-0.70, y 0.12-0.40 | ADS131A04, its crystal, reference and input filters, MCP4728 DAC: top centre, nearest the head connectors, over unbroken GND |
| LED sinks | x 0.09-0.29, y 0.12-0.40 | TLV9062, SN74LVC1G3157 gates, AO3400A, sense resistors |
| Device sink | x 0.72-0.93, y 0.12-0.42 | AOD4184A, TLV9062, gate |
| Plate driver | x 0.62-0.93, y 0.44-0.62 | OPA197 and its gain network |
| Boost | x 0.62-0.93, y 0.64-0.98 | MT3608, inductor, diode, filter: compact loop, far corner from the ADC |
| MCU | x 0.13-0.42, y 0.42-0.72 | RP2040, QSPI flash, crystal, buttons, status LEDs, decoupling |
| Sensors | x 0.44-0.61, y 0.42-0.62 | TMP117, LIS2DW12 |
| Power entry | x 0.30-0.70, y 0.74-0.99 | USB-C, ESD, fuse, ferrite, two LP5907 |
| Motor drivers | x 0.07-0.29, y 0.74-0.98 | two AO3400A and flyback diodes |
Passives follow the anchor they share most signal nets with (`assign_blocks`), so decoupling stays with its IC.

## Keep-outs
Nothing from the boost, motor or device-sink blocks routed across the ADC block; the boost switching node stays inside its block; no signal routed on In1; mounting-hole keepout as above.

## Checks that must pass before fab outputs
`mainboard.py dfm` (DRC, geometry, netlist parity, mounting holes), WP6 render review, WP7 placement-preview precheck (connector directions, LED and crystal pin 1, ESD pin 1) by the user.
