"""
lockin.py — fixed-point digital lock-in for the optical channel (WP8). Integer arithmetic only: the reference for a viper/PIO port on the RP2040.

The LED is gated on for half of each modulation period and off for the other half, locked to the ADC frame count: 8 kSPS and an 8-sample period give a 1 kHz carrier
(4 samples on, 4 off). The photodiode signal is x[n] = DC + A * s[n] (s = 1 while the LED is on).
  1. Demodulate with a +-1 square reference r[n] and sum over exactly one carrier period: B = sum(x * r) = 4 * A for a whole period, whatever the DC and the ambient light
     (they cancel exactly: 4 samples of +DC against 4 of -DC). Integer, no ripple, because nothing is read out mid-period.
  2. Low-pass B at the period rate with a leaky integrator of time constant 2^shift periods:  Y += B - (Y >> shift);  y = Y >> shift  (unity gain, y -> B).
  3. A = y / 4 (in input counts, times 2^in_shift if the samples were pre-shifted).
A second reference a quarter period later gives the quadrature channel Q. The LED/optics/TIA delay of d samples is found by `best_phase`, which returns the phase offset
(period - d) % period that makes the in-phase output positive.
Headroom: Y reaches |B| * 2^shift. With 24-bit codes and shift 9 that is about 2^35; a 32-bit (viper) port feeds it 16-bit samples (`in_shift` = 8) and keeps it near 2^27.
(An earlier per-sample leaky integrator was rejected: its state is a triangle wave inside each period, so a DC of D leaves D / 2^(shift-1) at the period boundary.)
"""

PERIOD = 8


def reference(period=PERIOD):
    """+1 for the first half of the period, -1 for the second."""
    return [1 if k < period // 2 else -1 for k in range(period)]


class LockIn:
    def __init__(self, period=PERIOD, shift=9, in_shift=0, phase=0):
        self.period, self.shift, self.in_shift, self.phase = period, shift, in_shift, phase
        self.ref = reference(period)
        self.n = 0
        self.bi = 0  # this period's sums
        self.bq = 0
        self.Yi = 0  # leaky integrators (per period)
        self.Yq = 0
        self.yi = 0  # outputs at the last period boundary
        self.yq = 0
        self.max_state = 0

    def push(self, x):
        """One ADC sample (signed int). Returns (yi, yq): the filtered per-period sums (A_estimate = yi / 4 at the right phase)."""
        if self.in_shift:
            x >>= self.in_shift
        p = (self.n + self.phase) % self.period
        self.bi += x * self.ref[p]
        self.bq += x * self.ref[(p + self.period // 4) % self.period]
        self.n += 1
        if self.n % self.period == 0:
            self.Yi += self.bi - (self.Yi >> self.shift)
            self.Yq += self.bq - (self.Yq >> self.shift)
            self.bi = self.bq = 0
            self.yi = self.Yi >> self.shift
            self.yq = self.Yq >> self.shift
            self.max_state = max(self.max_state, abs(self.Yi), abs(self.Yq))
        return self.yi, self.yq

    def amplitude(self):
        """A estimate in input counts from the in-phase output."""
        return (self.yi >> 2) * (1 << self.in_shift)


def best_phase(samples, period=PERIOD, shift=7):
    """The phase offset (0..period-1) that maximizes the SIGNED in-phase output on a block of samples (a few 2^shift periods of them): for an optical delay of d samples,
    (period - d) % period. The signed maximum assumes the light rises when the LED turns on."""
    best, best_y = 0, None
    for ph in range(period):
        li = LockIn(period, shift, 0, ph)
        y = 0
        for x in samples:
            y = li.push(x)[0]
        if best_y is None or y > best_y:
            best, best_y = ph, y
    return best
