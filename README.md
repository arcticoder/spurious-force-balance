# spurious-force-balance

An open, low-cost torsion balance for measuring the spurious forces that dominate small-force and thrust
experiments, with printable mechanics, a validated force-noise model and fab-assembled electronics.

**The question.** On an open, fully SMT-assembled, low-cost torsion balance operating in air, quantify the
forces that usually pass for thrust: the Lorentz force of supply-lead currents in the ambient magnetic field,
and the thermal and convective forces of a dissipating device. Measure them as functions of current, lead
geometry and dissipated power, with the balance's force noise floor, calibration constant and drift fully
characterized. The instrument claim is a resolution of 0.4 nN or better (5σ on a 20 nN term) in a 1000 s
measurement, at a parts cost to be filled in from the final bill of materials.

## Status

| Piece | State |
|---|---|
| G1 measurement goal | confirmed 2026-10-23 |
| G2 mechanics | printable CadQuery model, collision-free over the swing, centre of mass solved onto the axis; stock-size acrylic enclosure; field-modelled eddy damper; cutting jigs; [assembly steps](docs/assembly.md) |
| G3 force-noise prediction | 0.108 nN (1σ, 1000 s, in air): a conditional go |
| WP1–WP3: requirements, 48 JLC-stocked parts, analog block simulations | done |
| WP4 schematic onward | not started |
| A5: prototype noise measurement | next; it decides layout and the board order |

The prediction is dominated by air currents (4.8 nN/√Hz), so the verdict flips at about 4 mm/s of air-speed
fluctuation; the enclosure is the biggest noise control. The model reproduces six published numbers, from
Soni and Roy (Rev. Sci. Instrum. 84, 095103, 2013) and the cryogenic torsion balance of arXiv:2206.02890.

## Layout

| Path | What |
|---|---|
| `docs/plan.md` | the plan: goal, mechanics, noise budget, environment control, calibration |
| `hardware/balance/` | parametric CAD (`balance.py`, STL and STEP in `cad/`), analytic model, parameters, checks |
| `hardware/instrument/` | the electronics: requirements, pin map, parts table, ngspice simulations, checks |
| `hardware/tools/jlc_query.py` | search of the JLCPCB parts snapshot |
| `tools/force_noise_budget.py` | the force-noise prediction and the anchor checks |
| `docs/TODO-agent.md`, `docs/TODO-arcticoder.md` | the work lists |

## Running the checks

Setup (Linux/WSL) is in [hardware/README.md](hardware/README.md): KiCad 9, a Python venv with CadQuery,
SKiDL and ngspice.

```
python3 tools/force_noise_budget.py                       # the noise prediction and anchor checks
~/.venvs/lab-hw/bin/python tools/run_all_smoke_tests.py   # CAD, pin map, power budget, simulations
```

## Construction rules

- Every electronic part is a machine-placed SMT part from JLCPCB's own library; nothing is hand-soldered
  and nothing is mailed to the fab.
- USB power only; nothing above 50 V DC or 30 V AC. The device current is capped at 300 mA by the USB budget.
- The balance carries no permanent magnet on the moving arm (a 6 × 3 mm N42 disc alone would add about
  7 nN/√Hz of field noise); masses on the arm are brass or plastic.

## Companion circuits

The bench circuits this experiment uses for its prototype check (lock-in amplifier, optical shadow readout,
R-2R signal generator) live in [arcticoder/lab](https://github.com/arcticoder/lab), which also holds the shared
parts inventory and order ledger.
