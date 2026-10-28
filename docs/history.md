I've written your points up as **Part F** at the top of [spurious-force-balance/docs/TODO-agent.md](../spurious-force-balance/docs/TODO-agent.md), for Sonnet to carry out next. Nothing else is changed or committed.

**Licenses (F1):** Sonnet will add CERN-OHL-P v2 for the hardware and MIT for the code in both repos. Each README will say which files fall under which license.

**Your compass test (F2):** it was inconclusive, not wrong.
- At 3 cm from the phone's compass sensor, the disc's field is about ten times the Earth's, so a disc magnetized across its diameter would have swung the needle all the way round.
- At around 10 cm it's weaker than the Earth's field, so a small wobble is all you'd see either way. The sensor was probably that far from where the disc sat.
- If your compass misbehaves now, the figure-of-eight recalibration fixes it; nothing is damaged.

A test that needs no phone:
- **Twist test:** stack two discs flat face to flat face and twist the top one. If it springs back to one angle, they're magnetized across the diameter. If it turns freely with no preferred angle, they're magnetized through the flat faces.
- **Nut check:** the twist test decides; the nut is only a hint. A steel nut is pulled to the rim of a flat face on a disc magnetized through its faces (the field is strongest at the edge, so it does not stay in the centre of the face), and to two opposite points on the curved side on a disc magnetized across the diameter. Result 2026-10-26: free turning, so through the flat faces.

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
I've added **Part G** at the top of [spurious-force-balance/docs/TODO-agent.md](docs/TODO-agent.md) and set the run order: take in your chat analysis, do Part F with the shipping amendments, then update the knowledge bases and write a handoff note. Nothing else is changed or committed.

**Your chat analysis (G1):** Sonnet will turn it into a knowledge-base note in its own words. Each claim gets a status tag: second-hand (from the chats), community data (the shipping price table the chats cite), confirmed on JLC's own help pages, or to check at checkout. The raw transcript stays untracked and is never committed, since the repo is public; whether to keep the file is up to you.

**How it changes the fabrication plan (G2):**
- **Every JLC package targets the cheap shipping tier.** Each order note gets a weight estimate, and a check keeps the board order under 0.25 kg for margin below the 0.3 kg cliff.
- **Two JLC shipments.** The free hold can't last through the weeks-long prototype measurement, so the structural boards ship now and the electronics later, each costing a few dollars to ship.
- **The 200 mm arm** is the one board over 100 mm. Sonnet compares paying the size premium, two half-arms bolted together, or a shorter arm. The noise budget gets rerun with a shorter arm, because the air-current force also shrinks with the arm's area.
- **Small boards go on one panel**, at 1.0–1.2 mm thick where stiffness allows. The five copies the minimum order forces become spares.
- **The electronics order** becomes 5 bare boards with 2 assembled. The sensor boards share one panel so they need only one assembly setup, and no stencil goes in the package.
- **OSHPark** is the fallback for the tiny gold-faced boards, only if it works out cheaper.

**Knowledge bases (G3):**
- **spurious-force-balance:** gets an index plus notes on the toolchain, the balance design findings, the electronics findings, fab ordering, and how the project works. That last one covers the two-repo split, the Opus-plans/Sonnet-acts routine and your standing preferences.
- **lab:** each of its 19 notes gets checked and updated where this work changed things, with no stale paths to the moved files, plus an index.

**Handoff (G4):** a dated note saying what's done, what waits on you, the next three tasks and which files to read first.

Here's a blurb to start the next chat with. Open it from `lab.code-workspace`, as you do now, so the same memory loads.

