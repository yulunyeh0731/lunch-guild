"""v2.2 食物圖示 32×32 重繪（不沿用 16 格舊形狀）。用 chars34.Sprite 組形狀＋自動明暗，外框用純深色（保留粗獷感）。
python3 foodhd.py → foodhd_*.png；to_rows() 轉成 index 的 FOOD/FPAL 格式。"""
import math
import numpy as np
from PIL import Image, ImageDraw
import chars34 as C

N = 32
C.R.update({
    'bowlR':  ['#5c1a17', '#a32f25', '#d2483a', '#ef7a62'],
    'porcW':  ['#8a8798', '#cdcad6', '#ecebf2', '#ffffff'],
    'broth':  ['#8a5a26', '#c99450', '#e6bd7c', '#f7e0b0'],
    'chashu': ['#6b2f1e', '#a3523a', '#cf8466', '#efb89c'],
    'yolk':   ['#a14d10', '#e4862a', '#f7b542', '#ffda8a'],
    'nori':   ['#0e1813', '#1c2e24', '#2c4636', '#44624e'],
    'scal':   ['#2a5a20', '#4c8e30', '#7cc24c', '#b6e47e'],
    'chop':   ['#6b4422', '#a8743c', '#d6a462', '#f2cf92'],
    'rice':   ['#9a96a0', '#d8d4da', '#f1eff2', '#ffffff'],
    'cutlet': ['#7a3e14', '#b8682a', '#e0973e', '#f7c36a'],
    'greens': ['#1f4a1c', '#3c7a2c', '#62a83e', '#9ad06a'],
    'tama':   ['#b07a12', '#e8b42c', '#f8d65a', '#fff09a'],
    'braise': ['#2c140a', '#5a2c14', '#8a4a22', '#b87442'],
    'radish': ['#b88a08', '#efc21a', '#fde24a', '#fff59a'],
    'blueP':  ['#1c2f5c', '#2f4f8f', '#5d82c4', '#9ab6e6'],
    'egg':    ['#5a2c12', '#8f4e22', '#b8743a', '#d8a062'],
    'kraft':  ['#6e4a26', '#a7774a', '#cfa274', '#ead0a6'],
    'fry':    ['#7c4210', '#bf7426', '#e6a446', '#f9d27e'],
    'basil':  ['#0f2a12', '#1f4a20', '#2f6a2c', '#4a8a3c'],
    'chili':  ['#6a1210', '#b0261c', '#e04a32', '#ff8a6a'],
    'bamboo': ['#7a6232', '#b89a5a', '#ddc486', '#f4e2ae'],
    'cup':    ['#7d8aa0', '#b9c6d8', '#dce6f2', '#f6faff'],
    'tea':    ['#6a3e22', '#a2683e', '#c99060', '#e6b88a'],
    'pearl':  ['#0c0806', '#22160e', '#3e2a1c', '#6a4c36'],
    'straw':  ['#7a1f3a', '#c23a5c', '#ec6a86', '#ffa6b8'],
    'salmon': ['#a33a1c', '#e0673e', '#f7925e', '#ffbe8e'],
    'tuna':   ['#5a0e1a', '#a01e30', '#d03a4a', '#f2707a'],
    'geta':   ['#4a2a14', '#7a4a26', '#a8703e', '#cf9a62'],
    'bun':    ['#8a4a14', '#c97a2c', '#eaa850', '#f8cf86'],
    'lettuce':['#2c6a1c', '#4e9a2a', '#7cc63e', '#b4ea72'],
    'cheese': ['#b8740a', '#efac1c', '#fbcc3a', '#ffe486'],
    'patty':  ['#2a140a', '#4e2814', '#74401e', '#9a5e30'],
    'redbox': ['#6a1010', '#b0201c', '#dc3a2a', '#f4705a'],
    'fries':  ['#b8820e', '#eab42a', '#f8d454', '#fff094'],
    'crepe':  ['#9a5e14', '#d4952e', '#efc05a', '#fbe08e'],
    'eggY':   ['#b88a10', '#f0c42a', '#fde060', '#fff2a6'],
    'paper':  ['#8f8a7a', '#cdc6b2', '#ebe4d0', '#fbf6e6'],
    'beefB':  ['#4a1a0c', '#7e3418', '#a85226', '#cc7a42'],
    'soupR':  ['#5a200e', '#92401c', '#bc6430', '#dc9254'],
    'bokchoy':['#1f5a1c', '#3a8a2a', '#64b440', '#a2dc78'],
    'clear':  ['#a07a3a', '#d2ac64', '#ead08e', '#f8eac0'],
    'ricen':  ['#b6b0a4', '#e2ddd2', '#f4f1ea', '#ffffff'],
    'beefP':  ['#7a2e2a', '#b85a50', '#dc8678', '#f4b0a2'],
    'lime':   ['#2a6a14', '#5aa424', '#94d046', '#d2f08a'],
    'skin':   ['#a49a86', '#ddd4c0', '#f2ecdc', '#fffaf0'],
    'soy':    ['#140a06', '#2e1a0e', '#4a2c18', '#6e4428'],
    'crisp':  ['#6e360e', '#ae6420', '#dc9a3e', '#f6c872'],
    'wrap':   ['#8a96a8', '#c4cedc', '#e2e8f0', '#f8fbff'],
    'teaG':   ['#3a5a14', '#6a8a22', '#9cb83a', '#d0e27a'],
    'lacq':   ['#1a0c0a', '#3a1612', '#5e2620', '#8a3e32'],
    'onion':  ['#a89a7a', '#d8ccae', '#eee4cc', '#fbf6e6'],
    'curry':  ['#6a3a0a', '#a8661a', '#d4952e', '#f0c060'],
    'potato': ['#a8803a', '#dcb466', '#f2d48e', '#fff0be'],
    'carrot': ['#a8400e', '#e0701e', '#f89a3a', '#ffc27a'],
    'tray':   ['#5a6272', '#8e98aa', '#bcc4d2', '#e2e8f0'],
    'tofu':   ['#b0a88e', '#e2dcc4', '#f4f0e0', '#ffffff'],
    'tomato': ['#7a1410', '#c0281c', '#e8503a', '#ff8a6a'],
    'silver': ['#525a6a', '#8e98ac', '#c6cede', '#f2f6ff'],
    'chick':  ['#b8946a', '#dcbc92', '#f0d8b4', '#fff2dc'],
    'cream':  ['#b8aea0', '#e6e0d6', '#f6f2ea', '#ffffff'],
    'sponge': ['#b88a3a', '#e2b866', '#f4d690', '#fff0c2'],
    'berry':  ['#7a0e1a', '#c41e30', '#ec4a52', '#ff8a8a'],
    'coffee': ['#1e0e06', '#3e2010', '#64381c', '#8e5a32'],
    'roast':  ['#6a2a0a', '#a8501a', '#d8822e', '#f4b24e'],
    'iron':   ['#0e0e14', '#22232c', '#3a3c48', '#5a5e6e'],
    'flame':  ['#a8200a', '#e8501a', '#f8a02a', '#ffe27a'],
    'charsiu':['#5a0e0e', '#9a1e1a', '#c84a2a', '#e8805a'],
    'duck':   ['#5a2a0e', '#9a5420', '#c88438', '#eab868'],
    'pasta':  ['#c09a3a', '#e8c86a', '#f6e09a', '#fff4cc'],
    'sauceR': ['#6a120a', '#b02a14', '#d8502a', '#f08a5a'],
    'fork':   ['#5a606e', '#9aa2b2', '#c8cedc', '#eef2f8'],
    'kelp':   ['#0a1a10', '#14301e', '#22482c', '#36643c'],
    'dtofu':  ['#4a2a10', '#7a4a20', '#a87036', '#cc9a58'],
    'fishb':  ['#a8a090', '#d8d2c2', '#eeeae0', '#ffffff'],
    'blackT': ['#08080c', '#18181f', '#2c2c36', '#46464f'],
    'sweetp': ['#9a4a14', '#d87a2a', '#f4a446', '#ffcc7a'],
    'brice':  ['#6a5440', '#9a8064', '#bca486', '#dcc8aa'],
    'board':  ['#6a4422', '#a06c3a', '#c99258', '#e6b87a'],
    'duckR':  ['#3a0c06', '#74200e', '#ac3e1a', '#d86a2c'],
    'csIn':   ['#9a4436', '#cc6e5e', '#eb9888', '#ffc4b4'],
    'chW':    ['#b0a090', '#ddd0c0', '#f4ebe0', '#fffaf2'],
    'stemW':  ['#7a9a5a', '#b4cc86', '#d8eab0', '#f2fadc'],
    'csM':    ['#a85a48', '#cc7c66', '#e09a82', '#f2bca4'],
    'cer':    ['#6a7488', '#b4bccc', '#e2e6ee', '#ffffff'],
    'roastS': ['#5e2208', '#94400e', '#c4661c', '#e69232', '#fbbf55'],
    'bone':   ['#a89878', '#d4c6a2', '#efe4c8', '#fffaec'],
    'grape':  ['#3a1440', '#6a2a6e', '#9a4a9a', '#c87ac4'],
    'mug':    ['#7a2e22', '#b4483a', '#d86a58', '#f29a86'],
})

def disc_chain(p0, r0, p1, r1, n=40):
    """兩個圓之間平滑連起來的形狀（雞腿：上粗下細）"""
    m = np.zeros((N, N), bool)
    for i in range(n + 1):
        t = i / n
        cx, cy = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        r = r0 + (r1 - r0) * t
        m |= emask((cx - r, cy - r, cx + r, cy + r))
    return m

OUTLINE = '#191322'


def sp_new():
    C.W = C.H = N
    s = C.Sprite()
    return s


def emask(box):
    im = Image.new('L', (N, N), 0)
    ImageDraw.Draw(im).ellipse(box, fill=255)
    return np.array(im) > 127


