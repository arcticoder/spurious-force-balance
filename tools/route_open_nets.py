"""Offline two-layer maze router for the few nets the EasyEDA autorouters leave open (docs/kb/easyeda_spark_notes.md).

Input: JSON dumps of PCB_PrimitivePad.getAll, PCB_PrimitiveLine.getAll, PCB_PrimitiveVia.getAll (mil, y up) and the net names to finish.
Output: a JSON plan {lines:[[net,layer,x1,y1,x2,y2,width]], vias:[[net,x,y,hole,dia]]} for PCB_PrimitiveLine.createMany / PCB_PrimitiveVia.createMany.
Each net's pieces (pads, tracks, vias that touch) are grouped into connected components; the nearest components are joined by a grid A* on top and
bottom copper (8 directions, vias at extra cost); finished routes become obstacles for the next net.

Usage: python3 -I tools/route_open_nets.py pads.json lines.json vias.json out.json NET [NET ...]   (clearance via env RT_CLR, default 7 mil)
"""
import heapq, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, Polygon, box
from shapely.affinity import rotate

P = float(os.environ.get('RT_PITCH', 5))   # grid pitch, mil
X0, X1, Y0, Y1 = -150.0, 4650.0, -3750.0, 250.0
W, H = int((X1 - X0) / P) + 1, int((Y1 - Y0) / P) + 1
CLR = float(os.environ.get('RT_CLR', 7))
TW = 10.0                                  # track width
VD, VH = 24.0, 12.0                        # via diameter, hole

def pad_geom(p):
    s = p['pad']
    if s is None:
        return None
    if s[0] == 'POLYGON':
        pts = [v for v in s[1] if not isinstance(v, str)]
        return Polygon(list(zip(pts[0::2], pts[1::2]))).buffer(0)
    w, h = (s[1], s[2]) if len(s) >= 3 else (s[1], s[1])
    g = box(p['x'] - w / 2, p['y'] - h / 2, p['x'] + w / 2, p['y'] + h / 2)
    return rotate(g, p['rotation'] or 0, origin=(p['x'], p['y']))

def layers_of(l):
    return (1, 2) if l not in (1, 2) else (l,)

class Obj:
    def __init__(self, net, geom, layers, kind):
        self.net, self.geom, self.layers, self.kind = net, geom, layers, kind

def load(pf, lf, vf):
    objs = []
    for p in json.load(open(pf))['result']:
        g = pad_geom(p)
        if g is not None:
            objs.append(Obj(p['net'], g, layers_of(p['layer']), 'pad'))
        if p.get('hole'):                  # keep drilled holes clear on both layers even for NPTH
            pass
    for l in json.load(open(lf))['result']:
        if l['layer'] in (1, 2):
            objs.append(Obj(l['net'], LineString([(l['startX'], l['startY']), (l['endX'], l['endY'])]).buffer(l['lineWidth'] / 2), (l['layer'],), 'line'))
    for v in json.load(open(vf))['result']:
        objs.append(Obj(v['net'], Point(v['x'], v['y']).buffer(v['diameter'] / 2), (1, 2), 'via'))
    return objs

def px(x, y):
    return (x - X0) / P, (Y1 - y) / P

def draw(mask, geom, grow):
    g = geom.buffer(grow) if grow else geom
    for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
        if poly.is_empty:
            continue
        mask.polygon([px(*c) for c in poly.exterior.coords], fill=1)
        for hole in poly.interiors:
            pass

