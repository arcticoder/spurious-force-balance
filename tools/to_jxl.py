"""
to_jxl.py — convert PNGs to lossless JPEG XL (the repo stores pictures as .jxl).

    ~/.venvs/lab-hw/bin/python tools/to_jxl.py picture.png [...]    # writes picture.jxl, removes picture.png

Importable: to_jxl(path) -> path of the .jxl. Needs pillow and pillow-jxl-plugin (pip install pillow-jxl-plugin).
Generators write a temporary .png (matplotlib, kicad-cli) and call this on it.
"""
import os
import sys

import pillow_jxl  # noqa: F401  (registers the JXL codec with Pillow)
from PIL import Image


def to_jxl(png):
    out = os.path.splitext(png)[0] + ".jxl"
    with Image.open(png) as im:
        im.save(out, format="JXL", lossless=True)
    os.remove(png)
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, "->", to_jxl(p))
