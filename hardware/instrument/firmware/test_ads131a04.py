"""
test_ads131a04.py — pass/fail checks of the ADS131A04 driver against the simulated device (WP8).

    ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/test_ads131a04.py

These prove the driver implements the data sheet as read; they do not prove the real chip behaves the same (bringup_adc.py does that on the board).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

import ads131a04 as A  # noqa: E402
import fake_ads131a04 as F  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


def make(signals=(0, 0, 0, 0)):
    dev = F.FakeADS131A04(signals=signals)
    drv = A.ADS131A04(dev, dev.cs, dev.reset, dev.drdy)
    return dev, drv


# 1. the CRC against the standard check value of CRC-16/CCITT-FALSE
check("CRC-16/CCITT-FALSE of '123456789' is 0x29B1 (the published check value)", A.crc16(b"123456789") == 0x29B1, "0x%04X" % A.crc16(b"123456789"))

# 2. data rate and code scaling from the register values
rate = A.data_rate()
check("CLK1/CLK2 values give 8 kSPS from the 16.384 MHz crystal (fMOD 4.096 MHz, OSR 512)", abs(rate - 8000) < 1e-6, "%.1f Hz" % rate)
check("the default register values (CLK_DIV 8, ICLK_DIV 8, OSR 400) give 16.384e6 / 8 / 8 / 400 = 640 Hz", abs(A.data_rate(0x08, 0x86) - 640) < 1e-6, "%.1f Hz" % A.data_rate(0x08, 0x86))
check("code 0x7FFFFF is +VREF - 1 LSB and 0x800000 is -VREF", abs(A.code_to_volts(0x7FFFFF) - (2.442 - 2 * 2.442 / 2**24)) < 1e-12 and abs(A.code_to_volts(0x800000) + 2.442) < 1e-12, "")

# 3. bring-up against the simulated device
dev, drv = make()
try:
    did = drv.start(settle_ms=0)
    check("start(): READY, UNLOCK, configuration, ADCs enabled and WAKEUP all acknowledged", True, "device ID byte 0x%02X" % did)
except A.ADSError as e:
    check("start(): READY, UNLOCK, configuration, ADCs enabled and WAKEUP all acknowledged", False, str(e))
expected = {A.A_SYS_CFG: 0xE8, A.D_SYS_CFG: 0x7F, A.CLK1: 0x02, A.CLK2: 0x25, A.ADC_ENA: 0x0F}
got = {k: dev.regs[k] for k in expected}
check("registers after start(): charge pump on, internal 2.442 V reference, fixed frame with CRC, 8 kSPS, four ADCs", got == expected, "{%s}" % ", ".join("0x%02X: 0x%02X" % kv for kv in got.items()))
check("A_SYS_CFG enables the negative charge pump (VNCPEN, bit 7) and the internal reference (INT_REFEN, bit 3), REFP at 2.442 V (VREF_4V = 0)", dev.regs[A.A_SYS_CFG] & 0x88 == 0x88 and not dev.regs[A.A_SYS_CFG] & 0x10, "0x%02X" % dev.regs[A.A_SYS_CFG])
check("the device is awake, unlocked, and no frame-size or CRC error was flagged", dev.awake and not dev.locked and dev.regs[A.STAT_1] == 0, "STAT_1 = 0x%02X" % dev.regs[A.STAT_1])

# 4. register read back
check("read_reg returns what was written (CLK2)", drv.read_reg(A.CLK2) == 0x25, "")

# 5. samples
volts = (1.0, -0.5, 0.0123, -2.4)
dev, drv = make(volts)
drv.start(settle_ms=0)
codes, status = drv.read_samples()
lsb = 2 * 2.442 / 2**24
err = max(abs(A.code_to_volts(c) - v) for c, v in zip(codes, volts))
check("four channels decode to the input voltages within 1 LSB (positive and negative)", err <= lsb, "worst error %.2e V, LSB %.2e V" % (err, lsb))
dev.signals = [3.0, -3.0, 0, 0]
codes, _ = drv.read_samples()
check("inputs beyond full scale clip at 0x7FFFFF and 0x800000", codes[0] == 0x7FFFFF and codes[1] == -0x800000, str(codes[:2]))

# 6. integrity
dev.corrupt_dout_crc = 1
try:
    drv.read_samples()
    check("a bad DOUT CRC raises ADSError", False)
except A.ADSError:
    check("a bad DOUT CRC raises ADSError", True)
check("the next frame recovers (CRC good again)", len(drv.read_samples()[0]) == 4)

dev, drv = make()
drv.start(settle_ms=0)
orig = dev.write_readinto


def bad_din(tx, rx):
    tx = bytearray(tx)
    tx[-1] ^= 0xFF  # damage the CRC word on DIN (the low bytes are padding; flip the CRC byte)
    tx[-4] ^= 0xFF
    orig(tx, rx)


dev.write_readinto = bad_din
before = dev.regs[A.CLK1]
try:
    drv.write_reg(A.CLK1, 0x04)
except A.ADSError:
    pass
dev.write_readinto = orig
check("a command with a bad CRC on DIN is ignored by the device and flagged F_CHECK", dev.regs[A.CLK1] == before and dev.regs[A.STAT_1] & F.F_CHECK, "CLK1 0x%02X, STAT_1 0x%02X" % (dev.regs[A.CLK1], dev.regs[A.STAT_1]))

# 7. a frame of the wrong length is flagged
dev, drv = make()
drv.start(settle_ms=0)
drv.words = 3
drv.crc = False
drv.frame(A.NULL)
check("a frame of the wrong length sets F_FRAME", dev.regs[A.STAT_1] & F.F_FRAME, "STAT_1 0x%02X" % dev.regs[A.STAT_1])

# 8. locked device ignores configuration
dev = F.FakeADS131A04()
drv = A.ADS131A04(dev, dev.cs, dev.reset, dev.drdy)
drv.hardware_reset()
drv.frame(A.NULL)
try:
    drv.write_reg(A.CLK1, 0x02)
except A.ADSError:
    pass
check("a locked device (before UNLOCK) does not accept a register write", dev.regs[A.CLK1] == 0x08, "CLK1 0x%02X" % dev.regs[A.CLK1])

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