```
Context: I'm building a small experimental-physics lab across two repos, both open in this workspace.
- lab (github.com/arcticoder/lab): reusable bench instruments — Raspberry Pi Pico/RP2040 circuits with
  SPICE netlists, breadboard guides and pass/fail smoke tests — plus the shared parts inventory and
  order ledger (docs/inventory.md, docs/orders.md).
- spurious-force-balance (github.com/arcticoder/spurious-force-balance): the first experiment — an open,
  low-cost torsion balance that quantifies the spurious forces (supply-lead Lorentz forces, heating,
  convection) that dominate small-thrust measurements. Printable mechanics (CadQuery), a force-noise model,
  and JLCPCB-assembled RP2040 electronics (KiCad 9, ngspice).
Constraints: no hand soldering; fab boards use only JLC's machine-placed SMT parts; USB power, under
50 V DC / 30 V AC; PLA only on my Creality K1; AliExpress for stock parts (no single-item shipping fees),
JLC PCB/3DP/CNC when fabrication beats buying and cutting by hand; design to stock sizes.
Workflow: in Opus mode, analyze and write tasks as lettered Parts at the top of docs/TODO-agent.md without
actioning; in Sonnet mode, action them top to bottom. My hands-on tasks live in docs/TODO-arcticoder.md.
Start by reading docs/kb/README.md and docs/kb/session_handoff.md in spurious-force-balance, then
lab/docs/kb/README.md.
```
<!-- ------ -->
---
I chose Option B, the CLI (`@jlcpcb/cli`). I haven't installed it yet: the install is step H1 of a new **Part H** at the top of [docs/TODO-agent.md](docs/TODO-agent.md), which Sonnet will do next.

**What I checked on npm:**
- Both options come from the same unofficial project (l3wi/jlc-cli, v0.5.0, not affiliated with JLCPCB) and use the same data source. Picking the CLI loses nothing the MCP server would give.
- The MCP config you pasted wouldn't work. `jlc-mcp@latest` returns 404 on npm. The real package is `@jlcpcb/mcp`, and `jlc-mcp` is only the name of the command it installs. The plan pins version 0.5.0 instead of using `@latest`.

**Why the CLI:**
- Sonnet can already run terminal commands, so the CLI needs no setup. The MCP server needs a config change and a session restart, and it adds its tool definitions to every session in every repo.
- `jlc info C<n> --json` can be scripted into a repo check that you or I can rerun before an order. MCP lookups only happen inside a chat.
- If browsing parts in chat ever proves useful, the MCP server can be added later with one command.

**Part H steps:**
- **H1:** install the CLI, look up the RP2040 and the ADS131A04, record which fields it returns, and check that its search command doesn't hang when run from a script.
- **H2:** add a `parts.py --live` check that flags four problems in the 48-part list:
  - parts out of stock or running low;
  - "Standard only" parts, since one of these forces the whole board onto the more expensive Standard assembly;
  - parts that moved from basic to extended, which adds a fee per part.

  It stays out of the smoke tests because it needs the network. Flagged parts get fixed before the schematic work (WP4) starts.
- **H3:** compare the CLI's KiCad footprint output with `easyeda2kicad`, the tool WP4 currently plans to use, on the ADS131A04. Switch only if the CLI's output is clearly better.
- **H4:** record the tool and its pitfalls in the knowledge base.

I also added Part H to the next-task list in [docs/kb/session_handoff.md](docs/kb/session_handoff.md), ahead of WP4. Your TODO list doesn't change because none of this needs your hands. Both edits are uncommitted.
<!-- ------ -->
---
H1–H4 are done and committed locally as 5c777ae (not pushed). H5 stays open. Your TODO list and JLC order are unchanged, since none of this needs your hands. The smoke tests pass (2 run, 0 failed).

- **H1, install:** `@jlcpcb/cli` 0.5.0 is installed globally under nvm.
  - `jlc info --json` returns no stock, price or assembly type. The live data comes from `jlc search C<n> --json`.
  - `search` only gives clean output with `--json`. Without it, it prints a terminal UI full of escape codes.
  - JLC returns HTTP 429 when lookups come too fast.
- **H2, live check:** `parts.py --live` checks all 48 BOM parts against JLC's live data. It takes about 80 seconds and exits non-zero if any part is flagged. It runs one lookup at a time with retry and backoff, because of the 429s. It stays out of the smoke tests because it needs the network.
  - **Result:** every part is in stock and no part has moved between basic and extended. Two parts are Standard-assembly-only: the LIS2DW12 accelerometer (C189624) and the MMC5983MA magnetometer (C404329). One such part forces the whole board onto Standard assembly, which costs about $17 more in setup and is the two-sided service.
