"""
午餐選困互助會 — 戰鬥角色 v2
做法：形狀組裝 → 自動明暗（光源左上）→ 部位內線 → 外框 → 手動細節
"""
from PIL import Image, ImageDraw
import numpy as np
import math

W, H = 64, 80
SELOUT = False
HAIRCLUMP = False
OUTLINE = (20, 13, 26)


def hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


# ---------- 色階：暗 / 中 / 亮 / 高光 ----------
R = {
    'skin':    ['#a9694f', '#d99a76', '#efc29c', '#fbdcbc'],
    # Yulun：丹寧藍外套 + 卡其褲
    'blue':    ['#262f4c', '#3b5381', '#5674a3', '#86a2c4'],
    'sand':    ['#5f4b3c', '#93795d', '#b89e7c', '#d8c49f'],
    # Eric：鼠尾草綠 + 炭灰褲
    'green':   ['#2b3d36', '#4a6550', '#6a8a63', '#9bb585'],
    'charcoal': ['#1f2029', '#363846', '#505363', '#6f7384'],
    # Karen：乾燥玫瑰長袍 + 奶油白披肩
    'pink':    ['#4f2a40', '#82506a', '#ab778c', '#d3a3ad'],
    'cream':   ['#857766', '#c4b59c', '#e3d7bf', '#f6efdf'],
    # 共用
    'boot':    ['#231713', '#432c22', '#634130', '#865d43'],
    'leather': ['#45281b', '#74452b', '#9e643c', '#c88f5c'],
    'hairY':   ['#130d0b', '#271c16', '#403024', '#5f4a37'],
    'hairE':   ['#3e2416', '#6c4226', '#946038', '#bd8754'],
    'hairK':   ['#21140f', '#432a1e', '#64432f', '#896349'],
    'metal':   ['#3a4150', '#737d8e', '#adb7c4', '#eef2f6'],
    'gold':    ['#664c1f', '#a07f3c', '#cdaf6c', '#eedca4'],
    'wood':    ['#3e2512', '#6b4422', '#966a3f', '#c39462'],
    'shieldw': ['#3a2416', '#5e3c25', '#80573a', '#a37650'],
    'orb':     ['#1f6466', '#3aa6a3', '#86e4db', '#e6fffb'],
    'orbG':    ['#3aa6a3', '#86e4db', '#c9fbf5', '#ffffff'],
    'string':  ['#b9b29c', '#e2dbc6', '#f2ecdc', '#ffffff'],
    'red':     ['#6e2623', '#ad4a3c', '#cf735d', '#ea9c86'],
}


