# KB: PCB and CAD toolchain in this repo (2026-10-22, updated 2026-10-24)

Audience: future LLM sessions. Facts found while setting up the fab-assembled instrument work
(`docs/plan.md`). User-facing setup is in `hardware/README.md`.

## What exists and what doesn't

- KiCad **9.0.9** (user installed it from the KiCad 9 PPA on 2026-10-23, replacing 7.0.11): `kicad-cli` has
  `sch erc`, `pcb drc`, `pcb render` and the exports. The symbol/footprint library packages stayed at 7.0.11.
  `pcbnew` imports under `/usr/bin/python3` (3.12), not under the
  conda Python (3.13): use `~/.venvs/lab-hw/bin/python`, a venv with `--system-site-packages`.
- No sudo from the session (a password is required), so apt installs are the user's to run.
- `pip install skidl` prints "KICADn_SYMBOL_DIR missing" warnings on import: set `KICAD7_SYMBOL_DIR=/usr/share/kicad/symbols` (and the footprint dir) before using SKiDL's KiCad library lookups.
- Freerouting 2.5.0's plain jar needs Java 25 (class file 69); the box has Java 21. The Linux release zip bundles a runtime and works headless (`-de`, `-do`, `-mp`).
- CadQuery 2.8 installs in the venv (pulls OCP); `Shape.matrixOfInertia` returns the inertia about the part's
  own centre of mass per unit density, so combine with m d² yourself (done in `balance.py`).

## Network facts

- analog.com and the Maxim mirror timed out for datasheets; ti.com, datasheets.raspberrypi.com, arxiv.org,
  github.com, jsdelivr and yaqwsx.github.io worked from curl. AliExpress pages return nothing readable.
- The JLC parts snapshot (jlcparts, `~/jlcparts/cache.sqlite3`, source-db-v2, fetched 2026-10-22) is a split
  zip: `cache.z01..z04` (50 MB each) plus `cache.zip` (10 MB). There is no `zip`/`unzip`/`7z`: concatenate
  nothing, instead read the last disk's central directory, add the sum of earlier disks' sizes to each entry's
  local-header offset (the entry carries a disk number), and inflate the deflate stream with zlib
  (`wbits=-15`). The result is one 1.6 GB sqlite file.
- Schema: `jlc_components(lcsc, category, subcategory, mfr, package, library_type, stock, price, description,
  datasheet, attributes, assembly_process, assembly_mode, ...)`. `library_type` is `base` (basic, no per-part
  setup fee) or `expand` (extended). `price` is a tier string `'1-199:0.0116,200-599:0.0092,...'`.
  **`assembly_process`/`assembly_mode` separate machine-placed parts (`SMT`/`smtWeld`, 836k rows) from
  hand-soldered through-hole parts (`THT`/`manualWeld`, 1.9M rows)**; the user's constraint is machine-placed SMT
  parts only, so every part query goes through `hardware/tools/jlc_query.py --smt`. Rows with no marking are
  basic resistors and capacitors (SMD sizes).
- The library has a category of pre-crimped leads (`Wire/Cable/DataCable`), but a fab assembles boards, not cables.

## Datasheet facts taken while selecting parts (read from the TI PDFs)

- ADS131A04 (24-bit, 4 simultaneous channels, up to 128 kSPS): AVDD 3.0 to 3.45 V with AVSS = 0 and the charge pump
  on (inputs then reach AVSS - 1.5 V), 2.442 V internal reference, 130 kΩ differential input impedance, needs a
  16.384 MHz clock or crystal; input-referred noise 5.01 µVrms at 8 kSPS gain 1 (about 79 nV/√Hz, white), 3.49 µVrms at 4 kSPS.
- LM358 (TI datasheet): the standard grade has 0.7 MHz gain-bandwidth and 0.3 V/µs slew rate; the B grade 1.2 MHz and 0.5 V/µs.

## Added 2026-10-24 (mechanical boards and the field model)

- **Venv packages** (`~/.venvs/lab-hw`): skidl, kiutils, easyeda2kicad, cadquery 2.8, numpy, scipy, matplotlib, **magpylib 6.0.0** (permanent-magnet fields; `getB` on a
  `Collection` of `magnet.Cylinder`s; diametric magnetization is a polarization along local x, then rotated; checked against the analytic axial on-axis field to 0.01%).
- **`hardware/balance/boards.py`** writes the FR4 boards as `.kicad_pcb` with kiutils from the CAD's constants, runs `kicad-cli pcb drc --format json --severity-all`,
  `pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts`, `pcb export drill --format excellon --excellon-separate-th`, zips with `zip -j`, and renders with
  `pcb render --side top`. Coordinates: KiCad X is the balance's x, KiCad Y is minus the balance's z; F.Cu is the arm's -y face, B.Cu its +y face.