- **H3, symbols and footprints:** `jlc install` and `easyeda2kicad` produced the same 32 pins and the same pad geometry for the ADS131A04. WP4 keeps `easyeda2kicad`.
- **H4, docs:** I updated the knowledge base, TODO-completed.md, and the pre-order step in docs/fabrication.md. parts.md was regenerated with a new line saying to run `parts.py --live` before ordering.

**H5, open:** it decides how to handle the two Standard-only sensors.
- **Accelerometer:** a drop-in LIS2DW12 clone from MSKSEMI (C50385411) is Economic-compatible at $0.49. Its datasheet needs a compatibility check first.
- **Magnetometer:** no Economic 3-axis magnetometer turned up in my searches.
- **Both sides:** H5 also asks whether the main board needs parts on both sides, because that alone forces Standard assembly.

It's queued ahead of the schematic work (WP4) in docs/TODO-agent.md and in the session handoff.
<!-- ------ -->
---
Part H is finished (H5 closed). The remaining items in `docs/TODO-agent.md` are the schematic (WP4), which I'm stopping before, and the A5 prototype noise measurement, which needs your build. Everything is committed locally (4beafe6 plus a small wording fix); nothing is pushed.

**H5 decision:** the electronics order will use Standard assembly. It keeps both Standard-only sensors, the LIS2DW12 accelerometer and the MMC5983MA magnetometer.
- **Magnetometer:** it measures the field term in the lead-force budget, and I found no Economic 3-axis magnetometer.
- **Accelerometer:** with Standard assembly already required, the genuine ST LIS2DW12 beats a substitute.
- **Rejected substitute:** the cheaper MSKSEMI LIS2DW12 clone (C50385411) has no datasheet link, and its listing says 12-bit ±16 g, which doesn't match ST's part.
- **Cost:** about $17 more in setup on that one order (a community figure). Standard assembly also allows parts on both board sides.
- **Fallback:** if the magnetometer is ever dropped, the NXP MMA8452Q (C11360) is the Economic accelerometer to use.

`parts.py --live` now reports 0 flagged parts and lists the two accepted exceptions. The accepted-exception set (`STANDARD_PCBA_ACCEPTED`) is in `hardware/instrument/parts.py`, and the order plan in `docs/fabrication.md`, the knowledge base and the handoff are updated to match.

WP4 is a large separate task, so I stopped here. The schematic work is next in `docs/kb/session_handoff.md`. Nothing new was added to your TODO list.
<!-- ------ -->
---
WP4 (the schematic) is done as checked netlists, not rendered sheets. The main board and the four head boards are written in SKiDL, all 50 parts have KiCad symbols and footprints, and the smoke tests pass (2 run, 0 failed). Nothing is committed, as you asked.

**Defects the build caught and fixed:**
- **Ferrite bead:** the BOM's 600 Ω bead (C1002) is rated 200 mA, but the 5 V rail carries up to 389 mA. The supply-entry and boost-input beads are now Murata's 120 Ω, 2 A part (C14709). C1002 stays on the analog rail, which draws under 50 mA.
- **RP2040 crystal:** the BOM's C9002 was 20 pF load and 80 Ω ESR. Raspberry Pi's design guide says a crystal with different specs needs extensive testing, so it's now their exact part (ABM8-272-T3) with 15 pF capacitors and a 1 kΩ series resistor.
- **Boost capacitors:** the 25 V capacitors would lose most of their capacitance at the 24 V boost output. They're now 50 V parts.
- **Plate voltage:** the DAC runs from 3.3 V, so the electrostatic plate reaches about 18.8 V, not the 22.8 V in the simulation. That is still far more than the experiment needs.

The extended-part budget went from 25 to 27 (the new crystal and 50 V capacitor), and the BOM is now 50 part numbers.

**How it's checked:** `schematic_test.py` runs inside the smoke tests. It checks that every pin is connected or has a data-sheet reason to float, that supply and strap pins sit on the nets the data sheets require, that symbol pins match footprint pads, and that the five boards' parts equal `parts.py` exactly. I confirmed it fails when a pin is unwired or a supply pin is on the wrong net.

