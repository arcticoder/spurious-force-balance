"""
analyze.py — noise analysis of logged ADC data (WP8): amplitude spectral density (Welch) and Allan deviation.

    python hardware/instrument/host/analyze.py run1_adc.csv --channel 1 --fs 8000

Prints the white-noise floor (median ASD between two frequencies), the rms over the record, the Allan deviation at tau = 1 s and the slope of the Allan deviation
(-0.5 for white noise). The functions are used by the tests with signals of known noise.
"""

import argparse
import csv

import numpy as np


def asd(x, fs, nperseg=4096):
    """One-sided amplitude spectral density in (input units)/sqrt(Hz), Welch with a Hann window and 50% overlap."""
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    nperseg = min(nperseg, len(x))
    step = nperseg // 2
    win = np.hanning(nperseg)
    scale = 1.0 / (fs * (win ** 2).sum())
    acc = None
    n = 0
    for i in range(0, len(x) - nperseg + 1, step):
        seg = x[i:i + nperseg] * win
        p = np.abs(np.fft.rfft(seg)) ** 2 * scale
        p[1:-1] *= 2
        acc = p if acc is None else acc + p
        n += 1
    return np.fft.rfftfreq(nperseg, 1 / fs), np.sqrt(acc / n)


def allan_deviation(x, fs, taus_s):
    """Non-overlapping Allan deviation of a series of readings x (not phase data) for each averaging time in seconds (at least 2 whole bins needed)."""
    x = np.asarray(x, dtype=float)
    out = []
    for tau in taus_s:
        m = int(round(tau * fs))
        nbins = len(x) // m
        if m < 1 or nbins < 2:
            out.append(float("nan"))
            continue
        means = x[: nbins * m].reshape(nbins, m).mean(axis=1)
        out.append(float(np.sqrt(0.5 * np.mean(np.diff(means) ** 2))))
    return np.array(out)


def load_channel(path, channel, column="code"):
    with open(path) as f:
        r = csv.DictReader(f)
        return np.array([float(row["ch%d_%s" % (channel, column)]) for row in r])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--channel", type=int, default=1)
    ap.add_argument("--fs", type=float, default=8000.0)
    ap.add_argument("--band", type=float, nargs=2, default=(10.0, 1000.0))
    a = ap.parse_args()
    v = load_channel(a.csv, a.channel, "V")
    f, s = asd(v, a.fs)
    sel = (f >= a.band[0]) & (f <= a.band[1])
    print("channel %d: %d samples, mean %.6f V, rms %.3e V" % (a.channel, len(v), v.mean(), v.std()))
    print("ASD floor (median %g-%g Hz): %.3e V/sqrt(Hz)" % (a.band[0], a.band[1], np.median(s[sel])))
    taus = [t for t in (0.01, 0.1, 1, 10, 100) if len(v) / a.fs >= 2 * t]
    ad = allan_deviation(v, a.fs, taus)
    for t, d in zip(taus, ad):
        print("Allan deviation at tau %g s: %.3e V" % (t, d))
    if len(taus) >= 2:
        slope = np.polyfit(np.log(taus), np.log(ad), 1)[0]
        print("Allan slope: %.2f (-0.5 white noise, 0 flicker, +0.5 random walk)" % slope)


if __name__ == "__main__":
    main()
