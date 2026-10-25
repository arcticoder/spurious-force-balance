"""
mcp4728.py — driver for the instrument's MCP4728 quad DAC (WP8), with the board's safety limits in code.

Channels (schematic/main_board.py): A LED1 reference, B plate driver, C device-current set point, D LED2 reference. I2C0 address 0x60, LDAC tied low,
so an output changes at the acknowledge of the last byte. Rules this driver enforces:
  - only the commands that leave the EEPROM alone: Multi-Write (0x40 | channel << 1: data, reference, power-down and gain) and Fast Write. The Single and
    Sequential Write commands also program the EEPROM (limited endurance, and they change the power-up values) and are not implemented;
  - the factory EEPROM state is 0 V on every channel (internal 2.048 V reference, gain 1, data 0), which is the safe power-up state;
  - limits: LED current <= 20 mA (reference <= 1.02 V across the 51 ohm sense resistor), plate <= 18.8 V (gain 5.7 on the 3.3 V DAC's full scale),
    device current <= 300 mA (set point = DAC / 11 across the 1 ohm shunt). A request above a limit raises ValueError and writes nothing.
The LED channels use the internal 2.048 V reference (0.5 mV per code); the plate and device channels use VDD as reference (0.8 mV per code at 3.3 V).
"""

ADDR = 0x60
CH_LED1, CH_PLATE, CH_DUT, CH_LED2 = 0, 1, 2, 3

VDD = 3.3  # the analog rail (LP5907-3.3, +-2%); a measured value can be passed to the constructor
VREF_INT = 2.048
R_SENSE = 51.0  # ohm, LED current sense (main_board.py)
LED_MAX_A = 0.020
PLATE_GAIN = 5.7  # 47k / 10k + 1
PLATE_MAX_V = 18.8
DUT_DIVIDER = 11.0  # 10k / 1k + 1: DAC volts = 11 x shunt volts
DUT_SHUNT = 1.0  # ohm
DUT_MAX_A = 0.300


class MCP4728:
    """i2c: object with writeto(addr, buf) and readfrom(addr, n) (machine.I2C or the fake)."""

    def __init__(self, i2c, addr=ADDR, vdd=VDD):
        self.i2c, self.addr, self.vdd = i2c, addr, vdd
        # per channel: use the internal 2.048 V reference (True) or VDD (False)
        self.vref_internal = [True, False, False, True]
        self.codes = [0, 0, 0, 0]

    # -- scaling ------------------------------------------------------------------------------------------------------------------------------
    def volts_to_code(self, ch, volts):
        full = VREF_INT if self.vref_internal[ch] else self.vdd
        code = int(volts / full * 4096 + 0.5)
        return max(0, min(4095, code))

    def code_to_volts(self, ch, code):
        return code / 4096 * (VREF_INT if self.vref_internal[ch] else self.vdd)

    # -- writes -------------------------------------------------------------------------------------------------------------------------------
    def write_channel(self, ch, code):
        """Multi-Write: DAC input register only (EEPROM untouched), with the reference, normal power-down and gain 1 for this channel."""
        if not 0 <= code <= 4095:
            raise ValueError("code %d out of range" % code)
        vref = 0x80 if self.vref_internal[ch] else 0
        self.i2c.writeto(self.addr, bytes((0x40 | (ch << 1), vref | (code >> 8), code & 0xFF)))
        self.codes[ch] = code

    def fast_write(self, codes):
        """Fast Write of all four channels (keeps each channel's reference and gain from the last Multi-Write): 2 bytes per channel."""
        if len(codes) != 4 or any(not 0 <= c <= 4095 for c in codes):
            raise ValueError("four codes of 0..4095")
        buf = bytearray()
        for c in codes:
            buf += bytes((c >> 8, c & 0xFF))  # PD1 PD0 = 00 (normal)
        self.i2c.writeto(self.addr, bytes(buf))
        self.codes = list(codes)

    def all_off(self):
        for ch in range(4):
            self.write_channel(ch, 0)

    def power_up(self):
        """Safe start: write every channel to 0 V with the references this board uses before anything is enabled."""
        self.all_off()

    # -- physical setters, with the limits -------------------------------------------------------------------------------------------------
    def set_led_current(self, ch, amps):
        if ch not in (CH_LED1, CH_LED2):
            raise ValueError("not an LED channel")
        if not 0 <= amps <= LED_MAX_A:
            raise ValueError("LED current %.4f A outside 0..%.3f A" % (amps, LED_MAX_A))
        self.write_channel(ch, self.volts_to_code(ch, amps * R_SENSE))

    def set_plate_voltage(self, volts):
        if not 0 <= volts <= PLATE_MAX_V:
            raise ValueError("plate voltage %.2f V outside 0..%.1f V" % (volts, PLATE_MAX_V))
        self.write_channel(CH_PLATE, self.volts_to_code(CH_PLATE, volts / PLATE_GAIN))

    def set_dut_current(self, amps):
        if not 0 <= amps <= DUT_MAX_A:
            raise ValueError("device current %.3f A outside 0..%.3f A" % (amps, DUT_MAX_A))
        self.write_channel(CH_DUT, self.volts_to_code(CH_DUT, amps * DUT_SHUNT * DUT_DIVIDER))

    # -- read back ------------------------------------------------------------------------------------------------------------------------------
    def read_back(self):
        """The four input registers: list of (internal_vref, power_down, gain2, code). Layout read as 6 bytes per channel (input register, then EEPROM),
        3 bytes each: [RDY/BSY POR DAC1 DAC0 0 A2 A1 A0] [VREF PD1 PD0 GX D11..D8] [D7..D0]. Unverified against the chip."""
        raw = self.i2c.readfrom(self.addr, 24)
        out = []
        for ch in range(4):
            b = raw[ch * 6:ch * 6 + 3]
            out.append((bool(b[1] & 0x80), (b[1] >> 5) & 3, bool(b[1] & 0x10), ((b[1] & 0x0F) << 8) | b[2]))
        return out
