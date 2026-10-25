"""
test_host.py — pass/fail checks of the streaming protocol, the logger and the noise analysis (WP8).

    ~/.venvs/lab-hw/bin/python hardware/instrument/host/test_host.py
"""

import io
import os
import random
import struct
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "firmware"))

import analyze as AN  # noqa: E402
import logger as LG  # noqa: E402
import protocol as P  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


# ---- protocol
frames = [(1, -2, 3, -4), (8388607, -8388608, 0, 12345)]
pk = P.packet(P.T_ADC, 7, P.adc_payload(123456, frames))
d = P.Decoder()
got = d.feed(pk)
check("an ADC packet round-trips (type, sequence, timestamp, frames)", len(got) == 1 and got[0][:2] == (P.T_ADC, 7) and P.parse_payload(*[got[0][0], got[0][2]]) == {"t_us": 123456, "frames": frames})
li = P.parse_payload(P.T_LOCKIN, P.lockin_payload(5, (1, 2, 3, 4), (-1, -2, -3, -4)))
env = P.parse_payload(P.T_ENV, P.env_payload(9, (2867, 2900, -5), (10, -20, 4100), (210000, -5000, 380000), (1000, 0, -1000)))
check("lock-in and environment payloads round-trip", li["i"] == (1, 2, 3, 4) and li["q"] == (-1, -2, -3, -4) and env["field_ug"] == (210000, -5000, 380000) and env["acc_raw"] == (10, -20, 4100) and env["temps_raw"][2] == -5)

# one byte at a time
d = P.Decoder()
out = []
for b in pk * 3:
    out += d.feed(bytes((b,)))
check("the decoder assembles packets fed one byte at a time", len(out) == 3 and d.bad_crc == 0)

# garbage, a corrupted packet, a false sync inside a payload
rnd = random.Random(3)
stream = bytearray()
good = []
for k in range(40):
    payload = P.adc_payload(k * 1000, [(k, k + 1, k + 2, k + 3)] * (1 + k % 5))
    stream += bytes(rnd.randrange(256) for _ in range(rnd.randrange(0, 7)))  # garbage between packets
    p = bytearray(P.packet(P.T_ADC, k, payload))
    if k == 10:
        p[12] ^= 0x40  # damage one packet
    else:
        good.append(k)
    stream += p
# a payload containing the sync pattern
tricky = P.packet(P.T_TEXT, 40, b"xx\xA5\x5Ayy\xA5\x5A\x01\x00\xff\xffzz")
stream += tricky
good.append(40)
d = P.Decoder()
got = d.feed(bytes(stream))
seqs = [s for _, s, _ in got]
check("with garbage between packets, one damaged packet and a payload that contains the sync pattern, every other packet is recovered", seqs == good, "%d of %d, bad CRC %d, skipped %d bytes" % (len(seqs), len(good), d.bad_crc, d.skipped_bytes))
check("the decoder counts the sequence gap of the damaged packet", d.gaps == 1, "gaps %d" % d.gaps)

# a header claiming an absurd length does not stall the decoder
d = P.Decoder()
bad = P.SYNC + struct.pack("<BBH", 1, 0, 60000)
got = d.feed(bad + P.packet(P.T_TEXT, 1, b"ok"))
check("a false header with a huge length is skipped and the next packet is found", len(got) == 1 and got[0][2] == b"ok")

# ---- logger
unw = LG.Unwrap()
t = [unw(x) for x in (4_294_000_000, 4_294_900_000, 100_000, 200_000)]
check("the microsecond counter is unwrapped across its 32-bit wrap", abs(t[2] - (4_294_967_296 + 100_000) * 1e-6) < 1e-9 and t[3] > t[2] > t[1], str([round(x, 3) for x in t]))