- **kiutils pitfalls:** `Board.create_new()` writes the KiCad 6 file format (kicad-cli 9 reads it). Every track, via, graphic and footprint needs a non-empty `tstamp` (an empty one
  writes `(tstamp)` and the file then fails to load back with an IndexError). Text on a back layer needs `Justify(mirror=True)` or DRC warns. Net-less tracks next to net-less pads make the
  DRC report `solder_mask_bridge`; give copper that is meant to be one conductor a shared net (`board.nets` plus `Net` on pads and `net=` on segments). Copper rectangles drawn as
  `GrRect` with `fill="solid"` export as copper regions; a matching rectangle on `F.Mask`/`B.Mask` opens the mask (bare ENIG). Footprints built without a library give
  `lib_footprint_issues` warnings; they're harmless.
- **JLC capabilities read 2026-10-24** (`jlcpcb.com/capabilities/Capabilities`): thickness 0.4 / 0.6 / 0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm for 2 layers, finish HASL / ENIG / OSP, mask colours
  include black, minimum non-plated hole 0.5 mm, minimum plated hole 0.15 mm, copper to routed edge 0.2 mm (0.4 mm to a V-cut), annular ring 0.25 mm recommended, outline +-0.1 mm
  with routed edges +-0.2 mm, thickness +-10% at 1.0 mm and over. No price tiers are published on that page. ENIG is charged extra when exposed copper exceeds 30% of the board area
  (`jlcpcb.com/help/article/In-what-cases-will-there-be-charged-extra`).
- Web tools worked in this session: `WebSearch` and `WebFetch` returned the JLC help pages above, OSH Park's docs and several community posts. JLC's interactive quote page can't be read, so
  prices are estimates until the user checks them.
- **Live JLC lookups: `jlc` (npm `@jlcpcb/cli` 0.5.0, installed globally under nvm; unofficial, from github.com/l3wi/jlc-cli, so it can break when JLC changes its web endpoints; if it does,
  fall back to the snapshot above).** Chosen over the sibling MCP server (`@jlcpcb/mcp`; the MCP README's `npx jlc-mcp` name 404s on npm, the binary is called `jlc-mcp` but the package is scoped) because a
  session has Bash and the CLI is scriptable. Behaviour found on 2026-10-24:
  - `jlc info C<n> --json` returns only name, manufacturer, package, pin count, `has3DModel`: **no stock, price or PCBA type.** Use `jlc search C<n> --json` instead: an exact-LCSC query returns the part
    plus look-alikes, so pick the row whose `lcsc_id` matches. Fields: `stock`, `price` (one unit price, no tiers), `library_type` (`basic`/`extended`), `pcba_type` (`economic-and-standard` or
    `standard-only`), `package`, `datasheet`, `attributes`. `--economic-only`, `--in-stock`, `--basic-only` filter.
  - Without `--json`, `search` renders an Ink TUI and prints escape codes even with stdin from `/dev/null` (it does not hang, but the output is unusable): always pass `--json`.
  - Rapid or parallel calls get `{"success": false, "error": {"code": "search_failed", "message": "JLCPCB API returned 429", "retryable": true}}`; `jlc_query.live()` retries with backoff and `parts.py --live` is sequential.
  - Pre-order check: `~/.venvs/lab-hw/bin/python hardware/instrument/parts.py --live` (network, not in the smoke tests); exit code 1 if any part is flagged.
  - `jlc install C<n> --project <dir> --yes --json` writes a project-local symbol library, footprint library, 3D STEP and `sym-lib-table`/`fp-lib-table`. On C882747 (ADS131A04) it gives the same 32 pins
    and the same pad geometry as `easyeda2kicad` (the same EasyEDA source); only the active-low names differ (`RESET#` versus `~{RESET}`) and both leave pin types unspecified. WP4 keeps `easyeda2kicad`.
- **SKiDL 3.0 and the `jlc` library (WP4):** see `instrument_electronics_notes.md` ("Pitfalls") for the net-merge name loss, `builtins.default_circuit`, the unspecified pin types that make KiCad's ERC noise, and the flat-sheet routing failure. `easyeda2kicad --lcsc_id=C<n> --symbol --footprint --output=<dir>/jlc` appends to one library; "Footprint ... already exists" errors are shared footprints (harmless). A burst of 50 calls worked; C21900468 returned HTTP 403 from the EasyEDA API.

