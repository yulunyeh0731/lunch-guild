"""App 圖示（60×60 像素，輸出 180 / 512）。三個方向：A 精修拉麵、B 公會徽章、C 寶箱。
python3 icon34.py → icon_A.png / icon_B.png / icon_C.png（180）+ *_512.png"""
import math
import numpy as np
from PIL import Image, ImageDraw
import chars34 as C

N = 60
C.W = C.H = N
C.R.update({
    'broth':  ['#7d5528', '#c4914f', '#e5bd7c', '#f6e1b4'],
    'porc':   ['#77748a', '#c3c0cc', '#e8e6ee', '#ffffff'],
    'bowlR':  ['#4a1514', '#87271f', '#bd4433', '#e2775a'],
    'meat':   ['#5a2a1c', '#94502f', '#c47d58', '#e8b18f'],
    'yolk':   ['#9a4a10', '#de8424', '#f5b13f', '#ffd987'],
    'nori':   ['#0d1712', '#1b2c23', '#2b4434', '#41604a'],
    'scal':   ['#2a5620', '#4b8a30', '#78bd4a', '#b2e27c'],
    'noodle': ['#99772a', '#d7b456', '#efd488', '#fff1c4'],
    'navyS':  ['#0b1024', '#18234e', '#2a3a78', '#41569c'],
    'rice':   ['#8f8a90', '#d6d2d6', '#f0eef0', '#ffffff'],
    'chest':  ['#3a2010', '#6a3d1d', '#94592b', '#bd7d45'],
    'ume':    ['#5c0f1e', '#a3203a', '#d4475c', '#f08b96'],
})
C.SELOUT = True


def bayer(v, x, y):
    m = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    return v + (m[y % 4][x % 4] / 16 - .5) / 3


def background(glow=(30, 36), warm=(232, 176, 92), inner='#1a2550', outer='#0c1230', thick=False):
    a = np.zeros((N, N, 3), np.float32)
    ci, co, cw = np.array(C.hx(inner), np.float32), np.array(C.hx(outer), np.float32), np.array(warm, np.float32)
    steps = 5
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - glow[0], (y - glow[1]) * 1.1) / 34
            t = min(1, max(0, bayer(d, x, y)))
            t = round(t * steps) / steps
            c = ci * (1 - t) + co * t
            g = max(0, 1 - math.hypot(x - glow[0], y - glow[1]) / 22)
            g = round(bayer(g, x, y) * 4) / 4 * .22
            a[y, x] = c * (1 - g) + cw * g
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    # 內框：金色細線圓角框（iOS 會再切圓角，框往內縮）
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, N - 3, N - 3), radius=11, outline=(0, 0, 0, 0), width=1)
    fr = Image.new('L', (N, N), 0)
    ImageDraw.Draw(fr).rounded_rectangle((3, 3, N - 4, N - 4), radius=10, outline=255, width=1)
    fa = np.array(fr) > 127
    arr = np.array(im)
    for y, x in zip(*np.nonzero(fa)):
        arr[y, x, :3] = C.hx('#b8954f') if (x + y) % 2 == 0 or y < 30 else C.hx('#8a6b34')
    if thick:          # 粗金框：外圈亮金、內圈暗金
        for inset, r, col_t, col_b in ((2, 11, '#f0d48a', '#c9a04e'), (3, 10, '#c9a04e', '#8a6b34'), (4, 9, '#6b5226', '#4a3818')):
            fr = Image.new('L', (N, N), 0)
            ImageDraw.Draw(fr).rounded_rectangle((inset, inset, N - 1 - inset, N - 1 - inset), radius=r, outline=255, width=1)
            for y, x in zip(*np.nonzero(np.array(fr) > 127)):
                arr[y, x, :3] = C.hx(col_t if y < N / 2 else col_b)
    return Image.fromarray(arr, 'RGBA')


def comp(bg, sp):
    fg = Image.fromarray(sp.rgb, 'RGBA')
    bg.alpha_composite(fg)
    return bg


def put(sp, pts, col):
    for x, y in pts:
        sp.px(int(round(x)), int(round(y)), col)


