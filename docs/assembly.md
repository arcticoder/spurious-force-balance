# Building the balance

Steps for the first (A5) prototype, in order. Numbers come from `hardware/balance/` (`python balance.py` prints
the ones that depend on your prints). Screws, nuts and washers are listed by what the CAD's holes take: 18 × M3×12
and 1 × M3×10 pan head screws, 15 hex nuts, 19 M3 washers (the lower clamp's two nuts on the moving arm are the 304
stainless ones; every other nut is the black carbon steel). The saw guide takes four more M3×14 screws, threaded into its pilot holes.

## 1. Slice first, print second

1. Slice every printed part that sits on the moving arm (`arm`, `low_clamp_a`, `low_clamp_b`, `vane_holder`, `flag`,
   `elec_arm`) without printing, and write down the slicer's mass for each, in grams.
2. Put them in `PRINTED_MASS_G` in `hardware/balance/params.py` (`{"arm": 22.9, ...}`), then run
   `~/.venvs/lab-hw/bin/python hardware/balance/balance.py` and `.../fixtures.py`. A real print differs from the CAD's
   density estimate by up to 15%, which would move the centre of mass by about 1 mm; the slicer's figure brings that to a few
   percent. The run prints the ballast's length and the arm's ballast-hole offset; the updated `arm.stl` carries the offset.
3. Print everything in `hardware/balance/cad/` that is a printed part (the list is in `TODO-arcticoder.md`), including the two
   jigs `fixture_saw_guide_*` and `fixture_strip_guide`. PLA, 3 walls, about 30% infill, 0.2 mm layers.

## 2. Cut the materials

**Strip (4 mm × 42 mm from the 0.05 mm sheet).** Lay the sheet on a flat board, butt a straight (factory) edge against the
ridge under `fixture_strip_guide`, hold the guide down with your free hand, and run a sharp craft-knife blade down the slot
with its side against the slot's far wall. Make three or four light passes. The cut lands 4.00 mm from the ridge. Then cut across
at 42 mm with the knife and a steel rule. Run a fine file lightly along both long edges (kinked or burred edges add friction in the
strip), and handle it by the ends: a crease ruins it. Cut two strips; the second is a spare.