def pmask(pts):
    im = Image.new('L', (N, N), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.array(im) > 127


SEL = True     # 選擇性外框：外框用旁邊顏色的深色調（跟人物一樣），不用純黑


def finish(sp):
    sp.render()
    old = C.SELOUT
    C.SELOUT = SEL
    sp.outline()
    C.SELOUT = old
    return sp


def plate(sp, name, box, z, mat='porcW'):
    """有立體感的盤子：下方一圈厚度（暗）、盤緣（亮）、往內凹的盤心（稍暗、有陰影）"""
    x0, y0, x1, y1 = box
    sp.ell(name + 'Edge', mat, z - .2, (x0, y0 + 1.6, x1, y1 + 1.6), shade='cylv', light=-.45)
    sp.ell(name, mat, z, box, shade='cylv', light=.35)
    w, h = x1 - x0, y1 - y0
    sp.ell(name + 'Well', mat, z + .1, (x0 + w * .16, y0 + h * .2, x1 - w * .16, y1 - h * .14), shade='sphere', light=-.25, line=False)


def plate_shine(sp, name, box):
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - .8, (y1 - y0) / 2 - .6
    for a in range(200, 250, 6):
        t = math.radians(a)
        x, y = round(cx + rx * math.cos(t)), round(cy + ry * math.sin(t))
        if nm(sp, x, y) == name: sp.px(x, y, '#ffffff')


def rtri(a, b, c, r):
    """圓角三角形（飯糰）：在 8 倍解析度畫三角形，往內縮 r 再往外長 r，角就變圓"""
    from PIL import ImageFilter
    S = 8
    im = Image.new('L', (N * S, N * S), 0)
    pts = [(x * S, y * S) for x, y in (a, b, c)]
    ImageDraw.Draw(im).polygon(pts, fill=255)
    k = int(r * S) * 2 + 1
    im = im.filter(ImageFilter.MinFilter(k if k < 60 else 59))
    im = im.resize((N * S // 4, N * S // 4))
    d = Image.new('L', im.size, 0)
    import numpy as _np
    a_ = _np.array(im) > 127
    yy, xx = _np.mgrid[-int(r * 2):int(r * 2) + 1, -int(r * 2):int(r * 2) + 1]
    disk = (xx ** 2 + yy ** 2) <= (r * 2) ** 2
    out = _np.zeros_like(a_)
    for dy, dx in zip(*_np.nonzero(disk)):
        oy, ox = dy - int(r * 2), dx - int(r * 2)
        out |= _np.roll(_np.roll(a_, oy, 0), ox, 1)
    im = Image.fromarray((out * 255).astype('uint8')).resize((N, N), Image.BOX)
    return _np.array(im) > 127


def nm(sp, x, y):
    return sp.parts_sorted[sp.pid[y, x]]['name'] if 0 <= x < N and 0 <= y < N and sp.pid[y, x] >= 0 else ''


# ---------------- 拉麵 ----------------
def ramen():
    sp = sp_new()
    body = emask((2, 4, 30, 31)); body[:17] = False
    sp.mask('bowl', 'bowlR', 5, body, shade='cyl', light=.15)
    sp.mask('rim', 'porcW', 6, emask((1, 11, 31, 22)), shade='cylv', light=.3, line=False)
    sp.mask('broth', 'broth', 7, emask((3, 12.5, 29, 20.5)), shade='sphere', light=.2)
    sp.poly('nori', 'nori', 8, [(5, 6), (11, 4), (13, 15), (7, 17)], shade='cyl')
    sp.ell('chashu', 'chashu', 9, (6, 12, 15, 18), shade='sphere')
    sp.ell('egg', 'porcW', 9.5, (17, 12, 24, 18), shade='sphere', light=.2)
    sp.ell('yolk', 'yolk', 10, (18.5, 13.5, 22.5, 16.5), shade='sphere', line=False)
    sp.ell('naru', 'porcW', 9.2, (13, 15, 18, 19.5), shade='sphere', light=.3)
    finish(sp)
    # 筷子：嚴格 45 度直線，兩根平行，筷頭方正
    for (x0, y0, n) in ((18, 13, 12), (21, 14, 10)):
        for t in range(n):
            x, y = x0 + t, y0 - t
            sp.px(x, y, '#e6b878'); sp.px(x, y + 1, '#8a5a2c')
        sp.px(x0 + n - 1, y0 - n + 1, '#6b4422')
    for x in range(4, 29):                          # 碗身白色雷紋帶
        y = 24 + (1 if 7 < x < 25 else 0) - (1 if x < 5 or x > 27 else 0)
        if nm(sp, x, y) == 'bowl':
            sp.px(x, y, '#f4e6d6' if (x // 2) % 2 == 0 else '#e2c8b4')
    for x in range(7, 14):                          # 叉燒肥邊
        if nm(sp, x, 12) == 'chashu' or nm(sp, x, 13) == 'chashu':
            sp.px(x, 13, '#f6d2bc')
    sp.px(10, 15, '#7a3420'); sp.px(12, 16, '#7a3420')
    for x, y in [(15, 16), (16, 16), (16, 17), (15, 17), (14, 17)]:   # 鳴門卷漩渦
        sp.px(x, y, '#e06d8c')
    for x, y in [(20, 19), (24, 19), (26, 16), (5, 18), (11, 19), (27, 18)]:
        sp.px(x, y, '#7cc24c'); sp.px(x + 1, y, '#3f7d2a')
    sp.px(4, 15, '#fff2d0'); sp.px(5, 14, '#fff2d0')   # 湯面油光
    for k, x0 in enumerate((13, 17)):               # 蒸氣（避開筷子）
        for y in range(1 + k % 2, 10):
            x = x0 + round(math.sin(y / 1.8 + k) * 1.2)
            if sp.rgb[y, x, 3] == 0 and (y + k) % 4 != 3:
                sp.rgb[y, x] = (236, 242, 255, 200)
    return sp


# ---------------- 便當（排骨飯） ----------------
def bento():
    sp = sp_new()
    sp.poly('box', 'kraft', 4, [(1, 9), (31, 9), (30, 29), (2, 29)], shade='cyl', light=.1)
    sp.poly('inner', 'kraft', 5, [(3, 10.5), (29, 10.5), (28.5, 27.5), (3.5, 27.5)], shade='flat', light=-.35, line=False)
    sp.poly('rice', 'rice', 6, [(4, 11), (20, 11), (20, 27), (4, 27)], shade='flat', light=.15)
    sp.poly('div', 'kraft', 6.5, [(20.5, 11), (21.5, 11), (21.5, 27), (20.5, 27)], shade='flat', line=False)
    sp.poly('veg', 'greens', 7, [(22, 11), (28, 11), (28, 16), (22, 16)], shade='sphere')
    sp.poly('tama', 'tama', 7, [(22, 17), (28, 17), (28, 21.5), (22, 21.5)], shade='cyl')
    sp.poly('rad', 'radish', 7, [(22, 22.5), (28, 22.5), (28, 27), (22, 27)], shade='flat', light=.2)
    sp.poly('cutlet', 'cutlet', 8, [(5, 15), (9, 12.5), (17, 13), (20, 16), (19, 22), (14, 25), (7, 24), (4.5, 20)], shade='sphere', light=.1)
    sp.ell('egg2', 'egg', 9, (13, 19, 19, 25), shade='sphere')
    finish(sp)
    for x, y in [(6, 6), (7, 6)]:
        pass
    for x, y in [(6, 26), (9, 26), (18, 12), (5, 12), (19, 25), (12, 26)]:   # 米粒、芝麻
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#ddd8de')
    for x, y in [(8, 26), (17, 25), (5, 13)]:
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#2a1c15')
    for (x, y) in [(8, 16), (11, 15), (14, 16), (7, 19), (10, 19), (13, 18), (16, 19), (9, 22), (12, 22)]:   # 排骨的麵衣顆粒
        if nm(sp, x, y) == 'cutlet': sp.px(x, y, '#8a4a18')
    for (x, y) in [(9, 15), (12, 14), (15, 15), (8, 18)]:
        if nm(sp, x, y) == 'cutlet': sp.px(x, y, '#ffd88a')
    sp.px(15, 20, '#e8b060'); sp.px(16, 21, '#f0c070')    # 滷蛋切面
    for y in (18, 20):                                    # 玉子燒層次
        for x in range(23, 28):
            if nm(sp, x, y) == 'tama': sp.px(x, y, '#d89a1c')
    for (x, y) in [(23, 13), (25, 12), (26, 14), (24, 15)]:
        if nm(sp, x, y) == 'veg': sp.px(x, y, '#a6dc78')
    for y in (24, 26):
        for x in range(23, 28):
            if nm(sp, x, y) == 'rad': sp.px(x, y, '#d8a810')
    return sp


# ---------------- 滷肉飯 ----------------
def luroufan():
    sp = sp_new()
    body = emask((3, 6, 29, 31)); body[:18] = False
    sp.mask('bowl', 'blueP', 5, body, shade='cyl', light=.1)
    sp.mask('rim', 'porcW', 6, emask((2, 13, 30, 23)), shade='cylv', light=.3, line=False)
    rice = emask((4, 9, 28, 23)); rice[20:] = False
    sp.mask('rice', 'rice', 7, rice, shade='sphere', light=.15)
    sauce = emask((5, 9, 27, 21)) & rice; sauce[18:] = False
    sp.mask('sauce', 'braise', 8, sauce, shade='sphere', light=.2)
    sp.ell('egg', 'egg', 9, (18, 11, 26, 18), shade='sphere')
    sp.ell('yolk2', 'yolk', 9.5, (20, 13, 24, 16.5), shade='sphere', line=False)
    sp.poly('rad1', 'radish', 9, [(4, 14), (9, 12.5), (10, 15), (5, 16.5)], shade='flat', light=.1)
    sp.poly('rad2', 'radish', 9.2, [(5, 17), (10, 15.5), (11, 18), (6, 19.5)], shade='flat', light=-.1)
    finish(sp)
    for x in range(5, 28):                           # 青花碗口的藍色紋
        y = 25 + (1 if 8 < x < 24 else 0)
        if nm(sp, x, y) == 'bowl' and x % 3 != 0:
            sp.px(x, y, '#cfdcf2')
    for (x, y) in [(6, 18), (12, 19), (19, 19), (25, 18)]:   # 碗口邊露出的米粒
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#d6d2d8')
    for (x, y) in [(10, 12), (13, 14), (15, 12), (11, 16), (16, 16), (14, 18)]:   # 肥肉丁、油光
        if nm(sp, x, y) == 'sauce': sp.px(x, y, '#e8c08a')
    for (x, y) in [(9, 11), (12, 10), (17, 11)]:
        if nm(sp, x, y) == 'sauce': sp.px(x, y, '#c8884a')
    sp.px(21, 14, '#ffe2a0')
    for (x, y) in [(6, 15), (7, 18)]:
        sp.px(x, y, '#fff6b8')
    return sp


# ---------------- 鹹酥雞（紙袋＋竹籤） ----------------
def friedchicken():
    sp = sp_new()
    sp.cap('stick', 'bamboo', 3, [(20, 18), (27, 1)], .8, shade='cyl')
    sp.poly('bagB', 'kraft', 4, [(4, 14), (28, 14), (27, 31), (5, 31)], shade='cyl', light=-.1)
    chunks = [(6, 9, 13, 15), (11, 6, 18, 13), (17, 8, 24, 14), (21, 11, 28, 17), (4, 13, 10, 18), (13, 11, 20, 17)]
    for i, b in enumerate(chunks):
        sp.ell('c%d' % i, 'fry', 5 + i * .1, b, shade='sphere', light=.1)
    sp.ell('bas1', 'basil', 6, (8, 8, 12, 11), shade='sphere')
    sp.ell('bas2', 'basil', 6, (19, 11, 23, 14), shade='sphere')
    sp.poly('bagF', 'kraft', 7, [(3, 16), (29, 16), (27, 31), (5, 31)], shade='cyl', light=.15)
    finish(sp)
    for (x, y) in [(8, 11), (10, 13), (13, 8), (16, 10), (19, 10), (22, 13), (25, 14), (6, 15), (15, 13), (18, 15)]:
        if nm(sp, x, y).startswith('c'): sp.px(x, y, '#8a4a14')       # 酥脆顆粒
    for (x, y) in [(9, 10), (14, 7), (20, 9), (23, 12), (16, 12), (5, 14)]:
        if nm(sp, x, y).startswith('c'): sp.px(x, y, '#ffe29a')
    for (x, y) in [(12, 9), (24, 15), (17, 14)]:
        if nm(sp, x, y).startswith('c'): sp.px(x, y, '#e04a32')       # 辣椒粉
    for x in range(6, 27):                            # 紙袋上的紅色店標
        if nm(sp, x, 22) == 'bagF' and 9 < x < 23:
            sp.px(x, 22, '#c0473a')
    for x in range(11, 21):
        if nm(sp, x, 24) == 'bagF':
            sp.px(x, 24, '#c0473a' if x % 2 else '#e0b890')
    for y in range(17, 30):                           # 紙袋摺痕
        if nm(sp, 24, y) == 'bagF': sp.px(24, y, '#b0805a')
    return sp


# ---------------- 手搖飲 ----------------
def boba():
    sp = sp_new()
    sp.poly('cup', 'cup', 5, [(7, 7), (25, 7), (23, 31), (9, 31)], shade='cyl', light=.1)
    sp.poly('tea', 'tea', 6, [(8, 11), (24, 11), (22.4, 30), (9.6, 30)], shade='cyl', light=.05, line=False)
    sp.poly('seal', 'porcW', 7, [(7, 6), (25, 6), (25, 9), (7, 9)], shade='cylv', light=.2)
    finish(sp)
    for (x, y) in [(11, 26), (14, 27), (17, 26), (20, 27), (12, 29), (15, 29), (18, 29), (21, 29), (13, 24), (19, 24), (16, 23)]:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            if nm(sp, x + dx, y + dy) == 'tea': sp.px(x + dx, y + dy, '#22160e')
        if nm(sp, x, y) == 'tea': sp.px(x, y, '#6a4c36')
    for y in range(12, 22):                           # 奶茶漸層（上淺）
        for x in range(9, 24):
            if nm(sp, x, y) == 'tea' and 12 <= y <= 13:
                sp.px(x, y, '#dcb28a')
    for y in range(10, 29):                           # 杯身反光
        if nm(sp, 10, y) in ('tea', 'cup') and y % 7 != 6:
            sp.px(10, y, '#f8ecdc')
    for x in range(8, 25):                            # 封膜上的圖案
        if x % 4 == 1 and nm(sp, x, 7) == 'seal': sp.px(x, 7, '#e0674a')
    for (x, y) in [(23, 13), (22, 18)]:              # 水珠
        sp.px(x, y, '#ffffff')
    for x in range(9, 24):                            # 水面奶泡線
        if nm(sp, x, 11) == 'tea': sp.px(x, 11, '#f2dcc0')
    # 吸管：一整根直線，從杯底 (12,29) 往上到杯外 (19,0)，每 4 列往右 1 格
    for y in range(0, 30):
        x0 = 12 + (29 - y) // 4
        if y <= 6:                                   # 杯外：鮮豔＋外框
            cols = ['#ffa6b8', '#ec6a86', '#b83456']
            sp.px(x0 - 1, y, '#5a1428'); sp.px(x0 + 3, y, '#5a1428')
        elif y <= 9:                                 # 穿過封膜那段
            cols = ['#e88aa0', '#c94c6a', '#8e2a46']
        else:                                        # 杯內：隔著奶茶，顏色變暗
            cols = ['#c78a8e', '#a8606c', '#7e4250']
        for i, cc in enumerate(cols):
            sp.px(x0 + i, y, cc)
    sp.px(19, 0, '#5a1428'); sp.px(20, 0, '#5a1428'); sp.px(21, 0, '#5a1428')
    for (x, y) in [(17, 8), (21, 8)]:                 # 封膜破口
        if nm(sp, x, y) == 'seal': sp.px(x, y, '#9a96a8')
    return sp


# ---------------- 壽司（木屐盤上兩貫） ----------------
def sushi():
    sp = sp_new()
    sp.poly('geta', 'geta', 3, [(1, 22), (31, 22), (31, 26), (1, 26)], shade='cylv', light=.1)
    sp.poly('leg1', 'geta', 2, [(4, 26), (8, 26), (8, 29), (4, 29)], shade='flat', light=-.3)
    sp.poly('leg2', 'geta', 2, [(24, 26), (28, 26), (28, 29), (24, 29)], shade='flat', light=-.3)
    sp.ell('riceA', 'rice', 5, (2, 13, 13, 23), shade='sphere', light=.15)
    sp.ell('riceB', 'rice', 5, (14, 13, 25, 23), shade='sphere', light=.15)
    sp.poly('salmon', 'salmon', 6, [(1, 13), (5, 9), (12, 9.5), (14, 13), (13, 17), (2, 17)], shade='cylv', light=.15)
    sp.poly('tuna', 'tuna', 6, [(13.5, 13), (17, 9.5), (24, 9), (26.5, 13), (25.5, 17), (14.5, 17)], shade='cylv', light=.15)
    sp.ell('wasabi', 'scal', 7, (26, 18, 31, 22.5), shade='sphere', light=.1)
    sp.ell('gari', 'chashu', 6.8, (25.5, 15.5, 30.5, 19.5), shade='sphere', light=.4)
    finish(sp)
    for k in range(4):                               # 鮭魚油花
        for t in range(6):
            x, y = 3 + k * 3 + t // 2, 10 + t
            if nm(sp, x, y) == 'salmon': sp.px(x, y, '#ffe2cc')
    for (x, y) in [(17, 11), (21, 12), (24, 14), (19, 15)]:   # 鮪魚光澤
        if nm(sp, x, y) == 'tuna': sp.px(x, y, '#f7a0a8')
    for (x, y) in [(4, 19), (8, 20), (11, 19), (6, 21), (16, 19), (20, 20), (23, 19), (18, 21)]:
        if nm(sp, x, y).startswith('rice'): sp.px(x, y, '#d6d2d8')
    sp.px(27, 19, '#c8f09a'); sp.px(28, 16, '#ffe0d4')   # 山葵、薑片亮點
    for x in range(2, 31, 5):
        sp.px(x, 24, '#5a3418')
    return sp



# ================= 第二組 =================
def mcd():
    """速食：漢堡＋紅盒薯條（不放任何品牌標誌）"""
    sp = sp_new()
    sp.poly('box', 'redbox', 4, [(19, 13), (30, 13), (28.5, 29), (20.5, 29)], shade='cyl', light=.1)
    for i, (x, top) in enumerate([(20, 6), (22, 4), (24, 5), (26, 3), (28, 6), (21, 8), (25, 7), (27, 8)]):
        sp.poly('f%d' % i, 'fries', 3 + i * .05, [(x, top), (x + 1.6, top), (x + 1.6, 16), (x, 16)], shade='cyl')
    sp.ell('bunB', 'bun', 6, (1, 22, 21, 30), shade='cylv', light=.1)
    sp.poly('patty', 'patty', 7, [(1.5, 20), (20.5, 20), (20, 24), (2, 24)], shade='cylv')
    sp.poly('cheese', 'cheese', 8, [(1, 18.5), (21, 18.5), (18, 22.5), (13, 20.5), (8, 23), (3, 20.5)], shade='flat', light=.15)
    sp.poly('let', 'lettuce', 8.5, [(0.5, 17), (21.5, 17), (20, 19.5), (16, 18.5), (11, 20), (6, 18.5), (2, 19.5)], shade='cylv', light=.1)
    top = emask((1, 6, 21, 25)); top[18:] = False
    sp.mask('bunT', 'bun', 9, top, shade='sphere', light=.1)
    finish(sp)
    for (x, y) in [(6, 10), (10, 9), (14, 10), (8, 13), (12, 12), (16, 13), (5, 14)]:    # 芝麻
        if nm(sp, x, y) == 'bunT': sp.px(x, y, '#fff2c8')
    sp.px(6, 9, '#ffe2a0'); sp.px(7, 9, '#ffe2a0')
    for y in range(17, 28):                                  # 薯條盒的白色線
        x = 24 + (0 if y < 24 else 0)
        if nm(sp, x, y) == 'box' and y % 2: sp.px(x, y, '#f4b0a0')
    return sp


def breakfast():
    """早餐店：蛋餅切段（看得到捲起來的切面）淋醬油膏＋一杯奶茶"""
    sp = sp_new()
    sp.poly('cup', 'paper', 4, [(21, 4), (30, 4), (29, 18), (22, 18)], shade='cyl', light=.1)
    sp.poly('lid', 'paper', 5, [(20, 2), (31, 2), (31, 5), (20, 5)], shade='cylv', light=.25)
    plate(sp, 'plate', (0, 17, 28, 29), 6)
    pos = [(4, 14), (10.5, 13), (17, 14)]
    for i, (x, y) in enumerate(pos):
        sp.ell('roll%d' % i, 'crepe', 7 + i * .1, (x, y, x + 8, y + 9), shade='sphere', light=.1)
        sp.ell('egg%d' % i, 'eggY', 7.5 + i * .1, (x + 2, y + 2, x + 6, y + 7), shade='flat', light=.15, line=False)
    finish(sp)
    for i, (x, y) in enumerate(pos):                       # 捲起來的切面：一圈螺旋線＋蔥花
        x = int(x)
        for (dx, dy) in [(4, 3), (5, 4), (5, 5), (4, 6), (3, 5), (3, 4)]:
            sp.px(x + dx, y + dy, '#c88a2a')
        sp.px(x + 6, y + 6, '#7cc24c'); sp.px(x + 2, y + 7, '#4c8e30')
    for t in range(0, 21):                                 # 醬油膏（之字形淋在上面）
        x = 5 + t; y = 14 + (t % 4 if t % 8 < 4 else 4 - t % 4) // 2
        if nm(sp, x, y).startswith('roll') or nm(sp, x, y).startswith('egg'):
            sp.px(x, y, '#3a1e10')
    for x in range(22, 30):                                # 杯子上的紅條紋
        if nm(sp, x, 9) == 'cup': sp.px(x, 9, '#d0473a')
        if nm(sp, x, 11) == 'cup': sp.px(x, 11, '#d0473a')
    plate_shine(sp, 'plate', (0, 17, 28, 29))
    return sp


def twnoodle():
    """台式麵店：紅燒牛肉麵＋湯匙"""
    sp = sp_new()
    body = emask((2, 4, 30, 31)); body[:17] = False
    sp.mask('bowl', 'porcW', 5, body, shade='cyl', light=.1)
    sp.mask('rim', 'porcW', 6, emask((1, 11, 31, 22)), shade='cylv', light=.4, line=False)
    sp.mask('soup', 'soupR', 7, emask((3, 12.5, 29, 20.5)), shade='sphere', light=.15)
    for i, pts in enumerate([[(5, 13), (9, 11.5), (13, 12.5), (13, 16.5), (9, 18), (5, 16.5)],
                             [(11, 15), (15, 13.5), (19, 14.5), (19, 18.5), (15, 20), (11, 18.5)],
                             [(15.5, 12), (19, 10.5), (22.5, 11.5), (22.5, 15), (19, 16.5), (15.5, 15)]]):
        sp.poly('beef%d' % (i + 1), 'beefB', 8 + i * .1, pts, shade='flat', light=0)
    sp.poly('bok', 'bokchoy', 9, [(21, 15), (27, 11.5), (28.5, 14.5), (23, 18.5)], shade='cyl')
    sp.poly('bok2', 'bokchoy', 9.1, [(22, 12.5), (26, 10), (27, 12), (23.5, 14.5)], shade='cyl', light=.3)
    sp.ell('suan', 'lettuce', 8.5, (6, 17, 11, 20), shade='sphere', light=-.2)
    finish(sp)
    for x in range(4, 29):                                   # 碗身紅色回紋
        y = 25 + (1 if 7 < x < 25 else 0)
        if nm(sp, x, y) == 'bowl': sp.px(x, y, '#c0473a' if (x // 2) % 2 == 0 else '#e8b4a8')
    for (x, y) in [(7, 18), (10, 19), (14, 12), (24, 19), (4, 16), (27, 17)]:    # 麵條、蔥花、油花
        if nm(sp, x, y) == 'soup': sp.px(x, y, '#f0d08a')
    for (x, y) in [(5, 15), (9, 13), (19, 18), (26, 18)]:
        if nm(sp, x, y) in ('soup', 'beef1', 'beef2'): sp.px(x, y, '#7cc24c')
    for i, (x0, y0) in enumerate([(5, 11), (11, 13), (15, 10)]):     # 方塊：上面亮、右側暗、一條半透明牛筋
        name = 'beef%d' % (i + 1)
        for x in range(x0, x0 + 9):
            for y in range(y0, y0 + 9):
                if nm(sp, x, y) != name: continue
                top = y < y0 + 3 + (1 if x > x0 + 4 else 0)
                right = x >= x0 + 5 and not top
                sp.px(x, y, '#c0703a' if top else ('#6a2a12' if right else '#94461e'))
        sp.px(x0 + 2, y0 + 4, '#e6c49a'); sp.px(x0 + 3, y0 + 5, '#e6c49a'); sp.px(x0 + 4, y0 + 5, '#d4a878')
    for (x, y) in [(23, 14), (25, 12), (26, 14)]:              # 青江菜梗（白綠色）
        if nm(sp, x, y).startswith('bok'): sp.px(x, y, '#dcefc0')
    for k, x0 in enumerate((9, 15, 21)):                       # 蒸氣
        for y in range(2 + k % 2, 10):
            x = x0 + round(math.sin(y / 1.8 + k) * 1.2)
            if sp.rgb[y, x, 3] == 0 and (y + k) % 4 != 3:
                sp.rgb[y, x] = (236, 242, 255, 200)
    return sp


def pho():
    """越南河粉：寬口碗、清湯、粉條、生牛肉片、香草、檸檬角、辣椒"""
    sp = sp_new()
    body = emask((1, 8, 31, 31)); body[:18] = False
    sp.mask('bowl', 'porcW', 5, body, shade='cyl', light=.1)
    sp.mask('rim', 'porcW', 6, emask((0, 11, 32, 24)), shade='cylv', light=.4, line=False)
    sp.mask('broth', 'clear', 7, emask((2, 12.5, 30, 22.5)), shade='sphere', light=.25)
    sp.ell('beefA', 'beefP', 8, (5, 13, 13, 18), shade='sphere', light=.1)
    sp.ell('beefB2', 'beefP', 8.1, (11, 15, 19, 20), shade='sphere', light=.1)
    sp.poly('herb', 'lettuce', 9, [(18, 13), (23, 11), (25, 14), (21, 17)], shade='sphere')
    sp.poly('herb2', 'basil', 9.1, [(14, 12), (18, 10.5), (19, 13), (16, 14.5)], shade='sphere', light=.3)
    sp.poly('lime', 'lime', 10, [(23, 16), (29, 13), (28, 18)], shade='flat', light=.15)
    finish(sp)
    for x in range(3, 30):                                   # 碗口綠色細線
        if nm(sp, x, 23 + (1 if 6 < x < 26 else 0)) == 'bowl': sp.px(x, 23 + (1 if 6 < x < 26 else 0), '#5aa45a')
    for (x, y) in [(4, 19), (8, 20), (20, 20), (25, 19), (6, 16), (15, 19)]:     # 河粉
        if nm(sp, x, y) == 'broth': sp.px(x, y, '#fbf8f0')
    for (x, y) in [(7, 15), (9, 14), (13, 17), (15, 16)]:     # 牛肉紋路
        if nm(sp, x, y).startswith('beef'): sp.px(x, y, '#f6c2b4')
    for (x, y) in [(20, 19), (10, 21), (26, 21)]:            # 辣椒圈
        sp.px(x, y, '#e03a2a'); sp.px(x + 1, y, '#a8201a')
    sp.px(26, 15, '#eaffb0'); sp.px(25, 16, '#eaffb0')
    for (x, y) in [(3, 17), (27, 20)]:                       # 豆芽
        sp.px(x, y, '#fffbe6'); sp.px(x + 1, y + 1, '#fffbe6')
    return sp


def dumpling():
    """水餃：一盤半月形水餃（有厚度的盤子）＋右後方一碟醬油（不疊在盤子上）"""
    sp = sp_new()
    plate(sp, 'dish', (22, 6, 32, 13), 2)
    sp.ell('sauce', 'soy', 2.5, (24, 7.5, 30, 11), shade='sphere', light=.3, line=False)
    plate(sp, 'plate', (0, 14, 30, 29), 4)
    pos = [(2, 11), (10.5, 10), (19, 11.5), (5.5, 17), (14.5, 17.5)]
    for i, (x, y) in enumerate(pos):
        d = emask((x, y, x + 10, y + 14)); d[int(y + 7):] = False
        sp.mask('d%d' % i, 'skin', 6 + i * .3, d, shade='sphere', light=.2)
    finish(sp)
    for i, (x, y) in enumerate(pos):
        x, y = int(x), int(y)
        for xx in range(x, x + 12):
            col = [yy for yy in range(y, y + 9) if nm(sp, xx, yy) == 'd%d' % i]
            if col:
                sp.px(xx, col[0], '#b4a98e' if xx % 2 else '#efe6d2')
                sp.px(xx, col[-1], '#9a907a')                  # 下緣深色線，跟後面那顆分開
                for yy in col:                                 # 被別顆擋住的交界也描一條
                    for dx in (-1, 1):
                        o = nm(sp, xx + dx, yy)
                        if o[:1] == 'd' and o[1:].isdigit() and int(o[1:]) > i:
                            sp.px(xx, yy, '#9a907a')
    sp.px(26, 9, '#c0392b'); sp.px(27, 9, '#e0503a'); sp.px(28, 10, '#c0392b')   # 辣油
    plate_shine(sp, 'plate', (0, 14, 30, 29))
    return sp


def potsticker():
    """鍋貼：側面看，長條狀、上緣一排摺痕、底部煎得金黃焦脆，三條斜斜排在盤上"""
    sp = sp_new()
    plate(sp, 'plate', (0, 15, 32, 29.5), 3)
    pos = [(2, 8), (8, 12), (13, 17)]
    for i, (x, y) in enumerate(pos):
        sp.ell('p%d' % i, 'skin', 5 + i, (x, y, x + 18, y + 9), shade='cylv', light=.25)
    finish(sp)
    for i, (x, y) in enumerate(pos):
        mine = lambda xx, yy: nm(sp, xx, yy) == 'p%d' % i
        for xx in range(x, x + 19):
            col = [yy for yy in range(y, y + 10) if mine(xx, yy)]
            if not col: continue
            top, bot = col[0], col[-1]
            if xx % 2 == 0 and 2 < xx - x < 16: sp.px(xx, top + 1, '#bdb39a')   # 上緣摺痕
            for k, cc in enumerate(('#7e3c0e', '#b0621c', '#dc9a3e')):          # 底部焦脆
                if bot - k > top + 2: sp.px(xx, bot - k, cc)
        sp.px(x + 4, y + 3, '#fffaf0'); sp.px(x + 5, y + 3, '#fffaf0')            # 麵皮反光
    plate_shine(sp, 'plate', (0, 15, 32, 29.5))
    return sp

# ================= 第三組 =================
def convenience():
    """便利商店：三角飯糰（包裝膜＋海苔）＋一瓶綠茶（不放品牌）"""
    sp = sp_new()
    sp.poly('bottle', 'teaG', 3, [(21, 8), (28, 8), (28, 29), (21, 29)], shade='cyl', light=.1)
    sp.poly('neck', 'teaG', 3.1, [(22.5, 5), (26.5, 5), (27.5, 8.5), (21.5, 8.5)], shade='cyl')
    sp.poly('cap', 'porcW', 3.2, [(22.5, 2), (26.5, 2), (26.5, 5), (22.5, 5)], shade='cyl', light=.2)
    sp.poly('label', 'porcW', 3.3, [(21, 15), (28, 15), (28, 22), (21, 22)], shade='cyl', light=.1)
    sp.mask('rice', 'rice', 5, rtri((12.5, 6.5), (-1, 30), (26, 30), 2.6), shade='sphere', light=.15)
    sp.poly('nori', 'nori', 6, [(8, 20), (17, 20), (17, 30), (8, 30)], shade='cyl')
    finish(sp)
    for (x, y) in [(10, 12), (13, 16), (9, 18), (15, 13), (12, 10)]:     # 米粒
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#dcd8de')
    for y in range(13, 22):                                                # 包裝膜反光
        x = 10 - (y - 13) // 2
        if nm(sp, x, y) == 'rice' and y % 5 != 4: sp.px(x, y, '#ffffff')
    for y in range(10, 29):                                                # 包裝上的紅色撕開條（直的，從頂端拉下來）
        if nm(sp, 12, y) in ('rice', 'nori'): sp.px(12, y, '#d0473a')
    for x in range(22, 28):                                                # 標籤上的綠葉圖案
        if nm(sp, x, 18) == 'label' and x % 2: sp.px(x, 18, '#6a8a22')
    for y in range(9, 28):
        if nm(sp, 22, y) in ('bottle', 'label'): sp.px(22, y, '#e6f0b8' if y % 6 else '#ffffff')
    return sp


def donburi():
    """丼飯：黑漆朱紅碗，白飯上鋪一片一片的牛肉（每片有外框分開）＋洋蔥＋紅薑＋蛋黃"""
    sp = sp_new()
    body = emask((2, 4, 30, 31)); body[:17] = False
    sp.mask('bowl', 'lacq', 5, body, shade='cyl', light=.15)
    sp.mask('rim', 'redbox', 6, emask((1, 11, 31, 22)), shade='cylv', light=.1, line=False)
    top = emask((3, 7, 29, 21)); top[19:] = False
    sp.mask('rice', 'rice', 7, top, shade='sphere', light=.15)
    slices = [[(4, 12.5), (10, 9.5), (15, 10.5), (13, 14.5), (6, 16)],
              [(14, 8.5), (20, 7.5), (26, 9.5), (23, 13), (16, 13)],
              [(8, 15), (14, 12.5), (21, 13.5), (19, 17.5), (11, 18.5)],
              [(19, 14.5), (24, 12), (28.5, 13.5), (26.5, 17.5), (21, 18.5)]]
    for i, pts in enumerate(slices):
        sp.poly('s%d' % i, 'chashu', 8 + i * .2, pts, shade='cylv', light=.25 if i % 2 else .05)
    sp.ell('ginger', 'chili', 9.5, (5, 15.5, 10, 19), shade='sphere', light=.3)
    sp.ell('yolk', 'yolk', 9.6, (13, 10.5, 17.5, 14.5), shade='sphere', light=.1)
    finish(sp)
    for i, pts in enumerate(slices):                     # 每片中間一條油花
        cx = int(sum(p[0] for p in pts) / len(pts)); cy = int(sum(p[1] for p in pts) / len(pts))
        for t in (-1, 0, 1):
            if nm(sp, cx + t, cy) == 's%d' % i: sp.px(cx + t, cy, '#f4d6bc')
    for (x, y) in [(11, 16), (22, 15), (8, 12)]:          # 洋蔥絲
        for t in range(2):
            if nm(sp, x + t, y).startswith('s'): sp.px(x + t, y, '#f8eccf')
    for (x, y) in [(19, 15), (25, 12), (7, 14), (16, 9)]:
        if nm(sp, x, y).startswith('s'): sp.px(x, y, '#7cc24c')
    for x in range(4, 29):                                # 碗身金色細線
        y = 25 + (1 if 7 < x < 25 else 0)
        if nm(sp, x, y) == 'bowl': sp.px(x, y, '#c9a24e')
    sp.px(14, 11, '#ffe6a0')
    return sp


def curry():
    """咖哩：橢圓盤，一半白飯一半咖哩（馬鈴薯、紅蘿蔔、肉塊）＋福神漬"""
    sp = sp_new()
    plate(sp, 'plate', (0, 9, 32, 28), 3)
    sp.ell('rice', 'rice', 5, (2.5, 10.5, 17.5, 24.5), shade='sphere', light=.15)
    pts = []
    for k in range(28):                                   # 邊緣有起伏的一灘咖哩，左邊流到飯的邊上
        a = k / 28 * math.tau
        r = 1 + .13 * math.sin(a * 3 + 1) + .08 * math.sin(a * 5)
        rx, ry = (10.5 if math.cos(a) > 0 else 8.5), 7.2
        pts.append((19.5 + math.cos(a) * rx * r, 19 + math.sin(a) * ry * r))
    sauce = pmask(pts) | pmask([(11, 22), (15, 19), (16, 26), (12, 27)])
    sp.mask('curry', 'curry', 6, sauce, shade='sphere', light=.15)
    sp.ell('pot1', 'potato', 7, (16, 14, 21, 18.5), shade='sphere')
    sp.ell('car1', 'carrot', 7, (23, 16, 27, 19.5), shade='sphere')
    sp.ell('meat', 'beefB', 7, (18, 19.5, 23, 23.5), shade='sphere')
    sp.ell('pot2', 'potato', 7, (24, 21, 28, 24.5), shade='sphere')
    sp.ell('fuku', 'chili', 7.5, (4, 21, 8.5, 24.5), shade='sphere', light=.2)
    finish(sp)
    for (x, y) in [(6, 14), (9, 13), (12, 15), (7, 18), (11, 19)]:
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#dcd8de')
    for (x0, y0, n) in [(13, 16, 3), (22, 13, 4), (15, 23, 3), (25, 22, 3)]:   # 弧形的油光，有流動感
        for t in range(n):
            x, y = x0 + t, y0 + (1 if t == n - 1 else 0) - (1 if t == 0 else 0)
            if nm(sp, x, y) == 'curry': sp.px(x, y, '#f8d27a')
    plate_shine(sp, 'plate', (0, 9, 32, 28))
    return sp


def buffet():
    """自助餐：分格餐盤，白飯＋三樣菜（青菜、滷雞腿、番茄炒蛋）＋滷豆腐"""
    sp = sp_new()
    sp.poly('trayE', 'tray', 2.8, [(1, 9.5), (31, 9.5), (30, 30.5), (2, 30.5)], shade='flat', light=-.4)
    sp.poly('tray', 'tray', 3, [(1, 8), (31, 8), (30, 29), (2, 29)], shade='cylv', light=.25)
    cells = {'c1': [(3, 10), (15, 10), (15, 19), (3, 19)], 'c2': [(17, 10), (29, 10), (29, 19), (17, 19)],
             'c3': [(3.5, 21), (11, 21), (11, 27.5), (4, 27.5)], 'c4': [(13, 21), (20, 21), (20, 27.5), (13, 27.5)],
             'c5': [(22, 21), (28.5, 21), (28, 27.5), (22, 27.5)]}
    for k, pts in cells.items():
        sp.poly(k, 'tray', 4, pts, shade='flat', light=-.15, line=False)
    sp.ell('rice', 'rice', 5, (4, 10.5, 14.5, 18.5), shade='sphere', light=.15)
    sp.ell('leg', 'egg', 5, (18, 11, 28, 18), shade='sphere', light=.1)
    sp.cap('bone', 'porcW', 5.1, [(25, 12.5), (28.5, 10.5)], .9, shade='cyl')
    sp.ell('veg', 'greens', 5, (4.5, 21.5, 10.5, 27), shade='sphere')
    sp.ell('tom', 'tomato', 5, (13.5, 21.5, 19.5, 27), shade='sphere', light=.1)
    sp.poly('tofu', 'braise', 5, [(23, 22), (27.5, 22), (27.5, 26.5), (23, 26.5)], shade='cyl', light=.6)
    finish(sp)
    for (x, y) in [(7, 13), (10, 12), (12, 15), (6, 16)]:
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#dcd8de')
    for (x, y) in [(15, 23), (17, 25), (14, 25)]:                          # 番茄炒蛋裡的蛋
        if nm(sp, x, y) == 'tom': sp.px(x, y, '#fbd44a')
    for (x, y) in [(20, 13), (22, 12), (24, 15)]:                          # 雞腿滷汁光澤
        if nm(sp, x, y) == 'leg': sp.px(x, y, '#e6a868')
    for (x, y) in [(6, 23), (8, 25), (9, 22)]:
        if nm(sp, x, y) == 'veg': sp.px(x, y, '#a6dc78')
    return sp


def feast():
    """大餐：銀色餐蓋。蓋緣是跟盤子一樣透視的橢圓弧（不是直線）"""
    sp = sp_new()
    plate(sp, 'plate', (0, 19, 32, 30), 3)
    dome = emask((2, 7, 30, 37)); dome[22:] = False
    dome |= emask((2, 18, 30, 26.5))                       # 下緣用橢圓補成弧形
    sp.mask('dome', 'silver', 5, dome, shade='sphere', light=.15)
    sp.ell('knob', 'silver', 6, (13.5, 4, 18.5, 8.5), shade='sphere', light=.35)
    sp.poly('stem', 'silver', 5.8, [(15, 8), (17, 8), (17, 9.5), (15, 9.5)], shade='flat', light=-.5)
    finish(sp)
    ramp = ['#454c5c', '#6c7588', '#959fb2', '#bcc5d6', '#dfe6f2', '#f6f9ff']
    L = (-.68, -.48, .55)
    rimTop = emask((2, 18, 30, 26.5)); rimIn = emask((3.5, 18.5, 28.5, 25))
    for y in range(N):
        for x in range(N):
            if nm(sp, x, y) != 'dome': continue
            nx, ny = (x + .5 - 16) / 14.5, (min(y, 22) + .5 - 22) / 15
            nz = max(0., 1 - nx * nx - ny * ny) ** .5
            d = max(0., nx * L[0] + ny * L[1] + nz * L[2])
            col = ramp[min(5, int(d * 5.4))]
            if nx > .8: col = ramp[1]
            if rimTop[y, x] and not rimIn[y, x] and y > 21:              # 蓋緣的一圈厚邊（沿著橢圓）
                col = '#eef2fa' if x < 16 else '#9aa4b6'
                if y >= 25 or (y >= 24 and (x < 6 or x > 26)): col = '#6c7588'
            sp.px(x, y, col)
    for x in range(12, 21):
        for y in (8, 9):
            if nm(sp, x, y) == 'dome': sp.px(x, y, '#6c7588')
    for (x, y) in [(7, 13), (6, 14), (6, 15), (8, 12), (9, 11)]:
        if nm(sp, x, y) == 'dome': sp.px(x, y, '#ffffff')
    for (cx, cy) in [(28, 6), (4, 4)]:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            sp.rgb[cy + dy, cx + dx] = (255, 244, 200, 255) if (dx, dy) != (0, 0) else (255, 255, 255, 255)
    return sp


def healthy():
    """健康餐：黑色塑膠分格餐盒（糙米飯、雞胸肉片、花椰菜、地瓜、水煮蛋、小番茄）"""
    sp = sp_new()
    sp.poly('boxE', 'blackT', 2.8, [(1, 8.5), (31, 8.5), (30, 30.5), (2, 30.5)], shade='flat', light=-.3)
    sp.poly('box', 'blackT', 3, [(1, 7), (31, 7), (30, 29), (2, 29)], shade='cylv', light=.35)
    sp.poly('c1', 'blackT', 4, [(3, 9), (16, 9), (16, 27), (3.5, 27)], shade='flat', light=-.1, line=False)
    sp.poly('c2', 'blackT', 4, [(18, 9), (29, 9), (28.5, 17), (18, 17)], shade='flat', light=-.1, line=False)
    sp.poly('c3', 'blackT', 4, [(18, 19), (28.5, 19), (28, 27), (18, 27)], shade='flat', light=-.1, line=False)
    sp.poly('brice', 'brice', 5, [(3.5, 18), (15.5, 18), (15.5, 26.5), (4, 26.5)], shade='sphere', light=.2)
    sp.mask('ch0', 'roast', 5, disc_chain((6.5, 13.5), 3.2, (13, 13), 3.8), shade='sphere', light=.45)
    sp.ell('broc1', 'bokchoy', 5, (18.5, 9.5, 23.5, 14), shade='sphere')
    sp.ell('broc2', 'bokchoy', 5.1, (22.5, 11, 28, 16.5), shade='sphere', light=.1)
    sp.ell('sp1', 'sweetp', 5, (18.5, 19.5, 23.5, 23.5), shade='sphere')
    sp.ell('sp2', 'sweetp', 5.1, (20, 22.5, 25, 26.5), shade='sphere', light=-.1)
    sp.ell('egg', 'porcW', 5.2, (23, 19.5, 28, 24.5), shade='sphere', light=.2)
    sp.ell('yolk', 'yolk', 5.3, (24.3, 20.8, 26.8, 23.2), shade='sphere', line=False)
    sp.ell('tom', 'tomato', 5.4, (24.5, 23.5, 28, 27), shade='sphere', light=.1)
    finish(sp)
    for y in range(N):                                                      # 雞胸上斜斜的烤痕
        for x in range(N):
            if nm(sp, x, y) == 'ch0' and (x + y) % 4 == 0: sp.px(x, y, '#7a3610')
    for (x, y) in [(6, 11), (7, 11), (9, 10)]:
        if nm(sp, x, y) == 'ch0': sp.px(x, y, '#ffe0a0')
    for (x, y) in [(6, 20), (9, 22), (12, 20), (7, 24), (13, 25), (10, 19)]:   # 糙米顆粒
        if nm(sp, x, y) == 'brice': sp.px(x, y, '#e6d4b4' if (x + y) % 2 else '#7a6048')
    for (x, y) in [(19, 10), (23, 12), (24, 13)]:
        if nm(sp, x, y).startswith('broc'): sp.px(x, y, '#9ad06a')
    for (x, y) in [(20, 20), (21, 23)]:
        if nm(sp, x, y).startswith('sp'): sp.px(x, y, '#ffe0a0')
    return sp

# ================= 第四組 =================
def coffee():
    """咖啡：貴族風白瓷咖啡杯（金邊、藍色垂墜花紋）配藍邊金線杯盤，裝黑咖啡。杯底弧形；杯把中間鏤空"""
    sp = sp_new()
    cx, ry_k = 14.8, .32
    # 杯盤
    sp.ell('sEdge', 'cer', 1, (0.5, 21, 31.5, 31), shade='flat')
    sp.ell('saucer', 'cer', 1.1, (0.5, 19.5, 31.5, 29.5), shade='flat')
    # 杯身：一圈一圈的橫切面（橢圓）疊起來，所以杯底自然是弧形
    def hw(t): return 4.8 + 5.9 * math.cos(t * math.pi / 2) ** .55
    y0, y1 = 8.3, 21.3
    body = np.zeros((N, N), bool)
    for i in range(101):
        t = i / 100; yc = y0 + (y1 - y0) * t; w = hw(t)
        body |= emask((cx - w, yc - w * ry_k, cx + w, yc + w * ry_k))
    for yc in np.arange(y1, 23.6, .25):                                     # 杯腳
        body |= emask((cx - 5.2, yc - 1.6, cx + 5.2, yc + 1.6))
    rx0 = hw(0)
    rim = emask((cx - rx0, y0 - rx0 * ry_k, cx + rx0, y0 + rx0 * ry_k))
    # 杯把：耳朵形的圈，中間是空的
    hdl = emask((21, 10.2, 29.6, 20.4)) & ~emask((23.6, 12.6, 27.2, 18))
    sp.mask('handle', 'cer', 2, hdl, shade='flat')
    sp.mask('cup', 'cer', 3, body, shade='flat')
    finish(sp)
    P = lambda x, y, c: sp.px(x, y, c)
    WR = ['#7c8298', '#a6acc0', '#ccd1df', '#e8ebf3', '#ffffff']
    BL = ['#4a64a0', '#6a88c8', '#8eaae0', '#b4caf0']
    GD = ['#8a6420', '#c49a3a', '#ecc860']
    # 杯盤：外圈藍色、金邊，中間白色，杯子底下有陰影
    inner = emask((5, 21.4, 27, 27.6))
    shadow = emask((6.8, 22.2, 23.4, 27.8))
    for y in range(N):
        for x in range(N):
            n = nm(sp, x, y)
            if n == 'sEdge': P(x, y, WR[1] if x > 6 else WR[2])
            elif n == 'saucer':
                if not inner[y, x]:
                    edge = nm(sp, x, y - 1) != 'saucer' or nm(sp, x - 1, y) not in ('saucer',) or nm(sp, x + 1, y) not in ('saucer',)
                    if edge: P(x, y, GD[2] if x < 16 else GD[1])
                    else: P(x, y, BL[2] if x < 12 else (BL[1] if x < 24 else BL[0]))
                else:
                    P(x, y, ('#8a92aa' if shadow[y, x] and y >= 24 else ('#b0b8cc' if shadow[y, x] else (WR[4] if x < 13 and y < 24 else WR[3]))))
    # 杯身亮暗：左前方打光，越靠右、越靠杯底越暗
    rows = {}
    for y in range(N):
        xs = [x for x in range(N) if nm(sp, x, y) == 'cup']
        if xs: rows[y] = (min(xs), max(xs))
    for y, (a, b) in rows.items():
        c, w = (a + b) / 2, max(1, (b - a) / 2)
        for x in range(a, b + 1):
            if nm(sp, x, y) != 'cup': continue
            u = (x + .5 - c) / (w + .5)
            nz = max(0, 1 - u * u) ** .5
            d = .55 * nz - .5 * u + .3 - (.18 if y >= 20 else 0)
            P(x, y, WR[max(0, min(4, int(d * 3.6 + .5)))])
        hx = int(round(c - w * .5))
        if 12 <= y <= 19 and nm(sp, hx, y) == 'cup': P(hx, y, '#ffffff')
    for x in range(N):                                                      # 杯腳和杯身的交界
        if abs(x + .5 - cx) < 5:
            y = int(round(21.3 + 1.5 * (1 - ((x + .5 - cx) / 5) ** 2) ** .5))
            if nm(sp, x, y) == 'cup': P(x, y, WR[1] if x > cx - 2 else WR[2])
    # 杯口：金邊＋裡面的黑咖啡
    opening = emask((cx - rx0 + 1, y0 - rx0 * ry_k + .8, cx + rx0 - 1, y0 + rx0 * ry_k - .8))
    coffee = emask((cx - rx0 + 1.6, y0 - rx0 * ry_k + 2.2, cx + rx0 - 1.6, y0 + rx0 * ry_k + .2)) & opening
    for y in range(N):
        for x in range(N):
            if nm(sp, x, y) != 'cup' or not rim[y, x]: continue
            if not opening[y, x]: P(x, y, GD[2] if x < cx + 3 else GD[1])
            elif coffee[y, x]: P(x, y, '#3a1e0e' if y > 8 else '#24120a')
            else: P(x, y, WR[2] if x < cx else WR[1])
    for (x, y) in [(8, 9), (9, 9), (10, 9)]: P(x, y, '#7a4a2a')              # 咖啡反光
    # 杯身花紋：從杯口垂下來的藍色鱗片，夾著金點，長短不一
    L = [3, 5, 4, 6, 3, 5, 7, 4, 6, 5, 3, 6, 4, 7, 5, 3, 4, 6]
    DR = ['#3e5a9c', '#5a7cc0', '#86a4dc', '#b6ccf0']
    for x in range(N):                                                      # 花紋：從金邊垂下來的藍色水滴（上深下淺），中間點綴金點
        if abs(x + .5 - cx) >= rx0 - .5: continue
        yr = y0 + rx0 * ry_k * (1 - ((x + .5 - cx) / rx0) ** 2) ** .5
        top = int(yr) + 1
        ln = L[x % len(L)] - (2 if x % 3 == 2 else 0)
        shade = -1 if x > cx + 5 else 0
        for r in range(ln):
            y = top + r
            if nm(sp, x, y) != 'cup' or rim[y, x]: continue
            k = min(3, int(r / max(1, ln - 1) * 3.2)) if ln > 1 else 3
            P(x, y, DR[max(0, k + shade)])
        g = top + ln // 2
        if x % 4 == 1 and ln > 3 and nm(sp, x, g) == 'cup': P(x, g, GD[2] if x < cx + 5 else GD[1])
    # 杯把：上面受光、右下暗，外緣描一條金線，跟背景分清楚
    for y in range(N):
        for x in range(N):
            if nm(sp, x, y) != 'handle': continue
            outer = sp.rgb[y, x + 1, 3] == 0 if x + 1 < N else True
            P(x, y, WR[4] if y < 13 else (WR[3] if y < 16 else WR[2]))
            if x >= 28 and y >= 15: P(x, y, WR[1])
            hole = any(0 <= x + dx < N and 0 <= y + dy < N and sp.rgb[y + dy, x + dx, 3] == 0 and 23 <= x + dx <= 27 and 12 <= y + dy <= 18 for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1)))
            if hole: P(x, y, WR[1] if y < 15 else WR[2])                    # 鏤空的內緣暗一點，洞比較明顯
    for y in range(N):                                                      # 金線：沿著杯把外緣
        for x in range(N):
            if nm(sp, x, y) == 'handle' and any(0 <= x + dx < N and 0 <= y + dy < N and nm(sp, x + dx, y + dy) == 'handle' for dx, dy in ((1, 0), (0, -1))) \
               and any(not (0 <= x + dx < N and 0 <= y + dy < N) or (sp.rgb[y + dy, x + dx, 3] == 0) or nm(sp, x + dx, y + dy) in ('',) for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1))):
                pass
    for y in range(N):                                                      # 杯底最下緣：深一點，跟杯盤分開
        for x in range(N):
            if nm(sp, x, y) == 'cup' and nm(sp, x, y + 1) != 'cup' and y > 20: P(x, y, '#5a6078')
    # 熱氣
    for k, x0 in enumerate((12, 18)):
        for y in range(0, 4):
            x = x0 + round(math.sin(y / 1.3 + k * 2))
            if sp.rgb[y, x, 3] == 0 and (y + k) % 3: sp.rgb[y, x] = (236, 242, 255, 170)
    return sp


def coffee_b():
    """咖啡 B：外帶紙杯（白色杯身、牛皮紙杯套、白色杯蓋），冒煙"""
    sp = sp_new()
    sp.poly('body', 'paper', 4, [(7.5, 9), (24.5, 9), (22, 30), (10, 30)], shade='cyl', light=.25)
    sp.poly('sleeve', 'kraft', 5, [(8.2, 14.5), (23.8, 14.5), (22.7, 24), (9.3, 24)], shade='cyl', light=.2)
    sp.poly('lidR', 'porcW', 6, [(5.5, 6), (26.5, 6), (26, 10), (6, 10)], shade='cyl', light=.3)
    sp.poly('lidT', 'porcW', 6.5, [(8, 2.5), (24, 2.5), (25.5, 6), (6.5, 6)], shade='cylv', light=.5)
    finish(sp)
    for x in range(11, 15): sp.px(x, 4, '#3a3a46')                          # 杯蓋喝口
    for x in range(9, 24):
        if nm(sp, x, 19) == 'sleeve': sp.px(x, 19, '#8a5e32')
    for (x, y) in [(10, 12), (10, 13), (10, 26), (11, 27)]:
        if nm(sp, x, y) == 'body': sp.px(x, y, '#ffffff')
    for k, x0 in enumerate((13, 19)):
        for y in range(0, 3):
            x = x0 + round(math.sin(y + k))
            if sp.rgb[y, x, 3] == 0: sp.rgb[y, x] = (236, 242, 255, 180)
    return sp


def dessert():
    """甜點：草莓蛋糕切片。尖端朝左前方，正面是切面（看得到夾層），頂面上下邊平行，透視一致"""
    sp = sp_new()
    plate(sp, 'plate', (0, 19, 32, 30), 3)
    T, BL, BR, H = (3, 12.5), (12, 5.5), (28.5, 8.5), 13.5
    sl = (BR[1] - T[1]) / (BR[0] - T[0])
    sp.poly('front', 'sponge', 6, [T, BR, (BR[0], BR[1] + H), (T[0], T[1] + H)], shade='flat', light=.1)
    sp.poly('top', 'cream', 7, [T, BL, BR], shade='flat', light=.45)
    for i, cx in enumerate((15, 19.5, 24)):                                  # 後緣一排奶油花
        cy = BL[1] + (BR[1] - BL[1]) * (cx - BL[0]) / (BR[0] - BL[0])
        sp.ell('ros%d' % i, 'cream', 7.5 + i * .01, (cx - 2.3, cy - 2.8, cx + 2.3, cy + 1.2), shade='sphere', light=.3)
    sp.ell('berry', 'berry', 8, (15.5, 2.5, 21.5, 9), shade='sphere', light=.1)
    sp.poly('leaf', 'scal', 8.1, [(17, 2.5), (19, 1), (20.5, 3)], shade='flat')
    finish(sp)
    for y in range(N):                                                      # 切面依深度上色：奶油→海綿→奶油草莓→海綿→奶油→海綿
        for x in range(N):
            if nm(sp, x, y) != 'front': continue
            d = y - (T[1] + sl * (x - T[0]))
            if d < 2: col = '#fbf8f0'
            elif 4.5 <= d < 6.5 or 9 <= d < 11: col = '#f8f2e6'
            else: col = '#efc878' if x < 16 else '#e2b464'
            if d >= 12.5: col = '#c8964a'
            if x >= BR[0] - 1.5 and d >= 2: col = '#e6ddd0'
            sp.px(x, y, col)
            for (lo, off) in ((4.5, 0), (9, 3)):
                if lo <= d < lo + 2 and (x + off) % 6 in (1, 2) and x < BR[0] - 3:
                    sp.px(x, y, '#d8283a' if (x + off) % 6 == 1 else '#f05a62')
    sp.px(17, 4, '#ffd0d0'); sp.px(18, 3, '#ffffff')
    plate_shine(sp, 'plate', (0, 19, 32, 30))
    return sp


def chickenmeat():
    """烤雞：整隻烤雞放在橢圓盤上，雞腿往右上翹露出腿骨；番茄、葡萄、香芹；焦點和香草用柔和色調"""
    sp = sp_new()
    plate(sp, 'plate', (0, 17.5, 32, 29.5), 2)
    sp.ell('body', 'roastS', 5, (2.5, 7.5, 25, 25), shade='sphere', light=.35)
    sp.mask('drumB', 'roastS', 5.6, disc_chain((19.5, 13.5), 4, (23.5, 6), 1.7), shade='sphere', light=-.1, line=False)
    sp.cap('boneB', 'bone', 5.65, [(23.6, 6.5), (24.6, 3.4)], .9, shade='cyl', light=.2)
    sp.mask('drumF', 'roastS', 5.9, disc_chain((20.5, 19), 5.2, (27.3, 9), 1.7), shade='sphere', light=.3, line=False)
    sp.cap('boneF', 'bone', 5.95, [(27.4, 9.5), (28.6, 6.3)], .9, shade='cyl', light=.2)
    for i, (x, y) in enumerate([(2, 21), (8, 23.2)]):                    # 小番茄（左前）
        sp.ell('tom%d' % i, 'tomato', 6.5 + i * .1, (x, y, x + 4.2, y + 4.2), shade='sphere', light=.2)
    for i, (x, y) in enumerate([(23, 22), (26, 22.5), (24.5, 24.5), (27.5, 24.8), (21.5, 24.3)]):   # 葡萄（右前）
        sp.ell('gr%d' % i, 'grape', 6.5 + i * .01, (x, y, x + 3.2, y + 3.2), shade='sphere', light=.2)
    finish(sp)
    P = sp.px
    # 骨頭末端的關節頭
    for (bx, by) in ((23, 1), (27, 4)):
        for (dx, dy) in [(0, 1), (1, 1), (2, 1), (0, 0), (2, 0)]:
            P(bx + dx, by + dy, '#fffaec' if dx < 2 else '#d4c6a2')
        for (dx, dy) in [(-1, 0), (3, 0), (-1, 1), (3, 1), (-1, 2), (3, 2), (0, 3), (2, 3), (1, 0)]:
            x, y = bx + dx, by + dy
            if 0 <= x < N and (sp.rgb[y, x, 3] == 0 or (dx, dy) == (1, 0)): P(x, y, '#7a6a4a')
        sp.rgb[by - 1, bx] = sp.rgb[by - 1, bx + 2] = (0, 0, 0, 0)
    for (x, y) in [(23, 6), (24, 6), (27, 9), (28, 9)]: P(x, y, '#5e2208')
    # 雞身：上面亮、油亮反光、焦點
    for (x, y) in [(7, 10), (8, 9), (9, 9), (10, 9), (11, 9), (6, 11), (7, 11), (12, 10)]:
        if nm(sp, x, y) == 'body': P(x, y, '#fff0b0')
    # 雞腿和雞身之間：用柔和的陰影帶分開（不畫硬線）
    for y in range(N):
        for x in range(N):
            n = nm(sp, x, y)
            if n == 'body' and (nm(sp, x + 1, y) == 'drumF' or nm(sp, x + 1, y - 1) == 'drumF'): P(x, y, '#94400e')
            if n == 'body' and nm(sp, x + 1, y) == 'drumB': P(x, y, '#a84e14')
            if n == 'drumB' and (nm(sp, x + 1, y) == 'drumF' or nm(sp, x, y + 1) == 'drumF'): P(x, y, '#94400e')
    for (x, y) in [(22, 13), (23, 12), (24, 11), (21, 15)]:                  # 雞腿上的油亮反光
        if nm(sp, x, y) == 'drumF': P(x, y, '#ffd890')
    for (x, y) in [(19, 9), (20, 8)]:
        if nm(sp, x, y) == 'drumB': P(x, y, '#f4b04e')
    for (x, y) in [(11, 13), (8, 15), (14, 11), (13, 17), (6, 18), (10, 20), (16, 10), (17, 18), (5, 14), (14, 21), (23, 16), (25, 13), (21, 21)]:   # 烤得酥脆的焦點（柔和一點的褐色）
        if nm(sp, x, y) in ('body', 'drumF'): P(x, y, '#a84a12')
    for (x, y) in [(12, 12), (9, 17), (15, 15), (19, 20), (24, 15)]:         # 灑的香草
        if nm(sp, x, y) in ('body', 'drumF'): P(x, y, '#3a7a2a')
    for (x, y) in [(15, 12), (12, 16), (7, 21)]:                             # 皮的小紋理亮點
        if nm(sp, x, y) == 'body': P(x, y, '#f6b24c')
    # 盤緣一圈香芹
    for (x, y) in [(2, 20), (3, 19), (1, 22), (12, 26), (13, 27), (14, 26), (17, 27), (18, 26), (29, 21), (30, 20), (28, 27), (20, 27)]:
        if nm(sp, x, y).startswith('plate'):
            P(x, y, '#4e9a2a' if (x + y) % 2 else '#2c6a1c')
    for (x, y) in [(3, 22), (9, 24)]: P(x, y, '#ffd0c0')
    for (x, y) in [(6, 25), (7, 26), (7, 24)]:                               # 兩顆番茄之間的縫
        if nm(sp, x, y).startswith('tom'): P(x, y, '#7a1410')
    for i, (x, y) in enumerate([(23, 22), (26, 22.5), (24.5, 24.5), (27.5, 24.8), (21.5, 24.3)]):   # 每顆葡萄一個反光點、下緣暗
        P(int(x) + 1, int(y) + 1, '#e8b0e0')
        if nm(sp, int(x) + 2, int(y) + 3).startswith('gr'): P(int(x) + 2, int(y) + 3, '#3a1440')
    plate_shine(sp, 'plate', (0, 17.5, 32, 29.5))
    return sp


def bbqrice():
    """燒臘：叉燒飯。白飯上斜斜疊著長條叉燒片（深紅焦糖邊、內部偏褐粉），旁邊兩株整顆青江菜"""
    sp = sp_new()
    plate(sp, 'plate', (0, 13, 32, 30), 3)
    sp.ell('rice', 'rice', 4, (4, 10, 28, 26), shade='sphere', light=.25)
    for i in range(4):                                                      # 長條叉燒片，像撲克牌一樣斜斜排開
        x = 3 + i * 3.6
        sp.poly('cs%d' % i, 'csM', 6 + i * .1, [(x, 12.5 - i * .3), (x + 4.5, 11 - i * .3), (x + 7, 23 - i * .2), (x + 2.5, 24.5 - i * .2)], shade='flat', light=.15)
    for j, (p0, p1) in enumerate((((19.5, 23.5), (26.5, 12)), ((23, 25), (29.5, 14.5)))):   # 整株青江菜：白綠色梗＋深綠葉
        mid = (p0[0] + (p1[0] - p0[0]) * .45, p0[1] + (p1[1] - p0[1]) * .45)
        sp.mask('st%d' % j, 'stemW', 7 + j * .2, disc_chain(p0, 1.2, mid, 1.9), shade='cyl', light=.2)
        sp.mask('lf%d' % j, 'bokchoy', 7.1 + j * .2, disc_chain(mid, 1.8, p1, 2.5), shade='sphere', light=.1)
    finish(sp)
    for i in range(4):
        n = 'cs%d' % i
        for y in range(N):
            for x in range(N):
                if nm(sp, x, y) != n: continue
                if nm(sp, x + 1, y) != n: sp.px(x, y, '#8a1410')                 # 右緣：紅亮的叉燒皮
                elif nm(sp, x + 2, y) != n: sp.px(x, y, '#d0281c' if y % 4 else '#ff6a40')
                elif nm(sp, x, y - 1) != n: sp.px(x, y, '#c02a1c')               # 上緣
                elif nm(sp, x, y + 1) != n or y > 20: sp.px(x, y, '#b8644e')     # 下半部稍暗
    for j, (p0, p1) in enumerate((((19.5, 23.5), (26.5, 12)), ((23, 25), (29.5, 14.5)))):   # 葉脈
        for t in (.55, .7, .85):
            x, y = round(p0[0] + (p1[0] - p0[0]) * t), round(p0[1] + (p1[1] - p0[1]) * t)
            if nm(sp, x, y) == 'lf%d' % j: sp.px(x, y, '#c8eca0')
    for (x, y) in [(6, 11), (9, 10), (13, 10), (17, 11), (5, 23), (9, 25)]:
        if nm(sp, x, y) == 'rice': sp.px(x, y, '#ffffff')
    return sp


def bbqrice_b():
    """燒臘 B：燒臘店櫥窗掛著的兩條叉燒（長條、邊緣焦紅、油亮）"""
    sp = sp_new()
    for i, (x0, x1) in enumerate(((10, 11.5), (21, 20))):
        sp.cap('cs%d' % i, 'charsiu', 4 + i * .1, [(x0, 7), (x1, 27)], 3.6, shade='cyl', light=.3)
    finish(sp)
    for i, x in enumerate((10, 21)):                                        # 鐵鉤
        for y in range(0, 5):
            sp.px(x, y, '#b8c0d0'); sp.px(x + 1, y, '#5a606e')
        sp.px(x - 1, 0, '#b8c0d0')
    for i, (x0, x1) in enumerate(((10, 11.5), (21, 20))):
        for y in range(6, 28, 3):                                           # 焦邊紋路、油亮
            x = round(x0 + (x1 - x0) * (y - 7) / 20)
            if nm(sp, x - 2, y) == 'cs%d' % i: sp.px(x - 2, y, '#ffb080')
            if nm(sp, x + 2, y + 1) == 'cs%d' % i: sp.px(x + 2, y + 1, '#3a0808')
    return sp


def pasta():
    """義大利麵：盤子正中間一坨捲起來的麵（山丘形），上面淋紅醬，羅勒葉，起司粉"""
    sp = sp_new()
    plate(sp, 'plate', (0, 15, 32, 30), 3)
    mound = emask((5, 6, 27, 34)); mound[21:] = False
    mound |= emask((5, 16, 27, 26))
    sp.mask('mound', 'pasta', 5, mound, shade='sphere', light=.2)
    sauce = emask((10, 7.5, 22.5, 13)) | emask((10.5, 10, 13.5, 15.5)) | emask((18.5, 10, 21.5, 14.5)) | emask((14.5, 11, 17, 17))
    sp.mask('sauce', 'sauceR', 6, sauce, shade='flat', light=.15)
    sp.poly('basil', 'lettuce', 7, [(19, 8), (23, 6.5), (24, 9.5), (20.5, 10.5)], shade='sphere', light=.1)
    finish(sp)
    cx, cy = 16, 15
    for y in range(N):                                                      # 麵條：繞著中心一圈一圈捲起來的線
        for x in range(N):
            if nm(sp, x, y) != 'mound': continue
            r = ((x + .5 - cx) ** 2 + ((y + .5 - cy) * 1.5) ** 2) ** .5
            a = math.atan2(y - cy, x - cx)
            v = (r + 1.3 * math.sin(a * 3 + r * .4)) % 3
            if v < .9: sp.px(x, y, '#b8862e')
            elif v < 1.5 and y < 22: sp.px(x, y, '#fff2c0')
    for (x, y) in [(13, 9), (17, 10), (20, 11), (12, 12), (15, 12), (16, 15), (19, 9)]:   # 肉醬的碎肉
        if nm(sp, x, y) == 'sauce': sp.px(x, y, '#7a2414')
    for (x, y) in [(12, 9), (13, 8), (14, 8)]:                                # 醬汁反光
        if nm(sp, x, y) == 'sauce': sp.px(x, y, '#f4906a')
    plate_shine(sp, 'plate', (0, 15, 32, 30))
    return sp


def luwei():
    """滷味：木砧板上的切盤（滷蛋對半、豆干片、海帶結、米血、蔥花辣椒）"""
    sp = sp_new()
    sp.poly('boardE', 'board', 2.8, [(1, 13.5), (31, 13.5), (30, 29.5), (2, 29.5)], shade='flat', light=-.5)
    sp.poly('board', 'board', 3, [(1, 12), (31, 12), (30, 28), (2, 28)], shade='cylv', light=.2)
    sp.ell('egg1', 'egg', 5, (2.5, 13, 10.5, 20.5), shade='sphere')
    sp.ell('w1', 'cream', 5.05, (3.7, 14.2, 9.3, 19.3), shade='flat', light=.1, line=False)
    sp.ell('y1', 'yolk', 5.1, (4.8, 15.2, 8.3, 18.5), shade='sphere', line=False)
    sp.ell('egg2', 'egg', 5.2, (7, 17.5, 15, 25), shade='sphere')
    sp.ell('w2', 'cream', 5.25, (8.2, 18.7, 13.8, 23.8), shade='flat', light=.1, line=False)
    sp.ell('y2', 'yolk', 5.3, (9.3, 19.7, 12.8, 23), shade='sphere', line=False)
    for i, x in enumerate((14, 17.5, 21)):
        sp.poly('dt%d' % i, 'dtofu', 5 + i * .1, [(x, 14), (x + 3, 13.5), (x + 3.5, 21), (x + .5, 21.5)], shade='cyl', light=.15)
    sp.ell('kelp', 'kelp', 6, (24, 14, 30, 20), shade='sphere', light=.3)
    sp.poly('blood', 'blackT', 5.5, [(16, 22), (24, 21.5), (24.5, 26), (16.5, 26.5)], shade='cyl', light=.7)
    finish(sp)
    for (x, y) in [(26, 16), (27, 17), (28, 16)]:                           # 海帶結的結
        if nm(sp, x, y) == 'kelp': sp.px(x, y, '#08140c')
    for i, x in enumerate((14, 17.5, 21)):                                  # 豆干切面
        xx = int(x) + 1
        for y in range(15, 21, 2):
            if nm(sp, xx, y) == 'dt%d' % i: sp.px(xx, y, '#5a3418')
    for (x, y) in [(18, 23), (21, 24), (19, 25), (23, 23)]:                 # 米血的米粒
        if nm(sp, x, y) == 'blood': sp.px(x, y, '#b0a8b4')
    for (x, y) in [(5, 23), (13, 25), (26, 22), (11, 15), (28, 24)]:        # 蔥花、辣椒
        sp.px(x, y, '#7cc24c'); sp.px(x + 1, y, '#3f7d2a')
    for (x, y) in [(6, 25), (25, 25)]:
        sp.px(x, y, '#e03a2a')
    for x in range(3, 30, 4):                                               # 砧板木紋
        if nm(sp, x, 27) == 'board': sp.px(x, 27, '#8a5a2e')
    return sp

ICONS = {'ramen': ramen, 'bento': bento, 'luroufan': luroufan, 'friedchicken': friedchicken, 'boba': boba, 'sushi': sushi,
         'mcd': mcd, 'breakfast': breakfast, 'twnoodle': twnoodle, 'pho': pho, 'dumpling': dumpling, 'potsticker': potsticker,
         'convenience': convenience, 'donburi': donburi, 'curry': curry, 'buffet': buffet, 'feast': feast, 'healthy': healthy,
         'coffee': coffee, 'chickenmeat': chickenmeat, 'dessert': dessert, 'bbqrice': bbqrice, 'pasta': pasta, 'luwei': luwei}

POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*+-/:;<=>?@^_~'


def to_rows(im):
    a = np.array(im.convert('RGBA'))
    inv, pal, rows = {}, {}, []
    for y in range(a.shape[0]):
        r = ''
        for x in range(a.shape[1]):
            px = a[y, x]
            if px[3] < 100:
                r += '.'; continue
            key = '#%02x%02x%02x' % tuple(px[:3])
            if key not in inv:
                ch = POOL[len(inv)]; inv[key] = ch; pal[ch] = key
            r += inv[key]
        rows.append(r)
    return rows, pal


if __name__ == '__main__':
    for k, f in ICONS.items():
        f().image(1).save('foodhd_%s.png' % k)
    print('ok')
