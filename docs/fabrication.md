# How the balance is made: fab boards, printed parts, and what is bought

Decision record, 2026-10-24. The home printer (Creality K1) prints PLA only, because the fumes of ABS, PETG and nylon are ruled out at
home. Fab services (JLCPCB's boards, 3D printing, CNC) are in scope wherever they beat buying a stock part and cutting it by hand,
on material cost + the user's time + the risk that a hand-made part adds noise or error to the measurement. The shipping rules this
relies on are in `kb/fab_ordering_notes.md`.

Cost figures that were not read from a live quote page are marked **[estimate; verify on the quote page]**. The quote page is
interactive, so the user confirms totals before paying.

## What the review found (true whatever the route)

1. **No zero adjustment.** The calibration electrodes' 1 mm gap allows only +-0.4 degrees of arm rotation, and the flag needs the arm
   near its design angle; a strip clamped by hand sits several degrees off. Fixed with a **torsion head**: a printed disc in a bore of the
   gantry carries the upper strip clamp, and two push-push M3 adjusting screws on a 26 mm lever set its angle over +-5 degrees at 0.5 mm
   of lever per turn (1.1 degrees a turn, so 0.1 degree a tenth of a turn).
2. **A dissipating device can't sit on PLA.** A device card dissipating 0.9 W in still air warms by over 100 K (about 130 K/W for a
   16 x 24 mm card) and PLA softens near 55-60 C; the creep would follow the device's power, which is the effect being measured. The
   card is now FR4 (glass transition about 130 C [verify on the order page]) on air spacers, and the top power is capped at 0.5 W (224 mA
   through the 10 ohm card), which puts the card at 87 C, 3 K under the Tg-minus-40-K rule (`smoke_test.py`, safety check).
3. **PLA in the strip's clamping loop.** Self-tapped screws into PLA relax under preload, and a relaxing clamp rotates: zero drift with no
   signature. Every part that carries the strip's clamping force is now FR4 or steel (the arm board, three clamp plates, the strip,
   through-bolts with nuts); a smoke check fails if a printed plastic part enters that loop.
4. **Centre-of-mass tilt.** The arm hangs below the strip's lower end, and its tilt is offset divided by that hang. The printed 20 mm
   arm hung 15 mm (66 mrad per mm of offset) against about 20 mrad of clearance. The FR4 board stands 60 mm on edge, so the centre of
   mass hangs 32 mm (31 mrad per mm), and the offset left after bench trim is under 0.2 mm.

## Part by part

