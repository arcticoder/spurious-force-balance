"""Deterministic floorplan for the instrument main board (EasyEDA coordinates, mil, y up).

Input: hardware/easyeda/exports/main_board_parts.json (per component: designator, x, y, rotation, footprint, pads with offsets, sizes, nets; made from
PCB_PrimitiveComponent.getAll + PCB_PrimitivePad.getAll through easyeda_api_call, see docs/kb/easyeda_spark_notes.md).
Output: hardware/easyeda/exports/main_board_placement.json (designator -> primitive id, x, y, rotation), applied with easyeda_pcb_place_batch.
Edge connectors keep signal pads facing inward (tabs outward); the greedy pass puts each remaining part next to the placed parts it shares signal nets with.
"""
import json, math, re, collections, os

EXP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hardware', 'easyeda', 'exports')
o = json.load(open(os.path.join(EXP, 'main_board_parts.json')))
POWER = re.compile(r'^(GND|V5|3V3_D|3V3_A|3V3_AR|VBUS|VBUS_F|V24|V24_RAW|V5_BOOST|DVDD_1V1)$')
SCALE = float(os.environ.get('FP_SCALE', '1.0'))   # spreads the anchor positions and the interior (1.0 = the 2026-11-01 106.7 x 87.6 mm board)
X0, X1, Y0, Y1 = -50, 4050 * SCALE, -3250 * SCALE, 100      # interior limits for part bodies
MARGIN = float(os.environ.get('FP_MARGIN', '28'))

def rot_pads(pads, d):
    d %= 360
    th = math.radians(d)
    c, s = round(math.cos(th)), round(math.sin(th))
    out = []
    for q in pads:
        dx, dy = q['dx'] * c - q['dy'] * s, q['dx'] * s + q['dy'] * c
        w, h = (q['w'], q['h']) if d in (0, 180) else (q['h'], q['w'])
        out.append(dict(q, dx=dx, dy=dy, w=w, h=h))
    return out

by_des = {v['des']: (k, v) for k, v in o.items()}
state = {}   # des -> dict(x, y, rot, pads)
boxes = []   # (x0,y0,x1,y1)

def bbox(pads, x, y):
    return (x + min(q['dx'] - q['w'] / 2 for q in pads) - MARGIN, y + min(q['dy'] - q['h'] / 2 for q in pads) - MARGIN,
            x + max(q['dx'] + q['w'] / 2 for q in pads) + MARGIN, y + max(q['dy'] + q['h'] / 2 for q in pads) + MARGIN)

def free(b, edge_ok=False):
    if not edge_ok and (b[0] < X0 or b[2] > X1 or b[1] < Y0 or b[3] > Y1):
        return False
    for t in boxes:
        if b[0] < t[2] and t[0] < b[2] and b[1] < t[3] and t[1] < b[3]:
            return False
    return True

