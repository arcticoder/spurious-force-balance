# KB: ordering fabrication from JLC (PCB, PCBA, 3D printing, CNC) — shipping, minimums, tactics

Audience: future LLM sessions. Ingested 2026-10-24 from a user-supplied pair of LLM chats (a Gemini answer on JLC shipping and a
Grok review of it) and checked against web sources the same day. The chat transcript itself was not committed. Tags: **[confirmed]**
read on a JLC/OSH Park page on 2026-10-24 (URL given); **[community]** third-party measurement or guide; **[second-hand]** stated
by an LLM chat and not checked; **[verify at checkout]** always read the live quote page. Prices drift with promotions and destination.
The user is in Canada (British Columbia area) and pays by the cheapest postal tier.

## Shipping

- JLC shipping is dearer than AliExpress's free tier because there is no retail margin to subsidize freight, FR-4 is dense, and each
  custom order is packed and tendered on its own; AliExpress consolidates thousands of parcels. [second-hand, plausible]
- **The 0.3 kg cliff on "Global Standard Direct Line":** one 2024 measurement (Peter Tanner, `petertanner.dev/posts/JLCPCB-shipping-price-hack/`)
  found the price jumping from 3.18 at 0.18–0.29 kg to 14.35 at 0.33 kg, **in Australian dollars for an Australian destination**, so the
  numbers don't transfer; only the shape does. [community; the 0.3 kg threshold is not on any JLC page found] Treat 0.3 kg as a
  working limit and read the quote.
- Board weight in the quote uses the **bounding rectangle × thickness**, so cutouts and odd outlines don't lower it; assembly raised one
  quoted mass past a tier. [community]
- Direct Line may be limited to orders under a total value, may not prepay duties, and the price has moved with promotions (about
  $1.50 for a 100 × 100 mm 5-piece order in some 2025 promos). [community / second-hand]
- **Canada:** JLC's shipping-policy page lists a 20 CAD threshold for Canada [community snippet of jlcmc.com/help/article/Shipping-Policies;
  read it before ordering]. Couriers (DHL, UPS, FedEx) bill brokerage on parcels over about CAD 20, which can double a small order's cost;
  postal tiers are usually cheaper, with an optional Canada Post collection fee (users report $5–10). [community] **Check at checkout** whether GST is collected up front.
- **Combine Shipping (a JLC add-on)** [confirmed, `jlcpcb.com/help/article/combine-shipping-service`, page dated Sep 2026]: turn it on under
  Add-On Services, choose a trigger (by weight, by order count, or a fixed weekly schedule), and orders are held until the trigger is
  met; you then pick a courier and pay storage and shipping. **Free storage is 15 days** from the first order's arrival at the warehouse
  (fees from day 16). A search snippet of an older version said 7 days; the live page says 15. The page does not list which products
  qualify or say whether one order can be split. Separate sources: PCB, stencil, SMT parts and JLCMC mechanical parts ship together
  since August 2024; JLC3DP and JLCCNC orders combine with PCB orders [second-hand; verify the qualifying list at checkout]. One order
  (one design × quantity) is one unit and cannot be split across parcels. [second-hand, consistent with the page]
- The slowest process sets the ship date of a combined parcel (CNC and 3D printing are usually slower than PCBs). [second-hand]
- A freight forwarder or factory pickup adds inbound fees and courier minimums that exceed the saving at this volume; not used.
  Paying for boards and having JLC discard them isn't an option. [second-hand]

## Board orders

- **Price tier:** 2-layer boards under 100 × 100 mm are the $2 tier for 5 pieces; 4–8 layers must be under 50 × 50 mm for the same
  price. [confirmed on a Hack Club guide, `hwdocs.hackclub.dev/user-contrib-guides/jlc-cost-optimizing/`, undated, US-focused]
- **Minimum 5 bare boards per design.** Keep or recycle the rest. Panelization (below) is the way to get several designs per 5 boards.
- **Assembly:** economic PCBA accepts 2–50 pieces [confirmed, `jlcpcb.com/solutions/pcb-prototype-assembly`], so a 5-board order can
  have 2 assembled; one assembled is not offered. Economic assembly places parts on one side. [community guide]
  Each **extended** part adds a loading fee of about $3 [community guide; the repo's `parts.py` counts 27 extended]. Standard (two-sided)
  assembly has a setup fee about $17 higher. [community guide] JLC also marks individual parts "Standard only"; one such part puts the whole board on Standard.
  As of the live check of 2026-10-24, two of the instrument BOM's 50 parts are (the accelerometer C189624 and magnetometer C404329); **Decision (H5, 2026-10-24): the electronics order uses Standard assembly**, keeping both sensors (the magnetometer measures the budget's field term and has no Economic equivalent). Fallbacks if it is dropped: NXP MMA8452Q C11360 for the accelerometer. [`jlc` CLI, live]
- **Thickness:** weight scales with thickness, so 1.0 or 1.2 mm instead of 1.6 mm cuts board mass about 35–40%. [arithmetic; second-hand]
  FR-4 is about 1.85 g/cm³, so a 100 × 100 mm 1.6 mm board is about 30 g and five are about 150 g, plus packing.
- **Panelizing:** designs can share a board with mouse-bites or V-cuts. JLC's panel page suggests 150–200 mm panels and says nothing
  about mixed-design surcharges [confirmed absent, `jlcpcb.com/help/article/panelizing-your-pcb-for-assembly`]; a fee of about
  $3–4 for multiple designs in one file is reported [second-hand; ask JLC support]. A board that is two designs joined once pays one
  assembly setup.
- Steel stencils add weight and area; leave them out unless needed. [second-hand]
- **Two small shipments under the weight limit can cost less than one over it.** [community]

## Alternatives

- **OSH Park** [confirmed, `docs.oshpark.com/services/two-layer/`]: 2-layer, ENIG finish standard, $5 per square inch for **3 copies**,
  free shipping worldwide, 9–12 days (Super Swift $10 per square inch, 4–5 business days); 1.6 mm board (a 0.8 mm 2-layer 2 oz service
  exists), purple mask. Customs and brokerage for Canada are not stated; check. Useful for tiny ENIG boards.

## How this repo uses it (decisions of 2026-10-24; full record in `docs/fabrication.md`)

- **FR4 boards as structure.** The balance's arm, strip clamp plates and fixed electrode are unassembled JLC boards (four designs, 5 pcs each, 1.2 mm, black mask, ENIG on three): they fix the thermal,
  creep and mass-uncertainty problems of printed parts and need no cutting. Everything fixed is PLA on the user's K1. No JLC3DP or JLCCNC part is needed now.
- **Every JLC parcel targets under 0.29 kg estimated** (boards 154 g for the mechanical order plus about 40 g packing [assume]); a smoke check holds the mechanical order to that.
- **Two JLC shipments:** the mechanical boards now, the electronics (5 bare, 2 assembled; sensor heads panelized together; no stencil) after the A5 prototype measurement, because 15 free days of Combine Shipping
  storage cannot bridge weeks of measurement.
- **Arm board over the cheap tier:** 200 x 60 mm. If its quote is over about $60 or the parcel over 0.29 kg, ask the user before changing anything: a shorter arm needs a damper rework (zeta 0.10 per pad at 75 mm).
- **Separate small designs rather than a mixed panel** unless the quote shows the panel cheaper (a mixed-design surcharge is unconfirmed). OSH Park is dearer for the arm and comparable for the small boards.
- **AliExpress for stock parts only after the design fixes the counts** (acrylic, washers, 304 nuts, JST-SH cable, weights, tools).
