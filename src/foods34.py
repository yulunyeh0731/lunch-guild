"""戰鬥用的大尺寸食物敵人（跟角色同密度，畫在 64×80 畫布上再裁切，顯示 2 倍）。
列表、圖示選單用的 16×16 小圖示不變，只有戰鬥畫面的敵人用這裡的版本。"""
import math
import numpy as np
from PIL import Image, ImageDraw
import chars34 as C
from chars34 import Sprite, P, B, R, M, OY

R.update({
    'bowl':    ['#5b1f24', '#8a2f33', '#b4473f', '#d8705a'],
    'bowlin':  ['#3a1418', '#5b1f24', '#7d2b2e', '#9c3a36'],
    'china':   ['#8c96a8', '#b8c2d0', '#dfe5ee', '#f6f8fb'],     # 白瓷
    'chinab':  ['#2c4a7a', '#3e63a0', '#5a82c0', '#86a8dc'],     # 青花
    'broth':   ['#8a5320', '#b8752f', '#d89a48', '#f0c070'],
    'brothR':  ['#6a2414', '#94361c', '#b8502a', '#d8743c'],     # 紅燒湯
    'noodle':  ['#b89a5a', '#d8bc78', '#efd89a', '#fff0c0'],
    'chashu':  ['#5a2e22', '#8a4a36', '#b86e52', '#e0a080'],
    'beef':    ['#3e1c12', '#62301e', '#8a4a2c', '#b06a40'],
    'egg':     ['#c8b898', '#e8dcc4', '#f8f2e4', '#ffffff'],
    'yolk':    ['#b86a10', '#e09020', '#f4b840', '#ffd870'],
    'tegg':    ['#5a3416', '#84501e', '#a8702e', '#c89048'],     # 滷蛋
    'nori':    ['#141c18', '#22302a', '#33463c', '#4a6052'],
    'naruto':  ['#c8bcb0', '#e8e0d8', '#f8f4f0', '#ffffff'],
    'veg':     ['#24502a', '#357038', '#4e9448', '#78b860'],
    'rice':    ['#b8b4a8', '#d8d6cc', '#efeee8', '#ffffff'],
    'lurou':   ['#3a1a0e', '#5e2c14', '#86441e', '#b06a30'],
    'radish':  ['#b89020', '#d8b030', '#f0d050', '#fff090'],
    'boxw':    ['#3a2418', '#5a3a26', '#7e5636', '#a07650'],     # 便當盒（木紋）
    'boxr':    ['#4a1a1a', '#6e2424', '#923230', '#b8483e'],
    'cutlet':  ['#7a4612', '#a8661c', '#cc8a30', '#eab25a'],
    'bun':     ['#8a4a14', '#b8701e', '#dc9a3a', '#f4c060'],
    'patty':   ['#2e1a12', '#4a2a1a', '#6a3e24', '#8a5634'],
    'cheese':  ['#c08010', '#e0a020', '#f4c840', '#ffe070'],
    'lettuce': ['#2e6a24', '#4a8a30', '#6eae40', '#9ad060'],
    'tomato':  ['#7a1a14', '#a8281c', '#d04030', '#f07058'],
    'fries':   ['#b07818', '#d89a28', '#f0c040', '#ffe070'],
    'redbox':  ['#6a1414', '#981e1a', '#c8302a', '#e85a48'],
    'cup':     ['#9aa4b4', '#c4ccd8', '#e2e8ef', '#f8fafc'],
    'milktea': ['#7a4e2a', '#9e6a3e', '#c08a56', '#dcac78'],
    'pearl':   ['#100a0c', '#22161a', '#3a2a2e', '#5a464a'],
    'straw':   ['#8a1a3a', '#b82a50', '#e04a70', '#f888a8'],
})
WHITE = '#ffffff'


def own(sp, name):
    m = M(sp, name)
    return np.vectorize(lambda i: i >= 0 and sp.parts_sorted[i]['name'] == name)(sp.pid) & m


def lineon(sp, pts, color, mask, width=1):
    im = Image.new('L', (C.W, C.H), 0)
    ImageDraw.Draw(im).line(P(pts), fill=255, width=width)
    for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
        if mask[yy, xx]:
            sp.px(xx, yy, color)