| Part | Made how | Why | Cost and time |
|---|---|---|---|
| **Arm** (200 x 60 mm, with the flag finger and the moving electrode) | FR4 board, JLCPCB, 1.2 mm, ENIG, black mask, 5 pcs (`boards/fab/arm_gerbers.zip`) | In-plane expansion about 14 ppm/K against PLA's 70; stiff when on edge (a 0.1 N end load bends it 0.05 um); known density, and a symmetric outline keeps the centre of mass where it was designed when the board thickness varies by +-10%; the electrode is a flat ENIG pad on the +y face, wired by a copper trace to the strip's contact pad, so there is no foil, tape or wire on the arm; the flag's finger has copper on both faces under black mask, which is opaque to IR. 1.2 mm keeps five boards at about 135 g | about $35-60 for five incl. ENIG [estimate; verify on the quote page]; zero hand time |
| **Strip clamp plates** (three: lower, upper -y, upper +y with the ground pad and a wire tab) | FR4 boards, 1.2 mm; two designs (`clamp_plate`, `clamp_ground`), 5 pcs each | FR4 faces carry the preload; the ground plate's ENIG pad touches the strip and a trace leads to a 1.6 mm plated hole in a tab (the ground wire is threaded through it; no soldering and no current, so a pressed contact is enough) | about $2 + finish per design [estimate] |
| **Fixed calibration electrode** (24 x 34 mm board) | FR4 board, ENIG, 5 pcs | The plates are the force reference: a flat ENIG pad of defined area (20 x 8 mm) inside a grounded ENIG guard beats foil tape on printed plastic (flatness, edges, oxide, patch potentials). The pad is wired through a via to the back face and a 1.6 mm plated hole | about $2 + ENIG [estimate] |
| **Device card** (16 x 24 mm) | part of the electronics order later (a small FR4 board with the resistor) | FR4 on 4.8 mm air spacers, a thermal break; 2 g assumed in the model | with the main order |
| **Gantry, torsion head, base, sensor bracket, damper holder, electrode bracket, enclosure posts, lid shelves, vane holder, jigs** | **PLA, printed on the K1** | Fixed parts. The thermal path through the printed frame to the sensor adds 0.63 nN/sqrt(Hz) at 1 mK/sqrt(Hz) of temperature noise, against the air term's 4.8 (under 1% in quadrature); the lock-in at 0.05 Hz rejects slow drift. The strip's clamping loop is not printed (above). The vane holder moves, but carries only 1 g | filament; about 12 hours of print time [estimate] |
| **Enclosure panels** | stock acrylic from AliExpress, 2 mm, 150 x 250 mm, 7 sheets | Used uncut; cheaper than any fab route | in the AliExpress order |
| **Strip** | cut by hand from the ordered 0.05 mm sheet with the printed guide | The stiffness is calibrated from the measured period, so +-0.2 mm of width doesn't matter. Edge quality sets anelastic loss (drift): A5 measures the quality factor. Fallback if it is poor: a photo-etched strip (stress-free edges) from a metal-etching service [find one]; JLC's laser-cut stainless stencils are probably 0.08 mm or thicker [verify], which would need a narrower strip for the same stiffness | the sheet is already ordered |
| **Ballast** | one saw cut from the ordered 10 x 100 mm brass rod, with the printed guide | The balance is trimmed on the bench anyway (+-0.5 mm of length is 0.6 mm of centre-of-mass shift, trimmed with spare copper pads). A JLCCNC brass part would cost more than a junior hacksaw ($5-8 on AliExpress) | 5 minutes |
| **Vane** | the ordered 20 x 20 x 0.3 mm copper pad, uncut | already right | ordered |
| **JLC3DP / JLCCNC parts** | none | Nothing left on PLA needs a non-PLA print or a machined part. Revisit if a printed part fails a creep, stress or tolerance check (the damper cradle lips, the head's lever tab); then JLC3DP's SLA or MJF nylon is the first choice since the user can't print those at home | |

## Arm length, thickness and the panel

- **Arm length.** Resolution against arm half-length with inertia scaled: 0.108 nN at 100 mm, 0.109 at 75 mm, 0.112 at 50 mm; the budget is
  air-current dominated and not sensitive to it. But a shorter arm is not a one-number change: at a 75 mm half-length the layout still builds (the electrode and vane
  positions keep their footprints apart), but the damper weakens to a damping ratio of 0.10 per pad (the vane sits closer to the axis and the inertia falls), so it would
  need four stacked pads or more magnets, and the budget's assumed 0.40 would be replaced. The 200 x 60 mm arm board is beyond JLC's cheap 100 x 100 mm tier. **Decision rule
  at the quote page:** if the 5-piece quote for the arm alone is over about $60, or the parcel is estimated over 0.29 kg, stop and put the question to the user, with these
  numbers, before changing the design. Splitting the arm into two 100 x 60 mm halves joined by a through-bolted splice was not chosen: it adds two designs, a joint in the
  torsion path, and a centre-of-mass error from the splice.
- **Thickness.** All mechanical boards are 1.2 mm. The arm's stiffness does matter: with the device card, the vane and the ballast on it, its first bending mode is about 36 Hz at 1.2 mm
  (`hardware/balance/material_study.py`, a cantilever estimate with FR4 E = 20 GPa), 29 Hz at 1.0 mm, 22 Hz at 0.8 mm, 8 Hz at 0.4 mm; building vibration lives at 5-50 Hz, so thinner
  boards put a line into the spectrum. 1.6 mm (JLC's default) gives about 54 Hz at +33% arm mass (and inertia). 1.2 mm is a menu option [confirmed: JLC lists 0.4 to 2.0 mm]; weight scales
  with thickness. The estimate for five of each design is 154 g plus about 40 g of packing [assume], under the 0.29 kg line (`tools/jlc_parcel_mass.py`).
- **One panel or four designs.** Four designs are generated (arm, plain plate, ground plate, electrode). One panel of all four would be 252 x 60 mm (two columns of small boards
  beside the arm, 2 mm apart; `arm_dxf.py` prints the layout): five panels give five of each design and ten clamp plates, 168 g by JLC's rule against 154 g. A mixed-design panel may carry a
  surcharge [unconfirmed], so the quote decides: `boards/fab/ORDER.md` ("Variant") says what to enter. The panel Gerbers (tabs, mouse bites) are built only if that quote wins.

## Material and process for the four mechanical parts (Part J; decision pending the user's quotes)

| Part | Needs | FR4 board (chosen) | Alternatives |
|---|---|---|---|
| arm | stiff, flat, light; the moving electrode, the strip contact and the flag | ENIG pads and the guard come with the board; 5 pieces; 138 g for 5 | **0.8 mm aluminium sheet** (JLCCNC sheet metal, one piece): same mass and first mode (24.8 g, 36 Hz), conductive so the arm itself is the grounded electrode (no pads, no guard), 23 ppm/K against 14; needs the electrode face and strip contact redesigned (J2 below). **Printed PLA**: 2 mm for a similar mode, but creeps and takes up moisture (zero drift), 68 ppm/K, warps over 208 mm, electrodes would be foil. HDI: no (it changes via technology, not the mass rule or the stiffness of a 2-layer arm) |
| elec_board | an exact flat pad inside a guard ring, two plated wire holes | a PCB is the right tool | none sensible |
| clamp_ground | a flat pad against the strip and a plated hole | a PCB is the right tool | a machined plate would need a wire terminal |
| clamp_plate | a rigid 16 x 14 mm plate, 2 mm holes | rides on the same order for almost nothing | JLCCNC from C$8 each plus a separate parcel: dearer |

**J2, a conductive arm:** the strip's lower clamp already grounds the arm, so the pad against the fixed electrode is just ground; an aluminium arm gives that for free and an electrostatic shield for the
rest of the arm. What changes: no ENIG pad (the bare face of the sheet is the electrode, anodizing off or masked), the strip contact is the clamp pressing on bare metal, the flag finger needs blackening for
the infrared (an anodized or painted finger), the device card must be insulated from the arm (it sits on it with two bolts: fibre washers), and the arm moves in the damper magnets' stray field, so an eddy-current
term appears (a vane-like loss in the arm itself: estimate before choosing). What is lost: pad flatness to the ENIG process, the guard-ring geometry (it lives on the fixed board, unchanged). The saving: one piece
instead of five, no 5-piece minimum. **J4, the decision rule** (the user's quote of 2026-10-28 puts an FR4 arm near C$26 with HASL and shipping before coupons, ENIG +C$25.25: the aluminium quote is now the first thing to read): keep FR4 unless the user's quotes show the aluminium arm cheaper than the arm board by more than the cost of the redesign
(a day of work, not the user's money) AND a review of the eddy-current and insulation points; the DXF for the quote is `boards/fab/arm_cnc.dxf`. Until then the order recipe in `ORDER.md` stands.

- **OSHPark** (for comparison, confirmed on its docs page): ENIG standard, 1.6 mm, free shipping worldwide, $5 per square inch for three copies. The arm would be
  about 18.6 square inches = $93, the electrode board about $6: dearer than JLC for the arm, comparable for small boards. Not used.

## Printed parts worth a JLC3DP job (Part K; a shortlist, nothing ordered)

PLA-only is the home printer's rule; JLC3DP's materials are open. A part earns a JLC job when its accuracy or stability moves a result, it is not mass-critical (a moving part's mass is trimmed on the
bench), and it is small, so a New User 3D Printing coupon (C$13.99 off over C$1.40) covers it. Solid masses are from the CAD volume (`tools/jlc_parcel_mass.py`).

| Part | Moves? | Why JLC | Solid mass (resin / nylon) | Call |
|---|---|---|---|---|
| `damper_holder` | no (fixed to the base) | its flat pockets set the discs' gap, and the damping ratio depends on that gap (0.2 mm of gap changes it visibly); SLA is accurate to about 0.1 mm and smooth | 14.0 g / 12.3 g | **yes** |
| `head` | no | holds the strip clamp and the torsion adjustment: dimensional stability and clean captured-nut pockets | 11.2 g / 9.8 g | **yes** |
| `gantry` | no | 74 cm3, the frame: nylon (MJF) is isotropic and creeps far less than home PLA, but it is the biggest part and the price is unknown | 85.3 g / 74.9 g | maybe: read the quote |
| `sensor_bracket`, `elec_bracket` | no | positions the optics and the electrode: ordinary tolerance is enough | 8.6 g / 15.6 g | no: print at home |
| `vane_holder` | **yes** (on the arm) | would be heavier solid than the 30%-infill print (1.6 g against 1.03 g, +1.3% of the arm's inertia), so trim and `params.py` change | 1.6 g | no: print at home |

Specification text for the quote form (`lab/docs/jlc/3dp_quote_ui.md`): upload the STL from `hardware/balance/cad/`; 3D Technology **SLA (Resin)** for the two small parts (accuracy), **MJF (Nylon)** only
if the gantry is quoted; Material **9600 Resin** (the page's default; "8001 Resin" and others are listed without properties, so ask nothing exotic); Color black if offered (an optical enclosure, less stray
light) else the default white; Surface Finish **No** (sanding adds cost and rounds the pockets); Thread **No** (the parts use captured nuts); Package Box **Blank Box**; Product Desc **Connectors,
Brackets, Fasteners Category**; Remark: "pockets for 6 mm diameter x 3 mm N42 discs are a light press fit: keep tolerance +-0.1 mm, do not sand the pockets". Both small parts in one order (about 25 g, one parcel) with
**New User 3D Printing 1**. The user decides after reading the quote; the second coupon (3D Printing 2, to 12-25) is for the gantry or a re-print.

## JLC orders, coupons and parcels (Part I2)

One coupon applies per checkout, and each parcel should stay under 0.29 kg by JLC's rule (bounding rectangle x thickness; `tools/jlc_parcel_mass.py`) to use the $3-4 Global Standard Direct Line tier. The
coupon ledger is `lab/docs/jlc/coupons.md`; prices on the user's account are in CAD (C$1.399 = US$1).

| # | Checkout | Coupon | Deadline | Mass | Status |
|---|---|---|---|---|---|
| 1 | mechanical boards (4 designs, `ORDER.md`) | JLCONE $8 PCB C$11.22 (min C$14.03); New User PCB C$8.42 for a second cart line if the cart allows | 11-26 / 11-25 | 194 g | ready: the user reads the quotes first |
| 2 | sensor-head PCBA panel (Part N, optional; `hardware/instrument/heads_panel/ORDER.md`) | New User SMT C$14.03 (a PCBA Special Offer of $9 expires in about 3 days: only worth it if ordered at once; the stencil coupons cannot stack) | 11-25 | 79 g of boards + packing | layout done; the user decides after the quote |
| 3 | printed parts at JLC3DP (the shortlist above) | New User 3D Printing 1 C$14.03 | 11-25 | about 25 g | needs the user's pick |
| 4 | second JLC3DP order, if more parts are worth it | New User 3D Printing 2 C$14.03 | 12-25 | | |
| 5 | JLCCNC, first checkout (aluminium arm or other part) | New User CNC C$28.06 | 11-25 | | only if the quote and J2 favour it |
| 6 | JLCCNC, second checkout | JLCONE-$20 CNC C$28.06 | 11-26 | | a second CNC part, if any |
| 7 | JLCMC fasteners (M3 304 nuts and washers) | Mechanical Parts 1 and 2, C$14.03 each | 11-25 and 12-25 | | needs the user to see the catalogue |
| - | any order that needs FDM, nylon or resin | the promotional coupons by material (minimums of $30 to $200) | 30 or 60 days | | only if a part needs that material |

Do not combine orders from different services in one parcel (3DP and CNC ship from other factories anyway). The shipping coupons (C$14.03 over C$21.04 of shipping, $10 over $40) need a
parcel that costs more than the cheap tier: they are not part of the plan. The electronics order (WP7) is not on this list: it comes after A5, and the SMT coupon will have lapsed.

## The orders

1. **JLC mechanical-board order (do first):** four designs, 5 pcs each, in one cart, Combine Shipping on (one parcel; 15 free days of storage
   [confirmed 2026-10-24]). Estimated parcel mass 154 g of boards + packing, under 0.29 kg. Order settings are in `boards/fab/ORDER.md`. Estimated total
   **$70-140 including shipping** [estimate; verify on the quote page]; ENIG can add a per-design surcharge when exposed copper passes 30% of a board's area (the
   electrode board is near it). Canada: prefer a postal tier; couriers bill brokerage on parcels over about CAD 20 [community; see kb].
2. **AliExpress (after the print list is final):** acrylic (7 sheets, 2 mm, 150 x 250 mm), 50 M3 flat washers (304), 20 M3 hex nuts (304; 10 needed), the JST-SH plate cable,
   weights, and the hand tools if not owned. Held until now because the redesign changed the fastener counts (computed in `balance.py`; the owned screws and nuts cover
   everything else).
3. **The electronics order (later, after the A5 prototype measurement):** 5 bare boards with 2 assembled (JLC assembly takes 2 of 5 [confirmed: minimum 2 pcs]; Standard rather than Economic PCBA, because two sensors are Standard-only, Part H5),
   Standard (not economic) assembly, because two sensors are Standard-only (`parts.py`, Part H5); the sensor heads on the main board's panel: Standard assembly needs boards of at least 70 x 70 mm with edge rails in the design [user's capture of the quote page, `lab/docs/jlc/pcba_quote_ui.md`] and a stencil per order, so the panel is one Standard-assembly board of the main board plus the four heads (panel by customer, rails), not separate tiny boards; the main board is likely over 70 x 70 mm by itself, so the Standard constraint costs little. Two JLC shipments in total, because the free hold can't bridge A5.
   Before placing it, run `~/.venvs/lab-hw/bin/python hardware/instrument/parts.py --live` (needs the `jlc` CLI and network): live stock, basic/extended and Economic-versus-Standard PCBA for every part.