def mask_ell(box):
    im = Image.new('L', (N, N), 0)
    ImageDraw.Draw(im).ellipse(box, fill=255)
    return np.array(im) > 127


# ---------------- A 精修拉麵 ----------------
def icon_A():
    sp = C.Sprite()
    # 碗身：大橢圓的下半部
    body = mask_ell((6, 12, 54, 56))
    body[:30] = False
    sp.mask('body', 'bowlR', 10, body, shade='sphere')
    foot = mask_ell((20, 47, 40, 56)); foot[:51] = False
    sp.mask('foot', 'bowlR', 9, foot, shade='flat', light=.3)
    rim = mask_ell((5, 23, 55, 37))
    sp.mask('rim', 'porc', 11, rim, shade='cylv', light=.35, line=False)
    broth = mask_ell((8, 25, 52, 35))
    sp.mask('broth', 'broth', 12, broth, shade='sphere', light=.15)
    # 海苔（插在後面）
    sp.poly('nori', 'nori', 13, [(14, 19), (21, 16), (24, 27), (17, 28)], shade='cyl')
    # 叉燒
    sp.ell('meat', 'meat', 14, (12, 25, 25, 32), shade='sphere')
    # 溏心蛋
    sp.ell('egg', 'porc', 15, (29, 26, 38, 33), shade='sphere', light=.2)
    sp.ell('yolk', 'yolk', 16, (31, 27.5, 36, 31.5), shade='sphere', line=False)
    # 鳴門卷
    sp.ell('naru', 'porc', 15, (22, 29, 29, 34), shade='sphere', light=.25)
    # 筷子（從右上斜插進碗，夾起麵）
    sp.cap('stickB', 'wood', 18, [(33, 18), (50, 5)], 1, shade='axis', axis=[(33, 18, 50, 5, 1, 1)], line=False)
    sp.cap('stickF', 'wood', 19, [(35, 21), (53, 9)], 1, shade='axis', axis=[(35, 21, 53, 9, 1, 1)], line=False)
    sp.render()
    sp.outline()
    # 碗口金色波紋帶
    for x in range(9, 52):
        y = 40 + round(1.2 * math.sin(x / 2.2)) + (0 if 14 < x < 46 else -1 if 10 < x < 50 else -2)
        if sp.pid[y, x] >= 0 and sp.parts_sorted[sp.pid[y, x]]['name'] == 'body':
            sp.px(x, y, '#e0b45a' if x < 34 else '#a8822f')
    # 碗口高光
    put(sp, [(12, 26), (13, 25), (14, 25)], '#ffffff')
    # 鳴門卷的粉紅漩渦
    put(sp, [(25, 31), (26, 31), (26, 32), (25, 32), (24, 31), (24, 30), (25, 30), (26, 30), (27, 31)], '#e06d8c')
    # 叉燒肥邊、紋路
    put(sp, [(14, 27), (15, 26), (16, 26), (17, 26), (18, 26), (19, 26)], '#f3d2b8')
    put(sp, [(17, 29), (18, 29), (19, 28), (21, 30)], '#7d3d23')
    # 蔥花
    for x, y in [(27, 27), (28, 28), (40, 31), (41, 30), (20, 33), (44, 33), (38, 34), (16, 32)]:
        sp.px(x, y, '#7cc04c'); sp.px(x + 1, y, '#3f7d2a')
    # 夾起的麵條：從筷子尖往下垂進湯
    for k, x0 in enumerate((34, 36, 38, 40)):
        for y in range(18 + (k % 2), 31):
            x = x0 + round(.9 * math.sin((y + k * 1.7) / 1.5))
            nm = sp.parts_sorted[sp.pid[y, x]]['name'] if sp.pid[y, x] >= 0 else ''
            if nm in ('stickB', 'stickF'):
                continue
            sp.px(x, y, '#fff1c4' if k == 0 else '#efd488' if k % 2 == 0 else '#c9a548')
            if sp.rgb[y, x + 1, 3] == 0:
                sp.px(x + 1, y, '#5a4416')
    # 筷尾
    put(sp, [(50, 5), (51, 4), (53, 9), (54, 8)], '#2a1a10')
    # 湯面油光
    put(sp, [(45, 28), (46, 28), (47, 30), (10, 30)], '#fbeccc')
    # 蒸氣
    for k, x0 in enumerate((20, 27, 46)):
        for y in range(5 + k % 2 * 2, 21 if k < 2 else 25):
            if (y + k) % 5 == 4:
                continue
            x = x0 + round(1.6 * math.sin(y / 2.4 + k))
            if sp.rgb[y, x, 3] == 0:
                sp.rgb[y, x] = (218, 228, 248, 230 if y > 9 else 130)
    return comp(background(glow=(30, 34)), sp)


