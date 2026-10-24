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
- **Thickness.** All mechanical boards are 1.2 mm: the arm's stiffness is not the limit (above), 1.2 mm is a menu option [confirmed: JLC lists 0.4 to 2.0 mm],
  and weight scales with thickness. The estimate for five of each design is 154 g plus about 40 g of packing [assume], under the 0.29 kg line.
- **One panel or four designs.** Four designs are generated (arm, plain plate, ground plate, electrode). The small three would fit one 60 x 50 mm panel, but a
  mixed-design panel may carry a surcharge [ask JLC support; unconfirmed], and the small boards cost little each. Order them as separate designs unless the quote
  shows the panel cheaper; the Gerbers are ready for either (JLC can also panelize them, "Pls help me make the panel").
- **OSHPark** (for comparison, confirmed on its docs page): ENIG standard, 1.6 mm, free shipping worldwide, $5 per square inch for three copies. The arm would be
  about 18.6 square inches = $93, the electrode board about $6: dearer than JLC for the arm, comparable for small boards. Not used.

## The orders

1. **JLC mechanical-board order (do first):** four designs, 5 pcs each, in one cart, Combine Shipping on (one parcel; 15 free days of storage
   [confirmed 2026-10-24]). Estimated parcel mass 154 g of boards + packing, under 0.29 kg. Order settings are in `boards/fab/ORDER.md`. Estimated total
   **$70-140 including shipping** [estimate; verify on the quote page]; ENIG can add a per-design surcharge when exposed copper passes 30% of a board's area (the
   electrode board is near it). Canada: prefer a postal tier; couriers bill brokerage on parcels over about CAD 20 [community; see kb].
2. **AliExpress (after the print list is final):** acrylic (7 sheets, 2 mm, 150 x 250 mm), 50 M3 flat washers (304), 20 M3 hex nuts (304; 10 needed), the JST-SH plate cable,
   weights, and the hand tools if not owned. Held until now because the redesign changed the fastener counts (computed in `balance.py`; the owned screws and nuts cover
   everything else).
3. **The electronics order (later, after the A5 prototype measurement):** 5 bare boards with 2 assembled (economic PCBA allows 2 of 5 [confirmed: minimum 2 pcs]),
   the sensor heads panelized together, no stencil. Two JLC shipments in total, because the free hold can't bridge A5.
