# Bringing up the electronics

For the day the JLC-assembled boards arrive (the main board with its two heads, or first the sensor-head panel). Each step says what to do, the `[PASS]` line to expect, and what a `[FAIL]` means. Nothing here has
been run on real hardware yet: the drivers were tested against simulated chips, and the lists of assumptions that only the real chips can confirm are in `docs/kb/instrument_electronics_notes.md`. Record every
surprise in the test log, because the surprises are the point of this procedure.

You need: the board, a USB-C cable to the host, a Pico or the board's own RP2040, the host with WSL (attach the USB device to WSL with `usbipd attach`; the serial port then appears as `/dev/ttyACM0`), a multimeter,
and for the analog steps a 10 ohm 1 W resistor and a 2.2 kohm resistor pair (below). Copy the firmware with `mpremote cp hardware/instrument/firmware/*.py hardware/instrument/pins.py :`.

## 0. Before power

1. Look at the board: the USB-C receptacle seated, both JST-SH connectors per head in place, no part visibly rotated or missing (compare with `hardware/instrument/schematic/out/*.net` and the CPL). JLC's placement
   preview was approved at order time; this is the physical check.
2. With nothing plugged in, measure resistance between 5 V (USB VBUS pad or the fuse's output) and ground, and between each 3.3 V rail and ground: tens of kilohms or more, not a short.

## 1. First power and the rails

1. Plug the board into a USB port that shows current (a USB power meter, or the host's own readout). Expect under 100 mA: the measurement mode budget is 89 mA (`pins.py`). The polyfuse holds 0.75 A, so a short
   shows as a hot board and a hot fuse: unplug at once.
2. Measure with the multimeter: 5 V rail 4.75 to 5.25 V, 3V3_D and 3V3_A 3.23 to 3.37 V (LP5907-3.3, +-2%), and the 24 V rail 0 V (the boost is off until `BOOST_EN` goes high, with its 100 k pulldown).
   A 3V3_A that differs from 3V3_D by more than 30 mV means the ferrite bead is carrying more current than expected.
3. Hold BOOTSEL while plugging in: the RP2040 should appear as a USB drive. If it does not, the 12 MHz crystal circuit (ABM8-272-T3, 15 pF capacitors, the 1 kohm on XOUT) or the flash is at fault.

## 2. Sensors and DAC: `bringup_sensors.py`

Run `mpremote run hardware/instrument/firmware/bringup_sensors.py`. Expected: a scan with 0x60, 0x49 and 0x18 (and 0x48, 0x30, 0x4A if the heads are plugged in), then `[PASS]` for the DAC at 0 V, each TMP117 between 5 and 45 C,
the LIS2DW12 at 1 g within 10% when the board rests, and the magnetometer's field between 0.05 and 1.5 G.
- A missing address: check the head's cable and that the board has 2.2 kohm pull-ups to 3V3_D (they are on the main board; on a bare head add two 2.2 kohm resistors on a breadboard).
- The LIS2DW12 fails first if its register values (from memory, unverified) are wrong: read its WHO_AM_I and the data sheet before trusting any acceleration.
- |B| far above 0.65 G: a magnet or steel is near the head; move it away (the damper's 6 mm N42 discs are fixed to the base, away from the heads).

## 3. The ADC: `bringup_adc.py`

Run it with the photodiode head and the shunt connected as in the experiment, or with the inputs shorted for a noise floor. Expected: the READY word, `RESET, READY, UNLOCK, configuration, ADC enable and WAKEUP all acknowledged`,
the five registers read back (charge pump on, internal reference, fixed frame with CRC, the clock settings), STAT_1 and STAT_S zero, DRDY at 8 kHz within 10%, and four channels that are neither stuck nor at full scale.
- No READY word: the RESET line, the 16.384 MHz crystal (it needs 5 ms or more to start), or SPI mode (CPOL 0, CPHA 1).
- CRC errors on the data frames: the CRC coverage in 32-bit words is the first thing in the unverified list; try CRC_MODE 0 in `ads131a04.py` (`D_SYS_CFG_VALUE`) and write down which one works.
- A DRDY rate of half or double: CLK1/CLK2 or the crystal frequency.
- A channel at full scale with nothing connected: the input is floating; the 1 kohm legs should hold it near ground: check the leg resistors and the solder.
- Noise: write the rms counts per channel in the log; `host/analyze.py` gives the spectrum from a logged run. The readout's budget is 146 pm/rtHz (`tools/force_noise_budget.py`); a much higher floor is a layout or grounding
  problem, not a firmware one.

## 4. The analog blocks, one at a time (each with the load that cannot hurt)

These steps use the drivers directly from the REPL (`mpremote repl`); a script (`bringup_analog.py`) is a blocked task, to be written once the board exists. Always start from `mcp4728.MCP4728(i2c).power_up()` (all channels 0 V) and
end with `all_off()`.
1. **LED sink:** the LED head connected. Set `set_led_current(CH_LED1, 0.005)`, drive `LED1_MOD` high. Expect 5 mA (the sense node, GP28 `MON_LED`, reads 0.255 V); step to 0.010 then 0.020 A. At 20 mA GP28 reads 1.02 V.
   Drive `LED1_MOD` low: the current must fall to zero. If the current does not follow, the op-amp loop is oscillating (look at the node with the ADC at full speed).
2. **Plate driver:** with nothing on the plate connector, set `BOOST_EN` high: the 24 V rail rises to about 24.1 V (GP26 `MON_24V` reads about 2.19 V). Set `set_plate_voltage(5.0)`; ADS131A04 channel 4 should read 0.4545 V
   (the divider is 1/11), within 3%. Step to 10, 15, 18.8 V and fit a line: gain 5.7 within 1%, offset under 20 mV. Then `all_off()` and `BOOST_EN` low.
3. **Device-current sink:** connect the 10 ohm 1 W resistor between the device connector's two pins. `DUT_EN` high, `set_dut_current(0.1)`: the shunt (ADS131A04 channel 3) reads 0.100 V (1 ohm shunt) within 3%, and a multimeter in series
   reads 100 mA. Step to 0.2 and 0.3 A (at 300 mA the MOSFET dissipates about 0.9 W and the 4.7 ohm ballast 0.4 W: the MOSFET rises about 50 K over ambient, so do not hold it, and keep 300 mA runs to a minute). With `DUT_EN` low the current must be zero whatever the DAC says.
4. **Motors:** each coin motor on its connector, PWM duty 30% then 60% (the cap): it spins; a duty above 60% is refused in firmware (the device-side `main.py` is blocked; until then keep the duty at or under 60% by hand).
5. **Power budget:** repeat step 1's USB current reading with all of the above on: measurement mode 89 mA, lead-current run 389 mA, disturbance run 329 mA (`pins.py`). More than 450 mA: stop and measure each load.

## 5. Sign-off

Fill this table in the test log before the board goes near the balance.

| Check | Expected | Measured |
|---|---|---|
| USB current idle | < 100 mA | |
| 5 V / 3V3_D / 3V3_A | 4.75-5.25 / 3.23-3.37 / 3.23-3.37 V | |
| ADC registers read back; STAT_1, STAT_S | as written; 0 | |
| DRDY rate | 8 kHz +-10% | |
| ADC noise (shorted inputs) | write it down | |
| LED current 20 mA | 1.02 V on GP28 | |
| 24 V rail; plate gain | 24.1 V; 5.7 +-1% | |
| Device current 100/200/300 mA | +-3% | |
| TMP117 vs a second thermometer | +-0.3 C | |
| Field |B| | 0.25-0.65 G typical | |

Then continue with `docs/procedures.md`.
