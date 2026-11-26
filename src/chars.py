"""
午餐選困互助會 — 戰鬥角色 v2
做法：形狀組裝 → 自動明暗（光源左上）→ 部位內線 → 外框 → 手動細節
"""
from PIL import Image, ImageDraw
import numpy as np
import math

W, H = 48, 66
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

    def add(self, name, mat, z, m, shade, light=0.0, line=True):
        p = dict(name=name, mat=mat, z=z, m=m, shade=shade, light=light, line=line)
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
                if p['shade'] == 'sphere':
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

    def outline(self):
        a = self.rgb[:, :, 3] > 0
        res = self.rgb.copy()
        for y in range(H):
            for x in range(W):
                if a[y, x]:
                    continue
                for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and a[yy, xx]:
                        res[y, x] = (*OUTLINE, 255)
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
#  共用身體
# ======================================================================
def body(sp, shirt, pants, hair_mat, skirt=False, ears=True):
    sp.ell('neck', 'skin', 1, (20, 13, 27, 20), 'cyl')
    if ears:
        sp.ell('earL', 'skin', 2, (15, 8, 18, 12))
        sp.ell('earR', 'skin', 2, (30, 8, 33, 12))
    sp.poly('torso', shirt, 10,
            [(18, 17), (30, 17), (33, 20), (32, 26), (30, 33), (18, 33), (16, 26), (15, 20)])
    if not skirt:
        sp.poly('hips', pants, 8, [(18, 32), (30, 32), (31, 37), (17, 37)])
        sp.poly('legL', pants, 7, [(17, 35), (23, 35), (22, 52), (18, 52)])
        sp.poly('legR', pants, 6, [(25, 35), (31, 35), (30, 53), (26, 53)])
    sp.poly('bootL', 'boot', 9, [(17, 51), (23, 51), (23, 57), (16, 57), (16, 54)], 'cyl')
    sp.poly('bootR', 'boot', 9, [(25, 52), (31, 52), (32, 55), (32, 58), (25, 58)], 'cyl')


def cloth_detail(sp, shirt, pants=None, seam=True):
    tm = M(sp, 'torso')
    if seam:
        sp.line([(24, 20), (24, 30)], R[shirt][0], tm)
    sp.line([(19, 22), (21, 24)], R[shirt][3], tm)
    sp.line([(28, 27), (30, 29)], R[shirt][0], tm)
    if pants:
        for nm, (a, b) in (('legL', ((18, 43), (22, 43))), ('legR', ((26, 44), (30, 44)))):
            lm = M(sp, nm)
            sp.line([a, b], R[pants][0], lm)
            sp.line([(a[0], a[1] + 5), (a[0] + 2, a[1] + 6)], R[pants][0], lm)
        sp.line([(18, 38), (19, 41)], R[pants][3], M(sp, 'legL'))
        sp.line([(24, 34), (24, 36)], R[pants][0], M(sp, 'hips'))


