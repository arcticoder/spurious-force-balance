"""
logger.py — host-side logger for the instrument's USB stream (WP8): decodes packets, writes CSV files, reports what was lost.

    python hardware/instrument/host/logger.py --port /dev/ttyACM0 --out run1        # live (needs pyserial)
    python hardware/instrument/host/logger.py --file capture.bin --out run1         # from a recorded byte stream

Writes <out>_adc.csv (t_s, ch1..ch4 codes and volts), <out>_lockin.csv, <out>_env.csv and <out>_log.txt. Timestamps are unwrapped from the device's 32-bit microsecond
counter (it wraps every 71.6 minutes) and the ADC frames inside a packet are spaced by the sample period `--fs` (8000 Hz by default).
"""

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "firmware"))

import protocol as P  # noqa: E402

VREF = 2.442


class Unwrap:
    """Unwraps a u32 microsecond counter into seconds."""

    def __init__(self):
        self.last = None
        self.offset = 0

    def __call__(self, t_us):
        if self.last is not None and t_us < self.last - (1 << 31):
            self.offset += 1 << 32
        elif self.last is not None and t_us > self.last + (1 << 31):  # a late packet from before the wrap
            return (t_us + self.offset - (1 << 32)) * 1e-6
        self.last = t_us
        return (t_us + self.offset) * 1e-6


class Writer:
    def __init__(self, prefix, fs=8000.0):
        self.fs = fs
        self.files = {}
        self.unwrap = {k: Unwrap() for k in ("adc", "lockin", "env")}
        self.counts = {"adc_frames": 0, "lockin": 0, "env": 0, "text": 0}
        for name, header in (("adc", ["t_s"] + ["ch%d_code" % i for i in range(1, 5)] + ["ch%d_V" % i for i in range(1, 5)]),
                             ("lockin", ["t_s"] + ["I%d" % i for i in range(1, 5)] + ["Q%d" % i for i in range(1, 5)]),
                             ("env", ["t_s", "T1_C", "T2_C", "T3_C", "ax_mg", "ay_mg", "az_mg", "Bx_G", "By_G", "Bz_G", "offx_G", "offy_G", "offz_G"])):
            f = open("%s_%s.csv" % (prefix, name), "w", newline="")
            w = csv.writer(f)
            w.writerow(header)
            self.files[name] = (f, w)
        self.log = open("%s_log.txt" % prefix, "w")

    def handle(self, ptype, payload):
        d = P.parse_payload(ptype, payload)
        if ptype == P.T_ADC:
            t0 = self.unwrap["adc"](d["t_us"])
            for k, fr in enumerate(d["frames"]):
                self.files["adc"][1].writerow(["%.6f" % (t0 + k / self.fs)] + list(fr) + ["%.9f" % (c * 2 * VREF / (1 << 24)) for c in fr])
            self.counts["adc_frames"] += len(d["frames"])
        elif ptype == P.T_LOCKIN:
            self.files["lockin"][1].writerow(["%.6f" % self.unwrap["lockin"](d["t_us"])] + list(d["i"]) + list(d["q"]))
            self.counts["lockin"] += 1
        elif ptype == P.T_ENV:
            self.files["env"][1].writerow(["%.6f" % self.unwrap["env"](d["t_us"])] + ["%.4f" % (r / 128) for r in d["temps_raw"]] + ["%.2f" % (r * 0.244) for r in d["acc_raw"]]
                                          + ["%.6f" % (v * 1e-6) for v in d["field_ug"]] + ["%.6f" % (v * 1e-6) for v in d["offset_ug"]])
            self.counts["env"] += 1
        elif ptype == P.T_TEXT:
            self.log.write(d["text"] + "\n")
            self.counts["text"] += 1

    def close(self):
        for f, _ in self.files.values():
            f.close()
        self.log.close()


def run(source, prefix, fs=8000.0, chunk=4096):
    """source: an object with read(n) returning bytes (b'' at the end of a file). Returns (counts, decoder)."""
    dec = P.Decoder()
    w = Writer(prefix, fs)
    try:
        while True:
            data = source.read(chunk)
            if not data:
                break
            for ptype, _seq, payload in dec.feed(data):
                try:
                    w.handle(ptype, payload)
                except (ValueError, Exception) as e:  # a CRC-good packet with a bad payload: log, keep going
                    w.log.write("bad payload type %d: %s\n" % (ptype, e))
    finally:
        w.close()
    return w.counts, dec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fs", type=float, default=8000.0)
    a = ap.parse_args()
    if a.file:
        src = open(a.file, "rb")
    else:
        import serial  # pyserial

        src = serial.Serial(a.port, timeout=1)
    counts, dec = run(src, a.out, a.fs)
    print("frames/packets:", counts, "| bad CRC:", dec.bad_crc, "| skipped bytes:", dec.skipped_bytes, "| sequence gaps:", dec.gaps)


if __name__ == "__main__":
    main()
