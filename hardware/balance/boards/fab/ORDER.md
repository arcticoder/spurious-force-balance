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
| Surface Finish | **HASL** (with lead, the page's default, or lead-free) for all four (ENIG added **C$25.25** to the arm alone, a quote the user read on 2026-10-28; HASL adds nothing) | the force scale comes from the weights calibration, so an uneven electrode surface (HASL is less flat than gold) costs stability, not accuracy; ENIG is only worth that money if the arm's first measurements show surface-potential drift. HASL with lead is the page's default; lead-free is the RoHS choice |
| Gold Thickness | not shown with HASL (only with ENIG; if ENIG is ever chosen: 2 u" for the arm and elec_board only if the quote adds a few dollars) | |
| Outer Copper Weight | 1 oz | |
| Via Covering | Tented (default) | the only via (0.8 mm, in the electrode pad's back-face wire) is not a contact surface |
| Via Plating Method | Not Specified | |
| Min Via Hole Size/Diameter | **0.3 mm / (0.4/0.45 mm)** (the no-surcharge option) | the smallest drill is the electrode board's 0.4 mm via |
| Board Outline Tolerance | **+-0.2 mm (Regular)** | the clamp reference is the hole pattern, not the edge; precision routing needs three 1.5 mm alignment holes and boards of at least 50 x 50 mm (only the arm qualifies) |
| Confirm Production File | **Yes** for this first order (answer the email within 48 h), No afterwards | catches a mask or outline misreading before production |
| Mark on PCB | **Remove Mark** | no serial number or order number on the faces |
| Electrical Test | the default (flying probe); take the free random test if offered | the boards have almost no nets |
| Gold Fingers, Castellated Holes, Edge Plating, Blind Slots, UL Marking, Humidity Indicator Card | No | |
| PCB Remark | "Arm: three copper areas are intentional: the flag pad at the end has copper on both faces under the mask; the strip contact pad and the large electrode pad are bottom-layer only, joined by a 0.6 mm bottom trace. No components." | |

## What the arm costs (user's quote, 2026-10-28, C$, before coupons)

Engineering fee 5.61 + Board 8.56 = **14.17** with HASL (+25.25 with ENIG), plus shipping: the Global Standard Direct Line jumped to **12.05** once the arm was uploaded. The small default board's C$2.81 "special offer" does not apply to the arm
(over 100 x 100 mm). The engineering fee is per design, so four separate designs may carry four fees: the panel variant below (one file, one fee) is worth quoting. The aluminium arm (JLCCNC, `arm_cnc.dxf`, New User CNC and JLCONE-$20 CNC coupons of C$28.06 each) is worth
quoting beside it: an FR4 arm is about C$26 with HASL and shipping before any coupon.

## Per design

| Design | File | Size (mm) | Finish | Colour | 5-piece mass (JLC's rule) | Note |
|---|---|---|---|---|---|---|
| arm | `arm_gerbers.zip` | 208 x 60 | HASL | black | 138 g | strip contact pad, moving electrode, flag finger, 7 holes |
| clamp_ground | `clamp_ground_gerbers.zip` | 17 x 19 | HASL | green | 4 g | strip pad and the plated wire hole |
| elec_board | `elec_board_gerbers.zip` | 24 x 34 | HASL | green | 9 g | fixed electrode and its guard |
| clamp_plate | `clamp_plate_gerbers.zip` | 16 x 14 | HASL with lead (as set 2026-11-08) | green | 3 g | plain plate; two per balance |

Per balance: 1 arm, 2 clamp_plate, 1 clamp_ground, 1 elec_board. Five of each arrive.

## Coupon and shipping (the arm order was quoted by the user on 2026-10-28)

- **Arm alone, 5 pieces, FR4 1.2 mm, green, HASL with lead: Engineering C$5.61 + Board C$8.56 + shipping C$2.10 = C$16.27; with the JLCONE coupon (-C$8.42, applied when the line went into the cart) the subtotal is C$7.86.**
  The page's default thickness is 1.6 mm: at 1.6 mm the estimated mass was **0.34 kg and shipping jumped to C$12.05**; at 1.2 mm it is under 0.3 kg and shipping is C$2.10. **Check the thickness field after every upload: it reverts to 1.6 mm.**
  (HASL with lead is the page's default and is fine here; LeadFree is only a RoHS choice.)
- **Order the arm alone.** JLC's mass estimate includes about 155 g of packing (`tools/jlc_parcel_mass.py`): the arm order is 294 g against the 300 g line, so adding the three small designs (+17 g) would cross it. Do **not** use Combine Shipping and do not add the small designs to
  the arm's order. The three small designs are a second order (170 g with packing, well under the line); a five-piece minimum applies to each, and the engineering fee may be charged per design: read their lines before paying.
- Coupons are applied in the cart, and the line's price falls by the coupon (a coupon cannot take a line below zero). The ledger is `lab/docs/jlc/coupons.md`.
- If the arm alone is over about $60 stop and ask; it is not (C$7.86 net).

## Variant: all four designs as one panel (quote probe first)

Upload the arm zip, then change Dimensions to **252 x 60**, Different Design to **4**, Delivery Format to **Panel by Customer** and Qty to 5 and read the price and mass: the three small boards would sit in two
columns beside the arm (elec_board over clamp_ground, then two clamp_plates), 2 mm apart. Five panels give 5 arms, 5 elec_boards, 5 clamp_grounds and 10 clamp_plates; the mass by JLC's rule is about 168 g
against 154 g. One finish applies to the whole panel (HASL for all) and the colour is black. If the quote beats the sum of the four separate ones, ask the agent to build the panel Gerbers (tabs, mouse bites);
do not upload the arm zip as a panel as it is.

## The three small designs: order them as three single boards (decided 2026-11-04 from the quote page)

Quote read from the JLCONE page for the panel file (`lab/docs/jlc/small_boards_panel_quote_2026-11-04.md`): **Panel by Customer with 3 designs is C$19.25** (Engineering 5.57 + Panel 11.31 + Board 2.37), while a **Single PCB gets the C$2.79 Special Offer**. So upload the three single-board zips one at a time (`elec_board_gerbers.zip`, `clamp_ground_gerbers.zip`, `clamp_plate_gerbers.zip`; settings in the table above, Single PCB, Different Design 1, 1.2 mm, HASL, 5 pieces) and confirmed on 2026-11-04: each upload shows the C$2.79 Special Offer (calculated C$2.92 for `elec_board` and `clamp_ground`, C$3.06 for `clamp_plate` with the small-board deburring line); no coupon applies (they need goods over C$2.79); leave "Confirm Production file" at No (Yes adds C$1.46). Check "Combine Shipping" at payment only if it merges the three small orders into one cheap parcel (together about 170 g with packing); the arm order is already placed.
The panel, `small_panel_gerbers.zip` (36 x 96.5 mm, from `boards.py`'s `panel_small()`, four boards on mouse-bite tabs, DRC clean apart from the open outlines), is the fallback if the Special Offer is refused on the later uploads: as **Panel by Customer** it carries the C$11.31 panel fee for 3 designs. Declaring it a single board to get the offer would misstate the file: do not.

## Order status

| Design | Status | Total (user's figures) |
|---|---|---|
| arm | placed 2026-11-03 (JLC's clock), in review | account page shows a bare $3.00 (merchandise 1.20 + shipping 1.80) with the JLCONE $8 coupon; see the currency note |
| elec_board | placed 2026-11-05 (user's report), 5 pieces | merchandise $2.10 USD + shipping $1.50 USD = **$3.60 USD (C$5.10)**, postal tier |
| clamp_ground | placed 2026-11-06 (user's report; JLC order Y5, In Production on 2026-11-08), 5 pieces, HASL with lead, 1.2 mm, postal tier | grand total **C$5.08** (the quote page's calculated price was C$2.96; the rest is shipping); the order page shows $3.60 USD |
| clamp_plate | set up in the app 2026-11-08 (calculated C$3.10 with deburring C$0.28), stopped before save to cart; user saves and pays | |

Currency note: the order pages show USD, and the user's card charge is in CAD (the elec_board order is $3.60 USD for C$5.10, a rate of about 1.42). The arm's "C$3.00" in earlier entries is the page's bare $3.00 and was probably USD too (about C$4.25 charged); the quote page's C$2.79 Special Offer and C$2.92 calculated price are CAD estimates, and the order's USD merchandise ($2.10 is about C$2.97) was a little above the calculated price.

## Checks done before this file was written

`kicad-cli pcb drc` (KiCad 9.0.9): no errors; the only warnings are that the generated hole footprints have no library entry. JLC's published limits [confirmed on jlcpcb.com/capabilities 2026-10-24]:
minimum non-plated hole 0.5 mm (smallest here 3.4 mm), minimum plated hole 0.15 mm (smallest here 0.4 mm via, 1.6 mm wire hole), copper to routed edge 0.2 mm (smallest here 0.5 mm), outline tolerance
+-0.2 mm for ordinary routing, thickness tolerance +-10% at 1.0 mm and up. The boards' mass estimates: `python3 hardware/balance/boards.py`.