def steam(sp, wisps):
    """熱氣：外框之後畫，半透明、不加框"""
    for (x0, y0, ph) in wisps:
        for t in range(9):
            x = int(round(x0 + 1.6 * math.sin(t * 0.8 + ph))); y = y0 - t + OY
            if 0 <= y < C.H and 0 <= x < C.W and sp.rgb[y, x, 3] == 0:
                sp.rgb[y, x] = (255, 255, 255, 150 - t * 12)


def bowl(sp, mat='bowl', inner='bowlin', soup='broth', x0=6, x1=58, rim=38, depth=20, foot=True, soupmat_shade='sphere'):
    """碗：碗身上寬下窄 + 碗口內側 + 湯面。回傳湯面的範圍"""
    cx = (x0 + x1) / 2; w = x1 - x0
    sp.poly('bowl', mat, 10, P([(x0, rim), (x1, rim), (x1 - w * .06, rim + depth * .6), (x1 - w * .19, rim + depth),
                               (x0 + w * .19, rim + depth), (x0 + w * .06, rim + depth * .6)]), 'cyl')
    if foot:
        sp.poly('foot', inner, 9, P([(cx - w * .23, rim + depth - 1), (cx + w * .23, rim + depth - 1),
                                     (cx + w * .2, rim + depth + 4), (cx - w * .2, rim + depth + 4)]), 'cyl')
    sp.ell('rim', inner, 11, B(x0 - 1, rim - 8, x1 + 1, rim + 6), 'cyl')
    if soup:
        sp.ell('soup', soup, 12, B(x0 + 2, rim - 6, x1 - 2, rim + 4), soupmat_shade)
    return (x0 + 2, rim - 6, x1 - 2, rim + 4)


def bowl_lip(sp, y, mat):
    m = own(sp, 'bowl')
    for x in range(C.W):
        if m[y + OY, x]:
            sp.px(x, y + OY, R[mat][3])


# ------------------------------------------------------------------ 第一批
def ramen():
    sp = Sprite()
    bowl(sp)
    sp.poly('nori', 'nori', 11.5, P([(40, 20), (51, 23), (49, 38), (39, 36)]), 'flat')
    sp.ell('chashu1', 'chashu', 13, B(13, 31, 27, 39), 'sphere')
    sp.ell('chashu2', 'chashu', 13.2, B(20, 29, 33, 37), 'sphere')
    sp.ell('egg', 'egg', 13.5, B(36, 32, 47, 40), 'sphere')
    sp.ell('yolk', 'yolk', 13.6, B(39, 34, 45, 38.5), 'sphere')
    sp.ell('naru', 'naruto', 13.4, B(30, 36, 38, 41), 'sphere')
    sp.render()
    sm = own(sp, 'soup')
    for k, y0 in enumerate((37.5, 39.5)):
        lineon(sp, [(x, y0 + .9 * math.sin(x * .7 + k)) for x in np.linspace(10, 30, 30)], R['noodle'][2 + (k == 0)], sm)
    for nm in ('chashu1', 'chashu2'):
        ys, xs = np.nonzero(own(sp, nm))
        for xx in set(xs.tolist()):
            sp.px(xx, ys[xs == xx].min(), R['egg'][2])
    for (x, y) in ((33, 38), (34, 38), (35, 39), (34, 40), (33, 39)):
        sp.px(x, y + OY, '#d66078')
    bowl_lip(sp, 39, 'bowl')
    bm = own(sp, 'bowl')
    for x in range(12, 54, 6):                                     # 雷紋
        for (dx, dy) in ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)):
            if bm[45 + dy + OY, x + dx]:
                sp.px(x + dx, 45 + dy + OY, R['egg'][1])
    for (x, y) in ((18, 34), (27, 33), (44, 35), (24, 40), (36, 34)):
        sp.px(x, y + OY, '#78b450'); sp.px(x + 1, y + OY, '#508c3c')
    sp.outline(); steam(sp, ((18, 26, 0), (30, 22, 1.5), (44, 15, 3)))
    return sp.ground()


