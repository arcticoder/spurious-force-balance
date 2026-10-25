# KB: how this repo and its sibling are worked

Audience: future LLM sessions. Facts about the repos, the Opus/Sonnet routine and the user's standing preferences, as of 2026-10-24. The user's own words are never quoted in files; decisions are paraphrased.

## The repos

- `~/Code/python/pico`: the user's Pico/RP2040 sandbox (the Claude Code memory directory is keyed to it).
- `~/Code/python/lab` (github.com/arcticoder/lab, public): reusable bench circuits (SPICE netlists, breadboard guides, pass/fail smoke tests, MicroPython) plus the shared parts ledger (`docs/inventory.md`,
  `docs/orders.md`, `docs/parts_reference.md`) and its own knowledge base (`docs/kb/`). Every circuit there is ephemeral on a breadboard; parts return to inventory.
- `~/Code/python/spurious-force-balance` (github.com/arcticoder/spurious-force-balance, public, split from `lab` on 2026-10-23 with history): the torsion-balance experiment: plan, CAD, noise model, FR4 boards for JLC,
  the fab-assembled electronics design. Experiment-specific work lives in its own repo; a circuit built for an experiment stays in `lab` if it is reusable (`optical_shadow_readout`, `lockin_amplifier`) and the experiment links to it.
  Cross-repo references are GitHub URLs, not relative paths. `lab/lab.code-workspace` lists all three folders; the user keeps that one workspace.
- Licenses (both repos): MIT for code, CERN-OHL-P v2 for hardware designs and their documentation (`LICENSE`, `LICENSE-HARDWARE`).
- Git identity in both: `Arcticoder <10162808+arcticoder@users.noreply.github.com>`. Commit only when asked or when the task says so; the user commits `lab` themselves. Commit messages end with the attribution line the session's system reminder gives.

## The Opus plans / Sonnet actions routine

The user alternates models with `/model`. In Opus mode nothing is actioned: Opus analyzes, then writes lettered **Parts** at the top of `docs/TODO-agent.md` (A, D, F, G so far) with concrete, checkable tasks. In Sonnet mode the user
says to process the tasks and Sonnet works them top to bottom, recording what was done in `docs/TODO-completed.md` and replacing a finished Part's task list with a short summary. `docs/TODO-arcticoder.md` is the user's own
list (hands, eyes, purchases only; one-line justifications; "En route" after the actionable sections), and anything the user must do goes at the top ("What I need from you").

## The user's standing preferences that shape this repo

- Paraphrase decisions; never quote the user or describe how they said it.
- **Design to stock sizes:** whole acrylic sheets, standard pads and rods; exact listing sizes in order lines; every cut needs a printed jig and a listed tool; the user has no saw, vise or scale in inventory.
- Carts must not incur single-item or under-threshold shipping fees; lines come from designs. AliExpress is the source for stock parts; no local-store suggestions; no mains parts on AliExpress.
- No hand soldering by the user; fab boards use only JLC's machine-placed SMT parts (nothing mailed in); one consolidated order where possible; USB power; under 50 V DC / 30 V AC.
- **Home printing is PLA only** (the fumes of ABS, PETG and nylon are ruled out). JLC PCB-as-structure, JLC3DP and JLCCNC are in scope when they beat buying and hand-cutting on cost, time or measurement risk.
- Instrument framing: never describe a circuit "without a multimeter"; name what it does. Real smoke tests (pass/fail safety and functional checks), not decorative simulations.
- Safety answers name the specific hazard or control gap; don't reassure or refuse.
- Jumper wires are never inventoried. Flux is not bought from AliExpress.

## Tools available to a session

`~/.venvs/lab-hw/bin/python` (CadQuery, magpylib, kiutils, SKiDL, numpy/scipy/matplotlib), KiCad 9.0.9 `kicad-cli`, ngspice, Freerouting (see `pcb_toolchain_notes.md`), `jlc` (live JLC stock/PCBA-type lookups; see `pcb_toolchain_notes.md`), `gh` (logged in as arcticoder), `git-filter-repo`,
`WebSearch`/`WebFetch` for vendor help pages, and read-only Pico probes through `mpremote` when the user leaves a rig plugged in (see `lab` `docs/kb/live_bench_measurement_notes.md`).
