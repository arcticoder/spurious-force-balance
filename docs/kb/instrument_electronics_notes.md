# KB: the instrument board — what was decided, what the simulations found, what is open

Audience: future LLM sessions. State of 2026-10-24: WP1 (requirements), WP2 (parts), WP3 (analog block simulations) are done; WP4 (schematic) is next and not started. Sources: `hardware/instrument/`
(`requirements.md`, `pins.py`, `parts.py`/`parts.md`, `analog_sims.py`, `sim/*.spice`, `smoke_test.py`). The board is a JLCPCB-assembled RP2040 design: no hand soldering, machine-placed SMT from JLC's library only, USB power, under 50 V DC.

## Decisions and their reasons

- **RP2040, not RP2350** (see `lab` `docs/kb/rp2350_notes.md`): the repo's MicroPython and register-level code uses RP2040 peripheral bases (on RP2350, 0x40050000 is PLL_SYS); RP2350 erratum E9. 16 Mbit W25Q16JV flash like the Pico.
- **ADC: ADS131A04** (24-bit, 4 simultaneous channels, 3 V analog with the charge pump, 16.384 MHz crystal, about 79 nV/sqrt(Hz) input-referred). The ADS1220 ($2.23, 2 kSPS) can't sample the signal and reference photodiodes at the same instant.
  Channels: 0 photodiode head, 1 reference photodiode on the LED head, 2 device-current shunt, 3 plate voltage.
- **DAC: MCP4728** (12-bit, I2C): LED current, plate drive, device-current set. A 16-bit DAC8554 costs $11; 12 bits give 42 pN steps on the plate and 10 uA on the LED.
- **Regulators:** one part number (LP5907-3.3) for the analog and digital rails to keep the extended-part count down. Connectors: two JST-SH sizes (4-pin, 2-pin) and one 2.54 mm SMD header.
- **Optical channel:** modulated 940 nm IR LED, VBPW34S photodiode, TIA (10 kohm, 1 nF, 80 dB at 1 kHz), digital lock-in. The LED is modulated from a PIO pin; a second photodiode on the LED head is sampled at the same instant to normalize LED intensity.
- **Plate driver:** MT3608 boost to 24 V, OPA197 non-inverting gain 5.7 (47 kohm over 10 kohm) with 10 pF across the feedback resistor; peak 22.8 V against the 50 V line.
- **Device-current source:** AOD4184A sink with a 1 ohm shunt, a 4.7 ohm 2512 ballast (takes the MOSFET's dissipation), TLV9062 loop with 1 kohm/10 nF compensation; capped at 300 mA by the USB budget.
- **Coin motors** (two AO3400A drivers, PWM capped at 60% duty from 5 V) disturb the balance for transfer-function measurements; environment sensors: TMP117 (three), LIS2DW12 accelerometer, MMC5983MA magnetometer (heads on JST-SH cables).
- **Power budget** (`pins.py`): measurement 89 mA; lead-current run 389 mA; disturbance 329 mA from the 5 V USB rail; polyfuse holds 750 mA; each mode stays under 90% of USB's 500 mA.
- **Pins:** 30 signals on 30 GPIOs, every function checked against RP2040 datasheet Table 2; ADC on SPI0 (GP16-19), I2C0 on GP4/GP5, motor PWMs on one slice, four ADC monitors on GP26-29.
- **Parts:** 48 part numbers, 25 extended (each extended part adds about a $3 loading fee at assembly [community]); all in stock at 20x the order's need (2 assembled boards of 5 bare).
- **The device card** (16 x 24 mm FR4 with the device's resistor and a header) belongs to the electronics order; its power cap is 0.5 W (see `balance_design_notes.md`).

## What the simulations found (ngspice, behavioral op-amp models from the data sheets; TI macro models replace them before layout)

- First TIA run had the photocurrent polarity wrong (op-amp railed; 40 dB instead of 80): the photodiode's cathode goes to the inverting input.
- LED current sink stalls with ideal switches: use a behavioral selector plus Ron; it needs no gate resistor or compensation capacitor (every added one made it worse). 20.00 mA at a 1.02 V reference, zero when gated off.
- Device-current sink: no overshoot and 300 mA to 0.5% across gain, Ciss and load corners with 1 kohm/10 nF; 0.94 W in the MOSFET at 300 mA (52 K rise at 55 K/W).
- Plate driver: 8.6% overshoot without feedback capacitance; 10 pF removes it (linear to 0.001%, settles in 3.9 us into 300 pF of cable).
- BOM errors caught by the checks: a 100 mohm shunt where 1 ohm was needed; the ballast and sense resistors were missing.

## Open points before layout (WP4/WP5)

1. ADS131A04 input network, charge-pump pins (AVSS/VNCP) and input protection (datasheet pages).
2. The 24 V boost's feedback network and ripple filtering (mechanical bandwidth is 0.2 Hz, so ripple matters through the ADC and optics).
3. Analog ground partitioning: the plate driver and LED sinks are the noisiest blocks.
4. The real photocurrent (assumed 100 uA at mid-flag): the A5 prototype measures it, and Rf may change.
5. A5 itself, with the balance as built (FR4 arm): the measured noise spectrum, before layout or the electronics order. WP5 (layout) and WP7 (order) wait on A5.
6. Tools: schematic via SKiDL + `kicad-cli sch erc`; symbols/footprints from `easyeda2kicad` by LCSC number (library packages are still KiCad 7.0.11).