# ---------------- A2 精修拉麵（滿版、亮）----------------
def background2():
    a = np.zeros((N, N, 3), np.float32)
    ci, co, cw = np.array(C.hx('#3a4f96'), np.float32), np.array(C.hx('#1d2b66'), np.float32), np.array((255, 196, 112), np.float32)
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - 30, (y - 30) * 1.05) / 40
            t = round(min(1, max(0, bayer(d, x, y))) * 5) / 5
            c = ci * (1 - t) + co * t
            g = max(0, 1 - math.hypot(x - 28, y - 22) / 26)
            g = round(bayer(g, x, y) * 4) / 4 * .38
            a[y, x] = c * (1 - g) + cw * g
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


def icon_A2():
    sp = C.Sprite()
    body = mask_ell((3, 6, 57, 55)); body[:33] = False
    sp.mask('body', 'bowlR', 10, body, shade='cyl', light=.2)
    foot = mask_ell((20, 47, 40, 57)); foot[:51] = False
    sp.mask('foot', 'bowlR', 9, foot, shade='flat', light=.2)
    sp.mask('rim', 'porc', 11, mask_ell((2, 25, 58, 41)), shade='cylv', light=.35, line=False)
    sp.mask('broth', 'broth', 12, mask_ell((5, 27, 55, 39)), shade='sphere', light=.2)
    sp.poly('nori', 'nori', 13, [(9, 14), (18, 10), (23, 29), (12, 31)], shade='cyl')
    sp.ell('meat2', 'meat', 14, (15, 25, 30, 33), shade='sphere')
    sp.ell('meat1', 'meat', 14.5, (7, 28, 23, 37), shade='sphere')
    sp.ell('egg', 'porc', 15, (31, 27, 42, 35), shade='sphere', light=.2)
    sp.ell('yolk', 'yolk', 16, (33.5, 28.5, 39.5, 33), shade='sphere', line=False)
    sp.ell('naru', 'porc', 15.5, (23, 31, 31, 37), shade='sphere', light=.25)
    sp.cap('stickB', 'wood', 18, [(37, 19), (53, 5)], 1, shade='axis', axis=[(37, 19, 53, 5, 1, 1)], line=False)
    sp.cap('stickF', 'wood', 19, [(39, 22), (56, 9)], 1, shade='axis', axis=[(39, 22, 56, 9, 1, 1)], line=False)
    sp.render()
    sp.outline()
    nm = lambda y, x: sp.parts_sorted[sp.pid[y, x]]['name'] if sp.pid[y, x] >= 0 else ''
    # 金色波紋帶
    for x in range(6, 55):
        y = 44 + round(1.2 * math.sin(x / 2.2)) + (0 if 12 < x < 48 else -1 if 8 < x < 52 else -2)
        if nm(y, x) == 'body':
            sp.px(x, y, '#ecc56a' if x < 38 else '#b48d38')
    # 海苔光澤、紋理
    for y in range(13, 29):
        x = 11 + round((y - 13) * .32)
        if nm(y, x) == 'nori':
            sp.px(x, y, '#5b7f66')
    for x, y in [(15, 16), (17, 21), (14, 24), (19, 26), (16, 13)]:
        if nm(y, x) == 'nori':
            sp.px(x, y, '#13211a')
    put(sp, [(9, 28), (10, 27), (11, 27), (12, 27)], '#ffffff')
    # 叉燒：肥邊＋紋路（兩片）
    for (x0, x1, y) in ((17, 27, 26), (9, 21, 29)):
        put(sp, [(x, y) for x in range(x0, x1)], '#f3d2b8')
    put(sp, [(20, 29), (22, 30), (25, 29), (12, 32), (14, 33), (17, 32), (19, 34)], '#7d3d23')
    # 鳴門卷漩渦
    put(sp, [(27, 33), (28, 33), (28, 34), (27, 34), (26, 33), (26, 32), (27, 32), (28, 32), (29, 33)], '#e06d8c')
    for x, y in [(30, 28), (31, 30), (44, 33), (45, 32), (22, 37), (47, 35), (41, 36), (34, 36), (8, 34)]:
        sp.px(x, y, '#7cc04c'); sp.px(x + 1, y, '#3f7d2a')
    # 夾起的麵
    for k, x0 in enumerate((38, 40, 42, 44)):
        for y in range(19 + (k % 2), 34):
            x = x0 + round(.9 * math.sin((y + k * 1.7) / 1.5))
            if nm(y, x) in ('stickB', 'stickF', 'egg', 'yolk'):
                continue
            sp.px(x, y, '#fff1c4' if k == 0 else '#efd488' if k % 2 == 0 else '#c9a548')
            if sp.rgb[y, x + 1, 3] == 0:
                sp.px(x + 1, y, '#5a4416')
    put(sp, [(53, 5), (54, 4), (56, 9), (57, 8)], '#2a1a10')
    put(sp, [(48, 30), (49, 30), (50, 32), (46, 37)], '#fbeccc')
    # 蒸氣
    for k, x0 in enumerate((25, 32)):
        for y in range(4 + k * 2, 24):
            if (y + k) % 5 == 4:
                continue
            x = x0 + round(1.6 * math.sin(y / 2.4 + k))
            if sp.rgb[y, x, 3] == 0:
                sp.rgb[y, x] = (244, 248, 255, 255 if y > 8 else 160)
                if sp.rgb[y, x + 1, 3] == 0 and y > 8:
                    sp.rgb[y, x + 1] = (200, 214, 245, 150)
    return comp(background2(), sp)



