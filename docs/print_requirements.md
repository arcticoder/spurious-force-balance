# Print requirements for the balance's PLA parts

Written to hand to an outside model that proposes the remaining slicer parameters. It states what the parts must do, what is already loaded, and what is wrong in the loaded project. It does not prescribe values; the proposal should give a value and a one-line reason for each item in section 4.

## 1. What is being printed

A torsion balance for micro-newton force measurements: a 0.05 mm stainless strip holds an FR4 arm, and an optical sensor and a fixed electrode sit around it. The printed parts hold everything still, so the requirements are stiffness, no creep, no warp and accurate holes, not looks or speed.

- Printer: Creality K1, 0.4 mm nozzle, build volume 220 x 220 x 250 mm, enclosed. Slicer: OrcaSlicer 2.4.2. Material: PLA only (Creality Generic PLA High Speed). Plate: textured PEI. Single colour, one extruder.
- Project: `hardware/balance/cad/balance.3mf` (5 plates, one profile for all objects, no per-object overrides). STLs: `hardware/balance/cad/*.stl`.
- Loaded profile (the K1 stock "0.20mm Standard"): layer 0.2 mm, 2 walls, 5 top and 3 bottom layers, 15% grid infill, no supports, auto brim 5 mm, prime tower on, nozzle 220 C, bed 55 C, outer wall 200 mm/s, acceleration 10000, elephant-foot compensation 0.15 mm, XY contour and hole compensation 0, seam aligned, arc fitting on.
- `docs/assembly.md` asks for 3 walls, about 30% infill, 0.2 mm layers; the loaded project does not match it.

## 2. Parts and what matters for each

| Part (plate) | Size (mm, as oriented in the project) | What matters |
|---|---|---|
| `base` (1) | 218 x 218 x 6 | the flat reference everything stands on: flat within about 0.3 mm over its length, no corner lift; 218 mm on a 220 mm bed, so no 5 mm brim fits; M3 holes with nuts captured in the underside |
| `gantry` (2) | 105 x 135 x 50 (on its side) | carries the strip's torsion head; stiff, no creep; round bore for the `head` disc; M3 holes and captured hex nuts; biggest overhang area (about 4800 mm2) |
| `head` (2) | 41 x 30 x 28 | turns in the gantry bore: bore and disc must have a smooth, round fit (no seam bump on the bearing surface) |
| `sensor_bracket` (2) | 56 x 57.5 x 10 | holds the optical sensor; M3 holes |
| `damper_holder` (3) | 56 x 37.5 x 16 | round pockets for four N42 magnet discs (press fit, sizes in `params.py`), M3 holes; magnet pocket diameter accuracy matters |
| `elec_bracket` (3) | 56 x 19 x 28 | holds the fixed electrode board; M3 holes with captured nuts |
| `vane_holder` (3) | 12 x 12 x 12 | the only moving printed part, about 0.6 g in the CAD: keep walls thin enough that its mass does not grow; its sliced mass goes into `params.py` (`PRINTED_MASS_G`) |
| `encl_post_*` (4), `encl_shelf_*` (3) | posts 20 x 150 mm, shelves 6 x 114 x 6 | enclosure frame holding 2 mm acrylic sheets; stiff and straight (a bowed post tilts the walls) |
| `fixture_saw_guide_base/plate` (5) | 31 x 30 x 24, 28 x 30 x 4 | clamp a 10 mm brass rod for hacksaw cuts: the rod groove must grip the rod without slop; kerf slot 1.4 mm; the walls take sawing load |
| `fixture_strip_guide` (5) | 110 x 36 x 5.5 | a 0.8 mm knife slot exactly 4.00 mm from a ridge: slot width and position accuracy matter more than anything else on this part |
| `fixture_gap_gauge` (5) | 30 x 45 x 1 | a 1 mm thick feeler gauge: thickness within 0.05 mm |

Fasteners (from the CAD): M3 clearance holes 3.4 mm, pilot 2.6 mm, screw head recess 6.2 mm, hex nut pockets 6.35 mm across corners (5.5 mm across flats) and 2.6 mm deep; nuts are captured, so each nut pocket must print cleanly and hold the nut without a gap that lets it turn. Sawing and clamping loads are modest; fatigue is not a concern.

## 3. Orientation and project faults to fix first

An analysis of the loaded project (parts transformed as placed) found:

1. `gantry`, `encl_post_np` and `encl_post_pp` are tilted slightly off the bed (the gantry's footprint is 105.5 x 135.3 mm and 50.5 mm high against the CAD's 102 x 132 x 50). Re-lay them flat with the "place on face" tool.
2. `fixture_strip_guide` is placed ridge-down: 3660 mm2 of its plate hangs 0.5 mm above the bed. Flip it so the plate's flat face is on the bed and the 0.5 mm ridge faces up.
3. `base` fills the bed (218 x 218 on 220 x 220): the auto brim does not fit; use no brim or a skirt, and check the K1's usable area.
4. The prime tower is on for a single-colour print; turn it off.
5. Overhang areas over 45 degrees as oriented: gantry about 4800 mm2, `encl_post_np` 4290, the other posts 1290 each, `damper_holder` 188, the rest under 100 mm2.

## 4. What to propose (one value and a reason each)

1. Walls, infill density and pattern, and top and bottom layers for the frame parts (`base`, `gantry`, `head`, brackets, posts, shelves), for stiffness and low creep.
2. A different, thinner setting for `vane_holder` (low mass) and a stronger one for the saw-guide fixtures.
3. Supports: for which parts (gantry, posts, `damper_holder`), what type and angle, and how to keep them out of M3 holes, nut pockets and the magnet pockets; or an orientation that avoids them.
4. Hole and pocket compensation (XY contour and hole compensation, elephant-foot compensation) and the test print that finds it: M3 3.4 mm, the hex nut pocket, the 10 mm rod groove, the magnet pockets, the 0.8 mm slot.
5. Warp control for `base` and the long posts: bed temperature, brim or skirt choice, cooling, enclosure door, first-layer settings.
6. Speed and acceleration for the outer walls on the precision parts (the stock 200 mm/s and 10000 mm/s2 may cost accuracy), and layer height for the strip guide and gap gauge.
7. Seam position so the `head` disc and gantry bore have no bump on their bearing surfaces.
8. Bridging settings for the nut pockets if they print as bridges.
9. Plate grouping: whether the five plates are sensible as loaded (plate 3 holds seven objects), with an estimate of print time and filament per plate.

## 5. What comes back to this repo

- The settings as a list or a saved Orca profile, placed with the 3mf.
- The sliced mass of `vane_holder` in grams, for `params.py`.
- The result of the hole test print, with the compensation chosen.

## 6. Settings applied to `balance.3mf` (2026-11-06)

The user fixed the orientations and set `base` to no brim, the prime tower off, 3 walls and 30% sparse infill (global). The agent then set the rest in the file (the file as the user left it is backed up in the session scratchpad at /tmp/claude-1000/-home-echo--Code-python-pico/29f38dbc-9739-4248-b311-8203f0d31010/scratchpad/balance.3mf.bak). Printer: Creality K1, 0.4 mm brass nozzle, Hyper PLA, textured PEI; the print is made on a balcony in cool weather.

| Item | Value | Reason |
|---|---|---|
| Bed, first layer / rest | 65 / 60 C | cool ambient air; bonding of the 218 mm base and long posts |
| Nozzle, first layer / rest | 225 / 220 C | the extra 5 C helps the first layer's bond |
| First-layer speed, infill speed, acceleration | 30, 45 mm/s, 500 mm/s2 | slow first layer for bonding; wide first-layer line stays 0.5 mm |
| Fan off for first layers | 3 | bonding in cold air |
| Supports | tree (auto), 45 degrees, build plate only | the gantry, posts and `damper_holder` overhangs; nothing rests on a part, so nothing is left inside a pocket (nut pockets bridge) |
| Hole compensation | +0.1 mm | starting value only: PLA holes print small; confirm with a test print before the real parts |
| Outer wall / inner wall speed | 120 / 200 mm/s | accuracy over the stock 200 / 300 |
| Outer wall / default acceleration | 3000 / 6000 mm/s2 | less ringing, better holes |
| `vane_holder` | 2 walls, 10% infill | keeps the moving mass near the CAD's 0.6 g |
| saw guide base and plate | 4 walls, 40% infill | sawing load |
| `fixture_strip_guide` | 0.1 mm layers | the 0.5 mm ridge under a 5 mm plate is 2.5 layers at 0.2 mm; 0.1 mm layers give 0.2 + 53 x 0.1 = 5.5 mm |
| Seam, elephant-foot compensation | aligned, 0.15 mm (unchanged) | not changed without a test print |

Not done, because they need a print: the hole compensation check, the bearing-surface check on `head`, and the sliced mass of `vane_holder` for `params.py`. Close the K1's lid for these prints. Open the file in Orca once and reslice before printing; the agent could not run the slicer.