def twnoodle():
    """牛肉麵：白瓷青花碗、紅燒湯、牛肉塊、青江菜"""
    sp = Sprite()
    bowl(sp, mat='china', inner='china', soup='brothR')
    for k, (x, y) in enumerate(((14, 31), (24, 30), (19, 35), (34, 33))):
        sp.ell('beef%d' % k, 'beef', 13 + k * .1, B(x, y, x + 9, y + 6), 'sphere')
    sp.poly('bok1', 'veg', 13.6, P([(40, 28), (48, 26), (52, 33), (44, 37)]), 'cyl')
    sp.poly('bok2', 'veg', 13.7, P([(44, 33), (53, 31), (54, 38), (47, 40)]), 'cyl', light=.15)
    sp.render()
    sm = own(sp, 'soup')
    for k, y0 in enumerate((38, 40)):
        lineon(sp, [(x, y0 + .9 * math.sin(x * .6 + k * 2)) for x in np.linspace(9, 40, 40)], R['noodle'][2 + (k == 0)], sm)
    for (x, y) in ((12, 36), (30, 38), (39, 31), (50, 41)):           # 紅油
        if sm[y + OY, x]:
            sp.px(x, y + OY, '#e8803c'); sp.px(x + 1, y + OY, '#f0a050')
    for nm in ('bok1', 'bok2'):
        ys, xs = np.nonzero(own(sp, nm))
        lineon(sp, [(xs.min() - 1 + 2, (ys.min() + ys.max()) / 2 - OY), (xs.max() - 1, (ys.min() + ys.max()) / 2 - OY - 2)], '#c8e8a0', own(sp, nm))
    bowl_lip(sp, 39, 'china')
    bm = own(sp, 'bowl')                                           # 青花紋
    for x in range(10, 56):
        if bm[42 + OY, x] and x % 2:
            sp.px(x, 42 + OY, R['chinab'][2])
        if bm[50 + OY, x]:
            sp.px(x, 50 + OY, R['chinab'][1])
    for x in range(14, 52, 8):
        for (dx, dy) in ((0, 0), (1, -1), (2, 0), (1, 1)):
            if bm[46 + dy + OY, x + dx]:
                sp.px(x + dx, 46 + dy + OY, R['chinab'][2])
    for (x, y) in ((26, 34), (31, 31), (17, 40), (38, 40)):
        sp.px(x, y + OY, '#78b450')
    sp.outline(); steam(sp, ((20, 25, .5), (34, 22, 2), (46, 20, 3.5)))
    return sp.ground()


def luroufan():
    """滷肉飯：小碗白飯、滷肉燥、滷蛋、黃蘿蔔"""
    sp = Sprite()
    bowl(sp, mat='china', inner='china', soup=None, x0=12, x1=52, rim=42, depth=16)
    sp.ell('rice', 'rice', 12, B(13, 30, 51, 46), 'sphere')
    sp.ell('lurou', 'lurou', 13, B(16, 31, 44, 41), 'sphere')
    sp.ell('tegg', 'tegg', 14, B(36, 33, 47, 42), 'sphere')
    sp.ell('teggin', 'yolk', 14.1, B(39.5, 35.5, 44.5, 39.5), 'sphere', light=-.2)
    sp.poly('radish', 'radish', 13.5, P([(14, 38), (21, 36), (22, 40), (15, 42)]), 'flat')
    sp.render()
    lm = own(sp, 'lurou')
    rng = np.random.default_rng(3)
    for _ in range(26):                                            # 肉燥顆粒 + 油亮
        x, y = int(rng.integers(17, 43)), int(rng.integers(32, 41))
        if lm[y + OY, x]:
            sp.px(x, y + OY, R['lurou'][int(rng.integers(0, 2)) * 3])
    for (x, y) in ((22, 33), (30, 34), (26, 37)):
        if lm[y + OY, x]:
            sp.px(x, y + OY, '#e0a060')
    rm = own(sp, 'radish'); lineon(sp, [(15, 40), (21, 38)], R['radish'][1], rm)
    bowl_lip(sp, 43, 'china')
    bm = own(sp, 'bowl')
    for x in range(14, 52):
        if bm[48 + OY, x]:
            sp.px(x, 48 + OY, R['chinab'][2] if x % 4 else R['chinab'][1])
    sp.outline(); steam(sp, ((22, 28, 0), (34, 26, 2)))
    return sp.ground()