def icon_A3(k=.9, cx=30, cy=33, frame=True):
    T = lambda x, y: (cx + (x - cx) * k, cy + (y - cy) * k)
    TB = lambda x0, y0, x1, y1: (*T(x0, y0), *T(x1, y1))
    sp = C.Sprite()
    body = mask_ell(TB(3, 6, 57, 55)); body[:round(T(0, 33)[1])] = False
    sp.mask('body', 'bowlR', 10, body, shade='cyl', light=.2)
    foot = mask_ell(TB(20, 47, 40, 57)); foot[:round(T(0, 51)[1])] = False
    sp.mask('foot', 'bowlR', 9, foot, shade='flat', light=.2)
    sp.mask('rim', 'porc', 11, mask_ell(TB(2, 25, 58, 41)), shade='cylv', light=.35, line=False)
    sp.mask('broth', 'broth', 12, mask_ell(TB(5, 27, 55, 39)), shade='sphere', light=.2)
    sp.poly('nori', 'nori', 13, [T(9, 14), T(18, 10), T(23, 29), T(12, 31)], shade='cyl')
    sp.ell('meat2', 'meat', 14, TB(15, 25, 30, 33), shade='sphere')
    sp.ell('meat1', 'meat', 14.5, TB(7, 28, 23, 37), shade='sphere')
    sp.ell('egg', 'porc', 15, TB(31, 27, 42, 35), shade='sphere', light=.2)
    sp.ell('yolk', 'yolk', 16, TB(33.5, 28.5, 39.5, 33), shade='sphere', line=False)
    sp.ell('naru', 'porc', 15.5, TB(23, 31, 31, 37), shade='sphere', light=.25)
    sp.cap('stickB', 'wood', 18, [T(37, 19), T(53, 5)], 1, shade='axis', axis=[(*T(37, 19), *T(53, 5), 1, 1)], line=False)
    sp.cap('stickF', 'wood', 19, [T(39, 22), T(56, 9)], 1, shade='axis', axis=[(*T(39, 22), *T(56, 9), 1, 1)], line=False)
    sp.render()
    sp.outline()
    nm = lambda y, x: sp.parts_sorted[sp.pid[y, x]]['name'] if 0 <= y < N and 0 <= x < N and sp.pid[y, x] >= 0 else ''
    I = lambda x, y: tuple(int(round(v)) for v in T(x, y))
    def dot(x, y, col):
        xi, yi = I(x, y); sp.px(xi, yi, col)
    # 金色波紋帶（沿著碗身，縮放後的座標）
    x0b, _ = I(6, 0); x1b, _ = I(55, 0)
    for x in range(x0b, x1b):
        u = cx + (x - cx) / k
        y = int(round(T(0, 44 + 1.2 * math.sin(u / 2.2) + (0 if 12 < u < 48 else -1 if 8 < u < 52 else -2))[1]))
        if nm(y, x) == 'body':
            sp.px(x, y, '#ecc56a' if u < 38 else '#b48d38')
    # 海苔光澤、紋理
    for yy in range(13, 29):
        xi, yi = I(11 + (yy - 13) * .32, yy)
        if nm(yi, xi) == 'nori':
            sp.px(xi, yi, '#5b7f66')
    for x, y in [(15, 16), (17, 21), (14, 24), (19, 26), (16, 13)]:
        xi, yi = I(x, y)
        if nm(yi, xi) == 'nori':
            sp.px(xi, yi, '#13211a')
    for x, y in [(9, 28), (10, 27), (11, 27), (12, 27)]:
        dot(x, y, '#ffffff')
    # 叉燒：肥邊＋紋路（兩片）
    for (xa, xb, y) in ((17, 27, 26), (9, 21, 29)):
        for x in range(xa, xb):
            dot(x, y, '#f3d2b8')
    for x, y in [(20, 29), (22, 30), (25, 29), (12, 32), (14, 33), (17, 32), (19, 34)]:
        dot(x, y, '#7d3d23')
    # 鳴門卷漩渦（小一圈，直接畫在中心周圍）
    nx, ny = I(27, 34)
    for dx, dy in [(0, 0), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (2, 0)]:
        if dy == 1 and dx == 1:
            continue
        sp.px(nx + dx, ny + dy, '#e06d8c')
    for x, y in [(30, 28), (31, 30), (44, 33), (45, 32), (22, 37), (47, 35), (41, 36), (34, 36), (8, 34)]:
        xi, yi = I(x, y); sp.px(xi, yi, '#7cc04c'); sp.px(xi + 1, yi, '#3f7d2a')
    # 夾起的麵
    for j, xs in enumerate((38, 40, 42, 44)):
        ya, _ = I(0, 19 + (j % 2))[1], 0
        yb = I(0, 34)[1]
        for y in range(I(0, 19 + (j % 2))[1], yb):
            x = I(xs, 0)[0] + round(.9 * math.sin((y + j * 1.7) / 1.5))
            if nm(y, x) in ('stickB', 'stickF', 'egg', 'yolk'):
                continue
            sp.px(x, y, '#fff1c4' if j == 0 else '#efd488' if j % 2 == 0 else '#c9a548')
            if sp.rgb[y, x + 1, 3] == 0:
                sp.px(x + 1, y, '#5a4416')
    for x, y in [(53, 5), (54, 4), (56, 9), (57, 8)]:
        dot(x, y, '#2a1a10')
    for x, y in [(48, 30), (49, 30), (50, 32), (46, 37)]:
        dot(x, y, '#fbeccc')
    # 蒸氣
    for j, xs in enumerate((25, 32)):
        for y in range(I(0, 4 + j * 2)[1], I(0, 24)[1]):
            if (y + j) % 5 == 4:
                continue
            x = I(xs, 0)[0] + round(1.6 * math.sin(y / 2.4 + j))
            if sp.rgb[y, x, 3] == 0:
                sp.rgb[y, x] = (244, 248, 255, 255 if y > 9 else 160)
                if sp.rgb[y, x + 1, 3] == 0 and y > 9:
                    sp.rgb[y, x + 1] = (200, 214, 245, 150)
    bg = background(glow=(30, 26), warm=(240, 184, 100), inner='#22306a', outer='#0e1538', thick=True) if frame else background2()
    return comp(bg, sp)


