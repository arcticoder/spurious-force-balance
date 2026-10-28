# JLCPCB mechanical-board order — quote recipe (rewritten 2026-10-27)

Where: `cart.jlcpcb.com/quote`, product "Standard PCB/PCBA", with the PCB-only choice (the **PCB Assembly** toggle off: these boards carry no components, nothing for JLC to reflow).
Field names and order below follow the page as captured in the `lab` repo's [`docs/jlc/pcba_quote_ui.md`](https://github.com/arcticoder/lab/blob/main/docs/jlc/pcba_quote_ui.md).
Four designs, 5 pieces each. The Gerber zips are in this folder; each upload fills the page's dimensions itself.

## Fields, in the page's order

| Field | Choice | Why |
|---|---|---|
| Base Material | **FR-4** | stiff, light, flat; the arm's stiffness is the reason (`material_study.py`: first bending mode about 36 Hz at 1.2 mm with its loads) |
| Layers | **2** | no inner layers needed |
| Dimensions | as read from the zip: arm 208 x 60, elec_board 24 x 34, clamp_ground 17 x 19, clamp_plate 16 x 14 mm | JLC's mass estimate is this rectangle times the thickness |
| PCB Qty | **5** | the preset minimum; the rest are spares |
| Product Type | Industrial/Consumer Electronics | the default |
| Different Design | **1** for each separate upload (4 for the panel variant below) | |
| Delivery Format | **Single PCB** (panel variant: Panel by Customer) | |
| PCB Thickness | **1.2 mm** | the CAD, inertia and clamp stack assume it; 1.0 mm drops the arm's first mode to about 29 Hz, 1.6 mm raises it to about 54 Hz at +33% mass |
| PCB Color | **Black** for the arm; **Green** for the other three (fastest; colour is irrelevant) | black mask is low-reflectance beside the optical path; black adds 2 days, and the parcel waits for the slowest board anyway, so use black on all four if Combine Shipping waits |
| Silkscreen | White (default) | |
| Material Type | **FR4 TG135** (default) | arm temperature never nears 130 C |
| Surface Finish | **ENIG** for arm, clamp_ground, elec_board; **LeadFree HASL** for clamp_plate (no copper, cheapest) | flat gold pads are the electrodes and the strip contact; one finish applies to everything in a file |
| Outer Copper Weight | 1 oz | |
| Via Covering | Tented (default) | the only via (0.8 mm, in the electrode pad's back-face wire) is not a contact surface |
| Via Plating Method | Not Specified | |
| Min Via Hole Size/Diameter | **0.3 mm / (0.4/0.45 mm)** (the no-surcharge option) | the smallest drill is the electrode board's 0.4 mm via |
| Board Outline Tolerance | **+-0.2 mm (Regular)** | the clamp reference is the hole pattern, not the edge; precision routing needs three 1.5 mm alignment holes and boards of at least 50 x 50 mm (only the arm qualifies) |
| Confirm Production File | **Yes** for this first order (answer the email within 48 h), No afterwards | catches a mask or outline misreading before production |
| Mark on PCB | **Remove Mark** | no serial number or order number on the faces |
| Electrical Test | the default (flying probe); take the free random test if offered | the boards have almost no nets |
| Gold Fingers, Castellated Holes, Edge Plating, Blind Slots, UL Marking, Humidity Indicator Card | No | |
| PCB Remark | "Arm: the flag finger has copper on both faces under the mask and the large ENIG pads are intentional. No components." | |

## Per design

| Design | File | Size (mm) | Finish | Colour | 5-piece mass (JLC's rule) | Note |
|---|---|---|---|---|---|---|
| arm | `arm_gerbers.zip` | 208 x 60 | ENIG | black | 138 g | strip contact pad, moving electrode, flag finger, 7 holes |
| clamp_ground | `clamp_ground_gerbers.zip` | 17 x 19 | ENIG | green | 4 g | strip pad and the plated wire hole |
| elec_board | `elec_board_gerbers.zip` | 24 x 34 | ENIG | green | 9 g | fixed electrode and its guard |
| clamp_plate | `clamp_plate_gerbers.zip` | 16 x 14 | LeadFree HASL | green | 3 g | plain plate; two per balance |

Per balance: 1 arm, 2 clamp_plate, 1 clamp_ground, 1 elec_board. Five of each arrive.

## Coupon and shipping

- One coupon per checkout: apply **New User PCB (C$8.40, ends 2026-11-25)** to the order it saves most on (the arm). The ledger is `lab/docs/jlc/coupons.md`.
- The four uploads become four cart lines. Use **Combine Shipping** only while the combined estimated mass is under 0.29 kg: boards 194 g with packing (`tools/jlc_parcel_mass.py`), so one parcel is fine
  here, but do not combine this parcel with a 3D-printing or CNC order (JLC3DP and JLCCNC ship separately anyway, and the sum with the printed-part candidates is 314 g).
- Pick the cheap postal tier (Global Standard Direct Line) if offered for Canada; read its price at this mass and note it in `TODO-arcticoder.md`.
- If the arm alone is over about $60, or the parcel over 0.29 kg, stop and ask: a shorter arm needs a damper rework (see `docs/fabrication.md`), so it is not a quick switch.

## Variant: all four designs as one panel (quote probe first)

Upload the arm zip, then change Dimensions to **252 x 60**, Different Design to **4**, Delivery Format to **Panel by Customer** and Qty to 5 and read the price and mass: the three small boards would sit in two
columns beside the arm (elec_board over clamp_ground, then two clamp_plates), 2 mm apart. Five panels give 5 arms, 5 elec_boards, 5 clamp_grounds and 10 clamp_plates; the mass by JLC's rule is about 168 g
against 154 g. One finish applies to the whole panel (ENIG for all) and the colour is black. If the quote beats the sum of the four separate ones, ask the agent to build the panel Gerbers (tabs, mouse bites);
do not upload the arm zip as a panel as it is.

## Checks done before this file was written

`kicad-cli pcb drc` (KiCad 9.0.9): no errors; the only warnings are that the generated hole footprints have no library entry. JLC's published limits [confirmed on jlcpcb.com/capabilities 2026-10-24]:
minimum non-plated hole 0.5 mm (smallest here 3.4 mm), minimum plated hole 0.15 mm (smallest here 0.4 mm via, 1.6 mm wire hole), copper to routed edge 0.2 mm (smallest here 0.5 mm), outline tolerance
+-0.2 mm for ordinary routing, thickness tolerance +-10% at 1.0 mm and up. The boards' mass estimates: `python3 hardware/balance/boards.py`.