**What isn't done:**
- **KiCad's own ERC isn't a gate yet.** The generated symbols have no electrical pin types, so `kicad-cli sch erc` only reports noise.
- **The main board has no rendered sheet.** SKiDL couldn't place all 164 parts on one flat sheet. Three of the four head boards rendered; sensor head 1 failed to route.
- **The ADC crystal (C21900468) has no entry in EasyEDA**, so it uses the 12 MHz crystal's symbol and footprint as a stand-in. That needs checking against its datasheet.
- **Polarity of several parts is unchecked.** The photodiode, IR LED, Schottky diode, status LED and USB ESD chip use EasyEDA's pin assignments, not verified against datasheets.

These are queued as WP4b–WP4d in `docs/TODO-agent.md`, along with checking the boost ripple. The handoff and knowledge base are updated. I removed stray SKiDL logs and added a `.gitignore` for them.

Your TODO list is unchanged.
<!-- ------ -->
---
`TODO-agent.md` now holds only open items, in the aqei-bridge layout, and I finished WP4b–WP4d. The smoke tests pass (2 run, 0 failed). Nothing is committed.

**TODO restructure**
- `TODO-agent.md` has the same header pattern as aqei-bridge, pointing to the completed, blocked and backlog files, and the only open item is WP8.
- New [TODO-BLOCKED.md](docs/TODO-BLOCKED.md) holds A5, WP5–WP7 and a WP7 precheck.
- New [TODO-backlog.md](docs/TODO-backlog.md) holds WP4e (readable schematic sheets) and WP9–WP11.
- The old Part A planning text and the finished Parts D, F, G and H are archived in [kb/part_a_planning_archive.md](docs/kb/part_a_planning_archive.md). The convention is recorded in the workflow notes.

**WP4b, the ERC**
- **Pin types:** `lib/set_pin_types.py` gives the generated symbols datasheet pin types (132 IC pins, everything else passive).
- **Electrical rules on the netlist:** SKiDL's drawn wiring produced false KiCad ERC errors even though the netlist was right, so I run the rules on the netlist directly in `schematic_test.py`.
- **What the rules cover:** power inputs need a source, inputs need a driver, one driving part per net, and no unspecified pins. Four supply nets got PWR_FLAGs. I mutation-checked it.
- **Sheet rendering:** SKiDL's rendering is flaky (about half the head boards fail to route on any run), so the sheets moved to the backlog.