# ---------------- B 公會徽章 ----------------
def icon_B():
    sp = C.Sprite()
    # 交叉的劍與法杖在盾牌後面
    sp.poly('blade', 'metal', 5, [(49, 7), (51, 9), (17, 43), (13, 39)], shade='cyl')
    sp.cap('grip', 'leather', 6, [(14, 44), (9, 49)], 1.3, shade='cyl')
    sp.cap('guard', 'gold', 7, [(10, 38), (19, 47)], 1.4, shade='cyl')
    sp.ell('pommel', 'gold', 7, (6, 48, 11, 53), shade='sphere')
    sp.cap('staff', 'wood', 5, [(52, 53), (15, 15)], 1.3, shade='axis', axis=[(52, 53, 15, 15, 1.3, 1.3)])
    sp.cap('prong', 'gold', 6, [(17, 17), (11, 15), (10, 9)], .8, shade='cyl')
    sp.ell('orb', 'orb', 7, (8, 7, 17, 16), shade='sphere')
    # 盾牌
    shield = [(17, 13), (30, 10), (43, 13), (43, 30), (40, 40), (30, 50), (20, 40), (17, 30)]
    sp.poly('rimS', 'gold', 10, shield, shade='sphere')
    inner = [(20, 16), (30, 13.5), (40, 16), (40, 30), (37.5, 38.5), (30, 46), (22.5, 38.5), (20, 30)]
    sp.poly('field', 'navyS', 11, inner, shade='sphere', line=False)
    # 盾中央：一碗白飯＋梅子＋筷子
    bowl = mask_ell((21, 22, 39, 44)); bowl[:33] = False
    sp.mask('bowl', 'bowlR', 13, bowl, shade='sphere')
    sp.ell('bowlrim', 'porc', 14, (20, 30, 40, 36), shade='cylv', light=.35, line=False)
    rice = mask_ell((22, 23, 38, 37)); rice[34:] = False
    sp.mask('rice', 'rice', 15, rice, shade='sphere', light=.1)
    sp.ell('ume', 'ume', 16, (28, 24, 32, 28), shade='sphere')
    # 下方緞帶
    sp.poly('ribL', 'red', 20, [(8, 46), (17, 44), (17, 52), (8, 54), (11, 50)], shade='cyl')
    sp.poly('ribR', 'red', 20, [(52, 46), (43, 44), (43, 52), (52, 54), (49, 50)], shade='cyl')
    sp.poly('rib', 'red', 21, [(15, 44), (30, 46), (45, 44), (45, 51), (30, 53), (15, 51)], shade='cylv')
    sp.render()
    sp.outline()
    # 飯粒、蒸氣、星星
    for x, y in [(25, 30), (27, 31), (33, 29), (35, 31), (24, 33), (30, 33), (36, 33)]:
        sp.px(x, y, '#c9c4ca')
    put(sp, [(29, 25)], '#ffd0d6')
    for k, x0 in enumerate((26, 33)):
        for y in range(15, 22):
            if (y + k) % 4 != 3:
                sp.px(x0 + round(math.sin(y / 1.5 + k)), y, '#aebbdc')
    put(sp, [(48, 8), (49, 7)], '#ffffff')
    # 緞帶上的三顆金點
    for x in (25, 30, 35):
        sp.px(x, 49, '#eedca4'); sp.px(x, 48, '#cdaf6c')
    # 盾牌金框高光
    put(sp, [(17, 13), (18, 13), (16, 14), (16, 15)], '#fff4c8')
    return comp(background(glow=(30, 30), warm=(120, 150, 230)), sp)