def bento():
    """便當：從斜上方看進打開的紅色便當盒——白飯、排骨、滷蛋、青菜、黃蘿蔔；筷子"""
    sp = Sprite()
    sp.poly('box', 'boxr', 10, P([(5, 36), (59, 36), (59, 56), (5, 56)]), 'cylv')          # 盒身正面
    sp.poly('rimtop', 'boxr', 10.5, P([(8, 18), (56, 18), (59, 36), (5, 36)]), 'flat', light=.2)   # 盒口（上緣）
    sp.poly('inner', 'boxw', 11, P([(10, 20), (54, 20), (56, 34), (8, 34)]), 'flat', light=-.35)  # 盒內
    sp.poly('rice', 'rice', 12, P([(11, 21), (31, 21), (31, 33), (9.5, 33)]), 'sphere')
    sp.poly('divider', 'boxr', 12.2, P([(31, 20.5), (33, 20.5), (33.5, 33.5), (31.5, 33.5)]), 'flat', light=-.1)
    sp.poly('veg', 'veg', 12.5, P([(34, 21), (53, 21), (55, 33), (34, 33)]), 'sphere')
    sp.poly('cutlet', 'cutlet', 13, P([(12, 23), (36, 21), (39, 28), (14, 32)]), 'sphere')
    sp.ell('tegg', 'tegg', 13.5, B(40, 23, 50, 31), 'sphere')
    sp.poly('radish', 'radish', 13.2, P([(46, 27), (54, 26), (54.5, 31), (47, 32)]), 'flat')
    sp.cap('chop1', 'wood', 14, P([(3, 60), (60, 52)]), .8, 'flat')
    sp.cap('chop2', 'wood', 14.1, P([(5, 62), (61, 55)]), .8, 'flat', light=-.15)
    sp.render()
    cm = own(sp, 'cutlet')
    for k in range(4):                                             # 排骨麵衣紋路
        lineon(sp, [(17 + k * 5.5, 23), (19 + k * 5.5, 30)], R['cutlet'][1], cm)
    for (x, y) in ((20, 23), (27, 22), (33, 22)):
        if cm[y + OY, x]:
            sp.px(x, y + OY, R['cutlet'][3])
    vm = own(sp, 'veg')
    rng = np.random.default_rng(5)
    for _ in range(18):
        x, y = int(rng.integers(35, 54)), int(rng.integers(22, 33))
        if vm[y + OY, x]:
            sp.px(x, y + OY, R['veg'][int(rng.integers(0, 2)) * 3])
    rt = own(sp, 'rimtop')
    for x in range(C.W):                                           # 盒口前緣亮邊
        if rt[35 + OY, x]:
            sp.px(x, 35 + OY, R['boxr'][3])
    bxm = own(sp, 'box')
    for (x, y) in ((12, 45), (13, 45), (14, 46), (13, 47), (12, 47), (11, 46)):          # 盒身花紋
        for ox in (0, 18, 36):
            if bxm[y + OY, x + ox]:
                sp.px(x + ox, y + OY, R['radish'][2])
    sp.outline(); steam(sp, ((18, 19, 1), (30, 17, 2.5)))
    return sp.ground()