with tempfile.TemporaryDirectory() as tmp:
    pre = os.path.join(tmp, "run")
    data = bytearray()
    for k in range(5):
        data += P.packet(P.T_ADC, k, P.adc_payload(1_000_000 + k * 4000, [(100 * k + j, 0, -j, 8388607) for j in range(32)]))
    data += P.packet(P.T_LOCKIN, 5, P.lockin_payload(1_500_000, (4000, 0, 0, 0), (0, 0, 0, 0)))
    data += P.packet(P.T_ENV, 6, P.env_payload(1_600_000, (2867, 0, 0), (0, 0, 4100), (210000, 0, 380000), (0, 0, 0)))
    data += P.packet(P.T_TEXT, 7, b"started")
    counts, dec = LG.run(io.BytesIO(bytes(data)), pre, fs=8000.0, chunk=100)
    rows = list(__import__("csv").DictReader(open(pre + "_adc.csv")))
    check("the logger writes every ADC frame (5 packets x 32) with timestamps spaced by the sample period", len(rows) == 160 and abs(float(rows[1]["t_s"]) - float(rows[0]["t_s"]) - 1 / 8000) < 1e-6, "%d rows" % len(rows))
    check("an ADC code converts to volts: 8388607 is +VREF (2.442 V) to 1 LSB", abs(float(rows[0]["ch4_V"]) - 2.442) < 3e-7, rows[0]["ch4_V"])
    env_row = list(__import__("csv").DictReader(open(pre + "_env.csv")))[0]
    check("the environment row converts units (TMP117 raw 2867 = 22.4 C, LIS2DW12 4100 = 1000.4 mg, field in gauss)", abs(float(env_row["T1_C"]) - 22.3984) < 1e-3 and abs(float(env_row["az_mg"]) - 1000.4) < 0.1 and abs(float(env_row["Bz_G"]) - 0.38) < 1e-9, str(env_row))
    check("the logger counts and reports what it wrote", counts == {"adc_frames": 160, "lockin": 1, "env": 1, "text": 1} and dec.bad_crc == 0, str(counts))
    check("text packets land in the log file", open(pre + "_log.txt").read() == "started\n")

# ---- analysis
rng = np.random.default_rng(5)
fs = 8000.0
sigma = 0.002  # V rms, white
x = rng.normal(0, sigma, int(fs * 60))
f, s = AN.asd(x, fs)
floor = float(np.median(s[(f > 10) & (f < 3500)]))
expect = sigma / np.sqrt(fs / 2)
check("the ASD of white noise (2 mV rms at 8 kSPS) is sigma / sqrt(fs/2) = %.3e V/sqrt(Hz) within 3%%" % expect, abs(floor / expect - 1) < 0.03, "%.3e" % floor)
t_ax = np.arange(int(fs * 30)) / fs
tone = 0.1 * np.sin(2 * np.pi * 1000.0 * t_ax) + rng.normal(0, 1e-4, len(t_ax))
f, s = AN.asd(tone, fs, nperseg=8000)
k = int(np.argmax(s))
# amplitude of a sine from the ASD peak: A = ASD_peak * sqrt(ENBW) * sqrt(2), ENBW of a Hann window = 1.5 bins
enbw = 1.5 * (f[1] - f[0])
check("a 1 kHz tone is found at 1000 Hz and its amplitude is recovered within 2% (0.1 V)", abs(f[k] - 1000) < 1 and abs(s[k] * np.sqrt(enbw) * np.sqrt(2) / 0.1 - 1) < 0.02, "peak at %.1f Hz, A = %.4f V" % (f[k], s[k] * np.sqrt(enbw) * np.sqrt(2)))
taus = [0.01, 0.1, 1.0]
ad = AN.allan_deviation(x, fs, taus)
slope = np.polyfit(np.log(taus), np.log(ad), 1)[0]
check("the Allan deviation of white noise falls as tau^-1/2 (slope -0.5 +-0.05) and equals sigma at one sample", abs(slope + 0.5) < 0.05, "slope %.3f, ADEV(10 ms) %.2e vs sigma/sqrt(80) %.2e" % (slope, ad[0], sigma / np.sqrt(80)))
walk = np.cumsum(rng.normal(0, 1e-4, int(fs * 120)))
ad = AN.allan_deviation(walk, fs, [0.1, 1.0, 10.0])
slope = np.polyfit(np.log([0.1, 1.0, 10.0]), np.log(ad), 1)[0]
check("the Allan deviation of a random walk rises as tau^+1/2 (slope +0.5 +-0.1)", abs(slope - 0.5) < 0.1, "slope %.2f" % slope)

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