class Sprite:
    def __init__(self):
        self.parts = []

    # ---- 形狀 ----
    def _mask(self, fn):
        im = Image.new('L', (W, H), 0)
        fn(ImageDraw.Draw(im))
        return np.array(im) > 127

    def poly(self, name, mat, z, pts, shade='cyl', **kw):
        m = self._mask(lambda d: d.polygon(pts, fill=255))
        return self.add(name, mat, z, m, shade, **kw)

    def ell(self, name, mat, z, box, shade='sphere', **kw):
        m = self._mask(lambda d: d.ellipse(box, fill=255))
        return self.add(name, mat, z, m, shade, **kw)

    def cap(self, name, mat, z, pts, r, shade='cyl', **kw):
        def f(d):
            d.line(pts, fill=255, width=int(r * 2))
            for (x, y) in pts:
                d.ellipse((x - r + .5, y - r + .5, x + r - .5, y + r - .5), fill=255)
        m = self._mask(f)
        return self.add(name, mat, z, m, shade, **kw)

    def mask(self, name, mat, z, m, shade='cyl', **kw):
        return self.add(name, mat, z, m, shade, **kw)

    def add(self, name, mat, z, m, shade, light=0.0, line=True, axis=None):
        p = dict(name=name, mat=mat, z=z, m=m, shade=shade, light=light, line=line, axis=axis)
        self.parts.append(p)
        return p

    # ---- 合成 ----
    def render(self):
        parts = sorted(self.parts, key=lambda p: p['z'])
        pid = -np.ones((H, W), int)
        for i, p in enumerate(parts):
            pid[p['m']] = i
        rgb = np.zeros((H, W, 4), np.uint8)
        tone = np.zeros((H, W), int)

        for i, p in enumerate(parts):
            m = p['m']
            ys, xs = np.nonzero(m)
            if not len(ys):
                continue
            y0, y1 = ys.min(), ys.max()
            for y, x in zip(ys, xs):
                if pid[y, x] != i:
                    continue
                row = np.nonzero(m[y])[0]
                xl, xr = row.min(), row.max()
                tx = (x - xl) / max(1, xr - xl)
                ty = (y - y0) / max(1, y1 - y0)
                if p['shade'] == 'axis':
                    best = None
                    for (ax, ay, bx_, by_, r0, r1) in p['axis']:
                        vx, vy = bx_ - ax, by_ - ay
                        L2 = vx * vx + vy * vy or 1
                        t_ = max(0, min(1, ((x - ax) * vx + (y - ay) * vy) / L2))
                        cx, cy = ax + vx * t_, ay + vy * t_
                        dd = (x - cx) ** 2 + (y - cy) ** 2
                        if best is None or dd < best[0]:
                            Ln = math.sqrt(L2)
                            nx, ny = vy / Ln, -vx / Ln
                            best = (dd, ((x - cx) * nx + (y - cy) * ny) / (r0 + (r1 - r0) * t_))
                    s = 0.42 + 0.5 * best[1] + 0.12 * ty
                elif p['shade'] == 'sphere':
                    s = 0.62 * tx + 0.38 * ty
                elif p['shade'] == 'cylv':
                    s = ty
                elif p['shade'] == 'flat':
                    s = 0.5
                else:
                    s = tx * 0.85 + ty * 0.15
                s -= p['light']
                if s < 0.16:
                    t = 3
                elif s < 0.44:
                    t = 2
                elif s < 0.80:
                    t = 1
                else:
                    t = 0
                tone[y, x] = t
                rgb[y, x, :3] = hx(R[p['mat']][t])
                rgb[y, x, 3] = 255

        # 部位內線：後面那層貼著前面那層的地方畫暗線
        out = rgb.copy()
        for y in range(H):
            for x in range(W):
                i = pid[y, x]
                if i < 0 or not parts[i]['line']:
                    continue
                for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W:
                        j = pid[yy, xx]
                        if j > i and parts[j]['line'] and parts[j]['mat'] != 'string':
                            d = hx(R[parts[i]['mat']][0])
                            out[y, x, :3] = tuple(int(c * .62) for c in d)
                            break
        self.rgb, self.pid, self.parts_sorted = out, pid, parts
        return self

    # ---- 細節（直接上色）----
    def px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            self.rgb[y, x, :3] = hx(color) if isinstance(color, str) else color
            self.rgb[y, x, 3] = 255

    def line(self, pts, color, clip=None):
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).line(pts, fill=255, width=1)
        m = np.array(im) > 127
        for y, x in zip(*np.nonzero(m)):
            if clip is not None and not clip[y, x]:
                continue
            self.px(x, y, color)

    def line_behind(self, pts, color):
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).line(pts, fill=255, width=1)
        for y, x in zip(*np.nonzero(np.array(im) > 127)):
            if self.rgb[y, x, 3] == 0:
                self.px(x, y, color)

    def outline(self, sel=None):
        """外框。sel=True（或全域 SELOUT）時用「選擇性外框」：顏色取旁邊材質的深色調；
        下緣（物體在上面）維持最深，受光的左上緣淡一點。"""
        sel = SELOUT if sel is None else sel
        a = self.rgb[:, :, 3] > 0
        res = self.rgb.copy()
        dk = np.array(OUTLINE, np.float32)
        for y in range(H):
            for x in range(W):
                if a[y, x]:
                    continue
                for dy, dx in ((-1, 0), (0, 1), (0, -1), (1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and a[yy, xx]:
                        if not sel:
                            res[y, x] = (*OUTLINE, 255)
                        else:
                            nb = self.rgb[yy, xx, :3].astype(np.float32)
                            if dy == -1:   k = .78        # 這個外框點在物體下面：最深
                            elif dx == 1 or dy == 1: k = .55   # 在物體左邊或上面（受光側）：淡一點
                            else:          k = .68
                            c = dk * k + nb * .32 * (1 - k) * 2.2
                            res[y, x] = (*np.clip(c, 0, 255).astype(np.uint8), 255)
                        break
        self.rgb = res
        return self

    def ground(self):
        rows = np.nonzero(self.rgb[:, :, 3].any(axis=1))[0]
        d = (H - 1) - rows.max()
        if d > 0:
            self.rgb = np.roll(self.rgb, d, axis=0)
            self.rgb[:d] = 0
        self.shift = max(d, 0)
        return self

    def image(self, scale=1):
        im = Image.fromarray(self.rgb, 'RGBA')
        return im.resize((W * scale, H * scale), Image.NEAREST) if scale > 1 else im


def M(sp, name):
    for p in sp.parts:
        if p['name'] == name:
            return p['m']
    return None



# ======================================================================
#  斜角版（幻水式）：角色面朝右上，鏡頭在左後方
#  看得到背部 + 右側：右耳、一點右臉頰、眼鏡邊；右手（拿劍）朝向鏡頭
# ======================================================================
OY = 8
def P(pts):
    return [(x, y + OY) for (x, y) in pts]
def B(x0, y0, x1, y1):
    return (x0, y0 + OY, x1, y1 + OY)


def hair_clumps(sp, name, mat, crown, R_=9, a0=-40, a1=210, n=8, curly=False, seed=0):
    """頭髮髮束：從髮旋往外放射的分界線（越往外越往下彎）+ 每束受光上半部的亮光；捲髮改成小捲 + 亮點"""
    m = M(sp, name)
    own = lambda x, y: 0 <= x < W and 0 <= y < H and m[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == name
    cx, cy = crown[0], crown[1] + OY
    rr = np.random.default_rng(seed)
    if curly:
        ys, xs = np.nonzero(m)
        for _ in range(int(len(xs) / 9)):
            i = int(rr.integers(0, len(xs))); x, y = int(xs[i]), int(ys[i])
            if not own(x, y) or not own(x + 1, y + 1) or not own(x - 1, y + 1): continue
            for (dx, dy) in ((-1, 1), (0, 1), (1, 1), (1, 0)):          # 小捲的暗弧
                if own(x + dx, y + dy): sp.px(x + dx, y + dy, R[mat][0])
            if own(x - 1, y) and y < cy + R_ * .9: sp.px(x - 1, y, R[mat][3])   # 捲上的亮點（受光側）
            elif own(x, y): sp.px(x, y, R[mat][2])
        return
    angs = np.linspace(a0, a1, n + 1)
    for k, a in enumerate(angs):                                         # 分界線
        th = math.radians(a + rr.uniform(-6, 6))
        for t in np.linspace(.25, 1.6, 40):
            r = t * R_
            x = cx + math.cos(th) * r; y = cy + math.sin(th) * r + (t ** 2) * 1.6
            X, Y = int(round(x)), int(round(y))
            if own(X, Y): sp.px(X, Y, R[mat][0])
    for k in range(n):                                                   # 每束的亮光（只在上半部、受光）
        th = math.radians((angs[k] + angs[k + 1]) / 2)
        for t in np.linspace(.3, .95, 14):
            r = t * R_
            x = cx + math.cos(th) * r - .6; y = cy + math.sin(th) * r + (t ** 2) * 1.6 - .6
            X, Y = int(round(x)), int(round(y))
            if own(X, Y) and Y < cy + R_ * .55 and (math.cos(th) < .6):
                sp.px(X, Y, R[mat][3] if t < .7 else R[mat][2])


def sword(sp, hx_, hy_, dx, dy, L, z=23):
    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    px_, py_ = -dy, dx
    gx, gy = hx_ + dx * 3, hy_ + dy * 3
    tx, ty = gx + dx * L, gy + dy * L
    bx, by = gx + dx * (L - 2.5), gy + dy * (L - 2.5)
    sp.poly('blade', 'metal', z, P([(gx + px_ * 1.6, gy + py_ * 1.6), (bx + px_ * 1.4, by + py_ * 1.4),
                                   (tx, ty), (bx - px_ * 1.4, by - py_ * 1.4), (gx - px_ * 1.6, gy - py_ * 1.6)]))
    sp.cap('grip', 'leather', z + 1, P([(hx_ - dx * 2.5, hy_ - dy * 2.5), (hx_ + dx * 2, hy_ + dy * 2)]), 1.1, 'flat')
    sp.ell('pommel', 'gold', z + 2, B(hx_ - dx * 4 - 1.5, hy_ - dy * 4 - 1.5, hx_ - dx * 4 + 1.5, hy_ - dy * 4 + 1.5))
    sp.cap('guard', 'gold', z + 4, P([(gx + px_ * 3.5, gy + py_ * 3.5), (gx - px_ * 3.5, gy - py_ * 3.5)]), 1.0, 'cylv')
    # highlight along the lit edge (light from upper-left)
    side = 1 if (px_ * -1 + py_ * -1) > 0 else -1
    return [(gx + dx * 2 + px_ * 0.6 * side, gy + dy * 2 + py_ * 0.6 * side),
            (tx - dx * 2.5 + px_ * 0.6 * side, ty - dy * 2.5 + py_ * 0.6 * side)]


def boot_geo(A, K, yb, ln=8, lift=0):
    # 靴子跟著小腿：靴筒沿 膝→踝 方向延伸到地面，再接朝右的腳掌
    dx, dy = A[0] - K[0], A[1] - K[1]
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    px_, py_ = uy, -ux
    top = (A[0] - ux * 2.5, A[1] - uy * 2.5)
    t = (yb - 3 - lift - A[1]) / max(uy, .3)
    bot = (A[0] + ux * t, A[1] + uy * t)
    hx_ = bot[0] - 3
    tx = bot[0] + ln - 2
    return dict(u=(ux, uy), p=(px_, py_), top=top, bot=bot, A=A, hx=hx_, tx=tx, yb=yb, lift=lift)


def boot(sp, name, g, z, light=0.0):
    (ux, uy), (px_, py_) = g['u'], g['p']
    top, bot, yb, lift, hx_, tx = g['top'], g['bot'], g['yb'], g['lift'], g['hx'], g['tx']
    shaft = [(top[0] + px_ * 3.3, top[1] + py_ * 3.3), (bot[0] + px_ * 3.0, bot[1] + py_ * 3.0),
             (bot[0] - px_ * 3.0, bot[1] - py_ * 3.0), (top[0] - px_ * 3.3, top[1] - py_ * 3.3)]
    foot = [(hx_, yb - 4 - lift), (bot[0] + 3, yb - 4), (tx - 1, yb - 2), (tx, yb - 1), (tx, yb),
            (hx_ + 1, yb - lift), (hx_, yb - 1 - lift)]
    def f(d):
        d.polygon(P(shaft), fill=255); d.polygon(P(foot), fill=255)
    sp.mask(name, 'boot', z, sp._mask(f), 'cyl', light=light)
    cuff = [(top[0] + px_ * 4.2, top[1] + py_ * 4.2), (top[0] + px_ * 4.2 + ux * 2.2, top[1] + py_ * 4.2 + uy * 2.2),
            (top[0] - px_ * 4.2 + ux * 2.2, top[1] - py_ * 4.2 + uy * 2.2), (top[0] - px_ * 4.2, top[1] - py_ * 4.2)]
    sp.poly(name + 'Cuff', 'leather', z + 0.05, P(cuff), 'cylv', light=light + .15)


def boot_detail34(sp, name, g):
    bm = M(sp, name)
    own = lambda xx, yy: 0 <= xx < W and 0 <= yy < H and bm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == name
    (ux, uy), (px_, py_), A = g['u'], g['p'], g['A']
    yb, lift, hx_, tx, bot = g['yb'], g['lift'], int(round(g['hx'])), int(round(g['tx'])), g['bot']
    # 腳踝綁帶（垂直於小腿）+ 金扣
    pts = []
    for k in range(-4, 5):
        xx, yy = int(round(A[0] + px_ * k * .8)), int(round(A[1] + OY + py_ * k * .8))
        if own(xx, yy):
            sp.px(xx, yy, R['leather'][0]); pts.append((xx, yy))
    if pts:
        bx_, by_ = max(pts)
        sp.px(bx_ - 1, by_, R['gold'][3])
    # 鞋底一排暗色；平踩時鞋跟與腳掌間留一格足弓
    Y = yb + OY
    for xx in range(W):
        if own(xx, Y):
            sp.px(xx, Y, R['boot'][0])
    if lift == 0:
        ax_ = int(round(bot[0])) + 1
        if own(ax_, Y):
            sp.rgb[Y, ax_, 3] = 0
    else:
        for xx in range(hx_, hx_ + 4):
            if own(xx, Y - lift):
                sp.px(xx, Y - lift, R['boot'][0])
    # 腳尖高光
    sp.px(tx - 2, Y - 2, R['boot'][3]); sp.px(tx - 3, Y - 2, R['boot'][2])
    # 反折靴口：上緣亮、下緣暗
    cm = M(sp, name + 'Cuff')
    ys, xs = np.nonzero(cm)
    for xx in set(xs.tolist()):
        col = ys[xs == xx]
        sp.px(xx, col.min(), R['leather'][3] if xx < xs.mean() else R['leather'][2])
        sp.px(xx, col.max(), R['leather'][0])


def pants_detail34(sp, name, h, k, a, cuffm, mat='charcoal'):
    lm = M(sp, name)
    own = lambda xx, yy: 0 <= xx < W and 0 <= yy < H and lm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == name
    (hx_, hy_), (kx, ky), (ax_, ay_) = P([h, k, a])
    kx, ky = int(round(kx)), int(round(ky))
    # 膝蓋前側皺摺（前 = 右邊，臉朝的方向）
    for (dx, dy) in ((1, -2), (2, -1), (1, 1), (2, 2)):
        if own(kx + dx, ky + dy):
            sp.px(kx + dx, ky + dy, R[mat][0])
    if own(kx, ky - 1):
        sp.px(kx, ky - 1, R[mat][3])
    # 大腿受光線
    for t in (0.25, 0.4, 0.55):
        xx, yy = int(round(hx_ + (kx - hx_) * t - 2)), int(round(hy_ + (ky - hy_) * t))
        if own(xx, yy):
            sp.px(xx, yy, R[mat][3])
    # 靴口上方褲管堆皺（沿靴口每一欄的上方）
    ys, xs = np.nonzero(cuffm)
    for i, xx in enumerate(sorted(set(xs.tolist()))):
        yy = ys[xs == xx].min() - 1
        if own(xx, yy) and i % 2 == 1:
            sp.px(xx, yy, R[mat][0])
        if own(xx, yy - 1) and i % 3 == 0:
            sp.px(xx, yy - 1, R[mat][0])


def leg(sp, name, h, k, a, z, light=0.0, r=(3.7, 3.0, 2.5), mat='charcoal'):
    # 一整塊的錐形腿：髖最寬→膝→踝收細；明暗沿腿的方向算
    # 規則：膝蓋必須在 髖→踝 連線上或往前（右），人的膝蓋只往前彎
    t = (k[1] - h[1]) / max(1, a[1] - h[1])
    lx = h[0] + (a[0] - h[0]) * t
    assert k[0] >= lx - 0.01, (name, 'knee bends backward')
    H2, K2, A2 = P([h, k, a])
    segs = [(H2, K2, r[0], r[1]), (K2, A2, r[1], r[2])]
    def f(d):
        for (p, q, r0, r1) in segs:
            vx, vy = q[0] - p[0], q[1] - p[1]
            Ln = math.hypot(vx, vy) or 1
            nx, ny = vy / Ln, -vx / Ln
            d.polygon([(p[0] + nx * r0, p[1] + ny * r0), (q[0] + nx * r1, q[1] + ny * r1),
                       (q[0] - nx * r1, q[1] - ny * r1), (p[0] - nx * r0, p[1] - ny * r0)], fill=255)
            for (c, rr) in ((p, r0), (q, r1)):
                d.ellipse((c[0] - rr + .5, c[1] - rr + .5, c[0] + rr - .5, c[1] + rr - .5), fill=255)
    axis = [(p[0], p[1], q[0], q[1], r0, r1) for (p, q, r0, r1) in segs]
    sp.mask(name, mat, z, sp._mask(f), 'axis', light=light, axis=axis)


ERIC_POSE = {
    # up: 上身位移(dx,dy)  lean: 上半部再前傾  hip: 骨盆位移
    # L/R: 髖、膝、踝（L=左腳在後、遠側；R=右腳在前、近側）  bootL/bootR: (x, 底y, 長, 抬跟)
    # arm: 肩→肘→手  sw: 劍方向(dx,dy), 長度
    'idle': dict(up=(0, 0), lean=0, hip=(0, 0),
                 L=[(23, 44), (21, 53), (18, 61)], R=[(30, 44), (33, 53), (35, 62)],
                 bootL=(15, 67, 8, 0), bootR=(32, 68, 8, 0),
                 arm=[(35, 28), (39, 34), (41, 40)], sw=((0.45, -0.89), 19), shield=(0, 0)),
    'atk':  dict(up=(-2, 0), lean=-1, hip=(-1, 0),
                 L=[(22, 44), (21, 53), (16, 61)], R=[(29, 44), (33, 53), (37, 62)],
                 bootL=(13, 67, 8, 0), bootR=(34, 68, 8, 0),
                 arm=[(35, 28), (40, 21), (37, 13)], sw=((-0.5, -0.87), 19), shield=(1, 0)),
    'hit':  dict(up=(1, 2), lean=1, hip=(1, 1),
                 L=[(24, 45), (19, 53), (14, 60)], R=[(31, 45), (38, 51), (39, 62)],
                 bootL=(10, 66, 8, 2), bootR=(36, 68, 8, 0),
                 arm=[(35, 28), (41, 32), (45, 36)], sw=((0.78, 0.62), 17), shield=(-1, 0)),
}


def eric34(pose='idle'):
    c = ERIC_POSE[pose]
    ux, uy = c['up']; ln = c['lean']; hx0, hy0 = c['hip']
    sp = Sprite()

    def U(pts, extra=0):          # 上身座標：位移 + 上半部前傾
        return [(x + ux + (ln if y < 32 else 0) + extra, y + uy) for (x, y) in pts]

    def UB(x0, y0, x1, y1):
        d = ux + (ln if y0 < 32 else 0)
        return (x0 + d, y0 + uy, x1 + d, y1 + uy)

    # ---- 頭 ----
    sp.ell('neck', 'skin', 1, B(*UB(23, 18, 30, 25)), 'cyl')
    sp.ell('ear', 'skin', 3, B(*UB(29, 13, 32, 18)))
    sp.poly('cheek', 'skin', 2, P(U([(31, 13), (34, 15), (34, 20), (32, 22), (29, 21)])), 'cyl', light=-.3)
    hd = ux + ln

    def hairfn(d):
        d.ellipse(B(18 + hd, 6 + uy, 33 + hd, 21 + uy), fill=255)
        for (x, y) in ((18, 12), (18, 16), (20, 19), (23, 21), (26, 21), (28, 20), (31, 8), (33, 11)):
            d.ellipse(B(x - 1 + hd, y - 1 + uy, x + 1 + hd, y + 1 + uy), fill=255)
    hair = sp._mask(hairfn)
    hair[13 + OY + uy:, 30 + hd:] = False
    hair[16 + OY + uy:, 29 + hd] = False
    sp.mask('hair', 'hairE', 30, hair, 'sphere')

    # ---- 身體 ----
    sp.poly('torso', 'green', 10, P(U([(20, 24), (31, 24), (35, 27), (35, 34), (33, 41), (21, 41), (18, 34), (17, 28)])))
    sp.poly('collar', 'green', 11, P(U([(22, 23), (30, 23), (31, 26), (21, 26)])), 'flat', light=.25)
    sp.poly('belt', 'leather', 12, P(U([(20, 39), (34, 39), (34, 41), (20, 41)])), 'cylv')
    sp.poly('hips', 'charcoal', 9, P([(20 + hx0, 40 + hy0), (34 + hx0, 40 + hy0), (34 + hx0, 45 + hy0), (20 + hx0, 45 + hy0)]), line=False)
    # 皮革護腿甲片（掛在腰帶下）+ 右腰小包
    sw_ = {'idle': 0, 'atk': -1, 'hit': 1}[pose]
    sp.poly('tassetL', 'green', 9.5, P([(20 + hx0, 41 + hy0), (27 + hx0, 41 + hy0), (27 + hx0 + sw_, 47 + hy0), (20 + hx0 + sw_, 48 + hy0), (19 + hx0 + sw_, 46 + hy0)]), light=.1)
    sp.poly('tassetR', 'green', 9.6, P([(28 + hx0, 41 + hy0), (33 + hx0, 41 + hy0), (35 + hx0 + sw_, 46 + hy0), (34 + hx0 + sw_, 48 + hy0), (28 + hx0 + sw_, 47 + hy0)]))
    sp.poly('pouch', 'leather', 13, P(U([(33, 38), (37, 38), (37, 44), (33, 44)])), light=-.1)
    # ---- 腳：大腿 + 小腿，看得出膝蓋 ----
    (h1, k1, a1), (h2, k2, a2) = c['L'], c['R']
    leg(sp, 'legL', h1, k1, a1, 6, light=-.3)
    leg(sp, 'legR', h2, k2, a2, 8)
    gL = boot_geo(a1, k1, c['bootL'][1], c['bootL'][2], c['bootL'][3])
    gR = boot_geo(a2, k2, c['bootR'][1], c['bootR'][2], c['bootR'][3])
    boot(sp, 'bootL', gL, 6.5, light=-.25)
    boot(sp, 'bootR', gR, 8.5)

    # ---- 盾（遠側左手，看到盾內側 + 抓握把的左手）----
    sdx, sdy = c['shield']
    sh_pts = [(4, 25), (17, 25), (18, 30), (17, 38), (10, 48), (5, 38), (3, 30)]
    sp.poly('shield', 'shieldw', 5, P(U(sh_pts, sdx)))
    sp.cap('armL', 'green', 5.4, P(U([(18, 31), (10, 32)], sdx)), 1.8, light=.1)
    sp.ell('fistL', 'skin', 5.6, B(*[v + (sdx + ux + ln if i % 2 == 0 else uy) for i, v in enumerate((7, 30, 10, 34))]), light=-.3)

    sp.ell('pauldron', 'metal', 22, B(*UB(31, 23, 40, 31)))

    # ---- 右手 + 劍 ----
    (s0, e0, w0) = [U([p])[0] for p in c['arm']]
    sp.cap('armU', 'green', 20, P([s0, e0]), 2.5)
    sp.cap('armF', 'green', 21, P([e0, w0]), 2.1)
    fx, fy = e0[0] + (w0[0] - e0[0]) * 0.55, e0[1] + (w0[1] - e0[1]) * 0.55
    sp.cap('bracer', 'leather', 21.5, P([(fx, fy), (w0[0] + (e0[0] - w0[0]) * 0.15, w0[1] + (e0[1] - w0[1]) * 0.15)]), 2.2, 'flat')
    (sdx_, sdy_), L = c['sw']
    hl = sword(sp, w0[0], w0[1], sdx_, sdy_, L, z=23 if pose != 'atk' else 15)
    sp.ell('hand', 'skin', 40, B(w0[0] - 2.5, w0[1] - 2.5, w0[0] + 2.5, w0[1] + 2.5))
    sp.render()

    # ---- 細節 ----
    sp.line(P(hl), R['metal'][3], M(sp, 'blade'))
    sm = M(sp, 'shield')
    for y in range(H):
        for x in range(W):
            if sm[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == 'shield':
                edge = any(not sm[min(y + dy, H - 1), min(x + dx, W - 1)] for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                if edge:
                    sp.px(x, y, R['metal'][2] if x < 10 + ux + sdx else R['metal'][1])
                elif (x - ux - sdx) in (8, 14) and y > 36 + OY + uy:
                    sp.px(x, y, R['shieldw'][0])     # 內側木板縫
    am = M(sp, 'armL')
    for sx in (14,):
        X = sx + ux + ln + sdx
        for y in range(H):
            if sm[y, X] and (am[y, X] or abs(y - (31 + OY + uy)) <= 3):
                sp.px(X, y, R['leather'][1]); sp.px(X + 1, y, R['leather'][2])
    fx0 = 7 + ux + ln + sdx
    for yy_ in (31, 33):
        sp.px(fx0 + 1, yy_ + OY + uy, R['skin'][0])   # 指節縫
    o = ux + ln
    for x in range(29, 34):
        sp.px(x + o, 15 + OY + uy, '#7a4f1c')
    for y in (14, 15, 16):
        sp.px(34 + o, y + OY + uy, '#c98a2e')
    hm = M(sp, 'hair')
    for (x, y) in ((19, 11), (18, 15), (20, 18), (21, 8), (23, 6), (22, 10)):
        if hm[y + OY + uy, x + o]:
            sp.px(x + o, y + OY + uy, R['hairE'][3])
    for (x, y) in ((25, 20), (28, 19), (29, 12)):
        if hm[y + OY + uy, x + o]:
            sp.px(x + o, y + OY + uy, R['hairE'][0])
    sp.line(P([(26 + o, 9 + uy), (25 + o, 16 + uy)]), R['hairE'][0], hm)
    sp.px(33 + o, 26 + OY + uy, R['gold'][3]); sp.px(37 + o, 26 + OY + uy, R['gold'][2])
    tm = M(sp, 'torso')
    sp.line(P(U([(22, 28), (24, 31)])), R['green'][3], tm)
    sp.line(P(U([(31, 33), (33, 37)])), R['green'][0], tm)
    for nm, g, (hh, kk, aa) in (('bootL', gL, c['L']), ('bootR', gR, c['R'])):
        pants_detail34(sp, 'leg' + nm[-1], hh, kk, aa, M(sp, nm + 'Cuff'))
        boot_detail34(sp, nm, g)
    # 甲片：上緣鉚釘、縫線、下緣暗
    for nm, rx in (('tassetL', (21, 25)), ('tassetR', (28, 32))):
        tm_ = M(sp, nm)
        ys, xs = np.nonzero(tm_)
        for xx in xs:                      # 下擺滾邊：奶油色縫線 + 暗邊
            col = [yy for yy in range(H) if tm_[yy, xx]]
            if col:
                sp.px(xx, max(col), R['green'][0])
                if len(col) > 2 and xx % 2 == 0:
                    sp.px(xx, max(col) - 1, R['cream'][2])
    pm = M(sp, 'pouch'); ys, xs = np.nonzero(pm)
    for xx in range(xs.min(), xs.max() + 1):
        sp.px(xx, ys.min() + 2, R['leather'][0])
    sp.px((xs.min() + xs.max()) // 2, ys.min() + 3, R['gold'][3])
    if HAIRCLUMP: hair_clumps(sp, 'hair', 'hairE', (23 + o, 10 + uy), R_=8, curly=True, seed=3)
    return sp.outline().ground()


def bow_mask(tT, g, tB, z_w=2):
    # 經過握把的二次曲線弓身
    cx, cy = 2 * g[0] - (tT[0] + tB[0]) / 2, 2 * g[1] - (tT[1] + tB[1]) / 2
    pts = []
    for i in range(41):
        t = i / 40
        x = (1 - t) ** 2 * tT[0] + 2 * (1 - t) * t * cx + t * t * tB[0]
        y = (1 - t) ** 2 * tT[1] + 2 * (1 - t) * t * cy + t * t * tB[1]
        pts.append((x, y + OY))
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).line(pts, fill=255, width=z_w)
    return np.array(im) > 127


YULUN_POSE = {
    # 左撇子射手：右手持弓、左手拉弦。拉弓時身體轉正（整片背對鏡頭），兩臂拉成水平 T 字
    'idle': dict(L=[(23, 44), (22, 53), (20, 61)], R=[(30, 44), (32, 53), (33, 62)], bootL=(0, 67, 8, 0), bootR=(0, 68, 8, 0),
                 torso=[(20, 24), (31, 24), (35, 27), (35, 34), (33, 41), (21, 41), (18, 34), (17, 28)],
                 armR=[(35, 28), (37, 34), (38, 40)], bow=((41, 21), (39.5, 40), (35, 59)), armL=None, handL=None),
    # 下面的關節位置由簡單 3D 推算：目標方向 t=(0.85, 0.54)（往右、往畫面深處），
    # 斜俯視投影 sx=x, sy=-z-0.5y。持弓右臂往 t 伸（透視變短）、拉弦左臂手肘往後抬，
    # 前臂折回下巴、被頭擋住。開放式站姿：右腳轉向目標（腳尖朝右上）。
    'draw': dict(L=[(22, 44), (21, 53), (18, 61)], R=[(31, 44), (34, 53), (36, 60)], bootL=(0, 68, 6, 0), bootR=(0, 66, 8, 0),
                 torso=[(18, 25), (33, 24), (36, 27), (35, 34), (33, 41), (21, 41), (18, 34), (16, 28)],
                 armR=[(34, 25), (41.5, 20.5), (49, 16)], bow=((45, -4), (49.5, 16), (45, 36)),
                 armL=[(19, 25), (10, 20), (27, 18)], handL=(27, 18)),
    'rel':  dict(L=[(22, 44), (21, 53), (18, 61)], R=[(31, 44), (34, 53), (36, 60)], bootL=(0, 68, 6, 0), bootR=(0, 66, 8, 0),
                 torso=[(18, 25), (33, 24), (36, 27), (35, 34), (33, 41), (21, 41), (18, 34), (16, 28)],
                 armR=[(34, 25), (41.5, 21), (49, 17)], bow=((47, -3), (49.5, 17), (46, 37)),
                 armL=[(19, 25), (10, 22), (15, 17)], handL=(15, 17)),
}


def yulun34(pose='idle'):
    c = YULUN_POSE[pose]
    sp = Sprite()
    # ---- 頭：俐落黑短髮，臉轉向右邊（敵人方向）----
    sp.ell('neck', 'skin', 1, B(23, 18, 30, 25), 'cyl')
    sp.ell('ear', 'skin', 3, B(29, 13, 32, 18))
    sp.poly('cheek', 'skin', 2, P([(31, 13), (34, 15), (34, 20), (32, 22), (29, 21)]), 'cyl', light=-.3)
    def hairfn(d):
        d.ellipse(B(18, 6, 33, 19), fill=255)
        d.polygon(P([(30, 7), (34, 10), (34, 12), (31, 12)]), fill=255)     # 瀏海往前
        for (cx, cy, r) in ((19.5, 16.5, 1.6), (21.5, 18.5, 1.5), (24.5, 19.2, 1.4), (27.5, 18.6, 1.3)):
            d.ellipse(B(cx - r, cy - r, cx + r, cy + r), fill=255)           # 後頸髮尾參差
    hair = sp._mask(hairfn)
    hair[13 + OY:, 30:] = False
    hair[16 + OY:, 29] = False
    sp.mask('hair', 'hairY', 30, hair, 'sphere')

    # ---- 身體：丹寧外套 ----
    sp.poly('torso', 'blue', 10, P(c['torso']))
    sp.poly('collar', 'blue', 11, P([(21, 22), (30, 22), (32, 26), (20, 26)]), 'flat', light=.3)
    sp.poly('belt', 'leather', 12, P([(20, 39), (34, 39), (34, 41), (20, 41)]), 'cylv')
    sp.poly('hips', 'sand', 9, P([(20, 40), (34, 40), (34, 45), (20, 45)]), line=False)
    sp.poly('hemL', 'blue', 9.5, P([(20, 41), (27, 41), (27, 46), (20, 47), (19, 45)]), light=.1)
    sp.poly('hemR', 'blue', 9.6, P([(28, 41), (34, 41), (35, 45), (34, 47), (28, 46)]))
    (h1, k1, a1), (h2, k2, a2) = c['L'], c['R']
    leg(sp, 'legL', h1, k1, a1, 6, light=-.3, mat='sand', r=(3.5, 2.9, 2.4))
    leg(sp, 'legR', h2, k2, a2, 8, mat='sand', r=(3.5, 2.9, 2.4))
    gL = boot_geo(a1, k1, c['bootL'][1], c['bootL'][2], c['bootL'][3])
    gR = boot_geo(a2, k2, c['bootR'][1], c['bootR'][2], c['bootR'][3])
    boot(sp, 'bootL', gL, 6.5, light=-.25)
    boot(sp, 'bootR', gR, 8.5)

    # ---- 箭筒：掛在左腰側（左手抽箭），底部微微往後斜 ----
    QB, QT, QW = (11, 52), (12.5, 39), 2.2   # 箭尾朝身體前方（右上、遠離鏡頭）          # 底、開口、半寬
    qx, qy = QT[0] - QB[0], QT[1] - QB[1]
    qn = math.hypot(qx, qy); qx, qy = qx / qn, qy / qn
    qpx, qpy = -qy, qx
    sp.poly('quiver', 'leather', 9.3, P([(QB[0] + qpx * QW, QB[1] + qpy * QW), (QT[0] + qpx * QW, QT[1] + qpy * QW),
                                        (QT[0] - qpx * QW, QT[1] - qpy * QW), (QB[0] - qpx * QW, QB[1] - qpy * QW)]), 'cylv')
    sp.cap('qrim', 'leather', 9.35, P([(QT[0] + qpx * (QW + .8), QT[1] + qpy * (QW + .8)),
                                       (QT[0] - qpx * (QW + .8), QT[1] - qpy * (QW + .8))]), 0.9, 'flat', light=.3)
    # 吊帶：從腰帶左端繞過箭筒上段（有金屬扣）
    sp.poly('qstrap', 'leather', 9.4, P([(21, 39), (21, 42), (16, 43), (11, 42), (11, 40), (16, 40)]), 'cylv', light=-.05)
    arrows = []
    for k, (off, ln_, fan) in enumerate(((-1.6, 8, -.5), (0, 11, 0), (1.6, 7, .5))):   # 三支箭：從筒口微微散開、高低錯開
        a0 = (QT[0] + qpx * off, QT[1] + qpy * off)
        dxa, dya = qx + qpx * fan, qy + qpy * fan
        na = math.hypot(dxa, dya); dxa, dya = dxa / na, dya / na
        a1 = (a0[0] + dxa * ln_, a0[1] + dya * ln_)
        sp.cap('shaft%d' % k, 'wood', 9.2, P([a0, a1]), 0.6, 'flat', line=False)
        arrows.append(a1)

    # ---- 右手（持弓，近側）----
    s0, e0, w0 = c['armR']
    sp.cap('armRU', 'blue', 20, P([s0, e0]), 2.5)
    sp.cap('armRF', 'blue', 21, P([e0, w0]), 2.1)
    fx, fy = e0[0] + (w0[0] - e0[0]) * .55, e0[1] + (w0[1] - e0[1]) * .55
    bA = (e0[0] + (w0[0] - e0[0]) * .35, e0[1] + (w0[1] - e0[1]) * .35)
    bB = (w0[0] + (e0[0] - w0[0]) * .22, w0[1] + (e0[1] - w0[1]) * .22)
    sp.cap('bracerR', 'leather', 21.2, P([bA, bB]), 2.2, 'cyl')          # 射手護臂
    tT, g, tB = c['bow']
    sp.mask('bow', 'wood', 25, bow_mask(tT, g, tB), 'cyl')
    sp.ell('handR', 'skin', 40, B(w0[0] - 2.2, w0[1] - 2.2, w0[0] + 2.2, w0[1] + 2.2))

    # ---- 左手（拉弦）：上臂水平往左、手肘撐開；手勾在下巴旁（被頭擋住）----
    if c['armL']:
        ls, le, lw = c['armL']
        sp.cap('armLU', 'blue', 11, P([ls, le]), 2.5, light=.1)
        # 上臂往後抬（比背更靠近鏡頭）→ 蓋在背上
        # 前臂在下巴高度、臉的前方（比背和脖子更遠）→ 在肩膀上方水平延伸，被脖子/頭擋住
        zf = 0.5 if pose == 'draw' else 11.3        # 放箭後手往後甩到耳朵旁，回到近側
        sp.cap('armLF', 'blue', zf, P([le, lw]), 1.9, light=.25)
        hx_, hy_ = c['handL']
        sp.ell('handL', 'skin', zf + .1, B(hx_ - 2, hy_ - 2, hx_ + 2, hy_ + 2))
    sp.render()

    # 弓握把纏皮
    bm = M(sp, 'bow')
    for yy in range(int(g[1]) - 2 + OY, int(g[1]) + 3 + OY):
        for xx in range(W):
            if bm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == 'bow':
                sp.px(xx, yy, R['leather'][1])
    # 箭羽：在箭尾，沿同一條軸線
    qm = M(sp, 'quiver')
    sp.line(P([(QB[0] + qx * 4, QB[1] + qy * 4 - 1), (QT[0] - qx * 3, QT[1] - qy * 3 - 1)]), R['leather'][3], qm)
    for t_ in (4, 9):
        sp.px(int(round(QB[0] + qx * t_)), int(round(QB[1] + qy * t_ + OY)), R['gold'][3])
    sm_ = M(sp, 'qstrap')
    sp.px(17, 41 + OY, R['metal'][3]); sp.px(17, 42 + OY, R['metal'][1])
    ys, xs = np.nonzero(sm_)
    for xx in set(xs.tolist()):
        sp.px(xx, ys[xs == xx].min(), R['leather'][3])
    # 頭髮髮流 + 眼鏡腳
    hm = M(sp, 'hair')
    # 髮旋放射的髮流（暗）
    for (p1, p2) in (((21, 11), (19, 15)), ((23, 12), (21, 17)), ((26, 12), (25, 18)), ((28, 10), (29, 14))):
        sp.line(P([p1, p2]), R['hairY'][0], hm)
    # 左上光澤（一條弧）
    for (x, y_) in ((20, 10), (21, 9), (22, 8), (23, 8), (19, 12)):
        if hm[y_ + OY, x]:
            sp.px(x, y_ + OY, R['hairY'][3])
    for (x, y_) in ((24, 7), (20, 13), (22, 11)):
        if hm[y_ + OY, x]:
            sp.px(x, y_ + OY, R['hairY'][2])
    for x in range(29, 34):
        sp.px(x, 15 + OY, '#5a3620')
    for y in (14, 15, 16):
        sp.px(34, y + OY, '#3a2418')
    # 護臂綁帶、握弓指節
    brm = M(sp, 'bracerR')
    for t_ in (.3, .7):
        cx_ = bA[0] + (bB[0] - bA[0]) * t_; cy_ = bA[1] + (bB[1] - bA[1]) * t_
        dx_, dy_ = bB[0] - bA[0], bB[1] - bA[1]; n_ = math.hypot(dx_, dy_) or 1
        for k in (-2, -1, 0, 1, 2):
            xx, yy = int(round(cx_ - dy_ / n_ * k)), int(round(cy_ + dx_ / n_ * k + OY))
            if 0 <= yy < H and 0 <= xx < W and brm[yy, xx]:
                sp.px(xx, yy, R['leather'][0])
    hrm = M(sp, 'handR'); ys, xs = np.nonzero(hrm)
    if len(xs):
        kx_ = xs.max() - 1
        for yy in range(ys.min() + 1, ys.max()):
            if hrm[yy, kx_] and yy % 2 == 0:
                sp.px(kx_, yy, R['skin'][0])
    if c['armL']:
        ls, le, lw = c['armL']
        aum = M(sp, 'armLU')
        ex, ey = int(round(le[0] + 1)), int(round(le[1] + OY))
        for (dx_, dy_) in ((1, 0), (2, 1), (1, 2)):
            if aum[ey + dy_, ex + dx_]:
                sp.px(ex + dx_, ey + dy_, R['blue'][0])          # 手肘皺摺
        for (dx_, dy_) in ((3, 1), (4, 2)):
            if aum[ey + dy_, ex + dx_]:
                sp.px(ex + dx_, ey + dy_, R['blue'][3])
    # 肩膀接縫
    tm = M(sp, 'torso')
    for (x, y_) in ((19, 27), (20, 28), (33, 26), (32, 27)):
        if tm[y_ + OY, x] and sp.parts_sorted[sp.pid[y_ + OY, x]]['name'] == 'torso':
            sp.px(x, y_ + OY, R['blue'][0])
    # 丹寧縫線、下擺
    tm = M(sp, 'torso')
    for yy in range(27, 38, 2):
        if tm[yy + OY, 25]:
            sp.px(25, yy + OY, R['gold'][1])
    for nm in ('hemL', 'hemR'):
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]
            sp.px(xx, col.max(), R['blue'][0])
            if xx % 2 == 0 and len(col) > 2:
                sp.px(xx, col.max() - 1, R['gold'][1])
    for nm, gg, (hh, kk, aa) in (('bootL', gL, c['L']), ('bootR', gR, c['R'])):
        pants_detail34(sp, 'leg' + nm[-1], hh, kk, aa, M(sp, nm + 'Cuff'), mat='sand')
        boot_detail34(sp, nm, gg)

    if HAIRCLUMP: hair_clumps(sp, 'hair', 'hairY', (23, 8), R_=9, a0=-30, a1=200, n=8, seed=1)
    pid0 = sp.pid.copy(); names = [p['name'] for p in sp.parts_sorted]
    sp.outline()
    okn = ('quiver', 'qrim', 'qstrap', 'shaft0', 'shaft1', 'shaft2')
    def fpx(xx, yy, col):
        if 0 <= yy < H and 0 <= xx < W:
            i_ = sp.pid[yy, xx]
            if i_ < 0 or sp.parts_sorted[i_]['name'] in okn:     # 被身體擋住的箭羽不畫
                sp.px(xx, yy, col)
    # 箭羽：箭尾兩側各一片羽片（比箭桿寬、往前收窄），最尾端是箭扣
    for (ax_, ay_) in arrows:
        X, Y = int(round(ax_)), int(round(ay_ + OY))
        fpx(X, Y - 1, R['boot'][1])                                  # 箭扣
        for dy_ in (0, 1, 2):
            fpx(X, Y + dy_, R['wood'][2])
            fpx(X - 1, Y + dy_, R['cream'][3] if dy_ < 2 else R['cream'][2])   # 左羽片（受光）
            fpx(X + 1, Y + dy_, R['red'][2] if dy_ < 2 else R['red'][1])       # 右羽片
        fpx(X - 1, Y + 3, R['cream'][1]); fpx(X + 1, Y + 3, R['red'][0])     # 羽片前端收窄
    # ---- 弦與箭：最後畫、不加外框；被身體/頭擋住的部分不畫 ----
    free = np.vectorize(lambda i: i < 0 or names[i] in ('bow',))(pid0) & ~M(sp, 'handR')
    if pose == 'idle':
        sp.line(P([tT, tB]), R['string'][1], free)
    elif pose == 'draw':
        anc = c['handL']
        sp.line(P([tT, anc]), R['string'][1], free)
        sp.line(P([tB, anc]), R['string'][1], free)
        dx, dy = g[0] - anc[0], (g[1] - 1) - anc[1]
        n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
        tip = (anc[0] + dx * (n + 6), anc[1] + dy * (n + 6))
        sp.line(P([anc, tip]), R['wood'][2], free)
        tx, ty = int(round(tip[0])), int(round(tip[1] + OY))
        for (ox, oy, cc) in ((0, 0, R['metal'][3]), (-1, 0, R['metal'][2]), (-1, -1, R['metal'][1]), (-1, 1, R['metal'][1])):
            sp.px(tx + ox, ty + oy, cc)
    else:
        sp.line(P([tT, (tT[0] - 1, g[1]), tB]), R['string'][2], free)
    return sp.ground()


def sleeve(sp, name, mat, z, e, w, r0=2.2, r1=3.6, droop=1.5, light=0.0):
    # 鐘形袖：手肘窄→袖口寬，袖口下緣因重力往下垂
    vx, vy = w[0] - e[0], w[1] - e[1]
    n = math.hypot(vx, vy) or 1
    nx, ny = vy / n, -vx / n
    p1 = (e[0] + nx * r0, e[1] + ny * r0); p2 = (w[0] + nx * r1, w[1] + ny * r1)
    p3 = (w[0] - nx * r1, w[1] - ny * r1 + droop); p4 = (e[0] - nx * r0, e[1] - ny * r0)
    lo = p2 if p2[1] > p3[1] else p3
    pts = [p1, p2, (lo[0], lo[1] + droop), p3, p4]
    def f(d):
        d.polygon(P(pts), fill=255)
        d.ellipse(B(e[0] - r0, e[1] - r0, e[0] + r0, e[1] + r0), fill=255)
    sp.mask(name, mat, z, sp._mask(f), 'cyl', light=light)
    return (p2, p3)


KAREN_POSE = {
    'idle': dict(arm=[(33, 27), (37.5, 33), (40.5, 38.5)], hand=(41.5, 39.5), staff=((0.125, -1), 30, 27.5), bare=False,
                 hem=[(15, 62), (39, 62)], boots=((17, 67, 6), (31, 67, 8)), tail=0, glow=0),
    'raise': dict(arm=[(33, 27), (38.5, 28), (41.5, 22)], hand=(42.5, 21), staff=((0.125, -1), 21, 25), bare=False,
                  hem=[(15, 62), (39, 62)], boots=((17, 67, 6), (31, 67, 8)), tail=0, glow=1),
    'cast': dict(arm=[(33, 27), (39, 25), (45, 22)], hand=(46, 21), staff=((0.5, -0.87), 19, 30), bare=False,
                 hem=[(15, 62), (41, 61)], boots=((16, 67, 6), (34, 67, 8)), tail=-1, glow=2),
}


def karen34(pose='idle'):
    c = KAREN_POSE[pose]
    sp = Sprite()
    # ---- 頭：深棕長髮綁高馬尾，臉轉向右（看敵人）----
    sp.ell('neck', 'skin', 1, B(23, 18, 30, 25), 'cyl')
    sp.ell('ear', 'skin', 3, B(29, 13, 32, 18))
    sp.poly('cheek', 'skin', 2, P([(31, 13), (34, 15), (34, 20), (32, 22), (29, 21)]), 'cyl', light=-.3)
    def hairfn(d):
        d.ellipse(B(18, 6, 33, 20), fill=255)
        d.polygon(P([(30, 7), (34, 10), (34, 13), (31, 12)]), fill=255)       # 瀏海
    hair = sp._mask(hairfn)
    hair[14 + OY:, 30:] = False
    # 耳前鬢髮直接併進頭髮同一塊：明暗連續、沒有接縫
    hair |= sp._mask(lambda d: d.polygon(P([(28.5, 10), (31.5, 11.5), (33, 14.5), (32.8, 18), (31.6, 21), (30.4, 22.6),
                                             (30.2, 20.5), (30.9, 17.5), (30.6, 14.5), (29, 12.5)]), fill=255))
    sp.mask('hair', 'hairK', 30, hair, 'sphere')
    # 原本順順的馬尾：髮帶在後腦，馬尾從頭後面垂到披肩
    t = c['tail']
    # 馬尾：從髮圈正下方長出來，沿一條柔和的中心線往下、先微微鼓起再收尖；跟頭髮之間不畫接縫
    def tail_c(u):
        return 25 + 0.9 * math.sin(math.pi * u * 0.9) - 1.6 * u + t * u
    def tail_w(u):
        return 1.5 + 1.5 * math.sin(math.pi * min(u * 1.7, 1.0)) * (1 - u * 0.55) - 1.1 * max(0, u - 0.75) * 4
    L_, R_ = [], []
    for i in range(21):
        u = i / 20; y_ = 15.5 + 17.5 * u; w_ = max(0.35, tail_w(u))
        L_.append((tail_c(u) - w_, y_)); R_.append((tail_c(u) + w_, y_))
    sp.poly('tail', 'hairK', 30.5, P(R_ + L_[::-1]), 'cyl', light=-.08, line=False)
    sp.cap('tie', 'gold', 31.5, P([(23.8, 15.2), (26.2, 15.2)]), 1.0, 'cylv')

    # ---- 身體：長袍 + 披肩 ----
    sp.poly('torso', 'pink', 10, P([(21, 24), (31, 24), (34, 27), (33, 33), (31.5, 40), (22.5, 40), (20, 33), (18, 28)]))
    (hl, hr) = c['hem']
    # 收腰 → 往下展開；底邊是往下彎的弧（從斜上方看圓筒形裙襬）
    hem_curve = []
    for i in range(1, 8):
        u = i / 8
        hem_curve.append((hr[0] + (hl[0] - hr[0]) * u, hr[1] + (hl[1] - hr[1]) * u + 2.2 * math.sin(math.pi * u)))
    sp.poly('skirt', 'pink', 9, P([(22, 38), (32, 38), (34.5, 44), (37, 51), (hr[0] - .5, 57), hr] + hem_curve + [hl, (hl[0] + 1, 57), (17.5, 51), (19.5, 44)]))
    sp.cap('sash', 'gold', 12, P([(21, 39.5), (33, 39.5)]), 1.1, 'cylv')
    sp.ell('knot', 'gold', 12.6, B(21.3, 39.6, 23.9, 42))                       # 繩結
    sp.poly('tassel', 'gold', 12.5, P([(22.2, 43.5), (23, 43.5), (24.4, 48.5), (20.8, 48.5)]), 'cylv', light=-.05)   # 穗子
    sp.poly('cape', 'cream', 14, P([(19, 23), (32, 23), (36, 27), (35.5, 31), (28, 34), (21, 34), (17, 31), (17, 26)]))
    # 靴尖從袍底露出
    for k, (bx, yb, ln) in enumerate(c['boots']):
        sp.poly('boot%d' % k, 'boot', 6.5 + k * 2, P([(bx, yb - 5), (bx + 5, yb - 5), (bx + 6, yb - 3), (bx + ln, yb - 2),
                                                   (bx + ln + 1, yb), (bx + 1, yb)]), 'cylv', light=-.25 if k == 0 else 0)

    # ---- 左手（遠側）----
    if pose == 'cast':
        # 雙手施法：左手往前伸、掌心朝敵人，出現在頭和法杖之間；手臂其餘被頭擋住
        cuffL = sleeve(sp, 'sleeveL', 'pink', 0.6, (31, 20), (36, 15.5), r0=2.0, r1=3.0, droop=1.2, light=-.15)
        sp.ell('handL', 'skin', 0.7, B(36, 12.5, 39.5, 16.3), light=-.1)
    else:
        # 自然垂在左側：寬袖口從身體左邊緣露出（遠側，暗一階）
        cuffL = sleeve(sp, 'sleeveL', 'pink', 8.8, (19, 33), (18, 42), r0=2.2, r1=3.2, droop=1.0, light=-.3)
        sp.ell('handL', 'skin', 8.7, B(16.3, 42.5, 19.3, 45.5), light=-.3)

    # ---- 右手 + 法杖 ----
    s0, e0, w0 = c['arm']
    hx_, hy_ = c['hand']
    sp.cap('armU', 'pink', 20, P([s0, e0]), 2.4)
    if c['bare']:
        # 手舉高：鐘形袖滑到手肘、往下垂，前臂露出
        sp.cap('forearm', 'skin', 21, P([e0, w0]), 1.6)
        cuff = sleeve(sp, 'sleeve', 'pink', 21.5, s0, (e0[0] - .5, e0[1] + 3), r0=2.4, r1=3.6, droop=2.5)
    else:
        cuff = sleeve(sp, 'sleeve', 'pink', 21, e0, w0)
    (dx, dy), up, down = c['staff']
    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    top = (hx_ + dx * up, hy_ + dy * up); bot = (hx_ - dx * down, hy_ - dy * down)
    sp.cap('staff', 'wood', 18, P([bot, top]), 1.0, 'cyl')
    ox, oy = top[0] + dx * 2.5, top[1] + dy * 2.5
    sp.ell('orb', 'orbG' if c['glow'] else 'orb', 19.5, B(ox - 2.8, oy - 2.8, ox + 2.8, oy + 2.8))
    sp.cap('claw', 'gold', 19.2, P([(top[0] - dy * 2.6, top[1] + dx * 2.6), top, (top[0] + dy * 2.6, top[1] - dx * 2.6)]), 0.8, 'flat')
    sp.ell('hand', 'skin', 40, B(hx_ - 2.2, hy_ - 2.2, hx_ + 2.2, hy_ + 2.2))
    sp.render()

    # ---- 細節 ----
    # 披肩金邊（下緣兩排）+ 中央扣飾
    cm = M(sp, 'cape'); ys, xs = np.nonzero(cm)
    for xx in set(xs.tolist()):
        col = ys[xs == xx]
        if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] == 'cape':
            sp.px(xx, col.max(), R['gold'][1])
            sp.px(xx, col.max() - 1, R['gold'][3] if xx % 2 else R['gold'][2])
    sp.px(26, 27 + OY, R['gold'][3]); sp.px(26, 28 + OY, R['gold'][1])
    # 長袍：背中縫、垂墜褶、下襬奶油色滾邊
    km = M(sp, 'skirt')
    own = lambda xx, yy: km[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == 'skirt'
    for (x0, y0, x1, y1, col) in ((26, 42, 26, 60, R['pink'][0]), (21, 46, 19, 60, R['pink'][0]), (31, 46, 34, 60, R['pink'][0]),
                                 (23, 47, 22, 58, R['pink'][3]), (29, 48, 30, 58, R['pink'][2])):
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).line(P([(x0, y0), (x1, y1)]), fill=255)
        for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
            if own(xx, yy):
                sp.px(xx, yy, col)
    ys, xs = np.nonzero(km)
    for xx in set(xs.tolist()):
        col = ys[xs == xx]
        yb_ = col.max()
        if own(xx, yb_):
            sp.px(xx, yb_, R['cream'][1])
            if own(xx, yb_ - 1):
                sp.px(xx, yb_ - 1, R['cream'][2] if xx % 3 else R['gold'][2])
    # 流蘇：細繩 + 穗子條紋 + 參差下緣
    sp.px(22, 42 + OY, R['gold'][1]); sp.px(22, 43 + OY, R['gold'][1])
    tsm = M(sp, 'tassel'); ys, xs = np.nonzero(tsm)
    for xx in set(xs.tolist()):
        col = ys[xs == xx]
        for yy in col:
            if xx % 2 == 0:
                sp.px(xx, yy, R['gold'][0])
        if xx % 2 == 1:
            sp.rgb[col.max(), xx, 3] = 0              # 下緣參差
    # 袖口滾邊（左右）
    for nm, (p2, p3), col in (('sleeve', cuff, R['cream'][2]), ('sleeveL', cuffL, R['cream'][1])):
        sm = M(sp, nm)
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).line(P([p2, (p3[0], p3[1])]), fill=255, width=1)
        for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
            if sm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == nm:
                sp.px(xx, yy, col)
    if pose == 'cast':   # 張開的手指
        for (x, y_) in ((39, 12), (40, 14)):
            sp.px(x, y_ + OY, R['skin'][1])
    # 馬尾髮絲（原本的）
    tm = M(sp, 'tail')
    own_t = lambda xx, yy: tm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == 'tail'
    for (off, col, u0, u1) in ((-0.6, R['hairK'][3], .08, .8), (0.9, R['hairK'][0], .25, .7)):   # 沿中心線的光澤與髮絲
        pts = [(tail_c(i / 20) + off * max(0.35, tail_w(i / 20)) / 2, 15.5 + 17.5 * i / 20) for i in range(int(u0 * 20), int(u1 * 20) + 1)]
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).line(P(pts), fill=255)
        for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
            if own_t(xx, yy):
                sp.px(xx, yy, col)
    hm = M(sp, 'hair')
    own_h = lambda xx, yy: hm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == 'hair'
    for (x, y_) in ((20, 10), (21, 9), (22, 8), (19, 12)):
        if own_h(x, y_ + OY):
            sp.px(x, y_ + OY, R['hairK'][3])
    for (x, y_) in ((31, 14), (31, 16), (31, 18)):           # 鬢髮上一點光澤
        if own_h(x, y_ + OY):
            sp.px(x, y_ + OY, R['hairK'][2])
    # 四道往髮帶收攏的髮流：柔和的中暗色、互不交叉
    for p1 in ((19.5, 11), (21.5, 7.5), (28, 8), (20.5, 17)):
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).line(P([p1, (25, 14.6)]), fill=255)
        for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
            if own_h(xx, yy) and (xx - 25) ** 2 + (yy - 14.6 - OY) ** 2 > 3:
                sp.px(xx, yy, R['hairK'][1])
    tim = M(sp, 'tie'); ys, xs = np.nonzero(tim)
    for xx in set(xs.tolist()):
        sp.px(xx, ys[xs == xx].max(), R['gold'][0])        # 髮帶下緣暗邊
    # 法杖金環
    stm = M(sp, 'staff')
    for tt in (0.12, 0.55):
        X = int(round(bot[0] + (top[0] - bot[0]) * (1 - tt))); Y = int(round(bot[1] + (top[1] - bot[1]) * (1 - tt) + OY))
        for ddx in (-1, 0, 1):
            if 0 <= X + ddx < W and stm[Y, X + ddx]:
                sp.px(X + ddx, Y, R['gold'][2])
    # 寶珠高光
    sp.px(int(round(ox - 1)), int(round(oy - 1 + OY)), R['orb'][3])
    if HAIRCLUMP: hair_clumps(sp, 'hair', 'hairK', (25, 14.6), R_=8, a0=185, a1=355, n=6, seed=2)
    sp.outline()
    # 發光：外框之後畫，光點不加框
    if c['glow']:
        rr = 5 if c['glow'] == 1 else 7
        pts = [(-rr, 0), (rr, 0), (0, -rr), (0, rr), (-rr + 2, -rr + 2), (rr - 2, rr - 2), (rr - 2, -rr + 2), (-rr + 2, rr - 2)]
        for i, (px_, py_) in enumerate(pts):
            X, Y = int(round(ox + px_)), int(round(oy + py_ + OY))
            if 0 <= X < W and 0 <= Y < H and sp.rgb[Y, X, 3] == 0:
                sp.px(X, Y, R['orbG'][3] if i < 4 else R['orbG'][1])
        if c['glow'] == 2:
            for (px_, py_) in ((-9, -3), (8, 4), (3, -10), (-4, 8)):
                X, Y = int(round(ox + px_)), int(round(oy + py_ + OY))
                if 0 <= X < W and 0 <= Y < H and sp.rgb[Y, X, 3] == 0:
                    sp.px(X, Y, R['orbG'][2])
    return sp.ground()


if __name__ == '__main__':
    S = 5
    out = Image.new('RGBA', (3 * (W * S + 14) + 20, H * S + 20), (74, 118, 70, 255))
    for i, ps in enumerate(('idle', 'atk', 'hit')):
        im = eric34(ps).image(S)
        out.paste(im, (12 + i * (W * S + 14), 10), im)
    out.save('eric34.png')
    print('ok')