def mcd():
    """漢堡 + 薯條"""
    sp = Sprite()
    sp.poly('fbox', 'redbox', 9, P([(38, 30), (56, 30), (54, 56), (40, 56)]), 'cylv')
    for k, x in enumerate((39, 42, 45, 48, 51, 53)):
        sp.poly('fry%d' % k, 'fries', 8.5 - k * .01, P([(x, 18 + (k * 5) % 7), (x + 3, 18 + (k * 5) % 7), (x + 3, 32), (x, 32)]), 'cyl')
    sp.ell('bunb', 'bun', 10, B(5, 46, 41, 58), 'sphere', light=-.1)
    sp.ell('patty', 'patty', 11, B(4, 42, 42, 52), 'sphere')
    sp.poly('cheese', 'cheese', 12, P([(5, 42), (41, 42), (38, 48), (32, 45), (24, 49), (16, 45), (9, 48)]), 'flat')
    sp.ell('lettuce', 'lettuce', 12.5, B(3, 38, 43, 46), 'sphere')
    sp.ell('tomato', 'tomato', 12.6, B(6, 36, 40, 42), 'sphere')
    sp.ell('bunt', 'bun', 13, B(5, 20, 41, 41), 'sphere')
    sp.render()
    lm = own(sp, 'lettuce')
    for x in range(4, 43, 3):                                      # 生菜波浪邊
        for yy in range(C.H):
            if lm[yy, x] and not lm[yy + 1, x] if yy + 1 < C.H else False:
                sp.px(x, yy, R['lettuce'][3])
    bm = own(sp, 'bunt')
    rng = np.random.default_rng(9)
    for _ in range(16):                                            # 芝麻
        x, y = int(rng.integers(10, 37)), int(rng.integers(23, 33))
        if bm[y + OY, x] and bm[y + OY, x + 1]:
            sp.px(x, y + OY, '#fff4d8'); sp.px(x + 1, y + OY, '#e8d4a8')
    fb = own(sp, 'fbox')
    for (x, y) in ((44, 40), (45, 39), (46, 40), (47, 41), (48, 40), (49, 39), (50, 40)):     # 盒上金色 M 字樣（簡化成弧線）
        if fb[y + OY, x]:
            sp.px(x, y + OY, R['cheese'][2])
    sp.outline()
    return sp.ground()


def boba():
    """珍珠奶茶：封膜杯、珍珠、粗吸管"""
    sp = Sprite()
    sp.poly('cupb', 'cup', 9, P([(19, 18), (45, 18), (42, 62), (22, 62)]), 'cyl', light=.1)
    sp.poly('tea', 'milktea', 10, P([(20, 22), (44, 22), (41.5, 60), (22.5, 60)]), 'cyl')
    sp.ell('seal', 'cup', 11, B(18, 15, 46, 21), 'cyl', light=.2)
    sp.cap('straw', 'straw', 12, P([(38, -2), (33, 40)]), 1.8, 'cyl')
    sp.render()
    tm = own(sp, 'tea')
    rng = np.random.default_rng(2)
    for _ in range(26):                                            # 珍珠（沉在底部）
        x, y = int(rng.integers(23, 41)), int(rng.integers(47, 59))
        if tm[y + OY, x] and tm[y + OY, x + 1]:
            sp.px(x, y + OY, R['pearl'][1]); sp.px(x + 1, y + OY, R['pearl'][2])
            sp.px(x, y - 1 + OY, R['pearl'][3])
    for y in range(24, 46, 2):                                     # 杯身反光
        if tm[y + OY, 24]:
            sp.px(24, y + OY, R['milktea'][3])
    cm = own(sp, 'cupb')
    for y in range(C.H):
        for x in (20, 21):
            if cm[y, x]:
                sp.px(x, y, R['cup'][3])
    # 杯身標籤
    for y in range(32, 40):
        for x in range(26, 39):
            if tm[y + OY, x]:
                sp.px(x, y + OY, R['cup'][2] if 33 <= y <= 38 else R['cup'][1])
    for x in range(28, 37, 2):
        sp.px(x, 35 + OY, R['milktea'][1]); sp.px(x, 37 + OY, R['milktea'][2])
    sp.outline()
    return sp.ground()


FOODS = {'ramen': ramen, 'twnoodle': twnoodle, 'luroufan': luroufan, 'bento': bento, 'mcd': mcd, 'boba': boba}


def render(key):
    sp = FOODS[key]()
    im = sp.image(1)
    bb = im.getbbox()
    return im.crop(bb)


if __name__ == '__main__':
    import os
    ims = [render(k) for k in FOODS]
    k = 6
    Wt = sum(i.width * k for i in ims) + 20 * (len(ims) + 1); Ht = max(i.height for i in ims) * k + 40
    o = Image.new('RGB', (Wt, Ht), (200, 210, 190))
    x = 20
    for im in ims:
        big = im.resize((im.width * k, im.height * k), Image.NEAREST)
        o.paste(big, (x, Ht - 20 - big.height), big); x += big.width + 20
    o.save('/tmp/foods_batch1.png'); print('ok', [i.size for i in ims])
