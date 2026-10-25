"""
ads131a04.py — driver for the instrument's ADS131A04 (WP8). MicroPython on the RP2040 and CPython on the host (against fake_ads131a04.py).

Wiring (schematic/main_board.py): M0 high = asynchronous interrupt mode, M1 high = 32-bit device words, M2 low = no Hamming code;
SPI0 on GP16-19, DRDY on GP20, RESET on GP21; a 16.384 MHz crystal; AVSS on ground, so the negative charge pump must be enabled (VNCPEN)
before the inputs go below ground. Everything below is from SBAS590E (sections 9.4-9.6) and is checked against a simulated device;
what the real chip does differently is found at bring-up (bringup_adc.py).

Frame (fixed, CRC on): six 32-bit words on DIN and DOUT.
    DIN : command (16 MSBs), 0, 0, 0, 0, CRC (16 MSBs)        DOUT: status/response (16 MSBs), ch1..ch4 (24-bit two's complement, MSB first), CRC
A command is acknowledged in the FIRST word of the NEXT frame. The CRC is CRC-16/CCITT (poly 0x1021, init 0xFFFF) over every byte before the CRC
word (CRC_MODE = 1). Until FIXED and CRC_EN are written the frame is ONE word (the device is in dynamic-frame mode with the ADCs off).
"""

import time

# commands (16 bits)
NULL, RESET, STANDBY, WAKEUP, LOCK, UNLOCK = 0x0000, 0x0011, 0x0022, 0x0033, 0x0555, 0x0655
READY_PREFIX = 0xFF00  # READY response: 0xFFdd, dd = the device ID byte

# registers
ID_MSB, ID_LSB, STAT_1, STAT_P, STAT_N, STAT_S, ERROR_CNT, STAT_M2 = 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07
A_SYS_CFG, D_SYS_CFG, CLK1, CLK2, ADC_ENA = 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
ADC1, ADC2, ADC3, ADC4 = 0x11, 0x12, 0x13, 0x14

# register values this board uses
A_SYS_CFG_VALUE = 0x80 | 0x40 | 0x20 | 0x08  # VNCPEN, HRM (high resolution), reserved bit 5 = 1, INT_REFEN; VREF_4V = 0: REFP = 2.442 V
D_SYS_CFG_VALUE = 0x40 | 0x30 | 0x0C | 0x02 | 0x01  # CRC_MODE = 1, DNDLY = HIZDLY = 3 (defaults), FIXED, CRC_EN
CLK1_VALUE = 0x02  # CLK_DIV = 001: fICLK = fCLKIN / 2 = 8.192 MHz
CLK2_VALUE = 0x20 | 0x05  # ICLK_DIV = 001: fMOD = fICLK / 2 = 4.096 MHz; OSR = 0101 (512): 8 kSPS
VREF = 2.442
FCLKIN = 16.384e6
WORD_BYTES = 4
FRAME_WORDS = 6
OSR_TABLE = (4096, 2048, 1024, 800, 768, 512, 400, 384, 256, 200, 192, 128, 96, 64, 48, 32)
DIV_TABLE = (None, 2, 4, 6, 8, 10, 12, 14)  # for CLK_DIV and ICLK_DIV


class ADSError(Exception):
    pass


def crc16(data, crc=0xFFFF):
    """CRC-16/CCITT-FALSE: polynomial 0x1021, initial 0xFFFF, no reflection."""
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def data_rate(clk1=CLK1_VALUE, clk2=CLK2_VALUE, fclkin=FCLKIN):
    """Output data rate in Hz from the CLK1 and CLK2 register values."""
    fmod = fclkin / DIV_TABLE[(clk1 >> 1) & 7] / DIV_TABLE[(clk2 >> 5) & 7]
    return fmod / OSR_TABLE[clk2 & 15]


def code_to_volts(code, gain=1, vref=VREF):
    """Differential input voltage of a 24-bit code, raw (0..0xFFFFFF) or already signed: 1 LSB = 2 x VREF / gain / 2^24."""
    if code >= 0 and code & 0x800000:
        code -= 1 << 24
    return code * 2 * vref / gain / (1 << 24)


def _word(msb16):
    return bytes((msb16 >> 8 & 0xFF, msb16 & 0xFF, 0, 0))


def sleep_ms(ms):
    (time.sleep_ms if hasattr(time, "sleep_ms") else lambda m: time.sleep(m / 1000))(ms)


