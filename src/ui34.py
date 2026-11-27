"""v2.1 頭像（32×32）與底部選單圖示（16×16，4 色索引：1 外框 2 主色 3 亮 4 暗）。
python3 ui34.py → ui_demo.png（新舊對照）"""
import math
import numpy as np
from PIL import Image, ImageDraw
import chars34 as C

# ======================= 頭像 =======================
PN = 32


def _sprite():
    C.W = C.H = PN
    return C.Sprite()


def ell_mask(box, n=PN):
    im = Image.new('L', (n, n), 0)
    ImageDraw.Draw(im).ellipse(box, fill=255)
    return np.array(im) > 127


def poly_mask(pts, n=PN):
    im = Image.new('L', (n, n), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.array(im) > 127


C.R.update({
    'skinP': ['#b8765a', '#e2a882', '#f2c9a5', '#fbe0c4'],
})


def face_base(sp, glasses=None, brow='#2a1c15', blush=False, mouth='#b0604c'):
    """臉、耳朵、脖子（頭放大，32px 小圖也看得清楚）；回傳後續手動細節用的函式"""
    sp.ell('earL', 'skinP', 9, (6, 12.5, 9.5, 19), shade='sphere')
    sp.ell('earR', 'skinP', 9, (22.5, 12.5, 26, 19), shade='sphere', light=-.2)
    sp.poly('neck', 'skinP', 8, [(13, 21), (19, 21), (19, 27), (13, 27)], shade='cyl', light=.2)
    sp.ell('face', 'skinP', 10, (8, 4.5, 24, 25), shade='sphere', light=.3)

    def details():
        # 眉毛
        for x in (10, 11, 12, 13):
            sp.px(x, 12 if x > 10 else 13, brow)
        for x in (18, 19, 20, 21):
            sp.px(x, 12 if x < 21 else 13, brow)
        # 眼睛：上排睫毛、下排瞳孔＋眼白（左右對稱）
        for (xs, white, pup) in (((11, 12, 13), 11, (12, 13)), ((18, 19, 20), 20, (18, 19))):
            for x in xs:
                sp.px(x, 15, '#1b1310')
            sp.px(white, 16, '#ffffff')
            for x in pup:
                sp.px(x, 16, '#2a1c15')
            sp.px(pup[0] if white == 11 else pup[1], 16, '#4a3428')
        # 鼻子、嘴
        sp.px(16, 19, '#c98d6c'); sp.px(15, 19, '#e9b591')
        for x in (15, 16):
            sp.px(x, 22, mouth)
        sp.px(14, 21, '#d08a70'); sp.px(17, 21, '#d08a70')
        if blush:
            for x in (10, 11):
                sp.px(x, 19, '#eba496')
            for x in (20, 21):
                sp.px(x, 19, '#eba496')
        if glasses:
            fr, hi = glasses
            for (x0, x1) in ((9, 14), (17, 22)):
                for x in range(x0, x1 + 1):
                    sp.px(x, 14, fr); sp.px(x, 18, fr)
                for y in (15, 16, 17):
                    sp.px(x0, y, fr); sp.px(x1, y, fr)
                sp.px(x0 + 1, 15, hi) if x0 == 9 else None
            sp.px(15, 15, fr); sp.px(16, 15, fr)
            sp.px(8, 15, fr); sp.px(23, 15, fr)
    return details


def portrait_yulun():
    sp = _sprite()
    # 丹寧外套 + 米色上衣 + 箭袋背帶
    sp.poly('body', 'blue', 4, [(1, 32), (3, 26), (9, 23.5), (23, 23.5), (29, 26), (31, 32)], shade='cyl')
    sp.poly('shirt', 'cream', 5, [(12.5, 23.5), (19.5, 23.5), (16, 30)], shade='flat', light=.2)
    sp.poly('lapL', 'blue', 6, [(9, 23.5), (13, 23.5), (16, 31), (12, 32)], shade='cyl', light=.25)
    sp.poly('lapR', 'blue', 6, [(23, 23.5), (19, 23.5), (16, 31), (20, 32)], shade='cyl', light=-.05)
    sp.poly('strap', 'leather', 7, [(21, 24), (24, 24.5), (11, 32), (8, 32)], shade='cyl')
    det = face_base(sp, glasses=('#1b1310', '#cfe3f5'))
    # 短髮：頭頂＋往右撥的瀏海＋鬢角
    hair = ell_mask((6.5, 1, 25.5, 17))
    yy, xx = np.mgrid[0:PN, 0:PN]
    fringe = 8.6 + (xx - 8) * 0.24 + np.where((xx > 10) & (xx < 14), -1, 0)
    cap = hair & ((yy < fringe) | ((xx < 9) & (yy < 15)) | ((xx > 23) & (yy < 14)))
    sp.mask('hair', 'hairY', 12, cap, shade='sphere', light=-.15)
    sp.render(); sp.outline()
    det()
    # 髮絲亮光、瀏海分線、外套金色明線
    for x, y in [(11, 3), (12, 3), (13, 3), (10, 4), (16, 4), (17, 4), (9, 6)]:
        sp.px(x, y, '#5f4a37')
    for x, y in [(12, 8), (13, 7), (19, 9), (20, 9)]:
        sp.px(x, y, '#0d0907')
    for x, y in [(6, 28), (7, 27), (25, 27), (26, 28), (4, 30), (28, 30)]:
        sp.px(x, y, '#cdaf6c')
    for x, y in [(19, 27), (18, 28)]:          # 背帶金屬扣
        sp.px(x, y, '#e8d8a8')
    return sp


def portrait_eric():
    sp = _sprite()
    # 鼠尾草綠上衣、皮帶、右肩金屬肩甲
    sp.poly('body', 'green', 4, [(1, 32), (3, 26), (9, 23.5), (23, 23.5), (29, 26), (31, 32)], shade='cyl')
    sp.poly('collar', 'cream', 5, [(12, 23.5), (20, 23.5), (16, 28)], shade='flat', light=.15)
    sp.poly('strap', 'leather', 7, [(9, 25), (12, 24.5), (25, 32), (21, 32)], shade='cyl')
    sp.ell('pauld', 'metal', 8, (1, 25, 9, 31), shade='sphere')
    det = face_base(sp, glasses=('#a07f3c', '#fff4c8'))
    # 捲髮：比較蓬，邊緣一顆一顆
    yy, xx = np.mgrid[0:PN, 0:PN]
    hair = ell_mask((5, 0, 27, 16))
    for (cx, cy, r) in [(6.5, 12.5, 2.4), (25.5, 12.5, 2.4), (7, 15.5, 1.9), (25, 15.5, 1.9)]:
        hair |= ell_mask((cx - r, cy - r, cx + r, cy + r))
    fringe = 8.8 + 1.3 * np.abs(np.sin((xx - 6) * 0.72))
    cap = hair & ((yy < fringe) | (xx < 8.5) | (xx > 23.5))
    cap &= ~((yy > 17))
    sp.mask('hair', 'hairE', 12, cap, shade='sphere', light=.05)
    sp.render(); sp.outline()
    det()
    # 捲髮的小捲：暗色弧＋亮點
    for (x, y) in [(10, 3), (15, 2), (20, 3), (8, 7), (13, 6), (18, 6), (23, 7)]:
        sp.px(x, y + 1, '#3e2416'); sp.px(x + 1, y + 1, '#3e2416'); sp.px(x, y, '#bd8754')
    # 肩甲鉚釘、皮帶扣
    for x, y in [(3, 27), (6, 26)]:
        sp.px(x, y, '#eef2f6')
    sp.px(17, 28, '#e8d8a8'); sp.px(18, 29, '#e8d8a8')
    return sp


def portrait_karen():
    sp = _sprite()
    # 乾燥玫瑰長袍 + 奶油白披肩 + 金色繩結
    sp.poly('body', 'pink', 4, [(1, 32), (3, 26), (9, 23.5), (23, 23.5), (29, 26), (31, 32)], shade='cyl')
    sp.poly('shawl', 'cream', 6, [(2, 29), (5, 25.5), (11, 23.5), (16, 27), (21, 23.5), (27, 25.5), (30, 29),
                                  (24, 30.5), (16, 30), (8, 30.5)], shade='cyl', light=.1)
    # 馬尾從右肩垂到胸前（畫面右側）
    sp.cap('tail', 'hairK', 7, [(24, 15), (26, 22), (25.5, 29)], 2.1, shade='axis',
           axis=[(24, 15, 26, 22, 2, 2), (26, 22, 25.5, 29, 2, 1.6)])
    det = face_base(sp, blush=True, mouth='#b85a5a', brow='#3a2418')
    # 中分、往後梳，臉兩側各一束
    yy, xx = np.mgrid[0:PN, 0:PN]
    hair = ell_mask((6.5, 1, 25.5, 16))
    part = 9.8 - 2.4 * np.cos((xx - 16) / 8.0)
    cap = hair & ((yy < part) | ((xx < 9.2) & (yy < 23)) | ((xx > 22.8) & (yy < 15)))
    cap |= poly_mask([(7, 12), (9.6, 10.5), (9.6, 23), (7.5, 22)])
    sp.mask('hair', 'hairK', 12, cap, shade='sphere', light=.1)
    sp.render(); sp.outline()
    det()
    # 中分線、髮絲亮光、金色髮圈、繩結
    for y in range(2, 7):
        sp.px(16, y, '#21140f')
    for x, y in [(11, 3), (12, 4), (20, 3), (21, 4), (8, 9), (8, 15)]:
        sp.px(x, y, '#896349')
    for x, y in [(23, 15), (24, 15), (25, 15), (26, 15), (24, 16), (25, 16)]:
        sp.px(x, y, '#cdaf6c')
    sp.px(24, 15, '#eedca4')
    for x, y in [(16, 28), (15, 29), (17, 29), (16, 30), (16, 31)]:
        sp.px(x, y, '#cdaf6c')
    return sp


# ======================= 選單圖示（16×16 索引色） =======================
NI = 16


def icon_from(shapes, extra=None):
    """shapes: [(mask, z)]（z 大的在前）。自動：左上亮、右下暗、物件之間內線、外框。"""
    pid = -np.ones((NI, NI), int)
    order = sorted(range(len(shapes)), key=lambda i: shapes[i][1])
    for i in order:
        pid[shapes[i][0]] = i
    g = [['.'] * NI for _ in range(NI)]
    zof = {i: shapes[i][1] for i in range(len(shapes))}
    for y in range(NI):
        for x in range(NI):
            i = pid[y, x]
            if i < 0:
                continue
            m = shapes[i][0]
            out = lambda yy, xx: not (0 <= yy < NI and 0 <= xx < NI) or not m[yy, xx]
            front = lambda yy, xx: 0 <= yy < NI and 0 <= xx < NI and pid[yy, xx] >= 0 and pid[yy, xx] != i and zof[pid[yy, xx]] > zof[i]
            if any(front(y + dy, x + dx) for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                g[y][x] = '1'
            elif out(y - 1, x) or out(y, x - 1):
                g[y][x] = '3'
            elif out(y + 1, x) or out(y, x + 1):
                g[y][x] = '4'
            else:
                g[y][x] = '2'
    occ = pid >= 0
    for y in range(NI):
        for x in range(NI):
            if not occ[y, x] and any(0 <= y + dy < NI and 0 <= x + dx < NI and occ[y + dy, x + dx]
                                     for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                g[y][x] = '1'
    if extra:
        for (x, y, c) in extra:
            g[y][x] = c
    return [''.join(r) for r in g]


def im16(box=None, pts=None, ell=None):
    im = Image.new('L', (NI, NI), 0)
    d = ImageDraw.Draw(im)
    if box: d.rectangle(box, fill=255)
    if pts: d.polygon(pts, fill=255)
    if ell: d.ellipse(ell, fill=255)
    return np.array(im) > 127


def icon_party():
    s = [
        (im16(ell=(0.5, 3.5, 5.5, 8.5)), 1), (im16(pts=[(0, 15), (0.5, 11), (2, 9.5), (5, 9.5), (6, 11), (6, 15)]), 1),
        (im16(ell=(10.5, 3.5, 15.5, 8.5)), 1), (im16(pts=[(10, 15), (10, 11), (11, 9.5), (14, 9.5), (15.5, 11), (15.5, 15)]), 1),
        (im16(ell=(5, 1, 11, 7)), 3), (im16(pts=[(3.5, 15), (4, 10.5), (6, 8.5), (10, 8.5), (12, 10.5), (12.5, 15)]), 3),
    ]
    return icon_from(s)


def icon_dice():
    top = im16(pts=[(8, 1), (15, 4.5), (8, 8), (1, 4.5)])
    left = im16(pts=[(1, 4.5), (8, 8), (8, 15.5), (1, 12)])
    right = im16(pts=[(8, 8), (15, 4.5), (15, 12), (8, 15.5)])
    g = icon_from([(left, 1), (right, 2), (top, 3)])
    g = [list(r) for r in g]
    # 三個面分別亮／中／暗，點數用外框色
    for y in range(NI):
        for x in range(NI):
            if g[y][x] in '234':
                if top[y, x] and not (left[y, x] or right[y, x]): g[y][x] = '3'
                elif left[y, x]: g[y][x] = '2'
                elif right[y, x]: g[y][x] = '4'
    for (x, y) in [(8, 4), (4, 8), (5, 11), (10, 8), (12, 10), (11, 12)]:
        g[y][x] = '1'
    g[4][7] = '1'
    return [''.join(r) for r in g]


def icon_quill():
    vane = im16(pts=[(14.5, 0.5), (15.5, 2), (13, 7.5), (8.5, 11.5), (6, 11), (7, 8), (10.5, 3.5)])
    g = icon_from([(vane, 2)])
    g = [list(r) for r in g]
    # 羽軸（亮）、羽毛紋路（暗）
    for t in range(0, 12):
        x, y = round(14.5 - t * 0.8), round(1 + t * 0.95)
        if g[y][x] != '.':
            g[y][x] = '3'
    for (x, y) in [(11, 4), (12, 6), (10, 7), (9, 9), (13, 3)]:
        if g[y][x] in '234': g[y][x] = '4'
    # 筆桿＋筆尖
    for (x, y, c) in [(6, 12, '2'), (5, 13, '2'), (4, 14, '1'), (3, 15, '1'), (7, 12, '1'), (6, 13, '1'), (5, 12, '1'), (4, 13, '1'),
                      (5, 14, '1'), (3, 14, '1')]:
        g[y][x] = c
    # 墨點
    for (x, y) in [(1, 15), (2, 15)]:
        g[y][x] = '4'
    return [''.join(r) for r in g]


def icon_coin():
    bag = im16(ell=(1.5, 5, 14.5, 15.5))
    neck = im16(pts=[(5.5, 2), (10.5, 2), (9.5, 5.5), (6.5, 5.5)])
    g = icon_from([(bag, 1), (neck, 2)])
    g = [list(r) for r in g]
    # 綁繩、袋口、錢幣記號
    for x in range(5, 11):
        g[5][x] = '1'
    g[6][4] = '1'; g[6][11] = '1'
    for (x, y) in [(6, 1), (7, 1), (8, 1), (9, 1)]:
        g[y][x] = '1'
    for (x, y) in [(8, 8), (7, 9), (8, 10), (9, 11), (8, 12), (8, 13), (7, 12), (9, 9)]:
        g[y][x] = '3'
    return [''.join(r) for r in g]


def icon_chart():
    bars = [(im16(box=(1, 10, 4, 14)), 2), (im16(box=(6, 6, 9, 14)), 2), (im16(box=(11, 2, 14, 14)), 2)]
    g = icon_from(bars)
    g = [list(r) for r in g]
    for x in range(0, 16):
        g[15][x] = '1'
    # 長條頂端亮線
    for (x0, x1, y) in ((1, 4, 10), (6, 9, 6), (11, 14, 2)):
        for x in range(x0, x1 + 1):
            g[y][x] = '3'
    return [''.join(r) for r in g]


NAV_ICONS = {'party': icon_party, 'dice': icon_dice, 'quill': icon_quill, 'coin': icon_coin, 'chart': icon_chart}


def render_idx(rows, pal, s):
    im = Image.new('RGBA', (NI * s, NI * s))
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != '.':
                col = tuple(int(pal[int(c)][i:i + 2], 16) for i in (1, 3, 5)) + (255,)
                for yy in range(s):
                    for xx in range(s):
                        im.putpixel((x * s + xx, y * s + yy), col)
    return im


PORTRAITS = {'yulun': portrait_yulun, 'eric': portrait_eric, 'karen': portrait_karen}

if __name__ == '__main__':
    import json
    for k, f in PORTRAITS.items():
        f().image(1).save('port_%s.png' % k)
    rows = {k: f() for k, f in NAV_ICONS.items()}
    json.dump(rows, open('nav_icons.json', 'w'), ensure_ascii=False, indent=0)
    for k, r in rows.items():
        print(k); print('\n'.join(r))


POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*+-/:;<=>?@^_~'


def to_rows(im):
    """RGBA → (rows, palette)：給 index.html 的 draw() 用"""
    a = np.array(im.convert('RGBA'))
    pal, rows = {}, []
    inv = {}
    for y in range(a.shape[0]):
        r = ''
        for x in range(a.shape[1]):
            px = a[y, x]
            if px[3] < 128:
                r += '.'; continue
            key = '#%02x%02x%02x' % tuple(px[:3])
            if key not in inv:
                ch = POOL[len(inv)]
                inv[key] = ch; pal[ch] = key
            r += inv[key]
        rows.append(r)
    return rows, pal


def js_data():
    P, PP = {}, {}
    for k, f in PORTRAITS.items():
        P[k], PP[k] = to_rows(f().image(1))
    I = {k: f() for k, f in NAV_ICONS.items()}
    return P, PP, I
