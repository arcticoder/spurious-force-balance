"""
test_lockin.py — pass/fail checks of the fixed-point lock-in on synthetic photodiode streams (WP8).

    ~/.venvs/lab-hw/bin/python hardware/instrument/firmware/test_lockin.py
"""

import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lockin as L  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


def stream(n, amp, dc=0, delay=0, noise=0.0, mains=0.0, seed=1):
    """ADC codes: DC + amp on the LED-on half-period (delayed by `delay` samples) + noise + a 50 Hz interferer (8 kSPS)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        on = 1 if ((i - delay) % 8) < 4 else 0
        x = dc + amp * on + mains * math.sin(2 * math.pi * 50 * i / 8000) + rnd.gauss(0, noise)
        out.append(int(round(x)))
    return out


N = 40000  # 5 s at 8 kSPS, about 10 time constants of shift 12

# 1. amplitude, with a large DC and noise
li = L.LockIn(shift=9)
for x in stream(N, 20000, dc=2_000_000, noise=1000):
    li.push(x)
est = li.amplitude()
check("recovers a 20000-count modulation on a 2,000,000-count DC with 1000 counts rms noise within 0.5%", abs(est - 20000) < 100, "%d counts" % est)

# 2. DC rejection is exact over whole periods
li = L.LockIn(shift=9)
for x in stream(N, 0, dc=4_000_000):
    li.push(x)
check("a pure DC of 4,000,000 counts (ambient light) gives exactly zero output", li.yi == 0 and li.yq == 0 and li.max_state == 0, "I %d, Q %d" % (li.yi, li.yq))

# 3. 50 Hz interference
li = L.LockIn(shift=9)
for x in stream(N, 0, mains=1_000_000):
    li.push(x)
check("a 1,000,000-count 50 Hz interferer (a whole number of carrier periods per mains period) is rejected to under 0.01% of its amplitude", abs(li.amplitude()) < 100, "%d counts" % li.amplitude())

# 3b. 60 Hz is not a whole number of carrier periods (133.3 samples): the low-pass has to do the work
data = [int(round(1_000_000 * math.sin(2 * math.pi * 60 * i / 8000))) for i in range(N)]
li = L.LockIn(shift=9)
peak = 0
for i, x in enumerate(data):
    li.push(x)
    if i > N // 2:
        peak = max(peak, abs(li.amplitude()))
check("a 1,000,000-count 60 Hz interferer (not commensurate with the carrier) stays under 0.5% of its amplitude at the output", peak < 5000, "worst %d counts" % peak)

# 4. phase search
for delay in (0, 3, 6):
    data = stream(8000, 30000, dc=1_000_000, delay=delay, noise=1000)
    ph = L.best_phase(data)
    li = L.LockIn(shift=9, phase=ph)
    for x in stream(N, 30000, dc=1_000_000, delay=delay, noise=1000):
        li.push(x)
    check("an optical delay of %d samples gives phase offset %d and the amplitude is recovered within 0.5%%" % (delay, (8 - delay) % 8), ph == (8 - delay) % 8 and abs(li.amplitude() - 30000) < 150, "phase %d, %d counts" % (ph, li.amplitude()))

# 5. linearity
worst = 0
for amp in (1000, 5000, 20000, 100000, 1_000_000):
    li = L.LockIn(shift=9)
    for x in stream(N, amp, dc=500_000, noise=300):
        li.push(x)
    worst = max(worst, abs(li.amplitude() - amp) / amp)
check("linear from 1000 to 1,000,000 counts: worst error under 1%", worst < 0.01, "%.3f%%" % (worst * 100))

# 6. 32-bit headroom with 16-bit input
li24 = L.LockIn(shift=9)
li16 = L.LockIn(shift=9, in_shift=8)
for x in stream(N, 2_000_000, dc=-3_000_000, noise=20000):
    li24.push(x)
    li16.push(x)
check("full-scale 24-bit input (2,000,000 counts on a -3,000,000 DC) needs more than 31 bits of state, so the 32-bit port uses 16-bit input", li24.max_state >= 2**31, "max state 2^%.1f" % math.log2(li24.max_state))
check("with in_shift 8 the state stays under 2^31 (fits viper's 32-bit ints)", li16.max_state < 2**31, "max state 2^%.1f" % math.log2(li16.max_state))
check("the 16-bit-input version agrees with the full one to 0.1% at 2,000,000 counts", abs(li16.amplitude() - li24.amplitude()) < 2000, "%d vs %d" % (li16.amplitude(), li24.amplitude()))

# 7. integer-only
li = L.LockIn()
out = li.push(12345)
check("outputs are ints (no floating point on the RP2040)", all(isinstance(v, int) for v in out) and isinstance(li.amplitude(), int))

# 8. sign: the output follows the sign of the modulation
li = L.LockIn(shift=7)
for x in stream(8000, -10000, dc=100_000):
    li.push(x)
check("an inverted modulation (the signal falls when the LED turns on) gives a negative amplitude", li.amplitude() < -9000, "%d" % li.amplitude())

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