# ---------------- C 寶箱 ----------------
def icon_C():
    sp = C.Sprite()
    # 打開的蓋子（往後倒）
    sp.poly('lid', 'chest', 8, [(11, 26), (13, 13), (47, 13), (49, 26)], shade='cylv', light=.1)
    sp.poly('lidin', 'chest', 9, [(14, 26), (15.5, 16), (44.5, 16), (46, 26)], shade='flat', light=-.4, line=False)
    sp.poly('glow', 'noodle', 11.8, [(10, 25), (50, 25), (51, 31), (9, 31)], shade='flat', light=.5, line=False)
    # 箱子
    sp.poly('box', 'chest', 12, [(9, 30), (51, 30), (50, 51), (10, 51)], shade='cyl')
    sp.poly('front', 'chest', 13, [(9, 34), (51, 34), (50, 51), (10, 51)], shade='cyl', light=-.05)
    # 金屬包邊
    for x0 in (13, 43):
        sp.poly('band%d' % x0, 'gold', 14, [(x0, 30), (x0 + 4, 30), (x0 + 4, 51), (x0, 51)], shade='cyl')
    sp.poly('bandT', 'gold', 14, [(9, 33), (51, 33), (51, 36), (9, 36)], shade='cylv')
    sp.poly('lock', 'gold', 15, [(26, 34), (34, 34), (34, 42), (30, 44), (26, 42)], shade='sphere')
    # 箱子裡冒出來的便當（飯糰＋炸蝦）
    oni = Image.new('L', (N, N), 0)
    ImageDraw.Draw(oni).rounded_rectangle((0, 0, 1, 1), radius=0)
    sp.poly('oni', 'rice', 12.2, [(17, 31), (20, 22), (24, 17), (27, 17), (31, 22), (34, 31)], shade='sphere', light=.15)
    sp.poly('nori2', 'nori', 12.4, [(21, 26), (30, 26), (31, 31), (20, 31)], shade='cyl')
    sp.cap('shrimp', 'yolk', 12.1, [(35, 30), (42, 16)], 2.4, shade='axis', axis=[(35, 30, 42, 16, 2.4, 1.7)])
    sp.render()
    sp.outline()
    # 寶箱內部光芒（只畫在空白處）
    for k in range(-3, 4):
        for t in range(0, 14):
            x = 30 + k * (t * .9) * .55
            y = 26 - t
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= yi < N) or (t + k) % 3 == 0:
                continue
            nm = sp.parts_sorted[sp.pid[yi, xi]]['name'] if sp.pid[yi, xi] >= 0 else ''
            if sp.rgb[yi, xi, 3] == 0:
                sp.rgb[yi, xi] = (255, 226, 150, 210 if t < 8 else 120)
            elif nm == 'lidin':
                sp.rgb[yi, xi, :3] = (sp.rgb[yi, xi, :3] * .45 + np.array((255, 214, 130)) * .55).astype(np.uint8)
    # 炸蝦紋路、尾巴
    put(sp, [(36, 27), (37, 25), (38, 23), (39, 21), (40, 19)], '#a85a1a')
    put(sp, [(35, 24), (38, 27), (40, 22), (41, 25)], '#ffd987')
    put(sp, [(42, 14), (43, 13), (43, 14), (44, 13), (44, 12)], '#e0533f')
    put(sp, [(22, 21), (23, 20)], '#ffffff')
    for x, y in [(23, 23), (28, 21), (29, 24), (25, 19)]:
        sp.px(x, y, '#cfcace')
    # 鎖孔、星星
    put(sp, [(30, 37), (30, 38), (30, 39)], '#3a2010')
    for (x, y) in [(10, 10), (50, 8), (52, 22), (7, 22)]:
        put(sp, [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], '#fff2c0')
        sp.px(x, y, '#ffffff')
    # 木紋
    for y in (40, 46):
        for x in range(19, 43, 3):
            if sp.parts_sorted[sp.pid[y, x]]['name'] == 'front':
                sp.px(x, y, '#5a3418')
    return comp(background(glow=(30, 26)), sp)


def save(im, name):
    im.resize((180, 180), Image.NEAREST).save(name + '.png')
    big = Image.new('RGBA', (512, 512), im.getpixel((0, 0)))
    big.paste(im.resize((480, 480), Image.NEAREST), (16, 16))
    big.save(name + '_512.png')


if __name__ == '__main__':
    for k, f in (('A', icon_A), ('A2', icon_A2), ('A3', icon_A3), ('B', icon_B), ('C', icon_C)):
        save(f(), 'icon_' + k)
    print('ok')