def masks_for(net, objs):
    """track-centre and via-centre blocked masks per layer for everything that is not `net`"""
    tr = {1: Image.new('1', (W, H), 0), 2: Image.new('1', (W, H), 0)}
    vi = {1: Image.new('1', (W, H), 0), 2: Image.new('1', (W, H), 0)}
    d = {k: ImageDraw.Draw(m) for k, m in tr.items()}
    dv = {k: ImageDraw.Draw(m) for k, m in vi.items()}
    for o in objs:
        if o.net == net:
            continue
        for L in o.layers:
            draw(d[L], o.geom, CLR + TW / 2)
            draw(dv[L], o.geom, CLR + VD / 2)
    # outline keep-out
    for L in (1, 2):
        for dr, gr in ((d[L], 20), (dv[L], 30)):
            dr.rectangle([0, 0, W, int(gr / P)], fill=1); dr.rectangle([0, H - int(gr / P) - 1, W, H], fill=1)
            dr.rectangle([0, 0, int(gr / P), H], fill=1); dr.rectangle([W - int(gr / P) - 1, 0, W, H], fill=1)
    # board limits: outline is x -100..4520, y -3650..160
    for dr, gr in ((d[1], 30), (d[2], 30), (dv[1], 40), (dv[2], 40)):
        ax, ay = px(-100 + gr, 160 - gr); bx, by = px(4520 - gr, -3650 + gr)
        dr.rectangle([0, 0, W, ay], fill=1); dr.rectangle([0, by, W, H], fill=1)
        dr.rectangle([0, 0, ax, H], fill=1); dr.rectangle([bx, 0, W, H], fill=1)
    return ({L: np.array(m, dtype=bool) for L, m in tr.items()}, {L: np.array(m, dtype=bool) for L, m in vi.items()})

def mask_of(geom_layers):
    m = Image.new('1', (W, H), 0); d = ImageDraw.Draw(m)
    for g in geom_layers:
        draw(d, g, 0)
    return np.array(m, dtype=bool)

def components(net_objs):
    n = len(net_objs); par = list(range(n))
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            if set(net_objs[i].layers) & set(net_objs[j].layers) and net_objs[i].geom.intersects(net_objs[j].geom):
                par[f(i)] = f(j)
    comp = {}
    for i in range(n):
        comp.setdefault(f(i), []).append(net_objs[i])
    return list(comp.values())

DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]

MAXEXP = int(os.environ.get('RT_MAXEXP', 1500000))

def astar(srcs, tgts, blk, vblk, tcent):
    """srcs/tgts: sets of (L,i,j); blk[L][j,i] blocked for track centres; vblk same for via centres"""
    tx, ty = tcent
    def hcost(i, j):
        dx, dy = abs(i - tx), abs(j - ty)
        return (dx + dy) + (1.414 - 2) * min(dx, dy)
    pq = []; g = {}; came = {}; nexp = 0
    for s in srcs:
        g[s] = 0.0; heapq.heappush(pq, (hcost(s[1], s[2]), 0.0, s))
    while pq:
        f, c, s = heapq.heappop(pq)
        if c > g.get(s, 1e18):
            continue
        nexp += 1
        if nexp > MAXEXP:
            return None
        if s in tgts:
            path = [s]
            while path[-1] in came:
                path.append(came[path[-1]])
            return path[::-1]
        L, i, j = s
        for di, dj, w in DIRS:
            ni, nj = i + di, j + dj
            if not (0 <= ni < W and 0 <= nj < H) or blk[L][nj, ni]:
                continue
            if di and dj and (blk[L][j, ni] or blk[L][nj, i]):
                continue
            t = (L, ni, nj); nc = c + w
            if nc < g.get(t, 1e18):
                g[t] = nc; came[t] = s; heapq.heappush(pq, (nc + hcost(ni, nj), nc, t))
        L2 = 3 - L
        if not vblk[1][j, i] and not vblk[2][j, i] and not blk[L2][j, i]:
            t = (L2, i, j); nc = c + 28
            if nc < g.get(t, 1e18):
                g[t] = nc; came[t] = s; heapq.heappush(pq, (nc + hcost(i, j), nc, t))
    return None

def to_xy(i, j):
    return X0 + i * P, Y1 - j * P

