"""一般頁面的背景「公會前的廣場」：跟戰鬥背景同一套畫法（斜俯視、石板立體、光從左上、背景不描黑邊）。
216×470，顯示時整數 2 倍、貼齊底部（下半部最常從視窗之間露出來，細節放在下面；中段會被視窗擋住，石板對比調低）。"""
import os, math, re
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 216, 470
rng = np.random.default_rng(21)


def hx(c):
    c = c.lstrip('#'); return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def ramp(*cs): return [hx(c) for c in cs]


STONE = ramp('#5e564f', '#7a6f65', '#968a7c', '#aea190', '#c4b7a4', '#d6cab6')
STONEM = ramp('#6c645c', '#837a70', '#9a8f82', '#aca091', '#bdb1a0', '#cbbfae')   # 中段低對比石板
MORTAR = hx('#6e645a')
GRASS = ramp('#3a5a3a', '#4b6f45', '#5f8650', '#77a05c', '#92b96c', '#b0d08a')
WOOD = ramp('#3a2a26', '#553a2e', '#74503a', '#946a4a', '#b38a62')
CREAM = ramp('#8f8270', '#ae9f88', '#cbbda3', '#e2d6bd', '#f1e8d4')
TERRA = ramp('#4a2a2a', '#683834', '#87493e', '#a5604c', '#c07d62')
SLATE = ramp('#2c3242', '#3c4558', '#4f5b70', '#66748a', '#8291a6')
RED = ramp('#5e2028', '#86303a', '#a8443f', '#c75f50')
GOLD = ramp('#6e4a14', '#a0701e', '#d0a038', '#f0d070')
GLOW = ramp('#b8743a', '#e0a85a', '#f5d08a', '#fbe7b4')
DARK = ramp('#1e1820', '#2a2230', '#3a2f3c')
LEAF = ramp('#23402f', '#30573a', '#437248', '#5d8f55', '#7cab68')
METAL = ramp('#2a2a32', '#45454f', '#6a6a74', '#9a9aa2')
WATER = ramp('#2e5f7a', '#3f7d9a', '#5aa0bc', '#8cc8dc', '#d8f0f6')
SKY = ramp('#8fc7e4', '#a5d3ea', '#bfe0f0')
PAPER = ramp('#b8a888', '#d8ccb0', '#f0e8d4')
FLOW = [hx('#e8a3a8'), hx('#f3e9c9'), hx('#e8c860'), hx('#b9a6d8'), hx('#e07858')]

img = np.zeros((H, W, 3), np.float32)
yy, xx = np.mgrid[0:H, 0:W]


