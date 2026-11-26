"""Battle background for diagonal (Suikoden-style) view. 192x230 px, shown at 2x."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 192, 230
GY = 62  # ground starts (building foundation bottom)
rng = np.random.default_rng(7)


def hx(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def ramp(*cs):
    return [hx(c) for c in cs]


STONE = ramp('#5e564f', '#7a6f65', '#968a7c', '#ae a190'.replace(' ',''), '#c4b7a4', '#d6cab6')
MORTAR = hx('#6e645a')
GRASS = ramp('#3a5a3a', '#4b6f45', '#5f8650', '#77a05c', '#92b96c', '#b0d08a')
WOOD = ramp('#3a2a26', '#553a2e', '#74503a', '#946a4a', '#b38a62')
CREAM = ramp('#8f8270', '#ae9f88', '#cbbda3', '#e2d6bd', '#f1e8d4')
TERRA = ramp('#4a2a2a', '#683834', '#87493e', '#a5604c', '#c07d62')
SLATE = ramp('#2c3242', '#3c4558', '#4f5b70', '#66748a', '#8291a6')
MOSS = ramp('#2a3a36', '#38504a', '#4a675d', '#5f8073', '#7c9b8b')
RED = ramp('#5e2028', '#86303a', '#a8443f', '#c75f50')
INDIGO = ramp('#1f2a40', '#2d3d5c', '#3f5580', '#5a72a0')
AWN = ramp('#2f4a3a', '#3f644b', '#57805e')
GLOW = ramp('#b8743a', '#e0a85a', '#f5d08a', '#fbe7b4')
DARK = ramp('#1e1820', '#2a2230', '#3a2f3c')
LANT = ramp('#5e1f22', '#9a3a30', '#cc5a3c', '#f0a060')
LEAF = ramp('#23402f', '#30573a', '#437248', '#5d8f55', '#7cab68')
METAL = ramp('#2a2a32', '#45454f', '#6a6a74', '#9a9aa2')
FLOW = [hx('#e8a3a8'), hx('#f3e9c9'), hx('#e8c860'), hx('#b9a6d8')]

img = np.zeros((H, W, 3), np.float32)


def noise(cell, seed):
    r = np.random.default_rng(seed)
    gw, gh = W // cell + 2, H // cell + 2
    a = (r.random((gh, gw)) * 255).astype(np.uint8)
    im = Image.fromarray(a).resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:H, :W] / 255.0


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        img[y, x] = c


def rect(x0, y0, x1, y1, c):
    x0, x1 = max(x0, 0), min(x1, W)
    y0, y1 = max(y0, 0), min(y1, H)
    if x0 < x1 and y0 < y1:
        img[y0:y1, x0:x1] = c


def hline(x0, x1, y, c):
    rect(x0, y, x1, y + 1, c)


def vline(x, y0, y1, c):
    rect(x, y0, x + 1, y1, c)


def mul(mask, k=(0.70, 0.72, 0.84)):
    img[mask] *= np.array(k, np.float32)


def ellmask(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0


# ---------------------------------------------------------------- stone street
n_big = noise(28, 1)
y = GY + 10
row = 0
while y < H:
    h = int(round(5 + (y - GY) / (H - GY) * 5))
    x = -int(rng.integers(0, 10)) - (row % 2) * 5
    while x < W:
        w = int(h * 2.4 + rng.integers(-1, 5))
        x0, x1, y0, y1 = x + 1, x + w, y + 1, y + h
        cx, cy = min(max((x0 + x1) // 2, 0), W - 1), min(max((y0 + y1) // 2, 0), H - 1)
        base = 3 if rng.random() < 0.7 else (2 if rng.random() < 0.5 else 4)
        if n_big[cy, cx] > 0.7:
            base = min(base + 1, 4)
        if n_big[cy, cx] < 0.25:
            base = max(base - 1, 2)
        base = int(np.clip(base, 1, 4))
        rect(x, y, x + w, y + h, MORTAR)
        rect(x0, y0, x1, y1, STONE[base])
        hline(x0 + 1, x1, y0, STONE[base + 1])          # top light
        vline(x0, y0 + 1, y1 - 1, STONE[base + 1])      # left light
        hline(x0 + 1, x1, y1 - 1, STONE[base - 1])      # bottom shade
        vline(x1 - 1, y0 + 1, y1 - 1, STONE[base - 1])  # right shade
        for (px, py) in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
            put(px, py, MORTAR)                          # round corners
        if rng.random() < 0.35:                          # speckle / wear
            put(int(rng.integers(x0 + 1, max(x0 + 2, x1 - 1))), int(rng.integers(y0 + 1, max(y0 + 2, y1 - 1))), STONE[base - 1])
        x += w
    y += h
    row += 1

rect(0, GY, W, GY + 10, MORTAR)
for sx in range(-3, W, 15):
    rect(sx + 1, GY + 1, sx + 15, GY + 10, STONE[4])
    hline(sx + 1, sx + 15, GY + 1, STONE[5]); vline(sx + 1, GY + 1, GY + 10, STONE[5])
    hline(sx + 2, sx + 15, GY + 9, STONE[3]); vline(sx + 14, GY + 2, GY + 10, STONE[3])
hline(0, W, GY + 10, STONE[1])   # curb edge
hline(0, W, GY + 11, STONE[2])

# ---------------------------------------------------------------- grass corner
yy, xx = np.mgrid[0:H, 0:W]
ng = noise(14, 3)
field = (xx / W) * 0.95 + ((H - yy) / H) * 1.25 + (ng - 0.5) * 0.22
grass = field < 0.72
grass |= ((xx > W - 30) & (yy > H - 26) & (ng > 0.35))          # small patch bottom-right
n1 = noise(18, 4)
tone = np.full((H, W), 3)
tone[n1 > 0.64] = 4
tone[n1 < 0.30] = 2
fl = rng.random((H, W))
tone[(fl < 0.04)] = 2
tone[(fl > 0.97)] = 4
gcol = np.stack([GRASS[t] for t in range(6)])
img[grass] = gcol[tone[grass]]
# tufts
for _ in range(260):
    x, y = int(rng.integers(0, W)), int(rng.integers(GY, H))
    if grass[y, x] and y + 2 < H and grass[min(y + 2, H - 1), x]:
        put(x, y, GRASS[5]); put(x - 1, y + 1, GRASS[4]); put(x + 1, y + 1, GRASS[4])
        put(x, y + 1, GRASS[1]); put(x - 1, y + 2, GRASS[1]); put(x + 1, y + 2, GRASS[1])
# flowers
for _ in range(26):
    x, y = int(rng.integers(0, W)), int(rng.integers(GY, H))
    if grass[y, x] and field[y, x] < 0.66:
        c = FLOW[int(rng.integers(0, 4))]
        put(x, y, c); put(x, y + 1, GRASS[0])
# grass lip: highlight on grass edge, shadow on stone just below/right
gm = grass.copy()
edge_top = gm & ~np.roll(gm, 1, axis=0)
img[edge_top & (yy > GY)] = GRASS[4]
below = np.roll(gm, 1, axis=0) & ~gm
below2 = np.roll(gm, 2, axis=0) & ~gm
right = np.roll(gm, 1, axis=1) & ~gm
mul(below | right, (0.62, 0.64, 0.78))
mul(below2 & ~below, (0.82, 0.83, 0.9))
# moss in mortar near grass
near = np.zeros_like(gm)
for d in range(1, 6):
    near |= np.roll(gm, d, axis=0) | np.roll(gm, d, axis=1)
mor = (np.abs(img - MORTAR).sum(axis=2) < 4) & near & ~gm
img[mor & (rng.random((H, W)) < 0.5)] = GRASS[1]

# ---------------------------------------------------------------- buildings
img[:GY] = 0


def roof(x0, x1, y0, y1, R, seam=4):
    rect(x0, y0, x1, y1, R[2])
    for ty in range(y0, y1, 4):
        hline(x0, x1, ty, R[3])                  # tile row top light
        hline(x0, x1, min(ty + 3, y1 - 1), R[1])  # tile row bottom shade
        off = (ty // 4) % 2 * (seam // 2)
        for tx in range(x0 + off, x1, seam):
            vline(tx, ty + 1, min(ty + 3, y1), R[1])
    hline(x0, x1, y0, R[4])                       # ridge light
    hline(x0, x1, y1, R[0]); hline(x0, x1, y1 + 1, R[0])  # eave fascia
    for tx in range(x0 + 1, x1, 4):
        put(tx, y1 + 1, R[1])


def wall(x0, x1, y0, y1, C):
    rect(x0, y0, x1, y1, C[3])
    hline(x0, x1, y0, C[1]); hline(x0, x1, y0 + 1, C[2])  # under-eave shadow
    for _ in range((x1 - x0) * (y1 - y0) // 30):
        put(int(rng.integers(x0, x1)), int(rng.integers(y0 + 2, y1)), C[2])


def post(x, y0, y1):
    vline(x, y0, y1, WOOD[1]); vline(x + 1, y0, y1, WOOD[3]); vline(x + 2, y0, y1, WOOD[2])


def base(x0, x1):
    rect(x0, GY - 4, x1, GY, STONE[2])
    hline(x0, x1, GY - 4, STONE[4]); hline(x0, x1, GY - 1, STONE[1])
    for bx in range(x0 + 2, x1, 7):
        vline(bx, GY - 3, GY - 1, STONE[1])


def window(x0, y0, w, h):
    rect(x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1, WOOD[1])
    rect(x0, y0, x0 + w, y0 + h, GLOW[2])
    rect(x0, y0, x0 + w, y0 + 2, GLOW[1])
    put(x0, y0 + 2, GLOW[3]); put(x0 + 1, y0 + 2, GLOW[3])
    vline(x0 + w // 2, y0, y0 + h, WOOD[2]); hline(x0, x0 + w, y0 + h // 2, WOOD[2])
    hline(x0 - 1, x0 + w + 1, y0 + h + 1, WOOD[3])  # sill


def door_dark(x0, x1, y0, y1):
    rect(x0, y0, x1, y1, DARK[1])
    rect(x0, y1 - 3, x1, y1, DARK[2])
    for dx in range(x0 + 1, x1 - 1, 3):
        put(dx, y1 - 2, GLOW[0])                  # warm floor glints


def noren(x0, x1, y0, y1, P, mark=None):
    n = 3
    pw = (x1 - x0 - (n - 1)) // n
    hline(x0 - 1, x1 + 1, y0 - 1, WOOD[1])        # rod
    for i in range(n):
        px0 = x0 + i * (pw + 1)
        rect(px0, y0, px0 + pw, y1, P[2])
        vline(px0, y0, y1, P[3] if i == 0 else P[2])
        vline(px0 + pw - 1, y0, y1, P[1])
        hline(px0, px0 + pw, y1 - 1, P[1])
        hline(px0, px0 + pw, y0, P[1])
        if i % 2:
            hline(px0, px0 + pw, y1, P[1])         # uneven hem
    if mark is not None:
        mx, my = (x0 + x1) // 2 - 2, y0 + 3
        for j, r in enumerate(mark):
            for i, ch in enumerate(r):
                if ch == '#':
                    put(mx + i, my + j, CREAM[4])


def lantern(cx, y0):
    vline(cx, y0 - 2, y0, METAL[1])
    hline(cx - 1, cx + 2, y0, DARK[0])
    rect(cx - 2, y0 + 1, cx + 3, y0 + 8, LANT[2])
    vline(cx - 2, y0 + 2, y0 + 7, LANT[1]); vline(cx + 2, y0 + 2, y0 + 7, LANT[1])
    vline(cx - 1, y0 + 2, y0 + 6, LANT[3])
    hline(cx - 2, cx + 3, y0 + 4, LANT[1])
    hline(cx - 1, cx + 2, y0 + 8, DARK[0])
    put(cx, y0 + 9, LANT[1])


BOWL = ['#####', '.###.', '..#..']

# shop A: ramen (terracotta roof, cream wall, red noren)
roof(-4, 62, 0, 18, TERRA)
wall(-4, 62, 20, GY - 4, CREAM)
post(-1, 20, GY - 4); post(58, 20, GY - 4)
door_dark(18, 42, 27, GY - 4)
noren(18, 42, 27, 40, RED, BOWL)
window(4, 30, 9, 9)
window(47, 30, 8, 9)
lantern(14, 21); lantern(46, 21)
base(-4, 62)
# shop B: cafe (slate roof, wood wall, green awning)
roof(74, 130, 2, 18, SLATE, seam=5)
rect(74, 20, 130, GY - 4, WOOD[2])
for wy in range(22, GY - 4, 3):
    hline(74, 130, wy, WOOD[1]); hline(74, 130, wy + 1, WOOD[3])
hline(74, 130, 20, WOOD[0]); hline(74, 130, 21, WOOD[1])
post(74, 20, GY - 4); post(127, 20, GY - 4)
window(80, 34, 14, 13)
door_dark(100, 112, 33, GY - 4)
vline(100, 33, GY - 4, WOOD[3]); vline(111, 33, GY - 4, WOOD[1])
window(116, 34, 8, 13)
for ax in range(76, 128):                       # striped awning
    c = AWN[2] if (ax // 4) % 2 == 0 else CREAM[3]
    cs = AWN[1] if (ax // 4) % 2 == 0 else CREAM[2]
    vline(ax, 25, 29, c); put(ax, 29, cs)
    if ax % 4 in (1, 2):
        put(ax, 30, cs)                           # scallop
hline(76, 128, 24, AWN[0])
base(74, 130)
# shop C: bento (moss roof, cream wall, indigo noren)
roof(136, W + 4, 0, 18, MOSS)
wall(136, W + 4, 20, GY - 4, CREAM)
post(136, 20, GY - 4); post(W - 3, 20, GY - 4)
door_dark(150, 176, 27, GY - 4)
noren(150, 176, 27, 41, INDIGO, ['#####', '#.#.#', '#####'])
window(180, 30, 9, 9)
lantern(146, 21)
base(136, W + 4)
# alley gaps (between buildings): dark recess + back fence
for gx0, gx1 in ((62, 74), (130, 136)):
    rect(gx0, 0, gx1, GY, DARK[2])
    rect(gx0, 0, gx1, 14, LEAF[1])
    for fx in range(gx0, gx1, 3):
        vline(fx, 30, GY, WOOD[1])
    rect(gx0, GY - 4, gx1, GY, STONE[1])

# tree in front of alley A|B
tree_cx = 68
mul(ellmask(tree_cx + 4, GY + 3, 16, 4))
rect(tree_cx - 2, 30, tree_cx + 2, GY + 1, WOOD[2])
vline(tree_cx - 2, 30, GY + 1, WOOD[1]); vline(tree_cx + 1, 30, GY + 1, WOOD[3])
put(tree_cx - 3, GY, WOOD[1]); put(tree_cx + 2, GY, WOOD[1])
for (cx, cy, rx, ry) in ((68, 18, 14, 11), (59, 26, 8, 7), (78, 25, 9, 7), (68, 8, 9, 7), (63, 14, 7, 6), (74, 13, 7, 6)):
    m = ellmask(cx, cy, rx, ry)
    d = ((xx - cx + rx * 0.35) / rx) ** 2 + ((yy - cy + ry * 0.45) / ry) ** 2
    t = np.where(d < 0.25, 4, np.where(d < 0.6, 3, np.where(d < 0.95, 2, 1)))
    img[m] = np.stack(LEAF)[t[m]]
    edge = m & ~np.roll(m, -1, axis=0)
    img[edge] = LEAF[0]
for _ in range(70):                               # leaf clumps
    x, y = int(rng.integers(52, 88)), int(rng.integers(0, 34))
    if (np.abs(img[y, x] - LEAF[2]).sum() < 3) or (np.abs(img[y, x] - LEAF[3]).sum() < 3):
        put(x, y, LEAF[4]); put(x + 1, y + 1, LEAF[1])

# building cast shadow on street
sh = (yy >= GY) & (yy < GY + 4)
mul(sh & ~grass, (0.72, 0.73, 0.85))

# ---------------------------------------------------------------- props
# A-frame menu board in front of cafe
mul(ellmask(90, GY + 13, 6, 2))
rect(86, GY + 2, 95, GY + 12, WOOD[2])
rect(87, GY + 3, 94, GY + 10, DARK[1])
for ly in (GY + 5, GY + 7):
    hline(88, 93, ly, CREAM[3])
put(88, GY + 9, GLOW[2]); put(89, GY + 9, GLOW[2])
vline(86, GY + 2, GY + 13, WOOD[1]); vline(94, GY + 2, GY + 13, WOOD[1])
# crates by shop A
mul(ellmask(10, GY + 15, 12, 3))
for (bx, by) in ((0, GY + 2), (9, GY + 5)):
    rect(bx, by, bx + 10, by + 9, WOOD[3])
    hline(bx, bx + 10, by, WOOD[4]); hline(bx, bx + 10, by + 8, WOOD[1])
    vline(bx, by, by + 9, WOOD[1]); vline(bx + 9, by, by + 9, WOOD[1])
    hline(bx + 1, bx + 9, by + 4, WOOD[2])
    for k in range(1, 8):
        put(bx + k, by + 1 + k, WOOD[2])
# street lamp right edge
lx = 184
mul(ellmask(lx + 3, GY + 46, 6, 2))
rect(lx - 1, GY + 8, lx + 2, GY + 46, METAL[1])
vline(lx - 1, GY + 8, GY + 46, METAL[2])
rect(lx - 3, GY + 42, lx + 4, GY + 46, METAL[1]); hline(lx - 3, lx + 4, GY + 42, METAL[2])
rect(lx - 3, GY - 2, lx + 4, GY + 8, METAL[0])
rect(lx - 2, GY - 1, lx + 3, GY + 7, GLOW[2]); vline(lx - 2, GY - 1, GY + 7, GLOW[3])
hline(lx - 4, lx + 5, GY - 3, METAL[1])
# planter bottom-right
px0, py0 = 158, H - 22
mul(ellmask(px0 + 15, py0 + 19, 17, 3))
rect(px0, py0 + 8, px0 + 30, py0 + 18, WOOD[2])
hline(px0, px0 + 30, py0 + 8, WOOD[4]); hline(px0, px0 + 30, py0 + 17, WOOD[0])
for k in range(px0 + 5, px0 + 30, 6):
    vline(k, py0 + 9, py0 + 17, WOOD[1])
for (cx, cy) in ((px0 + 6, py0 + 5), (px0 + 15, py0 + 3), (px0 + 24, py0 + 5)):
    m = ellmask(cx, cy, 6, 5)
    img[m] = LEAF[2]
    img[m & ellmask(cx - 1, cy - 2, 3, 2)] = LEAF[3]
    img[m & ~np.roll(m, -1, axis=0)] = LEAF[0]
for k in range(10):
    put(px0 + 3 + k * 3, py0 + 2 + (k * 7) % 6, FLOW[k % 4])

out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
out.save(os.path.join(HERE, 'bg34.png'))
out.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(HERE, 'bg34_x3.png'))
print('ok')