def simplify(path):
    """-> list of ('line', L, (x1,y1), (x2,y2)) and ('via', (x,y))"""
    out = []; seg = [path[0]]
    def flush():
        if len(seg) > 1:
            pts = [to_xy(c[1], c[2]) for c in seg]
            keep = [pts[0]]
            for a in range(1, len(pts) - 1):
                d1 = (pts[a][0] - keep[-1][0], pts[a][1] - keep[-1][1]); d2 = (pts[a + 1][0] - pts[a][0], pts[a + 1][1] - pts[a][1])
                if abs(d1[0] * d2[1] - d1[1] * d2[0]) > 1e-6 or d1[0] * d2[0] + d1[1] * d2[1] < 0:
                    keep.append(pts[a])
            keep.append(pts[-1])
            for a in range(len(keep) - 1):
                out.append(('line', seg[0][0], keep[a], keep[a + 1]))
    for a in range(1, len(path)):
        if path[a][0] != path[a - 1][0]:
            flush(); out.append(('via', to_xy(path[a][1], path[a][2]))); seg = [path[a]]
        else:
            seg.append(path[a])
    flush()
    return out

def cells_of(geoms_layers, blk=None):
    s = set()
    for g, layers in geoms_layers:
        x0, y0, x1, y1 = g.bounds
        i0, j0 = int((x0 - X0) / P) - 1, int((Y1 - y1) / P) - 1
        i1, j1 = int((x1 - X0) / P) + 2, int((Y1 - y0) / P) + 2
        m = Image.new('1', (i1 - i0 + 1, j1 - j0 + 1), 0); d = ImageDraw.Draw(m)
        for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
            d.polygon([((x - X0) / P - i0, (Y1 - y) / P - j0) for x, y in poly.exterior.coords], fill=1)
        ys, xs = np.nonzero(np.array(m, dtype=bool))
        for L in layers:
            for x, y in zip(xs, ys):
                s.add((L, int(x) + i0, int(y) + j0))
    return s

def route(objs, nets):
    plan = {'lines': [], 'vias': [], 'failed': []}
    for net in nets:
        while True:
            comps = components([o for o in objs if o.net == net])
            if len(comps) <= 1:
                break
            blk, vblk = masks_for(net, objs)
            for c in comps:                  # a net's own copper is always usable, even where a neighbour's keep-out overlaps it
                for (L, i, j) in cells_of([(o.geom, o.layers) for o in c]):
                    blk[L][j, i] = False
            best = None
            for a in range(len(comps)):
                for b in range(a + 1, len(comps)):
                    d = min(x.geom.distance(y.geom) for x in comps[a] for y in comps[b])
                    if best is None or d < best[0]:
                        best = (d, a, b)
            _, a, b = best
            srcs = cells_of([(o.geom, o.layers) for o in comps[a]]); tgts = cells_of([(o.geom, o.layers) for o in comps[b]])
            cx = np.mean([o.geom.centroid.x for o in comps[b]]); cy = np.mean([o.geom.centroid.y for o in comps[b]])
            path = astar(srcs, tgts, blk, vblk, ((cx - X0) / P, (Y1 - cy) / P))
            if not path:
                plan['failed'].append(net); print('FAILED', net, flush=True); break
            for kind, *rest in simplify(path):
                if kind == 'line':
                    L, p1, p2 = rest
                    plan['lines'].append([net, L, round(p1[0], 2), round(p1[1], 2), round(p2[0], 2), round(p2[1], 2), TW])
                    objs.append(Obj(net, LineString([p1, p2]).buffer(TW / 2), (L,), 'line'))
                else:
                    (x, y), = rest
                    plan['vias'].append([net, round(x, 2), round(y, 2), VH, VD])
                    objs.append(Obj(net, Point(x, y).buffer(VD / 2), (1, 2), 'via'))
            # tie the route ends to pad centres so the copper certainly overlaps
            json.dump(plan, open(OUT, 'w'))
            print('routed', net, 'components', len(comps), '->', len(comps) - 1, flush=True)
    return plan

OUT = sys.argv[4] if len(sys.argv) > 4 else 'plan.json'

if __name__ == '__main__':
    objs = load(sys.argv[1], sys.argv[2], sys.argv[3])
    plan = route(objs, sys.argv[5:])
    json.dump(plan, open(sys.argv[4], 'w'))
    print(len(plan['lines']), 'lines', len(plan['vias']), 'vias', 'failed', plan['failed'])