**Ballast (brass, 10 mm rod).** Put the rod in the saw guide's groove with its end against the stop, close the plate with four
M3×14 screws, and saw down the slot with a junior hacksaw until the piece drops free: its length is the ballast length plus 0.5 mm.
File the sawn face flat until the piece is the length `balance.py` printed (18.3 mm with the CAD's masses), then check it fits the
arm's ballast hole (10.3 mm).

**Vane.** One 20 × 20 × 0.3 mm copper pad lies in the slot of `vane_holder` (a second pad on top is the stronger-damping option).
A 3 × 6 mm piece of foam tape on its inner end holds it flat. The holder fixes to the arm's +y side with a strip of foam tape.

## 3. The damper

The four N42 discs stand on edge in the two cradles above and the two below the vane's slot, axes along x, and slide in from the
+x end of each bore. Each disc turns freely in its bore until it settles with its upper or lower partner (the pair attract; the
N–S line ends up vertical, which is what the field through the vane needs). Cap each bore with a piece of foam tape. Whether the
two columns end up with the same or opposite polarity changes the damping by about 6%, so you needn't check. Keep steel tools
(tweezers, screwdrivers) away from loose discs.

## 4. Hang the arm

1. Fix `gantry`, `damper_holder`, `sensor_bracket` and `elec_fixed` to the base with M3×12 screws from below into the nuts captured in
   each foot's flange (a washer under each screw head).
2. Put the strip between `top_clamp_a` and `top_clamp_b` and bolt them with two M3×12 screws (nuts in half b); screw half a up into
   the gantry's beam. Check that the strip hangs vertically.
3. Lower the arm so the strip enters the lower clamp pair (`low_clamp_a`, `low_clamp_b`, nuts in half b: **304 stainless nuts here**) and
   bolt it, with the arm hanging by the strip alone. Do not let go of the arm until both clamp screws are tight.

## 5. The plates and their wiring (no solder)

1. **Moving plate.** Cut a 4 mm wide strip of copper foil tape (10 mm tape, lengthwise) about 130 mm long. Stick it on the +y face of
   `elec_arm` (faces the fixed plate), wrap it around the tab's −x edge, run it along the arm's +y side face low (z 58–60 mm, under the
   vane holder), over the hub's +x face, along the hub's +y face, up it to the hub's top, and up the outer face of `low_clamp_b` to
   its top edge. Press the last 5 mm into the gap between `low_clamp_b` and the strip; the clamp screws squeeze it against the strip.
   It adds about 0.3 g to the arm; the CAD includes it.
2. **Strip ground.** Another 4 mm foil strip goes between `top_clamp_a` and the strip (during step 4.2), wraps around the clamp's +x end
   and lies under the washer of the clamp screw at x = +7 on half a's outer face. The ground wire's stripped end goes under the same washer.
3. **Fixed plate.** A foil strip covers the −y face of `elec_fixed` (faces the arm's plate), wraps over its top, runs down the +y back
   face to the flange, and goes under the washer of the terminal screw (M3×10) at the flange's +y end, together with the plate wire's
   stripped end.
4. The plate driver's output cable is a JST-SH 1.0 mm 2-pin cable with flying leads: one lead to the fixed plate's terminal, the other to the
   strip ground. Route both leads down the gantry's leg to the base and tie them to the base, so they exert no torque on the arm.
5. Both plate faces need clean copper; no joint relies on the tape's adhesive conducting, since each is held by a clamp or a washer.

## 6. Balance (the trim) and level

The arm hangs 15 mm below the strip's lower end, so a centre-of-mass offset of 1 mm tilts it by about 66 mrad, and the vane and the flag
clearances allow about 16 mrad: this step is required, not a refinement. Aim for under 5 mrad.

1. Remove all drafts (enclosure panels in place, lid off), and put the base on the table, levelled with a bubble level on the base (shim the
   base's corners with folded card if the table is not flat).
2. Look at the arm from the side, along y at table height. The flag's tab must sit centred between the sensor bracket's two prongs (3.0 mm
   clear below it and 2.4 mm above, so a tab that touches or nearly touches either prong means the arm is off by over 10 mrad), and the vane must sit
   centred between the cradles' discs (at least 1.0 mm clear above and below; the discs' edges are visible through the cradle windows).
3. If the +x end is low, cut a small piece of a spare 20 × 20 copper pad (or a square of foil tape, 0.04 g per cm²) and tape it into the −x trim
   seat on the arm's top face (the seat at the high end), and the reverse if the −x end is low. Each 0.05 g at the seat moves the centre of mass by about 0.08 mm; two stacked
   pad pieces cover about 1 mm. Repeat until the flag and vane are centred. A lean across the arm (one side low) should be small, since the printed parts are
   symmetric in y and the CAD solves the ballast hole's y offset; if it is not, slide the ballast sideways within its hole (10.3 mm for a 10 mm rod) and look again.
4. Write the final trim down (what was added, and where) in the test log; the A5 noise measurement uses the balance as it is.

## 7. The enclosure

1. Press a strip of the foam tape (3 mm wide, 0.3 mm thick) onto both faces of each acrylic wall sheet's two ends (the part that sits in a post's slot),
   150 mm long. Stand the four posts at the corners (they locate on the table; nothing fixes them) and slide the four 250 mm walls in, one
   end in each slot, pinwheel fashion: each wall has one end in the corner square and one flush with the next wall.
2. Tape the four lid shelves (`encl_shelf_*`) to the inside of the two walls that run along y, 6 mm shelf toward the middle, top flush with the wall top.
3. Foam tape along the wall tops; lay the two lid sheets on, meeting at the middle, and tape the seam from above. Lift the lid only to adjust the balance.