def place(des, x, y, rot=None, edge=False):
    k, v = by_des[des]
    r = v['rot'] if rot is None else rot
    pads = rot_pads(v['pads'], r - v['rot'])
    b = bbox(pads, x, y)
    if edge or free(b):
        pass
    else:
        # spiral search for the nearest free spot
        found = False
        step = 25
        for ring in range(1, 400):
            cands = []
            for i in range(-ring, ring + 1):
                cands += [(x + i * step, y + ring * step), (x + i * step, y - ring * step),
                          (x + ring * step, y + i * step), (x - ring * step, y + i * step)]
            cands.sort(key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
            for cx, cy in cands:
                b2 = bbox(pads, cx, cy)
                if free(b2):
                    x, y, b, found = cx, cy, b2, True
                    break
            if found:
                break
        if not found:
            raise SystemExit('no room for ' + des)
    boxes.append(b)
    state[des] = dict(id=k, x=x, y=y, rot=r, pads=pads)

# ---- anchors: edge connectors (signal pads face inward, tabs face outward), then ICs
ANCH = [
    # left edge, rot 270
    ('CN10', 55, -600, 270, True), ('CN11', 55, -1000, 270, True), ('CN12', 55, -1400, 270, True),
    # top edge, rot 180
    ('CN4', 1400, 0, 180, True), ('CN5', 1800, 0, 180, True), ('CN3', 2300, 0, 180, True),
    # right edge
    ('USBC1', 3935, -650, 90, True),
    # bottom edge, rot 0
    ('CN6', 600, -3150, 0, True), ('CN9', 2800, -3150, 0, True), ('CN8', 3200, -3150, 0, True), ('CN7', 3650, -3150, 0, True),
    ('H5', 1000, -3140, None, True), ('H1', 1300, -3140, None, True), ('H2', 1500, -3140, None, True),
    ('H3', 1700, -3140, None, True), ('H4', 1900, -3140, None, True),
    # ICs
    ('U4', 2200, -1250, None, False), ('U12', 950, -1850, None, False), ('U11', 1550, -1150, None, False),
    ('U14', 700, -1000, None, False), ('U8', 2650, -1450, None, False), ('U19', 3050, -2350, None, False),
    ('U20', 3500, -1900, None, False), ('Q3', 900, -2750, None, False), ('U15', 1350, -2550, None, False),
    ('SW1', 3300, -250, None, False), ('SW2', 3650, -250, None, False),
    ('U9', 2200, -2500, None, False), ('U10', 2500, -2500, None, False),
    ('U5', 2700, -750, None, False), ('Q4', 2800, -2850, None, False), ('Q5', 3200, -2850, None, False),
]
for des, x, y, rot, edge in ANCH:
    # edge parts keep hugging their edge: left (x ~ 55) and top (y ~ 0) stay, right and bottom edges shift out with the board;
    # positions along an edge, and the ICs, spread with the scale
    if edge and x > 3900:
        x += 4050 * (SCALE - 1)
    elif x >= 100:
        x *= SCALE
    if edge and y < -3000:
        y -= 3250 * (SCALE - 1)
    elif y <= -100:
        y *= SCALE
    place(des, x, y, rot, edge)

# ---- greedy for everything else
net_pads = collections.defaultdict(list)
for des, (k, v) in by_des.items():
    for q in v['pads']:
        if q['net'] and q['net'] != 'GND':
            net_pads[q['net']].append(des)

def weight(net):
    n = len(set(net_pads[net]))
    base = 0.12 if POWER.match(net) else 1.0
    return base / max(1, n - 1)

def pad_abs(des):
    s = state[des]
    return [(s['x'] + q['dx'], s['y'] + q['dy'], q['net']) for q in s['pads']]

rest = [d for d in by_des if d not in state]
while rest:
    best = None
    for d in rest:
        k, v = by_des[d]
        score = 0
        for q in v['pads']:
            if not q['net'] or q['net'] == 'GND':
                continue
            for d2 in set(net_pads[q['net']]):
                if d2 in state and d2 != d:
                    score += weight(q['net'])
        if best is None or score > best[0]:
            best = (score, d)
    score, d = best
    k, v = by_des[d]
    sx = sy = sw = 0
    for q in v['pads']:
        if not q['net'] or q['net'] == 'GND':
            continue
        w = weight(q['net'])
        for d2 in set(net_pads[q['net']]):
            if d2 in state and d2 != d:
                # nearest pad of d2 on that net
                for (ax, ay, n2) in pad_abs(d2):
                    if n2 == q['net']:
                        sx += ax * w; sy += ay * w; sw += w
                        break
    if sw == 0:
        sx, sy, sw = 2000, -1600, 1
    place(d, sx / sw, sy / sw)
    rest.remove(d)

# ---- report + write
xs = [b[0] for b in boxes] + [b[2] for b in boxes]; ys = [b[1] for b in boxes] + [b[3] for b in boxes]
print('extent x', min(xs), max(xs), 'y', min(ys), max(ys), 'parts', len(state))
json.dump({d: dict(id=s['id'], x=round(s['x'], 3), y=round(s['y'], 3), rot=s['rot']) for d, s in state.items()}, open(os.path.join(EXP, 'main_board_placement.json'), 'w'), indent=0)
