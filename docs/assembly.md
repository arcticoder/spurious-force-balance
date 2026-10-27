# Building the balance

Steps for the first (A5) prototype, in order. The arm, the clamp plates and the fixed electrode are FR4 boards from JLCPCB
([fabrication.md](fabrication.md), [boards/fab/ORDER.md](../hardware/balance/boards/fab/ORDER.md)); everything fixed is printed in PLA. Numbers come from
`hardware/balance/` (`python balance.py` prints the ones that depend on the design). Fasteners, from the holes in the CAD: 8 × M3×12, 8 × M3×14 and 4 × M3×10 pan head
screws; 14 carbon-steel M3 nuts and 10 stainless (304) ones (the stainless ones are on the moving arm); 20 washers. The saw guide takes four more M3×14.

Terms: the arm board stands on edge. Its **+y face** has the strip contact and the moving electrode (the faces of the board are marked on the silkscreen); its **−y face** carries the device card.

## 1. Print

All of these from `hardware/balance/cad/`, PLA, 3 walls, about 30% infill, 0.2 mm layers: `base`, `gantry`, `head`, `sensor_bracket`, `damper_holder`, `elec_bracket`,
`vane_holder`, the four `encl_post_*`, the four `encl_shelf_*`, and the jigs `fixture_saw_guide_base`, `fixture_saw_guide_plate`, `fixture_strip_guide`, `fixture_gap_gauge`.
Largest part: the gantry, 132 × 102 × 50 mm. Lay the gantry on its side. The only moving printed part is `vane_holder` (about 0.6 g); no other printed part is in the
strip's clamping loop, so print variations don't shift the balance.

## 2. Cut the materials

**Strip (4 mm × 58 mm from the 0.05 mm sheet).** Lay the sheet on a flat board, butt a straight (factory) edge against the ridge under `fixture_strip_guide`, hold the guide
down with your free hand, and run a sharp craft-knife blade down the slot with its side against the slot's far wall. Make three or four light passes. The cut lands 4.00 mm
from the ridge. Then cut across at 58 mm with the knife and a steel rule. Run a fine file lightly along both long edges (kinked or burred edges add friction in the strip), and
handle it by the ends: a crease ruins it. Cut two strips; the second is a spare.

**Ballast (brass, 10 mm rod).** Put the rod in the saw guide's groove with its end against the stop, close the plate with four M3×14 screws, and saw down the slot with a
junior hacksaw until the piece drops free: its length is the ballast length plus 0.5 mm. File the sawn face flat until the piece is the length `balance.py` printed (15.1 mm
with the CAD's numbers); it must pass through the arm board's 10.2 mm hole.

**Vane.** The 20 × 20 × 0.3 mm copper pad is used uncut: it lies in the vane holder's slot (a second pad on top doubles the damping); a 3 × 6 mm piece of foam tape on its
inner end holds it flat.

## 3. The damper

The four N42 discs go flat in the round pockets, two above and two below the vane's slot (the twist test of 2026-10-26 showed they are magnetized through the flat faces: `MAGNET_MAGNETIZATION = "axial"`).
Press each disc into its pocket from the open face with its flat face toward the vane, and cap it with foam tape. Keep steel tools away from loose discs. (If another batch of discs turns out to be
magnetized across the diameter, set `MAGNET_MAGNETIZATION = "diametric"` and rerun `balance.py` for the on-edge cradles.)

## 4. Frame

1. Bolt `gantry` (4 screws), `sensor_bracket` (2) and `damper_holder` (2) to the base with M3×12 screws from below into the nuts captured in each foot's flange (a washer under each head).
2. Lay the `head` disc into the gantry's bore (its carrier block goes down through the ledge hole, its lever tab into the pocket on the +x side). Fit an M3×14 screw with a washer
   into each side of the gantry's +x extension, threaded through the nut captured there, and wind both until their tips just touch the tab. Zero is where the two screws hold the tab midway.
3. Leave `elec_bracket` off for now.

## 5. Hang the strip and the arm

1. **Upper clamp.** Lay a clamp plate (`clamp_plate`, either) and the ground plate (`clamp_ground`) on the strip's two faces with the ground plate on the +y side, its copper pad against the
   strip and its tab down. Thread one end of the ground wire (stripped 5 mm) through the tab's plated hole and bend it flat. Bolt the stack with two M3×10 screws (head and washer on the +y
   side, a carbon-steel nut on the −y side). The strip's top end should sit 14 mm up inside the stack. Slide the stack up into the head's slot from below so the bolt tips enter the −y wall's holes.
