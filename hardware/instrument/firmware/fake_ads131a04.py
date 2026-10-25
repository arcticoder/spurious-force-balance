"""
fake_ads131a04.py — a simulated ADS131A04 for host tests of ads131a04.py and the bring-up script (WP8).

It encodes the protocol as read from SBAS590E (the driver is tested against this reading, not against silicon):
  - after RESET the device answers READY (0xFFdd) in one-word frames and ignores everything but UNLOCK (and NULL, RREG, LOCK);
  - a command is acknowledged in the first word of the NEXT frame (ACK = the command, REG = 001a aaaa dddd dddd, NULL = STAT_1 as a REG word);
  - the frame is one word until FIXED (six words) or the ADCs and CRC change it; with CRC_EN the last word carries CRC-16/CCITT of the words before it
    (CRC_MODE = 1: every byte before it), a bad CRC on DIN sets F_CHECK in STAT_1 and the command does not run (except WREGS);
  - a frame of the wrong length sets F_FRAME in STAT_1;
  - conversion data: `signals` gives the input voltage per channel (volts, differential, gain 1), converted with VREF = 2.442 V.
Not modelled: timing, DRDY behaviour beyond a counter, the digital filter, Hamming codes, WREGS, STANDBY/LOCK details.
"""

import ads131a04 as A

F_CHECK = 0x01  # STAT_1 bit positions are the model's own (the driver only reads the register back)
F_FRAME = 0x02


class Pin:
    def __init__(self, v=0):
        self.v = v

    def value(self, v=None):
        if v is None:
            return self.v
        self.v = v


class FakeADS131A04:
    def __init__(self, device_id=0x04, signals=(0.0, 0.0, 0.0, 0.0)):
        self.id = device_id
        self.signals = list(signals)
        self.cs, self.reset, self.drdy = Pin(1), Pin(1), Pin(1)
        self.corrupt_dout_crc = 0  # number of upcoming frames whose DOUT CRC is wrong
        self.frames = 0
        self._por()

    def _por(self):
        self.regs = {A.ID_MSB: 0x04, A.ID_LSB: 0x00, A.STAT_1: 0, A.A_SYS_CFG: 0x60, A.D_SYS_CFG: 0x3C, A.CLK1: 0x08, A.CLK2: 0x86, A.ADC_ENA: 0,
                     A.ADC1: 0, A.ADC2: 0, A.ADC3: 0, A.ADC4: 0}
        self.locked = True
        self.awake = False
        self.pending = 0xFF00 | self.id  # READY

    # -- frame geometry -----------------------------------------------------------------------------------------------------------------------
    def expected_words(self):
        d = self.regs[A.D_SYS_CFG]
        if self.locked and self.pending >> 8 == 0xFF:
            return 1
        if d & 0x02:
            return A.FRAME_WORDS
        n = 1 + (4 if self.regs[A.ADC_ENA] == 0x0F else 0) + (1 if d & 0x01 else 0)
        return n

    # -- the SPI interface the driver uses ----------------------------------------------------------------------------------------------------
    def write_readinto(self, tx, rx):
        # the reset pin low puts the device back to POR (the driver pulses it); modelled at the first frame after it was low
        self.frames += 1
        n = len(tx) // 4
        crc_en = bool(self.regs[A.D_SYS_CFG] & 0x01)
        if n != self.expected_words():
            self.regs[A.STAT_1] |= F_FRAME
        cmd = (tx[0] << 8) | tx[1]
        ok = True
        if crc_en and n > 1:
            got = (tx[(n - 1) * 4] << 8) | tx[(n - 1) * 4 + 1]
            ok = got == A.crc16(tx[: (n - 1) * 4])
            if not ok:
                self.regs[A.STAT_1] |= F_CHECK
        # build DOUT first (it carries the response to the PREVIOUS command), then execute this command
        out = bytearray(n * 4)
        out[0] = self.pending >> 8
        out[1] = self.pending & 0xFF
        if n > 1 and self.regs[A.ADC_ENA] == 0x0F:
            for ch in range(4):
                if 1 + ch < n - (1 if crc_en else 0) or A.FRAME_WORDS == n:
                    code = int(round(self.signals[ch] / (2 * A.VREF) * (1 << 24)))
                    code = max(-(1 << 23), min((1 << 23) - 1, code)) & 0xFFFFFF
                    out[(1 + ch) * 4:(2 + ch) * 4] = bytes((code >> 16, code >> 8 & 0xFF, code & 0xFF, 0))
        if crc_en and n > 1:
            c = A.crc16(out[: (n - 1) * 4])
            if self.corrupt_dout_crc:
                self.corrupt_dout_crc -= 1
                c ^= 0x0001
            out[(n - 1) * 4] = c >> 8
            out[(n - 1) * 4 + 1] = c & 0xFF
        rx[:] = out
        if ok or (cmd >> 13) == 3:  # WREGS does not check the CRC first (unused here)
            self._execute(cmd)

    # -- commands ------------------------------------------------------------------------------------------------------------------------------
    def _execute(self, cmd):
        if cmd == A.NULL:
            self.pending = 0x2000 | (A.STAT_1 << 8) | self.regs[A.STAT_1]
            return
        if cmd == A.RESET:
            self._por()
            return
        if cmd == A.UNLOCK:
            self.locked = False
            self.pending = cmd
            return
        kind = cmd >> 13
        if self.locked and kind != 1:  # locked: only NULL, RREG(S) and UNLOCK are accepted
            return
        if cmd in (A.STANDBY, A.WAKEUP, A.LOCK):
            self.awake = cmd == A.WAKEUP if cmd != A.LOCK else self.awake
            if cmd == A.LOCK:
                self.locked = True
            self.pending = cmd
            return
        addr = cmd >> 8 & 0x1F
        if kind == 1:  # RREG
            self.pending = 0x2000 | (addr << 8) | self.regs.get(addr, 0)
        elif kind == 2:  # WREG
            self.regs[addr] = cmd & 0xFF
            self.pending = 0x2000 | (addr << 8) | (cmd & 0xFF)
