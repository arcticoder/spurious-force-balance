# TODO — agent, backlog

> Open items are in `docs/TODO-agent.md`; blocked ones in `docs/TODO-BLOCKED.md`.

- [ ] WP4e — human-readable schematic sheets (a PDF for review and the paper). SKiDL's `generate_schematic` is not dependable here: flat, the 169-part main board does not finish (over 15
      CPU-minutes) and the head boards route only some of the time (`retries=6`); its drawn wiring also produces false KiCad ERC errors (the netlist is right). Options: `@subcircuit`
      hierarchical sheets, or placing symbols with kiutils from the netlist. The electrical checks do not depend on it (`schematic_test.py` runs on the netlist).
- [ ] WP9 — Bring-up and experiment procedures for the user, including the calibration sequence (electrostatic plates against weights or wire riders) and the measurement campaign (durations,
      repeats, conditions logged).
- [ ] WP10 — The order: a "Next order" entry in `TODO-arcticoder.md` with the JLC upload steps and settings (the user gets the quote), plus off-board items (cables, enclosure materials,
      calibration masses) for an AliExpress cart in the same window.
- [ ] WP11 — The paper: a LaTeX skeleton (`docs/paper/`) filled as results come in: apparatus, noise model against measurement, calibration and its uncertainty, systematics, the G1 result,
      open-source availability.
- [ ] Decisions to put to the user when reached (one line each in `TODO-arcticoder.md`): the G3 go/no-go after A5; a budget ceiling for the order.
