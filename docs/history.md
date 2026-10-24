I've written your points up as **Part F** at the top of [spurious-force-balance/docs/TODO-agent.md](../spurious-force-balance/docs/TODO-agent.md), for Sonnet to carry out next. Nothing else is changed or committed.

**Licenses (F1):** Sonnet will add CERN-OHL-P v2 for the hardware and MIT for the code in both repos. Each README will say which files fall under which license.

**Your compass test (F2):** it was inconclusive, not wrong.
- At 3 cm from the phone's compass sensor, the disc's field is about ten times the Earth's, so a disc magnetized across its diameter would have swung the needle all the way round.
- At around 10 cm it's weaker than the Earth's field, so a small wobble is all you'd see either way. The sensor was probably that far from where the disc sat.
- If your compass misbehaves now, the figure-of-eight recalibration fixes it; nothing is damaged.

A test that needs no phone:
- **Twist test:** stack two discs flat face to flat face and twist the top one. If it springs back to one angle, they're magnetized across the diameter. If it turns freely with no preferred angle, they're magnetized through the flat faces.
- **Nut check:** a black steel nut jumps to the centre of a flat face on the second kind, and to two opposite points on the curved side on the first.

The CAD will get a layout for both kinds of magnet, so either answer is ready.

**Order (F3):** the five items go into the order log and inventory as en route.

**Fabrication (F4).** The review turned up four problems, and only the first is separate from how parts get made:
1. **No zero adjustment.** The 1 mm plate gap allows only ±0.4° of arm rotation. A strip clamped by hand will sit further off than that, so the build needs a rotatable, lockable top clamp (a torsion head), as every torsion balance has.
2. **A heating device can't sit on PLA.** At 0.9 W the device card warms by about 75 K, and PLA softens around 55–60 °C. A PLA mount would creep in step with the device's power, which is the very effect the experiment measures.
3. **The strip clamps screw into PLA.** PLA creeps under screw pressure, and the slow rotation of the clamps would look like signal drift.
4. **Tilt.** Most of the tilt sensitivity comes from printed parts with uncertain mass.

My recommendations:
- **FR4 circuit boards from JLCPCB as structural parts.** The arm (with the flag and moving plate built in), the strip clamp plates, the fixed plate (gold-faced, with a guard ring) and the device mount become unassembled boards. That fixes problems 2 to 4 with no printing or cutting on your part, and puts a copper ground path in place of the foil tape.
- **Everything fixed stays PLA on your K1.** At the 0.05 Hz measurement frequency its slow thermal movement contributes almost nothing to the force noise.
- **No JLC3DP or JLCCNC parts for now.** No part left on PLA needs a different plastic or machining. They're the fallback if a PLA part fails a creep or stress check.
- **The ballast is decided after the arm redesign.** In order of preference: a standard brass part used as is, then one saw cut from the rod you ordered, then a machined brass part only if a JLC order is happening anyway.
- **The strip stays hand-cut.** Its stiffness gets calibrated from the measured period anyway; a photo-etched strip is the fallback if the prototype measures poor quality or drift.

**Decisions for you:**
- **Two JLC orders.** I recommend a small order for the structural boards now, and the electronics order after the prototype measurement as before. The prototype should measure the mechanics the experiment will actually use. That adds one extra JLC shipment; Sonnet will estimate the cost and you'll confirm it on the quote page.
- **Hold the rest of your AliExpress list.** The washers, nuts, cable, weights and tools wait until the redesign settles the screw counts. Then it's one order with no small-item fees.
- **Hold all printing until the redesign lands.** The fixed parts move with the new arm.
<!-- ------ -->
---