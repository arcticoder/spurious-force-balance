# TODO — agent, backlog

> Open items are in `docs/TODO-agent.md`; blocked ones in `docs/TODO-BLOCKED.md`.

- [ ] WP4e — human-readable schematic sheets (a PDF for review and the paper). SKiDL's `generate_schematic` is not dependable here: flat, the 169-part main board does not finish (over 15
      CPU-minutes) and the head boards route only some of the time (`retries=6`); its drawn wiring also produces false KiCad ERC errors (the netlist is right). Options: `@subcircuit`
      hierarchical sheets, or placing symbols with kiutils from the netlist. The electrical checks do not depend on it (`schematic_test.py` runs on the netlist).
- [ ] Analysis of the experiment's results (after WP9 fixes the procedures): calibration of the plate force against weights or wire riders, lead-current and heating coupling coefficients with uncertainties, built on `host/analyze.py` (ASD, Allan deviation).
- [ ] WP10 — The order: a "Next order" entry in `TODO-arcticoder.md` with the JLC upload steps and settings (the user gets the quote), plus off-board items (cables, enclosure materials,
      calibration masses) for an AliExpress cart in the same window.
- [ ] Decisions to put to the user when reached (one line each in `TODO-arcticoder.md`): the G3 go/no-go after A5; a budget ceiling for the order.
- [ ] Next AliExpress order (staged; one order per day, none in the user's list until the day it is placed; whole-cart shipping must clear the free-shipping threshold, no single-item fees): a second M1 1 g calibration weight (same listing as the first, C$2.48, chosen by the user over trimming a filament piece), a craft knife and steel ruler for the filament pieces and strip cutting, a flat file only if the needle files arrive round. No acrylic: the enclosure is printed (decided 2026-11-12). Also stage for the same cart: ANSI Z87.1 safety glasses and FFP2/N95 dust masks (the user owns neither; needed for any abrasive-wheel or sanding work on brass), as separate low-cost lines so the cart clears the free-shipping threshold; no mains parts. Look for a deal and a coupon on the day, and keep a parcel always in transit (the 2026-11-10 order is the one in transit now).
- [ ] Standing duties (not tasks): watch for JLC and AliExpress deals and log coupons with expiry in `lab/docs/jlc/coupons.md`; when the user reports an arrival, inventory it with a bag in `lab/docs/inventory.md`.