class ADS131A04:
    """spi: object with write_readinto(tx, rx) (machine.SPI or the fake); cs, reset: objects with value(v); drdy: object with value()."""

    def __init__(self, spi, cs, reset, drdy=None, log=None):
        self.spi, self.cs, self.reset_pin, self.drdy = spi, cs, reset, drdy
        self.words = 1  # frame length until FIXED is written
        self.crc = False
        self.log = log
        self.cs.value(1)

    # -- frames -------------------------------------------------------------------------------------------------------------------------------
    def frame(self, command=NULL, extra=()):
        """One SPI frame: returns the list of 16/24-bit-meaningful words received (status, ch1..ch4, crc as ints) and checks the CRC."""
        n = self.words
        tx = bytearray(n * WORD_BYTES)
        tx[0:4] = _word(command)
        for i, w in enumerate(extra):  # additional device words (WREGS): 16 MSBs
            tx[(1 + i) * 4:(2 + i) * 4] = _word(w)
        if self.crc:
            c = crc16(tx[: (n - 1) * WORD_BYTES])
            tx[(n - 1) * 4:(n - 1) * 4 + 2] = bytes((c >> 8, c & 0xFF))
        rx = bytearray(n * WORD_BYTES)
        self.cs.value(0)
        self.spi.write_readinto(tx, rx)
        self.cs.value(1)
        if self.crc:
            got = (rx[(n - 1) * 4] << 8) | rx[(n - 1) * 4 + 1]
            want = crc16(rx[: (n - 1) * WORD_BYTES])
            if got != want:
                raise ADSError("DOUT CRC 0x%04X, expected 0x%04X" % (got, want))
        out = []
        for i in range(n):
            w = rx[i * 4:i * 4 + 4]
            out.append((w[0] << 24) | (w[1] << 16) | (w[2] << 8) | w[3])
        return out

    @staticmethod
    def response(words):
        return words[0] >> 16

    def command(self, cmd, extra=()):
        """Send a command and return its response word (read from the next frame, which is a NULL)."""
        self.frame(cmd, extra)
        return self.response(self.frame(NULL))

    # -- register access ------------------------------------------------------------------------------------------------------------------------
    def read_reg(self, addr):
        r = self.command(0x2000 | (addr << 8))
        if r >> 8 != (0x20 | addr):
            raise ADSError("RREG 0x%02X answered 0x%04X" % (addr, r))
        return r & 0xFF

    def write_reg(self, addr, value):
        r = self.command(0x4000 | (addr << 8) | value)
        if r != (0x2000 | (addr << 8) | value):
            raise ADSError("WREG 0x%02X=0x%02X answered 0x%04X" % (addr, value, r))

    # -- bring-up -------------------------------------------------------------------------------------------------------------------------------
    def hardware_reset(self):
        self.reset_pin.value(0)
        sleep_ms(1)  # tw(RSL) is a few microseconds
        self.reset_pin.value(1)
        sleep_ms(6)  # up to 4.5 ms to complete
        self.words, self.crc = 1, False

    def start(self, settle_ms=20):
        """Reset, unlock, configure (charge pump, internal reference, 16.384 MHz -> 8 kSPS, fixed frame with CRC), enable the ADCs and wake up.
        Returns the READY device ID byte."""
        self.hardware_reset()
        ready = self.response(self.frame(NULL))
        if ready >> 8 != 0xFF:
            raise ADSError("expected READY (0xFFdd), got 0x%04X" % ready)
        if self.command(UNLOCK) != UNLOCK:
            raise ADSError("UNLOCK was not acknowledged")
        # D_SYS_CFG first: it changes the frame size, so the next frame (the one that carries the acknowledgement) is already six words with a CRC
        self.frame(0x4000 | (D_SYS_CFG << 8) | D_SYS_CFG_VALUE)
        self.words, self.crc = FRAME_WORDS, True
        r = self.response(self.frame(NULL))
        if r != (0x2000 | (D_SYS_CFG << 8) | D_SYS_CFG_VALUE):
            raise ADSError("D_SYS_CFG write answered 0x%04X" % r)
        self.write_reg(A_SYS_CFG, A_SYS_CFG_VALUE)
        sleep_ms(settle_ms)  # charge pump and reference settle (the settling time is not in the data sheet's text: confirm on the bench)
        self.write_reg(CLK1, CLK1_VALUE)
        self.write_reg(CLK2, CLK2_VALUE)
        for reg in (ADC1, ADC2, ADC3, ADC4):
            self.write_reg(reg, 0)  # gain 1
        self.write_reg(ADC_ENA, 0x0F)
        if self.command(WAKEUP) != WAKEUP:
            raise ADSError("WAKEUP was not acknowledged")
        return ready & 0xFF

    def read_samples(self):
        """One data frame (call when DRDY falls): the four channels as signed 24-bit codes, and the status word of the previous command."""
        w = self.frame(NULL)
        codes = []
        for x in w[1:5]:
            c = x >> 8 & 0xFFFFFF
            codes.append(c - (1 << 24) if c & 0x800000 else c)
        return codes, w[0] >> 16