def boot_detail(sp):
    for (x0, x1, y) in ((17, 23, 52), (25, 31, 53)):
        for x in range(x0, x1 + 1):
            if sp.rgb[y, x, 3]:
                sp.px(x, y, R['boot'][3] if x < (x0 + x1) // 2 else R['boot'][2])
    for x in range(16, 24):
        if sp.rgb[57, x, 3]: sp.px(x, 57, R['boot'][0])
    for x in range(25, 33):
        if sp.rgb[58, x, 3]: sp.px(x, 58, R['boot'][0])


# ======================================================================
#  Yulun — 弓 + 背上箭筒
# ======================================================================
def yulun(pose='idle'):
    sp = Sprite()
    body(sp, 'blue', 'sand', 'hairY')
    # 頭髮：清爽短髮，頸後收齊
    hair = sp._mask(lambda d: d.ellipse((16, 2, 32, 17), fill=255))
    hair[15:, :19] = False
    hair[15:, 30:] = False
    hair[17:, :] = False
    sp.mask('hair', 'hairY', 30, hair, 'sphere')
    sp.poly('collar', 'blue', 11, [(19, 16), (29, 16), (30, 19), (18, 19)], 'flat', light=0.25)
    sp.poly('belt', 'leather', 12, [(17, 31), (31, 31), (31, 33), (17, 33)], 'cylv')
    # 箭筒（斜背在背上）
    sp.poly('quiver', 'leather', 20, [(31, 13), (34, 15), (22, 32), (19, 30)])
    sp.poly('qcap', 'leather', 21, [(30, 12), (35, 15), (34, 17), (29, 14)], 'flat', light=.3)
    for k, (x0, y0, x1, y1) in enumerate(((31, 13, 33, 6), (33, 14, 36, 7), (34, 15, 38, 9))):
        sp.cap('shaft%d' % k, 'wood', 19, [(x0, y0), (x1, y1)], 0.5, 'flat', line=False)
    # 手臂
    def make_bow(y0, y1, cx):
        b = np.zeros((H, W), bool)
        for y in range(y0, y1):
            t = (y - y0) / (y1 - 1 - y0)
            x = cx - 4.2 * math.sin(math.pi * t)
            if t < .06 or t > .94:
                x += 1.5
            b[y, int(round(x))] = True
            b[y, int(round(x)) + 1] = True
        return b

    if pose == 'idle':
        sp.cap('armL_u', 'blue', 14, [(17, 21), (13, 27)], 2.5)
        sp.cap('armL_f', 'blue', 15, [(13, 27), (11, 32)], 2.1)
        sp.cap('armR_u', 'blue', 14, [(31, 21), (34, 27)], 2.5)
        sp.cap('armR_f', 'blue', 15, [(34, 27), (35, 32)], 2.1)
        sp.mask('bow', 'wood', 25, make_bow(17, 51, 8), 'cyl')
        sp.ell('handL', 'skin', 40, (8, 31, 13, 36))
        sp.ell('handR', 'skin', 40, (33, 31, 38, 36))
    else:
        # 拉弓：左手往前舉弓，右手把弦拉到耳邊；放箭後右手往後甩
        sp.cap('armL_u', 'blue', 14, [(17, 21), (12, 19)], 2.5)
        sp.cap('armL_f', 'blue', 15, [(12, 19), (8, 18)], 2.1)
        sp.mask('bow', 'wood', 25, make_bow(2, 35, 9), 'cyl')
        sp.ell('handL', 'skin', 40, (3, 15, 8, 20))
        sp.cap('armR_u', 'blue', 14, [(31, 21), (37, 18)], 2.5)
        if pose == 'atk':
            sp.cap('armR_f', 'blue', 15, [(37, 18), (34, 14)], 2.1)
            sp.ell('handR', 'skin', 40, (30, 10, 35, 15))
        else:
            sp.cap('armR_f', 'blue', 15, [(37, 18), (39, 13)], 2.1)
            sp.ell('handR', 'skin', 40, (37, 9, 42, 14))
    sp.render()
    if pose == 'idle':
        for y in range(18, 50):
            if sp.pid[y, 9] < 0 or sp.parts_sorted[sp.pid[y, 9]]['name'] not in ('handL',):
                sp.px(9, y, R['string'][1])
    elif pose == 'atk':
        # 弦被拉成 V 字，經過身體後面的部分看不到
        sp.line_behind([(10, 3), (31, 12)], R['string'][1])
        sp.line_behind([(10, 33), (31, 13)], R['string'][1])
        # 搭在弓上的箭：箭頭從握把另一側冒出來
        sp.line_behind([(5, 17), (16, 15)], R['wood'][2])
        for (x, y, c) in ((0, 17, 'metal'), (1, 17, 'metal'), (2, 17, 'metal'), (1, 16, 'metal'), (1, 18, 'metal')):
            sp.px(x, y, R[c][3 if y == 17 else 1])
    else:
        # 放箭：弦彈回筆直
        for y in range(3, 34):
            if sp.rgb[y, 10, 3] == 0:
                sp.px(10, y, R['string'][2])
    # 箭羽
    for (x, y) in ((32, 4), (35, 5), (37, 7)):
        sp.px(x, y, R['cream'][3]); sp.px(x + 1, y, R['red'][1])
        sp.px(x, y + 1, R['cream'][2]); sp.px(x + 1, y + 1, R['red'][2])
        sp.px(x, y + 2, R['cream'][1])
    # 頭髮髮流
    hm = M(sp, 'hair')
    sp.line([(19, 5), (18, 10)], R['hairY'][3], hm)
    sp.line([(21, 4), (20, 8)], R['hairY'][3], hm)
    sp.line([(25, 7), (24, 14)], R['hairY'][0], hm)
    sp.line([(29, 8), (29, 14)], R['hairY'][0], hm)
    # 眼鏡腳（掛在耳朵上）
    for x in (15, 16, 17):
        sp.px(x, 10, '#5a3620')
    for x in (31, 32, 33):
        sp.px(x, 10, '#5a3620')
    # 箭筒皮帶
    sp.line([(32, 17), (22, 30)], R['leather'][0], M(sp, 'quiver'))
    cloth_detail(sp, 'blue', 'sand', seam=False)
    boot_detail(sp)
    return sp.outline().ground()


# ======================================================================
#  Eric — 劍與盾 + 肩甲
# ======================================================================
def eric(pose='idle'):
    sp = Sprite()
    body(sp, 'green', 'charcoal', 'hairE', ears=False)
    # 微捲短髮：底橢圓 + 外緣一圈小捲
    def hairfn(d):
        d.ellipse((16, 2, 32, 16), fill=255)
        for (x, y) in ((16, 10), (16, 13), (18, 16), (21, 17), (24, 17),
                       (27, 17), (30, 16), (32, 13), (32, 10)):
            d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=255)
    sp.mask('hair', 'hairE', 30, sp._mask(hairfn), 'sphere')
    sp.poly('belt', 'leather', 12, [(17, 31), (31, 31), (31, 33), (17, 33)], 'cylv')
    sp.cap('armL_u', 'green', 14, [(17, 21), (13, 27)], 2.5)
    sp.cap('armL_f', 'green', 15, [(13, 27), (8, 30)], 2.1)
    if pose == 'idle':
        sp.cap('armR_u', 'green', 14, [(31, 21), (34, 27)], 2.5)
        sp.cap('armR_f', 'green', 15, [(34, 27), (35, 32)], 2.1)
    else:
        # 蓄力：劍舉到右肩上方，劍身斜垂在背後
        sp.cap('armR_u', 'green', 14, [(31, 21), (37, 15)], 2.5)
        sp.cap('armR_f', 'green', 15, [(37, 15), (36, 9)], 2.1)
    sp.ell('pauldron', 'metal', 22, (27, 16, 36, 23))
    # 盾（背對我們 → 看到的是盾的背面：木板、皮帶，手臂在盾的前面）
    sp.poly('shield', 'shieldw', 12, [(2, 21), (13, 21), (14, 26), (13, 34), (8, 43), (3, 34), (1, 26)], 'cyl')
    sp.ell('handL', 'skin', 40, (5, 28, 10, 33))
    if pose == 'idle':
        sp.cap('grip', 'leather', 24, [(35, 35), (35, 38)], 1, 'flat')
        sp.poly('guard', 'gold', 27, [(31, 31), (40, 30), (40, 32), (31, 33)], 'cylv')
        sp.poly('blade', 'metal', 23, [(34, 30), (38, 30), (44, 7), (43, 5), (41, 7)], 'cyl')
        sp.ell('handR', 'skin', 40, (33, 32, 38, 37))
    else:
        sp.cap('grip', 'leather', 36, [(36, 7), (38, 4)], 1, 'flat')
        sp.poly('blade', 'metal', 35, [(32, 11), (36, 14), (18, 34), (15, 35), (16, 32)], 'cyl')
        sp.poly('guard', 'gold', 37, [(30, 9), (33, 8), (39, 15), (37, 17)], 'cylv')
        sp.ell('handR', 'skin', 40, (33, 6, 38, 11))
    sp.render()
    # 盾背：金屬包邊 + 木板縫 + 兩條皮帶（被手臂與手蓋住的地方不畫）
    sm = M(sp, 'shield')
    vis = lambda x, y: sp.pid[y, x] >= 0 and sp.parts_sorted[sp.pid[y, x]]['name'] == 'shield'
    for y in range(H):
        for x in range(W):
            if sm[y, x] and vis(x, y):
                edge = any(not (0 <= y + dy < H and 0 <= x + dx < W) or not sm[y + dy, x + dx]
                           for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                if edge:
                    sp.px(x, y, R['metal'][2] if x < 8 else R['metal'][1])
                elif x in (5, 8, 11):
                    sp.px(x, y, R['shieldw'][0])
    for yy in (25, 36):
        for x in range(2, 14):
            if sm[yy, x] and vis(x, yy) and sm[yy, x - 1] and sm[yy, x + 1]:
                sp.px(x, yy, R['leather'][1] if x < 8 else R['leather'][0])
                sp.px(x, yy + 1, R['leather'][0])
    # 劍身中線高光
    if pose == 'idle':
        sp.line([(36, 29), (42, 8)], R['metal'][3], M(sp, 'blade'))
    else:
        sp.line([(33, 13), (17, 33)], R['metal'][3], M(sp, 'blade'))
    # 捲髮高光
    hm = M(sp, 'hair')
    for (x, y) in ((16, 9), (16, 12), (18, 15), (21, 16), (19, 5), (22, 4), (20, 8)):
        if hm[y, x]:
            sp.px(x, y, R['hairE'][3])
    for (x, y) in ((24, 16), (27, 16), (30, 15), (31, 12)):
        if hm[y, x]:
            sp.px(x, y, R['hairE'][0])
    sp.line([(26, 6), (25, 12)], R['hairE'][0], hm)
    sp.line([(29, 8), (28, 13)], R['hairE'][0], hm)
    # 肩甲鉚釘
    sp.px(30, 19, R['gold'][3]); sp.px(33, 19, R['gold'][2])
    cloth_detail(sp, 'green', 'charcoal')
    boot_detail(sp)
    return sp.outline().ground()


# ======================================================================
#  Karen — 法杖 + 馬尾 + 白色披肩
# ======================================================================
def karen(pose='idle'):
    sp = Sprite()
    body(sp, 'pink', None, 'hairK', skirt=True, ears=False)
    sp.poly('skirt', 'pink', 11, [(18, 30), (30, 30), (34, 54), (14, 54)])
    sp.ell('hair', 'hairK', 30, (16, 2, 32, 16), 'sphere')
    sp.poly('cape', 'cream', 18, [(18, 15), (30, 15), (35, 20), (34, 25), (14, 25), (13, 20)], 'cyl')
    sp.poly('tail', 'hairK', 32, [(21, 15), (27, 15), (28, 22), (26, 31), (24, 35), (21, 29), (20, 22)])
    sp.ell('tie', 'gold', 33, (21, 13, 27, 17))
    if pose == 'idle':
        sp.cap('armL_u', 'pink', 14, [(17, 23), (13, 28)], 2.5)
        sp.poly('sleeveL', 'pink', 15, [(11, 27), (16, 27), (17, 35), (9, 36)])
        sp.cap('armR_u', 'pink', 14, [(32, 23), (36, 28)], 2.6)
        sp.poly('sleeveR', 'pink', 15, [(34, 24), (39, 24), (41, 33), (35, 33)])
        staff = np.zeros((H, W), bool)
        staff[9:59, 37:39] = True
        sp.mask('staff', 'wood', 24, staff, 'cyl')
        sp.ell('orb', 'orb', 27, (34, 1, 41, 8))
        sp.poly('claw', 'gold', 26, [(34, 6), (41, 6), (40, 10), (35, 10)], 'cylv')
        sp.ell('handL', 'skin', 40, (10, 34, 15, 39))
        sp.ell('handR', 'skin', 40, (35, 23, 40, 28))
    else:
        # 施法：法杖往前上方舉起、寶珠發光，左手張開
        sp.cap('armL_u', 'pink', 14, [(17, 23), (12, 21)], 2.5)
        sp.poly('sleeveL', 'pink', 15, [(6, 16), (12, 18), (14, 26), (6, 25)])
        sp.cap('armR_u', 'pink', 14, [(32, 23), (37, 18)], 2.6)
        sp.poly('sleeveR', 'pink', 15, [(35, 16), (41, 17), (42, 26), (36, 25)])
        sp.cap('staff', 'wood', 24, [(36, 9), (46, 39)], 1, 'cyl')
        sp.ell('orb', 'orbG', 27, (32, 1, 39, 8))
        sp.poly('claw', 'gold', 26, [(32, 6), (39, 6), (38, 10), (34, 10)], 'cylv')
        sp.ell('handL', 'skin', 40, (4, 13, 9, 18))
        sp.ell('handR', 'skin', 40, (36, 13, 41, 18))
    sp.render()
    # 披肩金邊
    cm = M(sp, 'cape')
    for x in range(14, 35):
        for y in range(23, 26):
            if cm[y, x] and (y == 25 or not cm[y + 1, x]):
                sp.px(x, y, R['gold'][2] if x < 24 else R['gold'][1])
    # 長袍下襬白邊、袖口白邊
    km = M(sp, 'skirt')
    for x in range(12, 37):
        for y in (52, 53):
            if km[y, x]:
                sp.px(x, y, R['cream'][2] if x < 24 else R['cream'][1])
    for nm, ys in ((('sleeveL', (34, 35)), ('sleeveR', (31, 32))) if pose == 'idle'
                   else (('sleeveL', (23, 24)), ('sleeveR', (24, 25)))):
        mm = M(sp, nm)
        for y in ys:
            for x in range(W):
                if mm[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == nm:
                    sp.px(x, y, R['cream'][2] if x < 24 else R['cream'][1])
    # 腰帶
    for x in range(17, 32):
        if sp.rgb[30, x, 3]: sp.px(x, 30, R['gold'][1])
    # 馬尾髮束
    tm = M(sp, 'tail')
    sp.line([(23, 17), (22, 29)], R['hairK'][3], tm)
    sp.line([(26, 18), (25, 31)], R['hairK'][0], tm)
    hm = M(sp, 'hair')
    sp.line([(19, 5), (18, 10)], R['hairK'][3], hm)
    sp.line([(22, 3), (21, 7)], R['hairK'][3], hm)
    sp.line([(28, 6), (29, 12)], R['hairK'][0], hm)
    # 寶珠光點
    if pose == 'idle':
        sp.px(36, 3, R['orb'][3]); sp.px(37, 3, R['orb'][3]); sp.px(36, 4, R['orb'][3])
    else:
        sp.px(34, 3, '#ffffff'); sp.px(35, 3, '#ffffff'); sp.px(34, 4, '#ffffff')
        for (x, y) in ((29, 2), (42, 3), (30, 9), (41, 10)):
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                if sp.rgb[y + dy, x + dx, 3] == 0:
                    sp.px(x + dx, y + dy, R['orbG'][2] if (dx or dy) else '#ffffff')
    km = M(sp, 'skirt')
    sp.line([(20, 33), (17, 51)], R['pink'][0], km)
    sp.line([(25, 34), (26, 51)], R['pink'][0], km)
    sp.line([(29, 33), (32, 51)], R['pink'][0], km)
    sp.line([(19, 34), (16, 46)], R['pink'][3], km)
    boot_detail(sp)
    return sp.outline().ground()


if __name__ == '__main__':
    out = Image.new('RGBA', (3 * (W * 6 + 20) + 20, H * 6 + 20), (74, 118, 70, 255))
    for i, fn in enumerate((yulun, eric, karen)):
        im = fn().image(6)
        out.paste(im, (12 + i * (W * 6 + 20), 10), im)
    out.save('new3.png')
    rows = [('yulun', yulun, ['idle', 'atk', 'rel']), ('eric', eric, ['idle', 'atk']), ('karen', karen, ['idle', 'atk'])]
    S = 5
    sheet = Image.new('RGBA', (3 * (W * S + 14) + 20, 3 * (H * S + 14) + 20), (74, 118, 70, 255))
    for r, (nm, fn, poses) in enumerate(rows):
        for c, ps in enumerate(poses):
            im = fn(ps).image(S)
            sheet.paste(im, (12 + c * (W * S + 14), 10 + r * (H * S + 14)), im)
    sheet.save('poses.png')
    print('ok')