**WP4c, symbols checked**
- **Verified:** the TMP117 pins, the VBPW34S polarity and land pattern (Vishay's drawing), the SS14 and the IR LED.
- **Not verifiable:** manufacturer sites blocked the status LED, USB ESD chip, JST tabs, tactile switch and the ADC crystal's pinout. They're now an explicit check in JLC's placement preview before ordering.

**WP4d, boost ripple and DAC ceiling**
- **Boost ripple:** the worst case is 0.29 V p-p on the plate driver's supply at about 1 kHz. That gives about 0.76 pN of plate force, under the 1 pN check (1% of the force-noise budget), before the pendulum's filtering.
- **Assumption:** the op-amp supply rejection is taken as 80 dB.
- **Plate driver:** it stays linear to 0.001% over the DAC's real range, which tops out at 18.8 V.

**Two small fixes**
- The tests only worked when `KICAD9_SYMBOL_DIR` was exported in my shell, because the code set the wrong variable name. It's fixed.
- SKiDL's logs no longer land in the repo root.

You've committed the earlier WP4 work. Regenerating the netlists deleted the committed `.kicad_sch` and ERC files for the LED and photodiode heads under `schematic/out/`, because those sheets didn't render on the new run. `git checkout -- hardware/instrument/schematic/out` restores them, but they predate the pin types and flags.

WP8 (firmware bring-up scripts and the host-side logger) is next.
<!-- ------ -->
---
The firmware drivers and the host side of WP8 are done and tested on the host, and the smoke tests pass. Nothing has run on a real board. Nothing is committed.

**What now exists**
- **ADS131A04 ADC driver:** it follows the datasheet protocol (32-bit words, six-word frames with CRC, the reset/unlock/configure/wake-up order). It enables the charge pump and sets 8 kSPS from the 16.384 MHz crystal, matching the schematic's wiring.
- **DAC driver:** the LED, plate and device-current limits (20 mA, 18.8 V, 300 mA) are enforced in code, and a request over a limit writes nothing. Only the DAC's non-EEPROM write commands are implemented, and a test proves no EEPROM command is ever sent. The datasheet shows factory defaults of 0 V, so power-up is safe.
- **Sensor drivers:** the TMP117 is tested against the datasheet's own temperature examples, and the MMC5983MA recovers field and offset to one count using the datasheet's SET/RESET procedure. The LIS2DW12's register values come from memory, because ST's site blocked the download, so they are flagged unverified.
- **Lock-in:** it recovers a 20,000-count modulation on a 2,000,000-count DC level, rejects DC and mains, finds the optical delay, and stays linear from 1,000 to 1,000,000 counts. A port to the Pico needs 16-bit input to fit 32-bit integers.
- **USB stream and host tools:**
  - The framed stream resynchronizes after garbage, a damaged packet and false sync patterns.
  - The logger writes CSV files, and the analysis tool computes noise spectra and Allan deviation, checked against signals of known noise.
- **Bring-up scripts:** `bringup_adc.py` and `bringup_sensors.py` run on the Pico, and on the host against the simulated chips to test the scripts themselves.

**Bugs the tests caught**
- A sign bug in the voltage conversion.
- The lock-in's first design failed its own tests. Its integrator ripples inside each carrier period, so a DC level leaked into the output. Summing whole periods first fixed it.

**Not verified against real chips:** the simulated devices encode my reading of the datasheets, so the tests can't catch where the real chips differ. The assumptions are listed in `kb/instrument_electronics_notes.md`. They include how the ADC's CRC covers 32-bit words, how long the charge pump takes to settle, and the DAC's read-back byte layout.

**TODO files:** `TODO-agent.md` now has two open items:
- **WP9:** bring-up and experiment procedures for you, in `docs/bringup.md` and `docs/procedures.md`.
- **WP11:** a skeleton for the paper.

The rest of WP8 (the on-board `main.py`, PIO/DMA, and running the bring-up scripts on hardware) moved to `TODO-BLOCKED.md`, because it needs the board.
<!-- ------ -->
---
**1. Twist test.** Free turning with no preferred angle means the discs are magnetized through the flat faces, so I switched the design to the flat-disc (axial) layout.
- I set `MAGNET_MAGNETIZATION = "axial"` in `params.py` and regenerated the CAD. `damper_holder.stl` and the four magnet models now have flat round pockets.
- The damping is 0.43 for one 0.3 mm pad and 0.86 for two, against the 0.40 the force-noise budget assumes. No parts overlap, the force-noise result is unchanged, and the smoke tests pass.
- The JLC board files don't depend on the magnets. They regenerated with only ID noise, so I reverted them and left the Gerbers alone.
- On the nut test, my instructions were wrong. I said a nut goes to the centre of a flat face on this kind of disc. It actually goes to the rim, where the field is strongest, so "jumps to the curved side" fits an axial disc. The twist test is the real discriminator. I corrected `docs/history.md`.
- I removed the twist test from your TODO list and unblocked printing `damper_holder`. The flat-disc assembly step is in `docs/assembly.md`.

**2.1. Why the JLC board order is bare.** The four boards in `ORDER.md` carry no components. The arm is a structural beam with gold pads, and the clamp plates and electrode are plain plates. They're ordered as FR4 mechanical parts, so there is nothing for JLC to reflow.

The reflow-soldered, JLC-assembled board is the separate electronics order: the main board and sensor heads, Standard assembly, with all 50 parts placed by JLC. It comes after the prototype noise measurement, because layout waits on that result. The device card (the small board with the load resistor and header) goes in that order too.

I haven't changed `ORDER.md`. If you meant to put parts on one of the mechanical boards, tell me which and I'll plan it. Nothing is committed.
<!-- ------ -->
---
I wrote the analysis up as Parts I–N in `docs/TODO-agent.md` and your hands-on items in `docs/TODO-arcticoder.md`, and nothing is actioned, since this is analysis mode. I can't read JLC's live quote pages, so most of the cost comparisons below need your quotes. Nothing is committed.

**1. `history.md`.** Understood: I'll leave it alone unless you ask for a specific change, and I won't treat it as analysis. I've saved that as a standing rule, and corrections go in the real docs from now on.

**2. Is FR4 the cheapest?** I can't claim that yet, because I haven't seen a quote for the alternatives.
- **Small boards:** the three small boards (clamp plates and the fixed electrode) add almost nothing to a PCB order, while a CNC part starts at C$8 each plus its own parcel. The electrode board also needs real pads and a guard ring, which only a PCB gives.
- **Arm:** it needs a flat, stiff, light beam, and its pads are functional electrodes.
  - 0.8 mm aluminium matches the FR4 arm in stiffness and mass (27 g vs 28 g), is conductive, and you'd buy one piece. That is a real candidate, and Part J1 will compute it properly.
  - PLA is weaker on stiffness than FR4 (about 33 Hz against 64 Hz for the first bending mode, by my estimate). That is only a rough figure.
- **PLA:** strength isn't the problem, since PLA is plenty strong. What counts for a balance arm is stiffness, creep and moisture, because a slow creep shows up as zero drift. Warping over 208 mm and having no electrodes also count against it.
- **Quantity:** we buy 5 of each of the four designs, not four of one design. A panel version (Part J3) would put the small boards beside the arm so they cost almost nothing extra.

**3. Coupons.** The ledger will go in `lab/docs/jlc/coupons.md` (Part I1).
- Most new-user coupons end **2026-11-25**: PCB C$8.40, SMT C$13.99, CNC C$27.99, 3D printing 1 and mechanical parts 1. The rest end 2026-12-25.
- One coupon applies per checkout, so each coupon needs its own order (Part I2).
- The shipping coupons only apply when shipping costs above C$20.99, so they don't combine with the cheap postal tier.
- The CNC coupon would make a first small CNC job almost free apart from freight, but only if Part K finds a part worth it.

**4. Splitting orders and HDI.**
- The mechanical boards come to about 195 g including packing, which is already under the 300 g cliff.
- JLC estimates mass from the board's bounding rectangle times its thickness. Cut-outs don't count, and HDI doesn't change the rule. HDI would only help by being thinner, and I don't know its thicknesses.
- Thinner isn't free: the arm's first bending mode drops from about 64 Hz at 1.2 mm to 42 Hz at 0.8 mm and 21 Hz at 0.4 mm, into the range where building vibration lives.
- With Combine Shipping on, separate orders merge into one parcel. So combine only below 0.29 kg, and otherwise two parcels at $3–4 each beat one heavy one (Part I3).
- **New constraint:** Standard assembly needs a board of at least 70 × 70 mm with edge rails (from your PCBA capture). The sensor heads therefore have to ride on a larger panel, and this puts my earlier decision to use Standard assembly under review (Part M).
- **Optional early order:** an early assembled sensor-head order (Part N) would use the SMT coupon and verify the sensor drivers on real hardware. It's your call after you see the quote.
- **Unverified tips:** 5.3 and 5.4 are recorded as unverified in the notes.

**6. Quote settings and the CNC page.** I can't see the CNC sheet-metal specifications: the page only shows an upload box until a file is uploaded. I put making that markdown file on your list. Part L rewrites `ORDER.md` field by field against your PCB-quote capture.

**Your list now:**
- Read three JLC quotes: the arm at 1.2 mm, the arm at 1.0 mm, and the four designs together.
- Read the Canadian shipping price at about 100, 200, 290 and 310 g.
- Note the dates on the 30- and 60-day coupons.
- Capture the CNC and HDI quote pages.
- Check whether JLCMC lists M3 stainless nuts and washers.-
<!-- ------ -->
---
I worked through the whole agent list: Parts I–N, WP9 and WP11. The smoke tests pass (2 run, 0 failed), and nothing is committed in either repo. I changed nothing in `history.md`.

**Coupons and orders (Part I)**
- **Ledger:** `lab/docs/jlc/coupons.md` lists all your coupons with expiry dates and planned use.
- **Order plan:** `docs/fabrication.md` has one row per checkout.
- **Stacking correction:** only one coupon applies per checkout, so the SMT and stencil coupons can't stack.
- **Parcel tool:** `tools/jlc_parcel_mass.py` applies JLC's mass rule. The mechanical boards come to 194 g. Adding the printed-part candidates would make 314 g, over the cheap-tier line, so don't combine across services.

**Is FR4 right for the arm? (Part J)**
- **Stiffness:** with the ballast and device card on it, the arm's first bending mode is about 36 Hz, not the 64 Hz I gave you earlier. That figure ignored those masses. At 1.6 mm it would be about 54 Hz.
- **Alternatives:** 0.8 mm aluminium matches FR4 on mass and stiffness (24.8 g and 36 Hz against 25.5 g and 36 Hz), is conductive, and you'd buy one piece. A printed PLA arm is ruled out because it creeps, takes up moisture and has about five times the thermal drift.
- **Decision:** the FR4 versus aluminium choice waits on your quotes, with a decision rule written in `fabrication.md`.
- **Quote inputs:** `boards/fab/arm_cnc.dxf` is the arm for the CNC quote. The panel numbers are 252 × 60 mm for all four designs.
- **Printed parts:** I shortlisted `damper_holder` and `head` for JLC3DP, with `gantry` as a maybe. The rest stay home-printed.

**Order recipe (Part L)**
- **`ORDER.md`:** I rewrote it field by field against your PCB quote capture, including the panel-quote variant.
- **Standard PCBA rule (Part M):** it needs at least 70 × 70 mm with edge rails, so the heads must ride on a larger panel. That is recorded in the WP5/WP7 plan.

**Early sensor-head order (Part N), optional**
- **Panel:** `hardware/instrument/heads_panel/` has a 76 × 70 mm panel with two head-1 and two head-2 boards. It is routed with 0 unconnected nets.
- **DRC:** the only errors are 16 "malformed outline" ones, from the tab gaps being open on purpose.
- **Files:** it has a JLC-format BOM, a placement file and `ORDER.md`.
- **Unconfirmed assumptions:** JLC's rail and tooling-hole sizes, the mouse-bite pattern and the part rotations in the placement file are my assumptions, not confirmed with JLC. The order recipe asks for both the production-file and parts-placement confirmations for that reason.
- **Coupon:** it would use the SMT coupon (C$13.99, ends 2026-11-25).

**Procedures and paper (WP9, WP11)**
- **Bring-up:** `docs/bringup.md` is the power-up order for the electronics, with the expected output and what each failure means.
- **Experiment:** `docs/procedures.md` covers the prototype check, the calibration, and the measurement campaign, with the model's numbers beside each measurement.
- **Paper:** `docs/paper/` is a LaTeX skeleton that builds. Model numbers are marked and every measurement is a red to-do. The bibliography has only the three references the repo already records, with authors and titles left to fill in from the papers.

**On your list now**
- Read the arm and four-design quotes and the Canadian shipping table.
- Note the dates on the 30- and 60-day coupons.
- Capture the CNC and HDI quote pages, and check whether JLCMC lists M3 stainless nuts and washers.
- Decide on the sensor-head order, which would also need a JST-SH cable on your AliExpress cart. The order recipe says to place it by 11-25 only if you want it.

What remains in `TODO-BLOCKED.md` needs your quotes or a physical board.
<!-- ------ -->
---
I've replaced the old coupon ledger in `lab/docs/jlc/coupons.md` with your two new lists, and revised the order plan around it. Nothing is committed.

**What changes in the plan**
- **Mechanical boards:** the JLCONE $8 PCB coupon (C$11.22 off over C$14.03, ends 2026-11-26) is larger than New User PCB (C$8.42), so it goes on the arm order. New User PCB goes on a second cart line, if the cart lets another line take its own coupon.
- **Cart lines:** the terms say one coupon per order, and I can't tell whether each cart line counts as its own order. I added that check to your list: apply a coupon to one line, try another on a second, and tell me what happens.
- **Sensor-head panel:** the best coupon is still New User SMT (C$14.03, ends 11-25). The PCBA Special Offers ($9 and $6) expire in about three days, so they're only worth it if you order immediately. The stencil coupons can't stack with it.
- **CNC:** there are now two coupons near C$28 (New User CNC to 11-25, JLCONE-$20 CNC to 11-26), so two CNC checkouts would be close to free apart from freight. Whether that's worth doing depends on the aluminium-arm quote.
- **Not usable or not relevant:**
  - The "EasyEDA Design" coupons only apply to EasyEDA files, so the KiCad exports can't use them.
  - JLCCNC $10 and both Parts Special coupons are maxed out.
  - The layout, multi-layer, flex, motion and enclosure coupons don't apply to this project.
  - The 3D-printing coupons with $30–$200 minimums won't be reached by two small parts, so only the New User 3D Printing ones apply.

Also, the first list shows amounts without a currency prefix, while the second uses C$ (C$14.03 = US$10 now). I treated the first as US$ and noted that this should be checked at checkout.

I updated `ORDER.md`, the heads-panel order recipe, the order plan in `fabrication.md` and the ordering notes to match. The smoke tests pass.
<!-- ------ -->
---
**1.1 Price estimate dropping to $0.** The coupon covers the goods (freight is excluded), so a C$2.81 board can't go below zero and the rest of the coupon is lost. The "calculated price" stays at C$2.81 because that is the price before the coupon.

I couldn't tell whether the extra coupon you selected went on the same order or a second one. Please tell me which coupons showed as applied. Put the big coupons on the dear lines and the small ones on the cheap boards. Don't spend a large coupon on a board that costs less than it. When you add the arm, check that JLCONE $8 PCB still applies. It needs goods over C$14.03, and the arm should clear that. I noted this in `lab/docs/jlc/coupons.md`.

**1.2.1 Gold thickness.** The choices are 1 µ" (default) or 2 µ".
- **Arm and electrode board:** take 2 µ" if the quote adds only a few dollars, otherwise 1 µ". The gold pad is the electrostatic electrode, and thicker gold has fewer pores over the nickel. That means fewer oxide patches that could shift the surface potential and so the force, which matters at nanonewton level. This is a precaution I haven't measured.
- **Strip-contact plate:** 1 µ" is fine, since nothing slides on it.
- **Wear:** it doesn't matter here.

I added the row to `ORDER.md`.
<!-- ------ -->
---
**1. Two coupons.** You told me two work, and I wrote one. I was wrong. The plan now assumes up to two per order, so my question about cart lines was a bad one and I've dropped it.

**2. ENIG's C$25.25.** No, I couldn't see it. The `jlc` tool only searches the parts catalogue (LCSC and EasyEDA). It has no PCB, CNC or shipping quote. JLC's quote pages are script-driven, so my web fetch can't read them either; I tried both pages. Every JLC price in this repo that isn't from your captures is an estimate. I'll stop sending you to click for numbers unless I have one specific question.

**3. FR4 isn't cheap here.**
- Engineering C$5.61 plus board C$8.56 comes to about C$14.17 with HASL. ENIG adds C$25.25 on top.
- I switched `ORDER.md` to LeadFree HASL, since the weights calibration absorbs the electrode's geometry. That makes the gold-thickness question moot.
- The engineering fee looks per design, so four separate designs may mean four fees. That makes the one-file panel version worth quoting. I haven't built real panel Gerbers yet; the 252 × 60 mm numbers in `ORDER.md` are for entering into the quote form.
- With about C$12 shipping, an FR4 arm is roughly C$26 before coupons. The aluminium arm via JLCCNC now looks worth pricing first. Its two coupons are C$28.06 each.

**4. The coupons and shipping.** Your read is plausible, but I can't confirm any of it.
- The quote page says "The coupon can be applied when you select a payment method". That means coupons are applied at payment, not in the quote lines.
- The ~C$2.81 "special offer" is the new-user price for a small board, up to 100 × 100 mm, not a coupon. The arm is over that size, so it lost that price.
- Locked coupons may be tied to an unsubmitted saved line in the cart. I'd delete those lines before anything else, then ask JLC support if they stay locked. That is a guess.
- The shipping jump probably isn't the "≤55 × 40 cm" limit, since the arm is far inside it. It's more likely the mass JLC estimates. The quote page's weight line is the missing number.

**Your list now:** nothing to do on the PCB page. When you next have the arm uploaded, read me the page's mass line and whether changing quantity or thickness moves the shipping. Separately, upload `boards/fab/arm_cnc.dxf` at the JLCCNC sheet-metal quote (6061, 0.8 mm, one piece) and send me the price and shipping.
<!-- ------ -->
---