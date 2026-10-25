"""
bringup_adc.py — ADS131A04 bring-up with [PASS]/[FAIL] lines (WP8). Same script on the board and on the host.

    on the Pico:   mpremote cp ads131a04.py bringup_adc.py ../pins.py :   then   mpremote run bringup_adc.py
    on the host:   ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/bringup_adc.py   (simulated device: tests the script itself)

Run with the photodiode head and the shunt connected as in the experiment, or with the inputs shorted for a noise floor. Checks: the READY word,
UNLOCK and configuration read-back (charge pump, reference, clock, fixed frame with CRC), STAT_1 clear, DRDY falling at the configured rate,
and per-channel statistics over 256 frames: none stuck, none at full scale. It reports volts and counts; it cannot judge the noise against the
experiment's needs: that is the A5 prototype measurement.
"""

import sys
import time

try:  # on the host the modules sit next to this file (python -I does not add the script directory)
    sys.path.insert(0, __file__.rsplit("/", 1)[0] or ".")
except NameError:  # mpremote run on the board
    pass

try:
    from machine import Pin, SPI  # the board
    ON_BOARD = True
except ImportError:
    ON_BOARD = False

import ads131a04 as A

try:
    import pins as P
except ImportError:  # copied next to this file on the board; on the host it sits one directory up
    sys.path.append("..")
    import pins as P

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + ((": " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def make_driver():
    gp = {n: v[0] for n, v in P.PINS.items()}
    if ON_BOARD:
        spi = SPI(0, baudrate=4_000_000, polarity=0, phase=1, bits=8, firstbit=SPI.MSB, sck=Pin(gp["ADC_SCK"]), mosi=Pin(gp["ADC_MOSI"]), miso=Pin(gp["ADC_MISO"]))
        cs = Pin(gp["ADC_CS"], Pin.OUT, value=1)
        rst = Pin(gp["ADC_RESET"], Pin.OUT, value=1)
        drdy = Pin(gp["ADC_DRDY"], Pin.IN)
        return A.ADS131A04(spi, cs, rst, drdy), None
    import fake_ads131a04 as F

    dev = F.FakeADS131A04(signals=(0.512, 0.031, 0.300, 0.9))
    return A.ADS131A04(dev, dev.cs, dev.reset, dev.drdy), dev


def wait_drdy_low(drv, dev, timeout_ms=50):
    if dev is not None:  # simulated: DRDY is always there
        return True
    t0 = time.ticks_ms()
    while drv.drdy.value():
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            return False
    return True


def main():
    drv, dev = make_driver()
    try:
        did = drv.start()
        check("RESET, READY, UNLOCK, configuration, ADC enable and WAKEUP all acknowledged", True, "device ID byte 0x%02X" % did)
    except A.ADSError as e:
        check("RESET, READY, UNLOCK, configuration, ADC enable and WAKEUP all acknowledged", False, str(e))
        return 1
    want = {A.A_SYS_CFG: A.A_SYS_CFG_VALUE, A.D_SYS_CFG: A.D_SYS_CFG_VALUE, A.CLK1: A.CLK1_VALUE, A.CLK2: A.CLK2_VALUE, A.ADC_ENA: 0x0F}
    got = {}
    for reg in want:
        try:
            got[reg] = drv.read_reg(reg)
        except A.ADSError as e:
            got[reg] = str(e)
    check("registers read back as written (A_SYS_CFG charge pump + internal reference, D_SYS_CFG fixed frame + CRC, CLK1, CLK2, ADC_ENA)", got == want,
          ", ".join("0x%02X=%s" % (k, ("0x%02X" % v) if isinstance(v, int) else v) for k, v in got.items()))
    stat = drv.read_reg(A.STAT_1)
    check("STAT_1 has no fault flags set", stat == 0, "0x%02X" % stat)
    stat_s = drv.read_reg(A.STAT_S)
    check("STAT_S (startup) has no fault flags set", stat_s == 0, "0x%02X" % stat_s)

    if not ON_BOARD:
        check("(simulated) DRDY rate not measured", True, "host run")
    else:
        edges, last, t0 = 0, drv.drdy.value(), time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < 100:
            v = drv.drdy.value()
            if last and not v:
                edges += 1
            last = v
        rate = edges * 10
        want_rate = A.data_rate()
        check("DRDY falls at the configured data rate (+-10%, 100 ms of polling)", abs(rate - want_rate) < 0.1 * want_rate, "%d Hz, expected %.0f Hz" % (rate, want_rate))

    n = 256
    acc = [[] for _ in range(4)]
    for _ in range(n):
        if not wait_drdy_low(drv, dev):
            check("DRDY arrives within 50 ms for every frame", False)
            return 1
        codes, _ = drv.read_samples()
        for i in range(4):
            acc[i].append(codes[i])
    full = 1 << 23
    for i in range(4):
        m = sum(acc[i]) / n
        sd = (sum((x - m) ** 2 for x in acc[i]) / n) ** 0.5
        print("       channel %d: mean %+.6f V, rms noise %.1f counts (%.2e V)" % (i + 1, A.code_to_volts(int(m)), sd, A.code_to_volts(int(sd))))
        check("channel %d is not at full scale" % (i + 1), max(abs(x) for x in acc[i]) < 0.95 * full)
        if dev is None:
            check("channel %d is not stuck (some noise)" % (i + 1), sd > 0.0, "%.2f counts" % sd)
    return 1 if failures else 0


if __name__ == "__main__":
    rc = main()
    print("\n%s" % ("All checks passed." if not rc else "%d check(s) failed: %s" % (len(failures), failures)))
    sys.exit(rc)
