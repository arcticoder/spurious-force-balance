"""
fake_mcp4728.py — a simulated MCP4728 on an I2C bus for host tests (WP8). Records every write so a test can prove which commands were sent.
Power-up state is the factory EEPROM: internal 2.048 V reference, gain 1, data 0 on every channel. Handles Multi-Write (0b01000), Fast Write (0b00xx)
and the 24-byte read; it flags the commands that program the EEPROM (Single 0b01011, Sequential 0b01010) in `eeprom_writes`.
"""


class FakeI2C:
    def __init__(self, addr=0x60):
        self.addr = addr
        self.writes = []
        self.eeprom_writes = 0
        self.vref = [1, 1, 1, 1]
        self.pd = [0, 0, 0, 0]
        self.gain = [0, 0, 0, 0]
        self.code = [0, 0, 0, 0]

    def writeto(self, addr, buf):
        if addr != self.addr:
            raise OSError(19)  # ENODEV
        buf = bytes(buf)
        self.writes.append(buf)
        c = buf[0] >> 3
        if c == 0b01000:  # Multi-Write, one or more 3-byte groups
            for i in range(0, len(buf), 3):
                ch = (buf[i] >> 1) & 3
                self.vref[ch] = buf[i + 1] >> 7
                self.pd[ch] = (buf[i + 1] >> 5) & 3
                self.gain[ch] = (buf[i + 1] >> 4) & 1
                self.code[ch] = ((buf[i + 1] & 0x0F) << 8) | buf[i + 2]
        elif c in (0b01010, 0b01011):
            self.eeprom_writes += 1
        elif buf[0] >> 6 == 0:  # Fast Write: 2 bytes per channel from A
            for ch in range(len(buf) // 2):
                self.pd[ch] = (buf[2 * ch] >> 4) & 3
                self.code[ch] = ((buf[2 * ch] & 0x0F) << 8) | buf[2 * ch + 1]
        else:
            raise ValueError("command not modelled: 0x%02X" % buf[0])

    def readfrom(self, addr, n):
        out = bytearray()
        for ch in range(4):
            reg = bytes((0xC0 | (ch << 1) | 0, (self.vref[ch] << 7) | (self.pd[ch] << 5) | (self.gain[ch] << 4) | (self.code[ch] >> 8), self.code[ch] & 0xFF))
            out += reg + reg  # input register, then the EEPROM image (not modelled separately)
        return bytes(out[:n])

    def volts(self, ch, vdd=3.3):
        full = 2.048 if self.vref[ch] else vdd
        return self.code[ch] / 4096 * full * (2 if self.gain[ch] else 1)