def put(x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H: img[y, x] = c


def rect(x0, y0, x1, y1, c):
    x0, x1 = max(int(x0), 0), min(int(x1), W); y0, y1 = max(int(y0), 0), min(int(y1), H)
    if x0 < x1 and y0 < y1: img[y0:y1, x0:x1] = c


def hline(x0, x1, y, c): rect(x0, y, x1, y + 1, c)
def vline(x, y0, y1, c): rect(x, y0, x + 1, y1, c)
def ell(cx, cy, rx, ry): return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0
def mul(mask, k=(0.70, 0.72, 0.84)): img[mask] *= np.array(k, np.float32)


def noise(cell, seed):
    r = np.random.default_rng(seed); gw, gh = W // cell + 2, H // cell + 2
    a = (r.random((gh, gw)) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(a).resize((gw * cell, gh * cell), Image.BICUBIC), np.float32)[:H, :W] / 255


# ================================================================ 道具
def shadow(cx, cy, rx, ry=None): mul(ell(cx, cy, rx, ry or max(2, rx * .3)))


def lamp(x, y0, h=46):
    shadow(x + 3, y0 + h, 6, 2)
    rect(x - 1, y0 + 8, x + 2, y0 + h, METAL[1]); vline(x - 1, y0 + 8, y0 + h, METAL[2])
    rect(x - 3, y0 + h - 4, x + 4, y0 + h, METAL[1]); hline(x - 3, x + 4, y0 + h - 4, METAL[2])
    rect(x - 3, y0 - 2, x + 4, y0 + 8, METAL[0]); rect(x - 2, y0 - 1, x + 3, y0 + 7, GLOW[2]); vline(x - 2, y0 - 1, y0 + 7, GLOW[3])
    hline(x - 4, x + 5, y0 - 3, METAL[1]); put(x, y0 - 4, METAL[2])


def tree(cx, base, s=1.0):
    shadow(cx + 6, base + 2, 18 * s, 5 * s)
    rect(cx - 2, base - 26 * s, cx + 2, base + 1, WOOD[2]); vline(cx - 2, base - 26 * s, base + 1, WOOD[1]); vline(cx + 1, base - 26 * s, base + 1, WOOD[3])
    for (dx, dy, rx, ry) in ((0, -40, 15, 12), (-9, -32, 9, 8), (10, -33, 10, 8), (0, -50, 10, 8), (-6, -45, 8, 7), (7, -46, 8, 7)):
        cx_, cy_ = cx + dx * s, base + dy * s
        m = ell(cx_, cy_, rx * s, ry * s)
        d = ((xx - cx_ + rx * s * .35) / (rx * s)) ** 2 + ((yy - cy_ + ry * s * .45) / (ry * s)) ** 2
        t = np.where(d < .25, 4, np.where(d < .6, 3, np.where(d < .95, 2, 1)))
        img[m] = np.stack(LEAF)[t[m]]
        img[m & ~np.roll(m, -1, axis=0)] = LEAF[0]
    for _ in range(60):
        x_, y_ = int(rng.integers(cx - 18 * s, cx + 18 * s)), int(rng.integers(base - 60 * s, base - 26 * s))
        if 0 <= x_ < W - 1 and 0 <= y_ < H - 1 and np.abs(img[y_, x_] - LEAF[3]).sum() < 3:
            put(x_, y_, LEAF[4]); put(x_ + 1, y_ + 1, LEAF[1])


def barrel(x, y):
    shadow(x + 5, y + 12, 7, 2)
    rect(x, y, x + 9, y + 12, WOOD[3]); vline(x, y, y + 12, WOOD[2]); vline(x + 8, y, y + 12, WOOD[1])
    for by in (y + 2, y + 9): hline(x, x + 9, by, METAL[1])
    rect(x + 1, y - 2, x + 8, y + 1, WOOD[4]); hline(x + 1, x + 8, y - 2, WOOD[3])


def crate(x, y, s=10):
    shadow(x + s // 2 + 2, y + s, s * .7, 2)
    rect(x, y, x + s, y + s, WOOD[3]); hline(x, x + s, y, WOOD[4]); hline(x, x + s, y + s - 1, WOOD[1])
    vline(x, y, y + s, WOOD[1]); vline(x + s - 1, y, y + s, WOOD[1])
    for k in range(1, s - 1): put(x + k, y + k, WOOD[2])


def bench(x, y):
    shadow(x + 13, y + 9, 14, 2)
    rect(x, y, x + 24, y + 3, WOOD[3]); hline(x, x + 24, y, WOOD[4]); hline(x, x + 24, y + 2, WOOD[2])
    rect(x, y - 6, x + 24, y - 4, WOOD[3]); hline(x, x + 24, y - 6, WOOD[4])
    for lx in (x + 2, x + 20): rect(lx, y + 3, lx + 2, y + 8, METAL[1]); rect(lx, y - 4, lx + 2, y, METAL[1])


def flowerbed(x0, y0, x1, y1):
    shadow((x0 + x1) / 2 + 2, y1 + 1, (x1 - x0) / 2, 2)
    rect(x0, y0, x1, y1, STONE[2]); hline(x0, x1, y0, STONE[4]); hline(x0, x1, y1 - 1, STONE[1])
    rect(x0 + 2, y0 + 1, x1 - 2, y1 - 2, hx('#4a3a2a'))
    for _ in range(int((x1 - x0) * (y1 - y0) / 4)):
        fx_, fy_ = int(rng.integers(x0 + 2, x1 - 2)), int(rng.integers(y0 - 3, y1 - 2))
        put(fx_, fy_, LEAF[int(rng.integers(2, 5))])
    for _ in range(int((x1 - x0) / 2)):
        fx_, fy_ = int(rng.integers(x0 + 2, x1 - 2)), int(rng.integers(y0 - 3, y1 - 3))
        c = FLOW[int(rng.integers(0, 5))]; put(fx_, fy_, c); put(fx_ + 1, fy_, c); put(fx_, fy_ - 1, c * .85 + 30)


def questboard(x, y):
    """公會委託告示板：木框 + 貼滿的委託單"""
    shadow(x + 18, y + 30, 18, 3)
    for px_ in (x + 2, x + 31): rect(px_, y + 4, px_ + 3, y + 30, WOOD[2]); vline(px_, y + 4, y + 30, WOOD[3])
    rect(x, y, x + 36, y + 20, WOOD[1]); rect(x + 1, y + 1, x + 35, y + 19, WOOD[3]); rect(x + 2, y + 2, x + 34, y + 18, hx('#8a6a48'))
    for i in range(-1, 38): put(x + i, y - 1, TERRA[2]); put(x + i, y - 2, TERRA[3])   # 小屋簷
    for (px_, py_, w_, h_, c) in ((x + 4, y + 4, 8, 9, PAPER[2]), (x + 14, y + 3, 7, 7, PAPER[1]), (x + 23, y + 5, 9, 10, PAPER[2]),
                                  (x + 13, y + 11, 8, 6, hx('#f0d8c8')), (x + 4, y + 14, 6, 3, PAPER[1])):
        rect(px_, py_, px_ + w_, py_ + h_, c); hline(px_, px_ + w_, py_ + h_ - 1, PAPER[0])
        put(px_ + w_ // 2, py_, RED[2])                    # 圖釘
        for ly in range(py_ + 2, py_ + h_ - 2, 2): hline(px_ + 1, px_ + w_ - 2, ly, PAPER[0])


def fountain(cx, cy):
    """噴水池：石砌圓池（看得到池壁高度，立在地上）+ 水面 + 中央水柱"""
    wall = 7                                                   # 池壁高度
    mul(ell(cx + 3, cy + wall + 2, 45, 13) & ~ell(cx, cy + wall, 43, 14))      # 影子貼著池腳（偏右下）
    base_m = ell(cx, cy + wall, 42, 14)                        # 池腳（底部輪廓）
    top_m = ell(cx, cy, 42, 14)                                # 池口
    body = base_m | (top_m & (yy > cy)) | ((np.abs(xx - cx) <= 42) & (yy >= cy) & (yy <= cy + wall) &
                                           (((xx - cx) / 42.0) ** 2 <= 1))
    img[body & ~top_m] = STONE[2]                              # 池壁正面
    for a in np.linspace(.05, math.pi - .05, 14):              # 池壁石塊縫（垂直）
        x_ = cx + 42 * math.cos(a)
        for y_ in range(int(cy + 14 * math.sin(a)), int(cy + 14 * math.sin(a) + wall)):
            put(x_, y_, STONE[1])
    for x_ in range(int(cx - 42), int(cx + 43)):               # 池壁明暗：左亮右暗、底部暗邊
        t = (x_ - cx) / 42.0
        if abs(t) > 1: continue
        yb = cy + wall + 14 * math.sqrt(max(0, 1 - t * t))
        put(x_, yb, STONE[0]); put(x_, yb - 1, STONE[1])
        if t < -.55:
            for y_ in range(int(cy + 14 * math.sqrt(max(0, 1 - t * t))) + 1, int(yb) - 1): put(x_, y_, STONE[3])
        if t > .55:
            for y_ in range(int(cy + 14 * math.sqrt(max(0, 1 - t * t))) + 1, int(yb) - 1): put(x_, y_, STONE[1])
    img[top_m] = STONE[4]                                      # 池緣上面（平的石頭）
    img[top_m & ~ell(cx, cy + 1, 42, 14)] = STONE[5]
    inner = ell(cx, cy - .5, 36, 10.5)
    img[inner] = WATER[2]
    img[inner & ell(cx - 8, cy - 3.5, 22, 4.5)] = WATER[3]
    img[inner & ~ell(cx, cy + 1.2, 36, 10.5)] = WATER[0]       # 內壁陰影（水面上緣）
    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):  # 池緣石塊接縫
        put(cx + 39 * math.cos(a), cy + 12.3 * math.sin(a), STONE[2])
    for (rx_, ry_) in ((11, 3.5), (21, 6.5)):                  # 漣漪
        for a in np.linspace(0, 2 * math.pi, 40):
            if math.sin(a * 3) > .3: put(cx + rx_ * math.cos(a), cy - .5 + ry_ * math.sin(a), WATER[4] if a < 3 else WATER[3])
    rect(cx - 4, cy - 12, cx + 5, cy + 1, STONE[3]); vline(cx - 4, cy - 12, cy + 1, STONE[5]); vline(cx + 4, cy - 12, cy + 1, STONE[1])
    img[ell(cx, cy - 13, 8, 3)] = STONE[4]; img[ell(cx, cy - 13.5, 6, 2)] = WATER[2]
    rect(cx - 1, cy - 30, cx + 2, cy - 13, WATER[3]); vline(cx - 1, cy - 30, cy - 13, WATER[4])
    for (dx, dy) in ((-3, -30), (3, -29), (-6, -26), (6, -25), (-8, -21), (8, -20), (-9, -16), (9, -15)):
        put(cx + dx, cy + dy, WATER[4]); put(cx + dx * .8, cy + dy + 2, WATER[3])




def scene_plaza():
    img[:] = 0
    # ================================================================ 天空 + 遠方屋頂（只有高螢幕才看得到）
    rect(0, 0, W, 60, SKY[1]); rect(0, 0, W, 18, SKY[0]); rect(0, 40, W, 60, SKY[2])
    for x in range(0, W, 2):
        put(x + 1, 17, SKY[1]); put(x, 40, SKY[1])
    x = -4
    for k in range(12):
        w = int(rng.integers(16, 26)); R_ = (TERRA, SLATE, TERRA)[k % 3]
        for i in range(w):
            top = 36 + abs(i - w / 2) / (w / 2) * 6
            rect(x + i, top, x + i + 1, 66, R_[2]); put(x + i, top, R_[3])
        x += w - 2

    # ================================================================ 石板廣場（斜俯視，越往下石頭越大）
    GY = 128
    n_big = noise(30, 1)
    y = GY; row = 0
    while y < H:
        h = int(round(5 + (y - GY) / (H - GY) * 5))
        # 被視窗擋住的中段：低對比，上下 20px 漸變過渡（看不出分界）
        wgt = float(np.clip(min((y - 140) / 24, (290 - y) / 24), 0, 1))
        S = [a * (1 - wgt) + b * wgt for a, b in zip(STONE, STONEM)]
        mid = wgt > .5
        x = -int(rng.integers(0, 10)) - (row % 2) * 6
        while x < W:
            w = int(h * 2.3 + rng.integers(-1, 5))
            x0, x1, y0, y1 = x + 1, x + w, y + 1, y + h
            cx, cy = min(max((x0 + x1) // 2, 0), W - 1), min(max((y0 + y1) // 2, 0), H - 1)
            base = 3 if rng.random() < .7 else (2 if rng.random() < .5 else 4)
            if n_big[cy, cx] > .7: base = min(base + 1, 4)
            if n_big[cy, cx] < .25: base = max(base - 1, 2)
            rect(x, y, x + w, y + h, MORTAR * (1 - wgt) + STONEM[1] * wgt)
            rect(x0, y0, x1, y1, S[base])
            hline(x0 + 1, x1, y0, S[base + 1]); vline(x0, y0 + 1, y1 - 1, S[base + 1])
            hline(x0 + 1, x1, y1 - 1, S[base - 1]); vline(x1 - 1, y0 + 1, y1 - 1, S[base - 1])
            for (px_, py_) in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
                put(px_, py_, MORTAR * (1 - wgt) + STONEM[1] * wgt)
            if not mid and rng.random() < .3:
                put(int(rng.integers(x0 + 1, max(x0 + 2, x1 - 1))), int(rng.integers(y0 + 1, max(y0 + 2, y1 - 1))), S[base - 1])
            x += w
        y += h; row += 1
    # 石縫青苔（下半部）
    mor = (np.abs(img - MORTAR).sum(axis=2) < 4) & (yy > 280)
    img[mor & (rng.random((H, W)) < .22)] = GRASS[1]

    # ================================================================ 草地：左下、右下兩角
    ng = noise(14, 3)
    field_l = (xx / W) * 1.2 + ((H - yy) / H) * 2.6 + (ng - .5) * .25
    field_r = ((W - xx) / W) * 1.2 + ((H - yy) / H) * 2.6 + (ng - .5) * .25
    grass = (field_l < .55) | (field_r < .5)
    n1 = noise(18, 4)
    tone = np.full((H, W), 3); tone[n1 > .64] = 4; tone[n1 < .3] = 2
    fl = rng.random((H, W)); tone[fl < .04] = 2; tone[fl > .97] = 4
    img[grass] = np.stack(GRASS)[tone[grass]]
    for _ in range(220):
        x_, y_ = int(rng.integers(0, W)), int(rng.integers(300, H - 2))
        if grass[y_, x_] and grass[min(y_ + 2, H - 1), x_]:
            put(x_, y_, GRASS[5]); put(x_ - 1, y_ + 1, GRASS[4]); put(x_ + 1, y_ + 1, GRASS[4])
            put(x_, y_ + 1, GRASS[1]); put(x_ - 1, y_ + 2, GRASS[1]); put(x_ + 1, y_ + 2, GRASS[1])
    for _ in range(40):
        x_, y_ = int(rng.integers(0, W)), int(rng.integers(320, H))
        if grass[y_, x_]: put(x_, y_, FLOW[int(rng.integers(0, 5))]); put(x_, y_ + 1, GRASS[0])
    edge_top = grass & ~np.roll(grass, 1, axis=0); img[edge_top] = GRASS[4]
    below = np.roll(grass, 1, axis=0) & ~grass
    mul(below, (.62, .64, .78))

    # ================================================================ 兩側的房子（填滿公會大樓旁邊）
    for (hx0, hx1, R_) in ((-6, 22, SLATE), (194, 222, SLATE)):
        for ty in range(58, 96, 4):
            rect(hx0, ty, hx1, ty + 4, R_[2]); hline(hx0, hx1, ty, R_[3]); hline(hx0, hx1, ty + 3, R_[1])
        rect(hx0, 95, hx1, 98, R_[0])
        rect(hx0, 98, hx1, 126, CREAM[2]); hline(hx0, hx1, 98, CREAM[0])
        wx = hx0 + 9; rect(wx - 1, 106, wx + 9, 116, WOOD[1]); rect(wx, 107, wx + 8, 115, GLOW[1]); vline(wx + 4, 107, 115, WOOD[2])
        rect(hx0, 124, hx1, 128, STONE[2])

    # ================================================================ 公會大樓（上方）
    gx0, gx1 = 18, 198
    # 屋頂（瓦片，斜俯視看到屋頂面）+ 中央山牆
    for ty in range(62, 92, 4):
        rect(gx0 - 8, ty, gx1 + 8, ty + 4, TERRA[2]); hline(gx0 - 8, gx1 + 8, ty, TERRA[3]); hline(gx0 - 8, gx1 + 8, ty + 3, TERRA[1])
        off = (ty // 4) % 2 * 3
        for tx in range(gx0 - 8 + off, gx1 + 8, 6): vline(tx, ty + 1, ty + 3, TERRA[1])
    hline(gx0 - 8, gx1 + 8, 62, TERRA[4])
    for i in range(70, 146):                                  # 山牆三角
        t = abs(i - 108) / 38
        top = int(52 + t * 22)
        rect(i, top, i + 1, 96, TERRA[2] if abs(i - 108) > 2 else TERRA[3]); put(i, top, TERRA[4])
    rect(gx0 - 8, 92, gx1 + 8, 95, TERRA[0])                  # 簷口
    for tx in range(gx0 - 7, gx1 + 8, 4): put(tx, 94, TERRA[1])
    # 牆：奶油色 + 木骨架
    rect(gx0, 95, gx1, 124, CREAM[3])
    hline(gx0, gx1, 95, CREAM[1]); hline(gx0, gx1, 96, CREAM[2])
    for bx in range(gx0, gx1 + 1, 30):
        rect(bx, 95, bx + 3, 124, WOOD[2]); vline(bx, 95, 124, WOOD[1]); vline(bx + 2, 95, 124, WOOD[3])
    for bx in range(gx0 + 3, gx1 - 3, 30):                   # 斜撐
        for k in range(10):
            put(bx + 2 + k, 98 + k, WOOD[2]); put(bx + 26 - k, 98 + k, WOOD[2])
    hline(gx0, gx1, 109, WOOD[1]); hline(gx0, gx1, 110, WOOD[3])
    # 窗（暖光 + 花台）
    for wx in (30, 60, 146, 176):
        rect(wx - 1, 112, wx + 11, 122, WOOD[1]); rect(wx, 113, wx + 10, 121, GLOW[2])
        rect(wx, 113, wx + 10, 115, GLOW[1]); vline(wx + 5, 113, 121, WOOD[2])
        rect(wx - 1, 122, wx + 11, 124, WOOD[3])
        for k in range(0, 12, 2): put(wx + k - 1, 121, LEAF[3]); put(wx + k, 121, FLOW[k % 5])
    # 大門 + 拱 + 招牌（拉麵碗徽章）
    rect(96, 104, 120, 124, DARK[1]); rect(98, 106, 118, 124, DARK[2]); vline(108, 106, 124, WOOD[1])
    for i in range(94, 122):
        t = abs(i - 108) / 14; top = int(100 + t * t * 4); put(i, top, WOOD[3]); put(i, top + 1, WOOD[1])
    for (x0_, y0_) in ((101, 113), (113, 113)): put(x0_, y0_, GOLD[3])
    rect(88, 76, 128, 90, WOOD[1]); rect(89, 77, 127, 89, WOOD[3]); hline(89, 127, 77, WOOD[4])
    for (dx, dy, c) in ((0, 0, RED[2]), (1, 0, RED[2]), (2, 0, RED[2]), (3, 0, RED[2]), (4, 0, RED[2]), (5, 0, RED[2]), (6, 0, RED[2]),
                        (1, 1, RED[1]), (2, 1, RED[2]), (3, 1, RED[2]), (4, 1, RED[2]), (5, 1, RED[1]), (2, 2, RED[1]), (3, 2, RED[1]), (4, 2, RED[1])):
        put(105 + dx, 83 + dy, c)
    for k in range(3): put(106 + k * 2, 80, CREAM[4]); put(106 + k * 2, 81, CREAM[3])   # 熱氣
    # 旗子
    for fx in (80, 136):
        rect(fx, 96, fx + 8, 112, RED[2]); vline(fx, 96, 112, RED[3]); vline(fx + 7, 96, 112, RED[1])
        put(fx + 2, 112, RED[2]); put(fx + 5, 112, RED[2]); put(fx + 3, 113, RED[1])
        for k in range(2, 6): put(fx + k, 102, GOLD[2]); put(fx + k, 103, GOLD[1])
        hline(fx - 1, fx + 9, 95, METAL[2])
    # 牆腳石基座
    rect(gx0, 124, gx1, 128, STONE[2]); hline(gx0, gx1, 124, STONE[4]); hline(gx0, gx1, 127, STONE[1])
    for bx in range(gx0 + 3, gx1, 8): vline(bx, 125, 127, STONE[1])
    # 台階
    for k, sy in enumerate((124, 127)):
        rect(90 - k * 4, sy, 126 + k * 4, sy + 3, STONE[4 - k]); hline(90 - k * 4, 126 + k * 4, sy, STONE[5 - k])
    # 大樓投影
    mul((yy >= 124) & (yy < 129) & ((xx < 82) | (xx > 134)), (.72, .73, .85))

    # 配置：隊伍頁最常露出來的是圖片底部往上約 40~90px（底下 32px 被導覽列蓋住），噴水池放在這一段
    tree(14, 236, 1.0); tree(204, 214, 1.0)
    lamp(8, 150); lamp(206, 150)
    barrel(4, 132); barrel(13, 134); crate(196, 132); crate(186, 136, 8)
    questboard(8, 330)
    bench(168, 346)
    lamp(62, 352); lamp(154, 348)
    fountain(108, 404)
    flowerbed(18, 404, 52, 412); flowerbed(164, 404, 198, 412)
    tree(8, 462, 1.0); tree(210, 456, 1.0)



# ================================================================ 戰鬥場景等級的草地與樹
def grass_fill(grass, seed=4):
    """跟戰鬥背景同一套草地：三階色塊 + 零星亮暗點 + 小草叢 + 小花 + 邊緣亮邊 + 壓在石板上的陰影 + 石縫青苔"""
    r = np.random.default_rng(seed)
    n1 = noise(18, seed)
    tone = np.full((H, W), 3); tone[n1 > .64] = 4; tone[n1 < .30] = 2
    fl = r.random((H, W)); tone[fl < .04] = 2; tone[fl > .97] = 4
    img[grass] = np.stack(GRASS)[tone[grass]]
    ys_, xs_ = np.nonzero(grass)
    for _ in range(int(len(xs_) / 38)):                       # 小草叢
        i = int(r.integers(0, len(xs_))); x, y = int(xs_[i]), int(ys_[i])
        if y + 2 < H and grass[y + 2, x]:
            put(x, y, GRASS[5]); put(x - 1, y + 1, GRASS[4]); put(x + 1, y + 1, GRASS[4])
            put(x, y + 1, GRASS[1]); put(x - 1, y + 2, GRASS[1]); put(x + 1, y + 2, GRASS[1])
    for _ in range(int(len(xs_) / 300)):                      # 小花
        i = int(r.integers(0, len(xs_))); x, y = int(xs_[i]), int(ys_[i])
        put(x, y, FLOW[int(r.integers(0, 5))]); put(x, y + 1, GRASS[0])
    def sh_(m, d, ax):                     # 位移但不從另一邊繞回來（np.roll 會把底部繞到最上面）
        o = np.roll(m, d, axis=ax)
        if ax == 0: o[:d] = False
        else: o[:, :d] = False
        return o
    edge_top = grass & ~sh_(grass, 1, 0)
    edge_top[0] = False
    img[edge_top] = GRASS[4]
    below = sh_(grass, 1, 0) & ~grass
    below2 = sh_(grass, 2, 0) & ~grass
    right = sh_(grass, 1, 1) & ~grass
    mul(below | right, (.62, .64, .78)); mul(below2 & ~below, (.82, .83, .9))
    near = np.zeros_like(grass)
    for d in range(1, 6): near |= sh_(grass, d, 0) | sh_(grass, d, 1)
    mor = (np.abs(img - MORTAR).sum(axis=2) < 8) & near & ~grass
    img[mor & (r.random((H, W)) < .5)] = GRASS[1]


def tree2(cx, base, s=1.0, seed=0):
    """樹：幾十簇葉子堆成不規則樹冠（每簇有受光面/陰影、邊緣葉片突出），樹冠下半整體壓暗；粗樹幹 + 樹皮 + 根"""
    r = np.random.default_rng(100 + seed)
    ccx, ccy, RX, RY = cx, base - 40 * s, 21 * s, 17 * s
    # 地上的影子（偏右下、不規則）
    shm = np.zeros((H, W), bool)                 # 影子：合併成一塊，只壓暗一次
    for k in range(7):
        shm |= ell(cx + 8 * s + r.normal(0, 4), base + 1 + r.normal(0, 1), 9 * s, 3 * s)
    mul(shm)
    # 樹幹 + 根
    tw = max(3, int(5 * s))
    for yy_ in range(int(base - 30 * s), base + 1):
        flare = max(0, (yy_ - (base - 6 * s)) * .6)
        x0, x1 = int(cx - tw / 2 - flare), int(cx + tw / 2 + flare)
        rect(x0, yy_, x1 + 1, yy_ + 1, WOOD[2]); put(x0, yy_, WOOD[1]); put(x1, yy_, WOOD[1]); put(x0 + 1, yy_, WOOD[3])
        if yy_ % 3 == 0: put(cx + int(r.integers(-1, 2)), yy_, WOOD[1])     # 樹皮紋
    for (bx, by, ex, ey) in ((cx, base - 26 * s, cx - 9 * s, base - 38 * s), (cx, base - 24 * s, cx + 10 * s, base - 36 * s)):
        for t in np.linspace(0, 1, 14): put(bx + (ex - bx) * t, by + (ey - by) * t, WOOD[1]); put(bx + (ex - bx) * t + 1, by + (ey - by) * t, WOOD[2])
    # 樹冠：葉簇
    clumps = []
    for _ in range(int(46 * s * s) + 10):
        a = r.uniform(0, 2 * math.pi); d = math.sqrt(r.uniform(0, 1))
        x = ccx + math.cos(a) * d * RX; y = ccy + math.sin(a) * d * RY
        clumps.append((y, x, r.uniform(3.2, 5.2) * s))
    clumps.sort()
    for (y, x, rad) in clumps:
        m = ell(x, y, rad, rad * .85)
        dd = ((xx - x + rad * .4) / rad) ** 2 + ((yy - y + rad * .45) / rad) ** 2
        t = np.where(dd < .22, 4, np.where(dd < .62, 3, np.where(dd < 1.0, 2, 1)))
        depth = (y - (ccy - RY)) / (2 * RY) + (x - (ccx - RX)) / (4 * RX)      # 越右下越暗
        t = np.clip(t - (1 if depth > .72 else 0) - (1 if depth > .95 else 0), 0, 4)
        img[m] = np.stack(LEAF)[t[m]]
        img[m & ~np.roll(m, -1, axis=0) & (t <= 2)] = LEAF[0]
    # 邊緣突出的葉片 + 葉縫暗點
    for _ in range(int(70 * s)):
        a = r.uniform(0, 2 * math.pi)
        x = int(ccx + math.cos(a) * (RX + r.uniform(0, 3))); y = int(ccy + math.sin(a) * (RY + r.uniform(0, 2)))
        if 0 <= x < W and 0 <= y < H:
            put(x, y, LEAF[2] if math.sin(a) < 0 else LEAF[1])
    for _ in range(int(30 * s)):
        x = int(ccx + r.uniform(-RX * .8, RX * .8)); y = int(ccy + r.uniform(-RY * .6, RY * .8))
        put(x, y, LEAF[0])


# ================================================================ 精修道具（商店街用）
def battle_band(y_off, rows=74):
    """直接用戰鬥背景那排店（src/bg34.py，寬度改 216 重畫），貼到 y_off：兩張圖就是同一條街"""
    src = open(os.path.join(HERE, 'bg34.py'), encoding='utf-8').read()
    src = src.replace('W, H = 192, 230', 'W, H = 216, 230')
    src = re.sub(r"out\.save\([^)]*\)\)?\n", "\n", src)
    src = re.sub(r"out\.resize\([^\n]*\n", "\n", src)
    src = src.replace("print('ok')", "")
    ns = {'__file__': os.path.join(HERE, 'bg34.py'), '__name__': 'bg34_band'}
    exec(compile(src, 'bg34_band', 'exec'), ns)
    band = ns['img'][:min(rows, H - y_off)]
    keep = band.sum(axis=2) > 0                       # 戰鬥背景裡沒塗到的純黑像素不貼（保留後面的遠景）
    region = img[y_off:y_off + band.shape[0]]
    region[keep] = band[keep]


def far_houses(y_base):
    """遠景房子：牆、窗、煙囪，顏色往天空淡化（空氣遠近感）"""
    haze = SKY[2]
    def hz(c, k=.42): return c * (1 - k) + haze * k
    x = -6; k = 0
    while x < W:
        w = int(rng.integers(18, 28)); hgt = int(rng.integers(14, 22)); R_ = (TERRA, SLATE, TERRA, SLATE)[k % 4]; k += 1
        top = y_base - hgt
        rect(x + 1, top + 8, x + w - 1, y_base, hz(CREAM[2]))                       # 牆
        for wx in range(x + 4, x + w - 4, 6):
            rect(wx, top + 11, wx + 2, top + 14, hz(GLOW[1], .3))
        for i in range(w):                                                           # 屋頂（中間高）
            t = abs(i - w / 2) / (w / 2); ry = int(top + t * 5)
            rect(x + i, ry, x + i + 1, top + 9, hz(R_[2])); put(x + i, ry, hz(R_[3]))
            if (i + k) % 3 == 0: put(x + i, ry + 3, hz(R_[1]))
        if k % 2: rect(x + w - 7, top - 3, x + w - 4, top + 3, hz(STONE[2])); put(x + w - 7, top - 3, hz(STONE[4]))   # 煙囪
        x += w - 1


def clouds():
    for (cx, cy, s) in ((40, 18, 1.0), (150, 30, 1.25), (196, 12, .7)):
        for (dx, dy, rx, ry) in ((0, 0, 12, 4), (-8, 2, 8, 3), (9, 1, 9, 3.5), (2, -3, 7, 3)):
            m = ell(cx + dx * s, cy + dy * s, rx * s, ry * s); img[m] = hx('#e9f5fb')
        img[ell(cx - 2 * s, cy - 2 * s, 9 * s, 2.2 * s)] = hx('#ffffff')
        img[ell(cx + 2 * s, cy + 3 * s, 12 * s, 1.5 * s) & (yy > cy + 2 * s)] = hx('#cfe6f2')


def barrel2(x, y):
    """木桶：頂面橢圓 + 木板條 + 兩道鐵箍 + 左亮右暗"""
    shadow(x + 7, y + 15, 8, 2.5)
    for i in range(12):
        t = (i - 5.5) / 6; bulge = 1 if 2 <= i <= 9 else 0
        c = WOOD[4] if t < -.5 else WOOD[3] if t < .2 else WOOD[2] if t < .7 else WOOD[1]
        rect(x + i, y + 2 - bulge, x + i + 1, y + 15 + bulge * 0, c)
        if i % 3 == 0: vline(x + i, y + 3, y + 14, WOOD[1])
    for by in (y + 4, y + 11):
        hline(x, x + 12, by, METAL[1]); put(x + 1, by, METAL[3]); put(x + 2, by, METAL[2])
    img[ell(x + 5.5, y + 2, 6, 2)] = WOOD[4]; img[ell(x + 5.5, y + 2, 4.5, 1.2)] = WOOD[3]
    hline(x + 2, x + 10, y + 15, WOOD[0])


def crate2(x, y, s=12):
    """木箱：頂面 + 正面板條 + 斜撐 + 釘子"""
    shadow(x + s // 2 + 3, y + s + 4, s * .7, 2)
    rect(x + 2, y, x + s + 2, y + 4, WOOD[4]); hline(x + 2, x + s + 2, y, CREAM[2])            # 頂面
    for k in range(x + 4, x + s + 2, 4): vline(k, y, y + 4, WOOD[3])
    rect(x, y + 4, x + s, y + s + 4, WOOD[3])                                                   # 正面
    hline(x, x + s, y + 4, WOOD[4]); hline(x, x + s, y + s + 3, WOOD[1])
    vline(x, y + 4, y + s + 4, WOOD[1]); vline(x + s - 1, y + 4, y + s + 4, WOOD[1])
    rect(x + s, y + 1, x + s + 2, y + s + 4, WOOD[1])                                           # 側面
    hline(x + 1, x + s - 1, y + 4 + s // 2, WOOD[2])
    for k in range(1, s - 1): put(x + k, y + 4 + k * (s - 1) // s, WOOD[2])
    for (nx, ny) in ((x + 1, y + 5), (x + s - 2, y + 5), (x + 1, y + s + 2), (x + s - 2, y + s + 2)): put(nx, ny, METAL[2])


def pot_plant(x, y, seed=0):
    """盆栽：陶盆（盆緣、土）+ 葉簇堆成的植物"""
    r = np.random.default_rng(300 + seed)
    shadow(x + 8, y + 13, 9, 2.5)
    for i in range(14):                                     # 盆身：上寬下窄、左亮右暗
        t = i / 13
        c = TERRA[3] if t < .25 else TERRA[2] if t < .7 else TERRA[1]
        inset = 1 if i in (0, 13) else 0
        rect(x + i, y + 3, x + i + 1, y + 12 - inset, c)
    rect(x - 1, y + 1, x + 15, y + 4, TERRA[3]); hline(x - 1, x + 15, y + 1, TERRA[4]); hline(x - 1, x + 15, y + 3, TERRA[1])   # 盆緣
    rect(x + 1, y + 1, x + 13, y + 2, hx('#4a3424'))                                             # 土
    hline(x + 1, x + 13, y + 11, TERRA[0])
    cl = [(r.uniform(-1, 1), r.uniform(0, 1), r.uniform(2.2, 3.4)) for _ in range(14)]
    cl.sort(key=lambda c: c[1])
    for (dx, dy, rad) in cl:
        cx_, cy_ = x + 7 + dx * 6, y - 1 - dy * 8
        m = ell(cx_, cy_, rad, rad * .85)
        dd = ((xx - cx_ + rad * .4) / rad) ** 2 + ((yy - cy_ + rad * .45) / rad) ** 2
        t = np.where(dd < .25, 4, np.where(dd < .65, 3, np.where(dd < 1.0, 2, 1)))
        if dx > .3: t = np.clip(t - 1, 0, 4)
        img[m] = np.stack(LEAF)[t[m]]
    for _ in range(10):
        a = r.uniform(0, 2 * math.pi); put(x + 7 + math.cos(a) * 8, y - 4 + math.sin(a) * 6, LEAF[2])
    for _ in range(3): put(x + 7 + r.uniform(-5, 5), y - 3 - r.uniform(0, 7), FLOW[int(r.integers(0, 5))])


def stool2(x, y, c):
    """台灣紅色塑膠椅：圓椅面（頂面）+ 往下張開的椅身 + 前面拱形鏤空"""
    shadow(x + 7, y + 14, 8, 2)
    for yy_ in range(y + 2, y + 14):                     # 椅身：上窄下寬
        t = (yy_ - y - 2) / 11; half = 5 + t * 1.6
        for xx_ in range(int(x + 6 - half), int(x + 7 + half)):
            u = (xx_ - (x + 6 - half)) / (2 * half)
            put(xx_, yy_, c[2] if u < .3 else c[1] if u < .75 else c[0])
    for yy_ in range(y + 8, y + 14):                     # 拱形鏤空（看到後面的石板）
        t = (yy_ - y - 8) / 5; half = 2.6 * math.sqrt(max(0, t)) + .8
        for xx_ in range(int(round(x + 6.5 - half)), int(round(x + 6.5 + half))):
            put(xx_, yy_, STONE[2] * .78)
    for k in (y + 5, y + 6): hline(x + 2, x + 11, k, c[0]) if k == y + 6 else None   # 椅身上緣的凹線
    img[ell(x + 6.5, y + 2, 6.5, 2.4)] = c[3]; img[ell(x + 6.5, y + 2, 4.5, 1.3)] = c[2]   # 椅面
    hline(x + 1, x + 13, y + 13, c[0])


def lantern_string(y0, sag=9):
    """燈籠串：繩子往下垂，圓燈籠（骨架紋、上下黑蓋、亮面、流蘇）"""
    for x in range(0, W):
        yr = y0 + sag * math.sin(math.pi * x / W); put(x, yr, WOOD[1]); put(x, yr + 1, WOOD[0] * .9)
    for x in range(10, W, 20):
        yr = int(y0 + sag * math.sin(math.pi * x / W)) + 1
        vline(x, yr, yr + 2, WOOD[0])
        img[ell(x, yr + 6, 3.6, 4)] = hx('#c84a32')
        img[ell(x - 1, yr + 5, 1.6, 2.4)] = hx('#f08a58')
        img[ell(x + 1.5, yr + 7, 1.5, 2.5) & ~ell(x - 1, yr + 5, 1.6, 2.4)] = hx('#9a3226')
        hline(x - 3, x + 4, yr + 6, hx('#a83a2a'))
        hline(x - 2, x + 3, yr + 2, DARK[0]); hline(x - 2, x + 3, yr + 10, DARK[0])
        vline(x, yr + 11, yr + 13, GOLD[2]); put(x, yr + 13, GOLD[1])


def menuboard(x, y):
    """A 字型菜單立牌：木框 + 黑板 + 粉筆字"""
    shadow(x + 9, y + 24, 10, 2.5)
    for (lx, rx_) in ((x + 1, x + 3), (x + 15, x + 17)):
        for k in range(24): put(lx + (k * 1 if lx < x + 5 else -0) * 0, y + k, WOOD[1])
    rect(x, y, x + 18, y + 22, WOOD[2]); vline(x, y, y + 22, WOOD[3]); vline(x + 17, y, y + 22, WOOD[1]); hline(x, x + 18, y, WOOD[4])
    rect(x + 2, y + 2, x + 16, y + 18, DARK[1])
    for (ly, w_) in ((5, 9), (8, 11), (11, 7), (14, 10)):
        for k in range(w_):
            if (k * 7 + ly) % 5: put(x + 3 + k, y + ly, CREAM[3] if k < w_ - 3 else GOLD[2])
    put(x + 4, y + 3, RED[3]); put(x + 5, y + 3, RED[3])
    rect(x + 1, y + 22, x + 3, y + 25, WOOD[1]); rect(x + 15, y + 22, x + 17, y + 25, WOOD[1])


def yatai2(cx, y):
    """路邊攤：一片片的陽傘（傘骨、波浪邊、傘頂）+ 木推車（檯面、暖簾、輻條輪）+ 湯鍋、碗"""
    shadow(cx + 6, y + 31, 38, 5)
    # 車身
    rect(cx - 30, y + 9, cx + 30, y + 28, WOOD[3])
    for px_ in range(cx - 30, cx + 30, 5): vline(px_, y + 9, y + 28, WOOD[2]); put(px_ + 1, y + 10, WOOD[4])
    hline(cx - 30, cx + 30, y + 27, WOOD[1]); vline(cx - 30, y + 9, y + 28, WOOD[4]); vline(cx + 29, y + 9, y + 28, WOOD[1])
    rect(cx + 30, y + 6, cx + 34, y + 27, WOOD[1])                                     # 側面
    # 檯面（看得到頂面）
    rect(cx - 33, y + 1, cx + 34, y + 7, WOOD[4]); hline(cx - 33, cx + 34, y + 1, CREAM[3]); hline(cx - 33, cx + 34, y + 6, WOOD[2])
    hline(cx - 33, cx + 34, y + 8, WOOD[1])
    # 暖簾（三片、白字）
    for i in range(3):
        px0 = cx - 26 + i * 18
        rect(px0, y + 9, px0 + 16, y + 17, RED[2]); vline(px0, y + 9, y + 17, RED[3]); vline(px0 + 15, y + 9, y + 17, RED[1])
        hline(px0, px0 + 16, y + 16, RED[1])
        for (dx, dy) in ((6, 2), (7, 2), (8, 2), (9, 2), (7, 3), (8, 3), (7, 4), (8, 5), (6, 5), (9, 5)): put(px0 + dx, y + 9 + dy, CREAM[4])
    # 輪子（輻條）
    for wx in (cx - 21, cx + 21):
        img[ell(wx, y + 28, 6.5, 6.5)] = WOOD[1]; img[ell(wx, y + 28, 5, 5)] = WOOD[3]; img[ell(wx, y + 28, 3, 3)] = WOOD[2]
        for a in np.linspace(0, math.pi, 4, endpoint=False):
            for t in range(-4, 5): put(wx + t * math.cos(a), y + 28 + t * math.sin(a), WOOD[1])
        put(wx, y + 28, METAL[2]); put(wx - 4, y + 25, WOOD[4])
    # 湯鍋（鍋耳、湯面、熱氣）
    px_ = cx + 14
    img[ell(px_, y + 4, 10, 3)] = METAL[1]; rect(px_ - 10, y - 4, px_ + 11, y + 4, METAL[2])
    for i in range(-10, 11):
        t = (i + 10) / 20; vline(px_ + i, y - 4, y + 4, METAL[3] if t < .25 else METAL[2] if t < .7 else METAL[1])
    img[ell(px_, y - 4, 10, 3)] = METAL[3]; img[ell(px_, y - 4, 8.5, 2.2)] = hx('#c8803a'); img[ell(px_ - 2, y - 5, 4, 1)] = hx('#e8a858')
    rect(px_ - 13, y - 2, px_ - 10, y, METAL[1]); rect(px_ + 11, y - 2, px_ + 14, y, METAL[1])
    for (x0_, ph) in ((px_ - 4, 0), (px_ + 3, 1.7)):
        for t in range(10):
            x_ = int(round(x0_ + 1.6 * math.sin(t * .8 + ph))); y_ = y - 8 - t
            if 0 <= y_ < H: img[y_, x_] = img[y_, x_] * (.4 + t * .05) + np.array([255, 255, 255]) * (.6 - t * .05)
    # 碗（疊著的 + 一碗盛好的）
    for k in range(3):
        img[ell(cx - 22, y + 3 - k * 2, 5, 1.8)] = CREAM[4 - (k % 2)]; hline(cx - 27, cx - 17, y + 3 - k * 2, CREAM[2])
    img[ell(cx - 8, y + 3, 5, 2)] = CREAM[4]; img[ell(cx - 8, y + 2.6, 3.6, 1.2)] = hx('#d89a48'); put(cx - 7, y + 2, hx('#78b450'))
    # 傘柱
    vline(cx - 2, y - 36, y + 1, METAL[1]); vline(cx - 1, y - 36, y + 1, METAL[3])
    # 陽傘：8 片紅白相間，分片從傘頂往外放射（傘骨就在分片交界上）；下緣每片一個弧；左亮右暗
    R0, top0, depth = 40, y - 47, 13
    ax_, ay_ = cx - 1, top0                                    # 傘頂
    def edge_y(ex): return y - 31 + (1 - abs((ex - cx) / R0)) * 2.5
    for py_ in range(int(top0), int(y - 26)):
        for px_ in range(cx - R0, cx + R0 + 1):
            t = (px_ - cx) / R0
            if py_ < top0 + t * t * depth: continue
            # 沿著傘頂→這個點的方向延伸到傘緣，看落在哪一片
            if py_ == ay_: continue
            k = (edge_y(px_) - ay_) / (py_ - ay_)
            ex = ax_ + (px_ - ax_) * k
            if ex < cx - R0 or ex > cx + R0: continue
            seg = int((ex - (cx - R0)) // 10); u = ((ex - (cx - R0)) % 10) / 10
            bot = edge_y(ex) + 1.6 * math.sin(math.pi * u)
            frac = (py_ - ay_) / max(1, bot - ay_)
            if frac > 1: continue
            base_c = RED if seg % 2 == 0 else [CREAM[1], CREAM[2], CREAM[3], CREAM[4]]
            sh = 3 if t < -.5 else 2 if t < .3 else 1
            if u < .18 and sh < 3: sh += 1
            if frac > .9: sh = max(0, sh - 1)                  # 傘緣暗一階
            if u < .06 or u > .96: sh = 0                       # 傘骨（分片交界）
            put(px_, py_, base_c[sh])
    img[ell(cx - 1, y - 48, 3, 2)] = GOLD[2]; put(cx - 2, y - 49, GOLD[3])                   # 傘頂


# ================================================================ 共用：天空、石板地、店面
def sky_roofs():
    rect(0, 0, W, 66, SKY[1]); rect(0, 0, W, 18, SKY[0]); rect(0, 40, W, 66, SKY[2])
    for x in range(0, W, 2): put(x + 1, 17, SKY[1]); put(x, 40, SKY[1])
    x = -4
    for k in range(12):
        w = int(rng.integers(16, 26)); R_ = (TERRA, SLATE, TERRA)[k % 3]
        for i in range(w):
            top = 36 + abs(i - w / 2) / (w / 2) * 6
            rect(x + i, top, x + i + 1, 66, R_[2]); put(x + i, top, R_[3])
        x += w - 2


def cobbles(GY, lo=140, hi=290, moss_from=280):
    n_big = noise(30, 1); y = GY; row = 0
    while y < H:
        h = int(round(5 + (y - GY) / (H - GY) * 5))
        wgt = float(np.clip(min((y - lo) / 24, (hi - y) / 24), 0, 1))
        S = [a * (1 - wgt) + b * wgt for a, b in zip(STONE, STONEM)]; Mo = MORTAR * (1 - wgt) + STONEM[1] * wgt
        x = -int(rng.integers(0, 10)) - (row % 2) * 6
        while x < W:
            w = int(h * 2.3 + rng.integers(-1, 5)); x0, x1, y0, y1 = x + 1, x + w, y + 1, y + h
            cx, cy = min(max((x0 + x1) // 2, 0), W - 1), min(max((y0 + y1) // 2, 0), H - 1)
            base = 3 if rng.random() < .7 else (2 if rng.random() < .5 else 4)
            if n_big[cy, cx] > .7: base = min(base + 1, 4)
            if n_big[cy, cx] < .25: base = max(base - 1, 2)
            rect(x, y, x + w, y + h, Mo); rect(x0, y0, x1, y1, S[base])
            hline(x0 + 1, x1, y0, S[base + 1]); vline(x0, y0 + 1, y1 - 1, S[base + 1])
            hline(x0 + 1, x1, y1 - 1, S[base - 1]); vline(x1 - 1, y0 + 1, y1 - 1, S[base - 1])
            for (px_, py_) in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)): put(px_, py_, Mo)
            x += w
        y += h; row += 1
    mor = (np.abs(img - MORTAR).sum(axis=2) < 4) & (yy > moss_from)
    img[mor & (rng.random((H, W)) < .22)] = GRASS[1]


def shop(x0, x1, roofR, kind):
    """一間店：瓦片屋頂（斜俯視）+ 牆 + 暖簾或遮陽棚 + 窗"""
    for ty in range(62, 92, 4):
        rect(x0 - 3, ty, x1 + 3, ty + 4, roofR[2]); hline(x0 - 3, x1 + 3, ty, roofR[3]); hline(x0 - 3, x1 + 3, ty + 3, roofR[1])
        off = (ty // 4) % 2 * 3
        for tx in range(x0 - 3 + off, x1 + 3, 6): vline(tx, ty + 1, ty + 3, roofR[1])
    hline(x0 - 3, x1 + 3, 62, roofR[4]); rect(x0 - 3, 92, x1 + 3, 95, roofR[0])
    if kind == 'cafe':
        rect(x0, 95, x1, 124, WOOD[2])
        for wy in range(97, 124, 3): hline(x0, x1, wy, WOOD[1]); hline(x0, x1, wy + 1, WOOD[3])
    else:
        rect(x0, 95, x1, 124, CREAM[3]); hline(x0, x1, 95, CREAM[1]); hline(x0, x1, 96, CREAM[2])
    vline(x0, 95, 124, WOOD[1]); vline(x0 + 1, 95, 124, WOOD[3]); vline(x1 - 1, 95, 124, WOOD[1])
    cx = (x0 + x1) // 2
    rect(cx - 10, 102, cx + 10, 124, DARK[1]); rect(cx - 10, 121, cx + 10, 124, DARK[2])
    for wx in (x0 + 5, x1 - 15):
        rect(wx - 1, 104, wx + 11, 114, WOOD[1]); rect(wx, 105, wx + 10, 113, GLOW[2]); rect(wx, 105, wx + 10, 107, GLOW[1])
        vline(wx + 5, 105, 113, WOOD[2])
    if kind == 'cafe':
        for ax in range(x0 + 2, x1 - 2):
            c = (hx('#57805e') if (ax // 4) % 2 == 0 else CREAM[3]); vline(ax, 97, 102, c)
            if ax % 4 in (1, 2): put(ax, 102, c * .85)
        hline(x0 + 2, x1 - 2, 96, hx('#2f4a3a'))
    else:
        P_ = RED if kind == 'ramen' else [hx('#1f2a40'), hx('#2d3d5c'), hx('#3f5580'), hx('#5a72a0')]
        hline(cx - 12, cx + 12, 101, WOOD[1])
        for i in range(3):
            px0 = cx - 11 + i * 8
            rect(px0, 102, px0 + 7, 114, P_[2]); vline(px0, 102, 114, P_[3] if i == 0 else P_[2]); vline(px0 + 6, 102, 114, P_[1])
            hline(px0, px0 + 7, 113, P_[1])
        for (dx, dy) in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1), (2, 2)): put(cx - 2 + dx, 106 + dy, CREAM[4])
        for lx in (x0 + 4, x1 - 5):
            vline(lx, 95, 97, METAL[1]); rect(lx - 2, 97, lx + 3, 104, hx('#cc5a3c')); vline(lx - 1, 98, 103, hx('#f0a060'))
            hline(lx - 2, lx + 3, 100, hx('#9a3a30'))
    rect(x0, 124, x1, 128, STONE[2]); hline(x0, x1, 124, STONE[4]); hline(x0, x1, 127, STONE[1])


# ================================================================ B：午休商店街
def stool(x, y, c):
    shadow(x + 4, y + 9, 5, 1.5)
    rect(x, y, x + 7, y + 8, c[1]); img[ell(x + 3.5, y, 3.5, 1.5)] = c[3]; vline(x, y, y + 8, c[2]); vline(x + 6, y, y + 8, c[0])
    for k in range(1, 7, 2): put(x + k, y + 4, c[0])


def yatai(cx, y):
    """路邊攤推車：木頭車身 + 紅白陽傘 + 冒煙的湯鍋"""
    shadow(cx + 6, y + 30, 36, 5)
    rect(cx - 30, y + 8, cx + 30, y + 28, WOOD[3])                     # 車身正面
    for px_ in range(cx - 30, cx + 30, 6): vline(px_, y + 8, y + 28, WOOD[2])
    hline(cx - 30, cx + 30, y + 27, WOOD[1])
    rect(cx - 33, y + 2, cx + 33, y + 9, WOOD[4]); hline(cx - 33, cx + 33, y + 2, CREAM[3]); hline(cx - 33, cx + 33, y + 8, WOOD[2])  # 檯面
    rect(cx - 26, y + 9, cx + 26, y + 15, RED[2])                      # 前面的小暖簾
    for i in range(cx - 26, cx + 26, 7): vline(i, y + 9, y + 15, RED[1])
    for (dx, dy) in ((-8, 11), (-7, 11), (-6, 11), (-7, 12), (2, 11), (3, 11), (4, 12), (3, 12)): put(cx + dx, y + dy, CREAM[4])
    for wx in (cx - 22, cx + 22):                                      # 車輪
        img[ell(wx, y + 28, 6, 6)] = WOOD[1]; img[ell(wx, y + 28, 4, 4)] = WOOD[3]; put(wx, y + 28, METAL[1])
    # 湯鍋 + 熱氣
    img[ell(cx + 12, y, 9, 3)] = METAL[2]; rect(cx + 3, y, cx + 22, y + 3, METAL[2]); vline(cx + 3, y, y + 3, METAL[3])
    img[ell(cx + 12, y - 1, 7, 2)] = hx('#d89a48')
    for (x0_, ph) in ((cx + 8, 0), (cx + 14, 1.7)):
        for t in range(8): put(x0_ + 1.5 * math.sin(t * .8 + ph), y - 3 - t, CREAM[4] if t < 5 else CREAM[3])
    for k, (bx, c) in enumerate(((cx - 24, hx('#f0e8d4')), (cx - 16, hx('#e8c860')))):   # 碗
        img[ell(bx, y + 1, 3, 1.5)] = c; put(bx, y + 2, c * .8)
    # 陽傘
    vline(cx - 2, y - 34, y + 2, METAL[1]); vline(cx - 1, y - 34, y + 2, METAL[2])
    for i in range(-36, 37):
        t = abs(i) / 36
        top = y - 44 + t * t * 12
        bot = y - 30 + (1 - t) * 3
        c = RED[2] if ((i + 36) // 9) % 2 == 0 else CREAM[4]
        cs = RED[1] if ((i + 36) // 9) % 2 == 0 else CREAM[2]
        rect(cx + i, top, cx + i + 1, bot, c); put(cx + i, bot, cs); put(cx + i, bot - 1, cs)
    put(cx - 2, y - 45, METAL[2])


def scene_street():
    img[:] = 0
    rect(0, 0, W, 60, SKY[1]); rect(0, 0, W, 16, SKY[0]); rect(0, 38, W, 60, SKY[2])
    for x in range(0, W, 2): put(x + 1, 15, SKY[1]); put(x, 38, SKY[1])
    clouds()
    far_houses(50)
    battle_band(46)                       # 戰鬥背景那排店 + 人行道（y 46~119）
    cobbles(120)
    lantern_string(148)
    ng = noise(14, 3)
    grass = (((xx / W) * 1.3 + ((H - yy) / H) * 2.8 + (ng - .5) * .25) < .5) | ((((W - xx) / W) * 1.3 + ((H - yy) / H) * 2.8 + (ng - .5) * .25) < .45)
    grass_fill(grass)
    lamp(8, 150); lamp(206, 150); tree2(12, 252, 1.0, 1); tree2(206, 238, 1.0, 2)
    barrel2(2, 124); crate2(196, 126)
    pot_plant(26, 326, 1); pot_plant(174, 322, 2)
    lamp(40, 352); lamp(176, 350)
    yatai2(108, 392)
    stool2(54, 410, [hx('#7a1a14'), hx('#a8281c'), hx('#d04030'), hx('#f07058')])
    stool2(68, 419, [hx('#1f2a60'), hx('#2d3d8c'), hx('#3f55b0'), hx('#6a82d8')])
    stool2(148, 413, [hx('#7a1a14'), hx('#a8281c'), hx('#d04030'), hx('#f07058')])
    menuboard(168, 396)
    tree2(8, 466, 1.05, 3); tree2(212, 460, 1.0, 4)


# ================================================================ C：公會食堂（室內）
def scene_tavern():
    img[:] = 0
    # 後牆：直木板
    rect(0, 0, W, 110, WOOD[2])
    for bx in range(0, W, 7):
        vline(bx, 0, 110, WOOD[1]); vline(bx + 1, 0, 110, WOOD[3])
        for k in range(3): put(bx + 3, int(rng.integers(4, 106)), WOOD[1])
    rect(0, 0, W, 10, WOOD[0]); hline(0, W, 10, WOOD[1])                 # 天花板橫樑
    for bx in (20, 108, 196):
        rect(bx - 3, 0, bx + 4, 12, WOOD[1]); vline(bx - 3, 0, 12, WOOD[2])
    # 吊燈
    for lx in (52, 164):
        vline(lx, 10, 22, METAL[1]); rect(lx - 4, 22, lx + 5, 28, METAL[0]); rect(lx - 3, 23, lx + 4, 27, GLOW[2]); vline(lx - 3, 23, 27, GLOW[3])
        mul(ell(lx, 60, 26, 30) & (yy > 28) & (yy < 110), (1.08, 1.05, .96))
    # 酒櫃：兩層架子 + 瓶罐
    for (sx0, sx1) in ((8, 82), (134, 208)):
        for sy in (40, 64):
            rect(sx0, sy, sx1, sy + 3, WOOD[4]); hline(sx0, sx1, sy + 3, WOOD[1])
            x = sx0 + 2
            while x < sx1 - 4:
                kind = int(rng.integers(0, 3)); c = [hx('#4a7a52'), hx('#8a3a2a'), hx('#c8a050'), hx('#5a6a9a')][int(rng.integers(0, 4))]
                if kind == 0:                                           # 瓶子
                    rect(x, sy - 10, x + 3, sy, c); rect(x + 1, sy - 13, x + 2, sy - 10, c); put(x, sy - 9, c * .6 + 100)
                    x += 5
                elif kind == 1:                                         # 罐子
                    rect(x, sy - 7, x + 6, sy, PAPER[1]); hline(x, x + 6, sy - 7, TERRA[2]); put(x + 1, sy - 5, PAPER[2])
                    x += 8
                else:                                                   # 碗疊
                    for k in range(3): rect(x, sy - 2 - k * 2, x + 7, sy - k * 2, CREAM[3 if k % 2 else 4])
                    x += 9
    # 菜單板（中間）
    rect(86, 26, 130, 70, WOOD[1]); rect(88, 28, 128, 68, DARK[1])
    for k, ly in enumerate(range(33, 64, 5)):
        hline(91, 91 + 20 + (k * 7) % 12, ly, CREAM[3]); hline(116, 125, ly, GOLD[2])
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1)): put(105 + dx, 30 + dy, RED[3])
    # 吧台
    rect(0, 100, W, 112, WOOD[4]); hline(0, W, 100, CREAM[3]); hline(0, W, 111, WOOD[2])   # 檯面
    rect(0, 112, W, 134, WOOD[2])
    for px_ in range(0, W, 12): vline(px_, 112, 134, WOOD[1]); vline(px_ + 1, 112, 134, WOOD[3])
    hline(0, W, 133, WOOD[0])
    img[ell(40, 98, 10, 3)] = METAL[2]; rect(30, 92, 50, 98, METAL[2]); vline(30, 92, 98, METAL[3]); img[ell(40, 92, 8, 2)] = hx('#d89a48')  # 大鍋
    for (x0_, ph) in ((36, 0), (43, 1.7)):
        for t in range(8): put(x0_ + 1.5 * math.sin(t * .8 + ph), 89 - t, CREAM[4] if t < 5 else CREAM[3])
    img[ell(176, 97, 4, 3)] = GOLD[2]; put(176, 94, GOLD[3])                                   # 服務鈴
    for k, mx in enumerate((150, 160)):                                                         # 啤酒杯
        rect(mx, 92, mx + 6, 100, GLOW[1]); rect(mx, 92, mx + 6, 94, CREAM[4]); vline(mx + 6, 94, 98, GLOW[0])
    # 地板：木地板（越往下板子越寬），中段低對比
    y = 134; row = 0
    while y < H:
        h = int(round(6 + (y - 134) / (H - 134) * 6))
        wgt = float(np.clip(min((y - 150) / 24, (290 - y) / 24), 0, 1))
        Wd = [a * (1 - wgt) + b * wgt for a, b in zip(WOOD, [WOOD[1] * .5 + WOOD[2] * .5, WOOD[2], WOOD[2] * .6 + WOOD[3] * .4, WOOD[3] * .7 + WOOD[2] * .3, WOOD[3]])]
        rect(0, y, W, y + h, Wd[3]); hline(0, W, y, Wd[4]); hline(0, W, y + h - 1, Wd[1])
        off = (row * 37) % 50
        for bx in range(-off, W, 50): vline(bx, y, y + h, Wd[1])
        for _ in range(4): put(int(rng.integers(0, W)), int(y + rng.integers(1, max(2, h - 1))), Wd[2])
        y += h; row += 1
    mul((yy >= 134) & (yy < 139), (.7, .7, .8))
    # 窗光（斜斜照在地板上）
    for (wx0, wy0) in ((24, 300), (150, 290)):
        m = (yy > wy0) & (yy < wy0 + 22) & (xx > wx0 + (yy - wy0) * .5) & (xx < wx0 + 30 + (yy - wy0) * .5)
        img[m] = np.clip(img[m] * np.array([1.12, 1.08, .98]), 0, 255)
    # 吧台高腳椅
    for sx in (30, 70, 146, 186):
        shadow(sx + 4, 150, 6, 2); vline(sx + 3, 140, 150, METAL[1]); vline(sx + 4, 140, 150, METAL[2])
        img[ell(sx + 3.5, 139, 6, 2.5)] = TERRA[2]; img[ell(sx + 3, 138, 4, 1.5)] = TERRA[3]
    # 角落的木桶、盆栽
    barrel(4, 300); barrel(12, 306); barrel(198, 296)
    shadow(206, 340, 8, 2); rect(200, 330, 212, 340, TERRA[2]); img[ell(206, 325, 9, 7)] = LEAF[2]; img[ell(203, 322, 4, 3)] = LEAF[4]
    # 圓桌 + 地毯 + 三人份餐點（隊伍頁最常露出來的位置）
    def table(cx, cy, r=44, food=True):
        shadow(cx + 5, cy + 16, r, 7)
        rect(cx - 3, cy + 4, cx + 4, cy + 18, WOOD[1])
        img[ell(cx, cy + 3, r, r * .32)] = WOOD[1]
        img[ell(cx, cy, r, r * .32)] = WOOD[3]; img[ell(cx - r * .18, cy - 3, r * .6, r * .15)] = WOOD[4]
        for a_ in np.linspace(0, math.pi, 9):                      # 桌面木紋
            put(cx + r * .7 * math.cos(a_), cy + 1, WOOD[2])
        if not food: return
        for (bx, by, c) in ((cx - 20, cy - 3, hx('#d89a48')), (cx + 18, cy - 4, hx('#b8502a')), (cx, cy + 4, hx('#86441e'))):
            img[ell(bx, by + 2, 9, 3.4)] = CREAM[1]; img[ell(bx, by, 9, 3.4)] = CREAM[4]; img[ell(bx, by, 7, 2.3)] = c
            put(bx - 3, by - 1, CREAM[3]); put(bx + 2, by, hx('#78b450')); put(bx - 1, by + 1, hx('#f0e0b0'))
            for t in range(6): put(bx + 1.2 * math.sin(t * .9), by - 4 - t, CREAM[4] if t < 4 else CREAM[3])
        for (mx, my) in ((cx - 34, cy + 2), (cx + 32, cy + 3)):
            rect(mx, my - 5, mx + 5, my + 1, CREAM[3]); vline(mx, my - 5, my + 1, CREAM[4]); put(mx + 5, my - 3, CREAM[2])
        for k in range(2):                                          # 筷子
            put(cx - 8 + k, cy + 6 - k, WOOD[4]); put(cx - 6 + k, cy + 6 - k, WOOD[4]); put(cx - 4 + k, cy + 6 - k, WOOD[4])
    def stool_w(sx, sy):
        shadow(sx + 5, sy + 12, 7, 2); rect(sx + 1, sy + 3, sx + 3, sy + 12, WOOD[1]); rect(sx + 7, sy + 3, sx + 9, sy + 12, WOOD[1])
        img[ell(sx + 5, sy + 2, 7, 2.5)] = WOOD[3]; img[ell(sx + 5, sy + 1.5, 5, 1.5)] = WOOD[4]
    cx, cy = 108, 402
    rug = ell(cx, cy + 8, 84, 26); img[rug] = RED[1]; img[rug & ~ell(cx, cy + 8, 80, 23)] = GOLD[1]
    img[ell(cx, cy + 8, 75, 20.5) & ~ell(cx, cy + 8, 73, 19)] = GOLD[1]
    for (sx, sy) in ((cx - 62, cy - 6), (cx + 52, cy - 8)): stool_w(sx, sy)
    table(cx, cy)
    stool_w(cx - 6, cy + 24)
    table(-14, 456, 34, False); table(230, 452, 34, False)            # 兩側角落的半張桌子
    stool_w(20, 440); stool_w(186, 436)


SCENES = {'plaza': scene_plaza, 'street': scene_street, 'tavern': scene_tavern}

if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or list(SCENES)):
        SCENES[k]()
        Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(HERE, 'bgtown_%s.png' % k))
        print('ok', k)
