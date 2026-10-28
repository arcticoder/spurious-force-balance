# KB: the instrument board — what was decided, what the simulations found, what is open

Audience: future LLM sessions. State of 2026-10-24: WP1 (requirements), WP2 (parts), WP3 (analog block simulations) and WP4 (schematic, as checked netlists) are done; rendering the main-board sheet and WP5 (layout, waits on A5) are next. Sources: `hardware/instrument/`
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
- **Parts:** 50 part numbers, 27 extended (each extended part adds about a $3 loading fee at assembly [community]); all in stock at 20x the order's need (2 assembled boards of 5 bare).
- **The device card** (16 x 24 mm FR4 with the device's resistor and a header) belongs to the electronics order; its power cap is 0.5 W (see `balance_design_notes.md`).

## What the simulations found (ngspice, behavioral op-amp models from the data sheets; TI macro models replace them before layout)

- First TIA run had the photocurrent polarity wrong (op-amp railed; 40 dB instead of 80): the photodiode's cathode goes to the inverting input.
- LED current sink stalls with ideal switches: use a behavioral selector plus Ron; it needs no gate resistor or compensation capacitor (every added one made it worse). 20.00 mA at a 1.02 V reference, zero when gated off.
- Device-current sink: no overshoot and 300 mA to 0.5% across gain, Ciss and load corners with 1 kohm/10 nF; 0.94 W in the MOSFET at 300 mA (52 K rise at 55 K/W).
- Plate driver: 8.6% overshoot without feedback capacitance; 10 pF removes it (linear to 0.001%, settles in 3.9 us into 300 pF of cable).
- BOM errors caught by the checks: a 100 mohm shunt where 1 ohm was needed; the ballast and sense resistors were missing.

## WP4 schematic: what was built, found and decided (2026-10-24)

Files: `hardware/instrument/schematic/` (`main_board.py`, `heads.py`, `generate.py`, `schematic_test.py`), `hardware/instrument/lib/` (the `jlc` symbol and footprint libraries from `easyeda2kicad`, one symbol per BOM part, each with its LCSC number in the symbol's "LCSC Part" field). The test is in the smoke tests; it checks pin accounting (every pin on a net with another pin or in `ALLOWED_OPEN` with a data-sheet reason), pins that need a given net (`EXPECT`), every symbol pin against its footprint's pads, the five boards' parts against `parts.BOM`, and design numbers. It was mutation-checked: a pin pulled off its net and a supply pin moved to GND both fail it.

Defects the work caught (all fixed in the BOM and schematic):
- The supply-entry ferrite bead (C1002, 600 ohm) is rated 200 mA with 450 mohm DCR, but the 5 V rail carries up to 389 mA: the entry and boost-input beads are now C14709 (120 ohm, 2 A, basic); C1002 stays on 3V3_A (under 50 mA).
- The RP2040 crystal (C9002) had 20 pF load and 80 ohm ESR; the hardware design guide wants 10 pF and 50 ohm max and says any deviation needs extensive testing. Now ABM8-272-T3 (C20625731, extended, 3,856 in stock) with 15 pF caps and a 1 kohm in series with XOUT.
- 25 V-rated 10 uF capacitors would have lost most of their capacitance at the boost's 24 V: boost output and filter use 4.7 uF 50 V (C132170).
- The MCP4728 cannot output 4.096 V from a 3.3 V supply (see requirements.md).
- The BOM's quantities were estimates; the schematic fixed them (the test enforces equality).

Design choices worth knowing: ADS131A04 with AVSS on ground and the negative charge pump on (VNCP to AVSS through three 100 nF in parallel, about the required 270 nF; the firmware must enable it), internal reference (1 uF on REFP-REFN and on REFEXT), M0 and M1 high (asynchronous interrupt mode, 32-bit words), M2 low, 100 kohm pull-up on DOUT, DONE and pin 24 floating; each input through 1 kohm legs with 1 nF across the pair; channels 1-4 = photodiode head, reference photodiode, shunt, plate monitor (the plate and the 24 V rail each have a 100k/10k divider, 2.19 V full scale). LED2's reference photodiode output goes to the RP2040's ADC3 (MON_SPARE), because the ADC has only four channels. The boost feedback is 200 kohm over 5.1 kohm, 24.1 V. Spare GPIOs are on four 2-pin headers; SWD on a fifth.

Pitfalls (SKiDL 3.0, KiCad symbols from easyeda2kicad):
- `net_a += net_b` merges the nets and keeps ONE name (the netlist then has no "3V3_D" if another net was named later): build() must alias one Net object (`iov = v3d`), and `schematic_test.py` fails if any name asked for does not survive. Rebinding a net with `+=` inside a nested function makes it a local variable: use `.__iadd__` or `net(name)`.
- The circuit is `builtins.default_circuit`, not importable from skidl. Use `-I` and put the schematic directory on `sys.path` yourself.
- The easyeda2kicad symbols come with pin types "unspecified" (ICs) or "input" (passives). `hardware/instrument/lib/set_pin_types.py` sets data-sheet types for the 12 IC/connector symbols in its TABLE and makes every other symbol passive (idempotent; rerun after regenerating the library). PWR_FLAG parts carry LCSC "C0" and are skipped by the BOM and footprint checks. Nets fed through a fuse, bead, inductor or filter resistor have no power-output pin and need a PWR_FLAG.
- **ERC is run on the netlist** (`schematic_test.py::check_erc`), not with `kicad-cli sch erc` on SKiDL's sheets: SKiDL's drawn wiring produces false errors (a flag shown attached to an op-amp output, `multiple_net_names`) while the netlist is right. The rules: power inputs need a power output or flag on the net; inputs need an output/bidirectional/power-output pin on the net or, through resistors, on a joined net; one driving part per net (a connector's two VBUS contacts are one part); no unspecified pins. Waivers (crystal-driven XIN, the RP2040's RUN pull-up, the debug probe, signals driven by a head over its cable) are in `ERC_WAIVERS` with reasons. Mutation-checked: removing the V24 flag fails it.
- `generate_schematic()` places and routes one flat sheet: it did not finish on the 169-part main board in 15 CPU-minutes, and on the head boards it routes only some of the time even with `retries=6` (different boards fail on different runs). Treat sheets as best effort (backlog WP4e).
- Tactile switch TS-1187A-B-A-B: wire only the diagonal pins (1 and 4); the pairs on one side are common, the contact bridges the sides.
- EasyEDA has no entry for C21900468 (the ADC crystal, HTTP 403): the 3.2 x 2.5 mm 4-pad symbol and footprint of the 12 MHz crystal stand in (pads 1 and 3 the crystal, 2 and 4 ground). Check against the 3X016384UP data sheet before layout.
- Component values come from the LCSC attribute list (`jlc search ... --json`, "Current Rating", "Load Capacitance", "ESR") and are a quick way to check a part against a design requirement.

## Open points before layout (WP5)

0. Panel rule (2026-10-27): the Standard PCBA the two Standard-only sensors force needs boards of at least 70 x 70 mm with edge rails; the heads ride on the main board's panel. See `docs/fabrication.md`.

1. Symbol/footprint verification is done where a source was reachable (2026-10-24): TMP117 pins, VBPW34S polarity and land pattern, SS14 and IR26-21C polarity. Unverified and queued as a WP7 precheck in JLC's placement preview: KT-0603R polarity, the ADC crystal's pad numbering, USBLC6 pin 1, JST tab pins, TS-1187A pairs.
2. The 24 V boost ripple is bounded by simulation (`sim/boost.spice`, smoke checks): worst case 0.29 V p-p at the plate driver's supply, about 1 kHz, 0.76 pN of plate force with PSRR assumed 80 dB. The assumptions to confirm at bring-up (WP9): the MT3608's real light-load behaviour (burst hysteresis and minimum on-time), and the OPA197's PSRR near 1 kHz; the RP2040's 12-bit ADC on MON_24V cannot see the ripple, so use the plate output on ADS131A04 channel 4. Analog ground partitioning is a layout rule: the plate driver and LED sinks are the noisiest blocks.
3. The real photocurrent (assumed 100 uA at mid-flag): the A5 prototype measures it, and Rf may change.
4. A5 itself, with the balance as built (FR4 arm): the measured noise spectrum, before layout or the electronics order. WP5 (layout) and WP7 (order) wait on A5.
5. TI SPICE macro models for the TLV9062 and OPA197 replace the behavioral models.

## Firmware layer (WP8): the ADS131A04 driver and what is unverified

`hardware/instrument/firmware/`: `ads131a04.py` (driver), `fake_ads131a04.py` (simulated device), `test_ads131a04.py` (host tests, in the smoke tests), `bringup_adc.py` (board and host). Protocol facts used (SBAS590E): SPI mode CPOL 0, CPHA 1; M1 high = 32-bit words (16-bit command/status in the MSBs, 24-bit data MSB-aligned); a command is acknowledged in the first word of the NEXT frame; after RESET the device sends READY (0xFFdd) in one-word frames and needs UNLOCK (0x0655); frame is one word until FIXED (six words) or ADCs/CRC change it, so D_SYS_CFG is written FIRST and the following frame is already six words with CRC; the ADCs are enabled together (ADC_ENA = 0x0F) and WAKEUP starts conversions; fMOD = fCLKIN / CLK_DIV / ICLK_DIV, rate = fMOD / OSR (CLK1 0x02, CLK2 0x25: 16.384 MHz -> 4.096 MHz -> 8 kSPS); the SPI clock is 4 MHz (a 24-byte frame is 48 us of the 125 us period).
Unverified against silicon (the fake encodes the same reading, so tests cannot catch these): (1) the CRC coverage in 32-bit mode with CRC_MODE = 1 (here: every byte before the CRC word, padding included); (2) the charge pump and reference settling time (the driver waits 20 ms; not given in the text read); (3) the READY frame length and the first frame after RESET; (4) STAT_1/STAT_S bit meanings (the bring-up script only requires them to read zero); (5) DRDY timing (the bring-up script polls it); (6) whether CS may be left high between frames at 8 kSPS without DONE handshaking. The bring-up script on the board is the check.

MCP4728 (`firmware/mcp4728.py`, data sheet DS22187E): factory EEPROM = internal 2.048 V reference, gain 1, data 0 (0 V out at power-up); Multi-Write `0x40 | ch << 1` + [VREF PD1 PD0 GX D11..D8][D7..D0] updates only the DAC input register (LDAC is low, so the output follows at once); Fast Write (2 bytes per channel from A) keeps the reference and gain; Single (0b01011) and Sequential (0b01010) Write also program the EEPROM and are never used. The read-back byte layout in `read_back()` is my reading (6 bytes per channel: input register then EEPROM; the figure was not in the copy of the data sheet that downloaded) and is unverified; the 12-bit step is 0.8 mV on VDD (plate 4.6 mV) and 0.5 mV on the internal reference (LED current 10 uA).



Sensors (`firmware/sensors.py`): TMP117 (ID 0x0117, 7.8125 mK per count, continuous conversion is the factory default); MMC5983MA (product ID 0x30 at register 0x2F, 18-bit unsigned counts with the null at 131072 and 16384 counts per gauss, control register 0 at 0x09: TM_M 0x01, SET 0x08, RESET 0x10; the field is (m1 - m2) / 2 and the bridge offset (m1 + m2) / 2 - null; Meas_M_Done is bit 0 of status 0x08; 8 ms per measurement at the 100 Hz bandwidth; the 10 uF CAP reservoir needs a few ms between SET and RESET); LIS2DW12 (UNVERIFIED, from memory: WHO_AM_I 0x44, CTRL1 0x44 = 50 Hz high-performance, CTRL2 0x0C, CTRL6 0x04, 0.244 mg per count at +-2 g in 14-bit left-justified data). Bring-up script: `bringup_sensors.py`.

Lock-in (`firmware/lockin.py`): the carrier is the LED gated on for 4 and off for 4 ADC samples (1 kHz at 8 kSPS), locked to the frame count in firmware, so the demodulation phase is a whole number of samples that `best_phase` finds at bring-up (the offset is (8 - d) % 8 for an optical delay of d samples; the signed maximum assumes the light rises when the LED turns on). Per-period sums of x times a +-1 reference cancel DC and ambient light exactly (a per-sample integrator does not: its state is a triangle wave inside the period); a leaky integrator of 2^9 periods (0.5 s, noise bandwidth about 0.3 Hz) follows; A = y / 4. A viper port needs 16-bit input (24-bit input drives the state to 2^32). Mains at 50 Hz is a whole 20 periods; 60 Hz relies on the low-pass.

Host side (`firmware/protocol.py`, `host/`): the stream is framed 0xA5 0x5A | type | seq | length | payload | CRC-16 (the ADC's CRC); the decoder resynchronizes by searching for the sync pattern after a bad CRC or garbage (a false sync inside a payload costs one skipped pair and is retried); gaps in the 8-bit sequence number are counted. A 32-frame ADC packet at 8 kSPS is 4 ms of data (5 + 512 bytes, 129 kB/s: about 1 Mbit/s of the CDC link). Run the logger as `python hardware/instrument/host/logger.py --port /dev/ttyACM0 --out run1` (from WSL, attach the Pico with usbipd first) and `analyze.py run1_adc.csv --channel 1`. Nothing here has been run against the real board.

