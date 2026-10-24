# JLCPCB mechanical-board order — settings (2026-10-24)

Four designs, unassembled (no components, no stencil), one cart, Combine Shipping on. Upload each `*_gerbers.zip`. Settings common to all:
2 layers, FR4, quantity 5, 1.2 mm thickness, lead-free solid color: **black solder mask**, white silkscreen, remove-order-number: specify a
location (the silkscreen text is on the back face; or choose "remove" if offered at no charge), no castellated holes, no edge plating.
Read the quote page's weight estimate before paying; it should stay under 0.29 kg for the parcel. Estimated board mass: about 154 g for all
twenty boards [assume FR4 at 1.85 g/cm^3, bounding rectangle x thickness].

| Design | File | Size (mm) | Finish | Why |
|---|---|---|---|---|
| arm | `arm_gerbers.zip` | 208 x 60 (200 plus the finger) | ENIG | flat gold pad for the strip contact and the moving electrode |
| clamp_ground | `clamp_ground_gerbers.zip` | 17 x 19 | ENIG | the pad that touches the strip, and the plated wire hole |
| elec_board | `elec_board_gerbers.zip` | 24 x 34 | ENIG | the fixed electrode and its guard, one flat gold surface |
| clamp_plate | `clamp_plate_gerbers.zip` | 16 x 14 | any (HASL is cheapest; it has no copper) | plain plate, two needed per balance (the lower plate and the upper -y plate) |

Per balance: 1 arm, 2 clamp_plate, 1 clamp_ground, 1 elec_board. Five of each arrive; the rest are spares.

Checks done before this file was written (`kicad-cli pcb drc`, KiCad 9.0.9): no errors; the only warnings are that the generated hole footprints have no
library entry. JLC's published limits [confirmed on jlcpcb.com/capabilities 2026-10-24]: minimum non-plated hole 0.5 mm (smallest here 3.4 mm), minimum plated hole 0.15 mm
(smallest here 0.4 mm via, 1.6 mm wire hole), copper to routed edge 0.2 mm (smallest here 0.5 mm), outline tolerance +-0.2 mm for ordinary routing, thickness
tolerance +-10% at 1.0 mm and up.

If the arm's quote is over about $60 or the parcel is over 0.29 kg, stop and ask: a shorter arm needs a damper rework (see `docs/fabrication.md`), so it is not a quick switch.
