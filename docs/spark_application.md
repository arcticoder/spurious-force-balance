# EasyEDA Spark 2026: registration answers

Text for the registration form at oshwlab.com/activities/easyeda-spark-2026 (maximum 3000 characters per box). The cost bracket should be re-checked against the final parts list once the boards are quoted.

## Cost of the DIY work

Keep the **$200-$500** bracket: the JLC boards are tens of dollars, the PLA and stock parts are small, and the assembled electronics board and the optical and lock-in parts are what bring the total up. A lower bracket would only fit if the electronics board is left out.

## Project idea

An open, low-cost torsion balance that measures the spurious forces that dominate small-force and small-thrust experiments. Papers that claim a tiny thrust from a powered device rarely separate it from the Lorentz force of the supply leads in the ambient magnetic field, heating, and convection in air. This project builds the instrument that can: it quantifies each of those effects as a function of current, lead geometry and dissipated power, so a claimed thrust can be compared with what the artifacts alone produce.

The balance hangs a 208 mm FR4 arm board, on edge, from a torsion head. The arm is a JLCPCB board that carries the electrode and device pads, so the experiment's wiring is part of the arm. The clamps, the fixed electrode and the sensor-head boards are further fabricated boards; the frame, torsion head, eddy-current damper holder and fixtures are PLA parts printed at home and designed in CadQuery; the enclosure is stock-size acrylic. Nothing needs hand soldering: the electronics are JLCPCB-assembled RP2040 boards (ADS131A04 converter, MCP4728 DAC, TMP117, MMC5983MA and LIS2DW12 sensors), designed with KiCad 9 and SKiDL, simulated in ngspice, with MicroPython firmware tested on the host.

The design target is a force noise of about 0.1 nN over a 1000 s measurement in air (a 5-sigma resolution of 0.4 nN or better), predicted by an open force-noise model that reproduces six published numbers. The model says air currents dominate, so the acrylic enclosure is the main noise control. The repository contains the model, every board's design files and DRC results, a bring-up procedure, an experiment procedure and a paper skeleton, so another maker can build it, check it and reuse the parts.

It is open hardware (CERN-OHL-P v2 for the hardware, MIT for the code) and is being moved into EasyEDA Pro for OSHWLab.

## Services needed besides PCB prototyping

- PCB assembly (SMT) for the RP2040 instrument board and the four sensor-head boards, using only machine-placed parts from JLC's library, so no hand soldering is needed.
- 3D printing for precision parts that must hold tolerance (the torsion head and damper holder, if the home-printed versions are not good enough).
- CNC machining for a fallback metal arm and clamps, if the FR4 arm's stiffness or flatness falls short.
- JLCMC fasteners: M3 stainless nuts and washers for the clamp stack.
- Shipping consolidated into parcels under JLC's 0.3 kg cheap-shipping tier, since the boards are small and light.