2. **Lower clamp.** Support the arm board level on two blocks at the height of the sensor bracket's window. Lay the strip's lower end on the arm board's +y face over the copper strip pad
   (the last 14 mm), cover it with the other `clamp_plate`, and bolt it with two M3×10 screws, head and washer on the plate's +y side, a **stainless** nut on the board's −y face. Remove the
   blocks slowly; the arm hangs by the strip alone.
3. The strip must hang straight with the free length between the two clamps (30 mm). Check it from two sides.

## 6. Everything else that moves

1. **Ballast.** Pass the rod through the arm board's hole at −90 mm, centred about 1 mm toward +y (its position along y levels the arm: `balance.py` prints the starting value).
2. **Vane holder.** Bolt the holder to the +y face at 55 mm with two M3×14 screws from the −y side through the board (head and washer on the −y face), nuts captured in the holder's +y face (stainless).
   Slip the copper pad into the slot.
3. **Device card.** Stack two stainless nuts on each of the two bolts through the arm board's −y face at the +x end, the card on those, a washer and a head outside; another
   stainless nut on the +y side. The card's resistor, leads and header go on before the trim.

## 7. Trim and zero (required)

The arm hangs 32 mm below the strip's lower end, so every millimetre of centre-of-mass offset tilts it by 31 mrad, and the vane and the flag clearances allow about 20 mrad. Aim for under 6 mrad.

1. Remove drafts (enclosure panels in place, lid off). Put the base on a table, levelled with a bubble level on the base (shim the base's corners with folded card if the table is not flat).
2. Look at the arm from the side, along y, at table height. The flag finger must sit centred between the sensor bracket's two prongs (3.0 mm clear each side), and the vane must sit
   centred between the cradles' discs (the discs' edges are visible through the cradle windows; at least 1.0 mm above and below). If the +x end is low, tape a piece of a spare 20 × 20 copper pad
   (1.1 g; foil tape is 0.04 g per cm²) to the board's face near −x (the board's faces are flat and need no seat); the reverse if the −x end is low. Each pad piece moves the centre of
   mass about 1.9 mm at the arm's end. If the arm leans across (one side low), slide the ballast rod along y within its hole.
3. Zero with the torsion head: with the arm trimmed level, turn the two adjusting screws (a tenth of a turn is 0.1 degree at the arm's flag) until the finger sits mid-window along the swing direction.
4. Write the final trim (what was added, and where) in the test log; the A5 noise measurement uses the balance as it is.

## 8. The calibration electrodes (after zeroing)

1. Stick the fixed `elec_board` into the bracket's pocket with a strip of foam tape on its back face, pad forward (the −y face), the two wire holes up.
2. Set the bracket on the base with its feet over the slack holes (the screws come from above through 6.6 mm holes into nuts captured in the base's underside, with a washer under each head),
   leaving the screws loose. Slide the `fixture_gap_gauge` between the two electrodes, press the bracket until the gauge is held lightly, and tighten. Pull the gauge out.
3. The plate driver's cable (JST-SH, flying leads): the signal lead through the wire hole marked SIG; the ground lead to the guard hole (GUARD), with a short second wire from it to the upper clamp's
   ground wire (threaded through the ground plate's tab hole). Route both leads down the gantry leg to the base and tie them there, so they exert no torque on the arm.

## 9. The enclosure

1. Press a strip of the foam tape (3 mm wide, 0.3 mm thick) onto both faces of each acrylic wall sheet's two ends (the part that sits in a post's slot), 150 mm long. Stand the four posts at the corners
   (they locate on the table; nothing fixes them) and slide the four 250 mm walls in, one end in each slot, pinwheel fashion: each wall has one end in the corner square and one flush with the next wall.
2. Tape the four lid shelves (`encl_shelf_*`) to the inside of the two walls that run along y, the 6 mm shelf toward the middle, top flush with the wall top.
3. Foam tape along the wall tops; lay the two lid sheets on, meeting at the middle, and tape the seam from above. Lift the lid only to adjust the balance.
