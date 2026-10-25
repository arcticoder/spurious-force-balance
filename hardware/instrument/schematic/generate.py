"""
generate.py — write the netlist (every board) and the KiCad schematic (head boards; see below) into out/.

    ~/.venvs/lab-hw/bin/python hardware/instrument/schematic/generate.py            # netlists + head schematics
    ~/.venvs/lab-hw/bin/python hardware/instrument/schematic/generate.py --main-sch # also the main board's schematic (very slow)

SKiDL's schematic generator places and routes a flat sheet; the 164-part main board did not finish in 15 CPU-minutes, so by default the
main board is delivered as a netlist (checked by schematic_test.py) and the schematic is rendered for the head boards. Splitting
build() into @subcircuit blocks (hierarchical sheets) is the way to get a main-board schematic; see docs/TODO-agent.md.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ.setdefault("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")

import heads  # noqa: E402
import main_board  # noqa: E402
from skidl import ERC, generate_netlist, generate_schematic  # noqa: E402

OUT = os.path.join(HERE, "out")
BOARDS = (
    ("main_board", main_board.build, "--main-sch" in sys.argv),
    ("led_head", heads.led_head, True),
    ("pd_head", heads.pd_head, True),
    ("sensor_head_1", heads.sensor_head_1, True),
    ("sensor_head_2", heads.sensor_head_2, True),
)


def main():
    os.makedirs(OUT, exist_ok=True)
    # project-local library tables so that KiCad finds the jlc symbols and footprints
    lib = os.path.join(HERE, "..", "lib")
    open(os.path.join(OUT, "sym-lib-table"), "w").write(f'(sym_lib_table\n  (version 7)\n  (lib (name "jlc")(type "KiCad")(uri "{os.path.abspath(lib)}/jlc.kicad_sym")(options "")(descr ""))\n)\n')
    open(os.path.join(OUT, "fp-lib-table"), "w").write(f'(fp_lib_table\n  (version 7)\n  (lib (name "jlc")(type "KiCad")(uri "{os.path.abspath(lib)}/jlc.pretty")(options "")(descr ""))\n)\n')
    for name, build, sch in BOARDS:
        build()
        cwd = os.getcwd()
        os.chdir(OUT)
        try:
            ERC()
            generate_netlist(file_=f"{name}.net")
            if sch:
                try:
                    generate_schematic(filepath=".", top_name=name, retries=6)
                except Exception as e:  # SKiDL's router can give up on a dense sheet
                    print(f"{name}: schematic not rendered ({type(e).__name__}); the netlist is still written and checked")
        finally:
            os.chdir(cwd)
        print("wrote", name)


if __name__ == "__main__":
    main()
