"""
sensors.py — drivers for the instrument's I2C environment sensors (WP8): TMP117 (temperature), MMC5983MA (magnetic field), LIS2DW12 (acceleration).

All three take an object with readfrom_mem(addr, reg, n) and writeto_mem(addr, reg, buf) (machine.I2C or fake_sensors.FakeI2C). Addresses (schematic):
TMP117 0x49 on the main board, 0x48 on sensor head 1, 0x4A on head 2; MMC5983MA 0x30 (head 1); LIS2DW12 0x18 (main board).
Sources: TMP117 SNOSD82D, MMC5983MA Rev. A (MEMSIC). The LIS2DW12 register values are from memory of ST's data sheet (the download was blocked) and are
UNVERIFIED: check WHO_AM_I and the scaling on the bench before trusting its numbers.
"""

import time


class SensorError(Exception):
    pass


def _sleep_ms(ms):
    (time.sleep_ms if hasattr(time, "sleep_ms") else lambda m: time.sleep(m / 1000))(ms)


class TMP117:
    DEVICE_ID = 0x0117
    LSB_C = 0.0078125

    def __init__(self, i2c, addr=0x49):
        self.i2c, self.addr = i2c, addr

    def _reg(self, reg):
        b = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (b[0] << 8) | b[1]

    def check(self):
        did = self._reg(0x0F)
        if did != self.DEVICE_ID:
            raise SensorError("TMP117 at 0x%02X: device ID 0x%04X, expected 0x0117" % (self.addr, did))
        return did

    def read_c(self):
        """Temperature in degC from the result register (continuous conversion, the factory default: 8 averages, 1 s cycle). Reading it clears Data_Ready."""
        raw = self._reg(0x00)
        if raw & 0x8000:
            raw -= 0x10000
        return raw * self.LSB_C

    def data_ready(self):
        return bool(self._reg(0x01) & 0x2000)


class MMC5983MA:
    PRODUCT_ID = 0x30
    COUNTS_PER_GAUSS = 16384  # 18-bit operation
    NULL = 131072  # output at zero field, 18-bit

    def __init__(self, i2c, addr=0x30):
        self.i2c, self.addr = i2c, addr

    def _w(self, reg, v):
        self.i2c.writeto_mem(self.addr, reg, bytes((v,)))

    def check(self):
        pid = self.i2c.readfrom_mem(self.addr, 0x2F, 1)[0]
        if pid != self.PRODUCT_ID:
            raise SensorError("MMC5983MA at 0x%02X: product ID 0x%02X, expected 0x30" % (self.addr, pid))
        return pid

    def _measure_counts(self, timeout_ms=40):
        """One magnetic measurement (TM_M), bandwidth 100 Hz (8 ms): X, Y, Z as 18-bit unsigned counts."""
        self._w(0x09, 0x01)
        waited = 0
        while not self.i2c.readfrom_mem(self.addr, 0x08, 1)[0] & 0x01:  # Meas_M_Done
            _sleep_ms(2)
            waited += 2
            if waited > timeout_ms:
                raise SensorError("MMC5983MA measurement did not complete")
        d = self.i2c.readfrom_mem(self.addr, 0x00, 7)
        x = (d[0] << 10) | (d[1] << 2) | (d[6] >> 6)
        y = (d[2] << 10) | (d[3] << 2) | ((d[6] >> 4) & 3)
        z = (d[4] << 10) | (d[5] << 2) | ((d[6] >> 2) & 3)
        return x, y, z

    def read_gauss(self):
        """Field and bridge offset, by the data sheet's SET/RESET procedure: SET, measure (= +H + offset), RESET, measure (= -H + offset); H = (m1 - m2) / 2,
        offset = (m1 + m2) / 2 - null. The 10 uF CAP reservoir must recharge between the pulses (a few ms)."""
        self._w(0x09, 0x08)  # SET
        _sleep_ms(2)
        m1 = self._measure_counts()
        self._w(0x09, 0x10)  # RESET
        _sleep_ms(2)
        m2 = self._measure_counts()
        field = tuple((a - b) / 2 / self.COUNTS_PER_GAUSS for a, b in zip(m1, m2))
        offset = tuple(((a + b) / 2 - self.NULL) / self.COUNTS_PER_GAUSS for a, b in zip(m1, m2))
        return field, offset


class LIS2DW12:
    WHO_AM_I = 0x44  # unverified
    MG_PER_LSB = 0.244  # +-2 g, 14-bit high-performance mode (unverified)

    def __init__(self, i2c, addr=0x18):
        self.i2c, self.addr = i2c, addr

    def check(self):
        who = self.i2c.readfrom_mem(self.addr, 0x0F, 1)[0]
        if who != self.WHO_AM_I:
            raise SensorError("LIS2DW12 at 0x%02X: WHO_AM_I 0x%02X, expected 0x44" % (self.addr, who))
        return who

    def configure(self):
        """50 Hz, high-performance mode (CTRL1 0x44), block data update + address auto-increment (CTRL2 0x0C), +-2 g, low noise (CTRL6 0x04)."""
        self.i2c.writeto_mem(self.addr, 0x20, bytes((0x44,)))
        self.i2c.writeto_mem(self.addr, 0x21, bytes((0x0C,)))
        self.i2c.writeto_mem(self.addr, 0x25, bytes((0x04,)))

    def read_mg(self):
        """Acceleration in milli-g (x, y, z): the 16-bit result is left-justified 14-bit data."""
        d = self.i2c.readfrom_mem(self.addr, 0x28, 6)
        out = []
        for i in range(3):
            v = d[2 * i] | (d[2 * i + 1] << 8)
            if v & 0x8000:
                v -= 0x10000
            out.append((v >> 2) * self.MG_PER_LSB)
        return tuple(out)
