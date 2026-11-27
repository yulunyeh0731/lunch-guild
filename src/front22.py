"""正面（面向鏡頭）角色試作。先畫 Yulun 站姿，風格對齊 chars34 的背面版（同一套 Sprite／材質／選擇性外框）。"""
import math
import numpy as np
from PIL import Image, ImageDraw
import chars34 as C
from chars34 import Sprite, P, B, OY, R, bow_mask, M, fold

GL = '#5a3620'      # 眼鏡框（跟頭像一樣的咖啡色粗框）
W_ = C.W


def leg(sp, name, h, k, a, z, light=0.0, r=(3.7, 3.0, 2.5), mat='charcoal'):
    """chars34.leg 的正面版：面向左邊，膝蓋往左彎，所以不檢查「膝蓋只往右」"""
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


def boot_front(sp, name, cx, z, light=0.0, dy=0):
    """斜角正面的靴子：靴筒＋往左下（面向的方向）伸出的鞋頭"""
    sp.poly(name, 'boot', z, P([(cx - 3.2, 60 + dy), (cx + 3.2, 60 + dy), (cx + 3.4, 66.5 + dy), (cx - 3.4, 66.5 + dy)]), 'cyl', light=light)
    sp.ell(name + 'Toe', 'boot', z + .05, B(cx - 6.5, 64 + dy, cx + 2.5, 69 + dy), 'sphere', light=light + .1)
    sp.poly(name + 'Cuff', 'leather', z + .1, P([(cx - 3.8, 59 + dy), (cx + 3.8, 59 + dy), (cx + 3.8, 61.2 + dy), (cx - 3.8, 61.2 + dy)]), 'cylv', light=light + .15)


YF_POSE = {
    # legR／legL：髖、膝、踝；bootR／bootL：(中心 x, 往上抬幾格, 圖層)；armR／armL：肩、肘、手（+ 圖層）；bow：上梢、握把、下梢
    'stand': dict(legR=[(21.5, 44), (21, 52.5), (20, 60.5)], legL=[(29, 44), (29.5, 52.5), (30, 60)],
                  bootR=(20, 0, 8.5), bootL=(30, 0, 8.4),
                  armR=([(16.2, 26.5), (14.6, 33.5), (14, 39.5)], 14), armL=([(34.5, 26.5), (36, 33.5), (35.8, 39.5)], 13.8),
                  bow=((10, 23), (13.2, 41), (11, 60)), bowz=15),
    # 跑 1：右腳（畫面左）抬膝往左前、左腳往右後蹬；拿弓的右手幾乎不擺（弓拿低）、左手握拳擺到肚子前
    'run1': dict(legR=[(21.5, 44), (17, 49), (17.5, 55)], legL=[(29, 44), (31.5, 51.5), (35, 57)],
                 bootR=(17, -6, 8.5), bootL=(35, -2, 7.5),
                 armR=([(16.2, 26.5), (14.8, 33), (15.5, 39)], 14), armL=([(34.5, 26.5), (35, 32.5), (31, 35.5)], 14),
                 bow=((11, 22), (15, 39.5), (13, 58)), bowz=15),
    # 跑 2：左腳（畫面右）抬膝往左前、右腳往右後蹬（從左腳後面過去）；左手往後擺到身體右後方
    'run2': dict(legR=[(21.5, 44), (25.5, 51), (30.5, 56.5)], legL=[(29, 44), (23.5, 48.5), (23, 54.5)],
                 bootR=(31, -2, 7.5), bootL=(22.5, -7, 8.6),
                 armR=([(16.2, 26.5), (14, 32.5), (12.5, 38)], 14), armL=([(34.5, 26.5), (37.5, 33), (40, 31)], 9),
                 bow=((7.5, 21.5), (12.5, 38.5), (11.5, 57)), bowz=15),
}


def yulun_front(pose='stand'):
    """斜角正面：轉身 180°，面向左下（朝鏡頭偏左）。看得到正面＋左側：臉偏左、左耳在畫面右邊、外套開襟偏左"""
    sp = Sprite()
    # ---- 頭 ----
    sp.ell('neck', 'skin', 9, B(22, 19, 28.5, 25), 'cyl', light=-.3)
    def hairfn(d):
        d.ellipse(B(17, 4, 35, 19.5), fill=255)
        for (cx, cy, r) in ((18.5, 7.5, 2.2), (21.5, 4.6, 2.4), (25.5, 3.6, 2.4), (29.5, 4.2, 2.4), (33, 7, 2.3), (34.8, 11, 1.9), (34, 15.5, 1.7)):
            d.ellipse(B(cx - r, cy - r, cx + r, cy + r), fill=255)
    sp.mask('hairBack', 'hairY', 29, sp._mask(hairfn), 'sphere')
    sp.ell('earL', 'skin', 29.5, B(29.8, 12.5, 33, 18), 'sphere', light=-.15)
    def facefn(d):
        d.ellipse(B(17.5, 8, 30.5, 22.5), fill=255)
    sp.mask('face', 'skin', 30, sp._mask(facefn), 'sphere', light=.2)
    sp.poly('bangs', 'hairY', 31, P([(17.5, 12.5), (17.6, 7), (21, 4.8), (26, 4.2), (31, 5.3), (33.5, 8.5), (33.6, 13.5),
                                     (32, 10.6), (30.4, 11.6), (28.8, 9.6), (27, 11.2), (25.2, 9.4), (23.4, 11), (21.6, 9.4), (19.8, 11), (18.6, 10)]), 'sphere')
    # ---- 身體：開襟偏左（身體轉向左邊）----
    sp.poly('torso', 'blue', 10, P([(17.5, 24), (33.5, 24), (36, 28), (35.5, 35), (34.5, 41), (17, 41), (16, 35), (15.5, 28)]))
    sp.poly('tee', 'cream', 11, P([(20.5, 24.2), (25.5, 24.2), (24.8, 40), (21, 40)]), 'flat', light=.25)
    sp.poly('lapelR', 'blue', 12, P([(18.5, 23.5), (21, 24), (21.2, 30), (19.4, 27)]), 'flat', light=.35)
    sp.poly('lapelL', 'blue', 12, P([(28.5, 23.5), (25, 24), (24.6, 31), (27.5, 27)]), 'flat', light=-.05)
    sp.cap('strap', 'leather', 12.5, P([(19.5, 25), (33, 38.5)]), .9, 'flat', light=.1)
    sp.poly('belt', 'leather', 13, P([(17, 39.2), (34.5, 39.2), (34.5, 41.6), (17, 41.6)]), 'cylv')
    sp.poly('hemR', 'blue', 9.6, P([(17, 41), (21, 41), (21, 46), (17, 47), (16.5, 45)]), light=.1)
    sp.poly('hemL', 'blue', 9.5, P([(25.5, 41), (34.5, 41), (35, 45), (34.5, 47.5), (25.5, 46.5)]), light=-.15)
    sp.poly('hips', 'sand', 8.5, P([(18, 41), (33.5, 41), (33.5, 46), (18, 46)]), line=False)
    # ---- 腿：左腳（畫面右、遠）稍後，右腳（畫面左、近）往左前 ----
    c = YF_POSE[pose]
    leg(sp, 'legR', *c['legR'], 8, light=.1, mat='sand', r=(3.6, 3.0, 2.5))
    leg(sp, 'legL', *c['legL'], 7.9, light=-.25, mat='sand', r=(3.6, 3.0, 2.5))
    boot_front(sp, 'bootR', c['bootR'][0], c['bootR'][2], light=.05, dy=c['bootR'][1])
    boot_front(sp, 'bootL', c['bootL'][0], c['bootL'][2], light=-.25, dy=c['bootL'][1])
    # ---- 箭袋：掛在左腰（畫面右邊、靠近鏡頭這側），箭羽朝後上 ----
    sp.poly('quiver', 'leather', 12.8, P([(33, 37), (37.5, 38.5), (37, 51), (33, 50)]), 'cylv', light=-.05)
    for k, (x0, x1, y1) in enumerate(((34, 34.8, 31.5), (35.5, 37, 30.5), (37, 39.2, 32.5))):
        sp.cap('shaft%d' % k, 'wood', 12.6, P([(x0, 37.5), (x1, y1)]), .6, 'flat', line=False)
        sp.poly('fl%d' % k, 'red' if k != 1 else 'cream', 12.7, P([(x1 - 1.2, y1 - 1), (x1 + 1.2, y1 - 1), (x1 + 1, y1 + 2.5), (x1 - 1, y1 + 2.5)]), 'flat', light=.2)
    # ---- 手臂：右手（畫面左）拿弓、左手（畫面右）垂在箭袋前 ----
    (s0, e0, w0), zR = c['armR']; (s1, e1, w1), zL = c['armL']
    sp.cap('armRU', 'blue', zR, P([s0, e0]), 2.5, light=.2)
    sp.cap('armRF', 'blue', zR + .1, P([e0, w0]), 2.2, light=.2)
    bA = (e0[0] + (w0[0] - e0[0]) * .45, e0[1] + (w0[1] - e0[1]) * .45)
    sp.cap('bracerR', 'leather', zR + .2, P([bA, w0]), 2.3, 'cyl')
    sp.cap('armLU', 'blue', zL, P([s1, e1]), 2.6, light=-.15)
    sp.cap('armLF', 'blue', zL + .1, P([e1, w1]), 2.3, light=-.15)
    sp.mask('bow', 'wood', c['bowz'], bow_mask(*c['bow']), 'cyl')
    sp.ell('handR', 'skin', zR + 2, B(w0[0] - 2.2, w0[1] - 2.2, w0[0] + 2.2, w0[1] + 2.2), 'sphere')
    sp.ell('handL', 'skin', zL + 1.2, B(w1[0] - 2.1, w1[1] - 2.1, w1[0] + 2.1, w1[1] + 2.1), 'sphere', light=-.15)
    sp.render()
    C.hair_clumps(sp, 'bangs', 'hairY', (25, 3), R_=8, a0=25, a1=155, n=7, seed=2)
    C.hair_clumps(sp, 'hairBack', 'hairY', (26, 10), R_=8, a0=-175, a1=-5, n=7, seed=3)
    Y = lambda y: y + OY
    face34(sp, glasses=GL)
    b = R['blue']
    fold(sp, 'torso', [(15.5, 29), (36, 28)], b[0])                        # 前胸剪接線（背面也有一條）
    fold(sp, 'torso', [(15.5, 30), (36, 29)], R['gold'][1], step=2)        # 明線
    for (x0, x1) in ((16, 19.5), (28, 32)):                                # 胸前口袋蓋＋明線
        fold(sp, 'torso', [(x0, 32), (x1, 32)], b[0]); fold(sp, 'torso', [(x0, 33), (x1, 33)], R['gold'][1], step=2)
    for yy in range(25, 39, 2):                                            # 開襟兩側的明線
        sp.px(19, Y(yy), R['gold'][1]); sp.px(26, Y(yy), R['gold'][1])
    fold(sp, 'torso', [(30, 34), (31, 38)], b[1]); fold(sp, 'torso', [(17, 34), (18, 38)], b[1])   # 拉扯褶
    for nm in ('hemL', 'hemR'):                                            # 下擺：最下一排暗＋明線（跟背面一樣）
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]
            if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] != nm: continue
            sp.px(xx, col.max(), b[0])
            if xx % 2 == 0 and len(col) > 2: sp.px(xx, col.max() - 1, R['gold'][1])
    for nm in ('armRU', 'armRF', 'armLU'):                                 # 手肘皺摺
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        cxm, cym = xs.mean(), ys.mean() - OY
        fold(sp, nm, [(cxm - 1, cym - 1), (cxm + 1, cym)], b[0])
    for nm, sgn in (('legL', 1), ('legR', -1)):                            # 褲子：大腿拉扯褶、膝蓋皺摺、靴口上方堆皺
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        top = ys.min() - OY
        fold(sp, nm, [(xs.mean() + sgn, top + 2), (xs.mean() - sgn, top + 6)], R['sand'][0])
        fold(sp, nm, [(xs.mean() - 2, top + 9), (xs.mean() - 1, top + 10)], R['sand'][0])
        cm = M(sp, 'boot' + nm[-1] + 'Cuff'); cys, cxs = np.nonzero(cm)
        for i, xx in enumerate(sorted(set(cxs.tolist()))):
            yy = cys[cxs == xx].min() - 1
            if i % 2 == 1 and m_[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == nm: sp.px(xx, yy, R['sand'][0])
    for nm in ('bootR', 'bootL'):                                          # 靴子：鞋底一排暗、腳尖高光、靴口上亮下暗、綁帶
        for part in (nm, nm + 'Toe'):
            m_ = M(sp, part); ys, xs = np.nonzero(m_)
            for xx in set(xs.tolist()):
                yy = ys[xs == xx].max()
                if sp.parts_sorted[sp.pid[yy, xx]]['name'] == part: sp.px(xx, yy, R['boot'][0])
        tm = M(sp, nm + 'Toe'); ys, xs = np.nonzero(tm)
        sp.px(xs.min() + 2, ys.min() + 1, R['boot'][3]); sp.px(xs.min() + 3, ys.min() + 1, R['boot'][2])
        cm = M(sp, nm + 'Cuff'); ys, xs = np.nonzero(cm)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]; sp.px(xx, col.min(), R['leather'][3] if xx < xs.mean() else R['leather'][2]); sp.px(xx, col.max(), R['leather'][0])
        bm = M(sp, nm); ys, xs = np.nonzero(bm)
        yy = ys.min() + 3
        for xx in range(xs.min() + 1, xs.max()):
            if sp.parts_sorted[sp.pid[yy, xx]]['name'] == nm: sp.px(xx, yy, R['leather'][0])
        sp.px(xs.min() + 1, yy, R['gold'][3])
    sp.px(25, Y(40), R['gold'][3]); sp.px(26, Y(40), R['gold'][2])        # 皮帶扣
    back_like(sp, 'blue', 'hairBack', pants='sand', drape=((30, 31),), lit=((16.5, 27), (19, 31)))
    for nm in ('armRU', 'armLU'):                                          # 袖子受光線
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for yy in range(ys.min() + 1, ys.max(), 2):
            r2 = [x for x in range(C.W) if m_[yy, x] and sp.parts_sorted[sp.pid[yy, x]]['name'] == nm]
            if len(r2) > 2: sp.px(r2[1], yy, R['blue'][3])
    sp.outline()
    return sp


# ======================================================================
#  共用：斜角正面的臉（頭像畫法：大鏡片或眼睛＋鼻子在兩眼中間偏左、陰影右下）
# ======================================================================
def face34(sp, glasses=None, lash=None, blush=None, mouth='#9a5a42'):
    """跟 Yulun 定稿的臉同一套：遠側鏡片窄一格、眼睛是鏡片裡的深色點＋淡色反光、鼻子在鼻樑架正下方、右半邊臉頰陰影。
    沒戴眼鏡（Karen）就把鏡框換成睫毛線，眼睛位置一樣。"""
    Y = lambda y: y + OY
    if glasses:
        g0 = glasses
        for x in range(18, 23): sp.px(x, Y(13), g0); sp.px(x, Y(16), g0)
        for x in range(24, 30): sp.px(x, Y(13), g0); sp.px(x, Y(16), g0)
        for y in (14, 15):
            for x in (18, 22, 24, 29): sp.px(x, Y(y), g0)
        sp.px(23, Y(14), g0); sp.px(30, Y(14), g0); sp.px(31, Y(14), g0)
        sp.px(19, Y(14), '#fbe8d4'); sp.px(25, Y(14), '#fbe8d4')
    else:
        for x in (19, 20, 21): sp.px(x, Y(14), lash)                      # 睫毛線（遠側短、近側長）
        for x in (25, 26, 27, 28): sp.px(x, Y(14), lash)
        sp.px(28, Y(13), lash)                                              # 眼尾上揚一點
        sp.px(19, Y(15), '#fbe8d4'); sp.px(25, Y(15), '#fbe8d4')
        if blush:
            for (x, y) in ((19, 18), (20, 18), (27, 18), (28, 18)): sp.px(x, Y(y), blush)
    sp.px(20, Y(15), '#1a1210'); sp.px(26, Y(15), '#1a1210')                # 兩隻眼睛一樣大
    if not glasses:
        sp.px(20, Y(16), '#1a1210'); sp.px(26, Y(16), '#1a1210')
    sp.px(23, Y(17), R['skin'][1]); sp.px(22, Y(18), R['skin'][1]); sp.px(23, Y(18), R['skin'][0])
    for x in (22, 23, 24): sp.px(x, Y(20), mouth)
    for x in range(19, 30):
        if sp.pid[Y(12), x] >= 0 and sp.parts_sorted[sp.pid[Y(12), x]]['name'] == 'face': sp.px(x, Y(12), R['skin'][1])
    for y in range(14, 21):
        for x in (29, 30):
            if sp.pid[Y(y), x] >= 0 and sp.parts_sorted[sp.pid[Y(y), x]]['name'] == 'face': sp.px(x, Y(y), R['skin'][1])


def head34(sp, hairmat, hairfn, bangs):
    sp.ell('neck', 'skin', 9, B(22, 19, 28.5, 25), 'cyl', light=-.3)
    sp.mask('hairBack', hairmat, 29, sp._mask(hairfn), 'sphere')
    sp.ell('earL', 'skin', 29.5, B(29.8, 12.5, 33, 18), 'sphere', light=-.15)
    sp.ell('face', 'skin', 30, B(17.5, 8, 30.5, 22.5), 'sphere', light=.2)
    sp.poly('bangs', hairmat, 31, P(bangs), 'sphere')


def back_like(sp, mat, hair, legs=('legR', 'legL'), pants=None, torso='torso', drape=((22, 21), (29, 30)), lit=((18, 27), (22, 30))):
    """把背面用的細節手法搬到正面：上衣下襬垂墜褶（暗＋亮成對）、左上受光條、褲子膝蓋褶與大腿受光線、頭髮受光點"""
    c = R[mat]
    for (x0, x1) in drape:
        fold(sp, torso, [(x0, 33), (x1, 38.5)], c[0]); fold(sp, torso, [(x0 - 1, 33), (x1 - 1, 38.5)], c[3])
    fold(sp, torso, list(lit), c[3])
    if pants:
        pc = R[pants]
        for nm in legs:
            m_ = M(sp, nm); ys, xs = np.nonzero(m_)
            if not len(xs): continue
            own = lambda x, y: m_[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == nm
            ky = int((ys.min() + ys.max()) / 2); row = [x for x in range(C.W) if own(x, ky)]
            if row:
                kx = row[0] + 1                                              # 膝蓋前側（面向左 → 左邊）
                for (dx, dy) in ((-0, -2), (-1, -1), (0, 1), (-1, 2)):
                    if own(kx + dx, ky + dy): sp.px(kx + dx, ky + dy, pc[0])
                for t in range(3, 9, 2):                                     # 大腿受光線
                    yy = ys.min() + t; r2 = [x for x in range(C.W) if own(x, yy)]
                    if len(r2) > 3: sp.px(r2[1], yy, pc[3])
    hm = M(sp, hair); ys, xs = np.nonzero(hm)
    for (dx, dy) in ((3, 3), (4, 2), (5, 2), (2, 5), (6, 3)):              # 頭髮左上受光點
        x, y = xs.min() + dx, ys.min() + dy
        if hm[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == hair: sp.px(x, y, HL[hair_mat(sp, hair)])


HL = {'hairY': R['hairY'][3], 'hairE': R['hairE'][3], 'hairK': R['hairK'][3]}


def hair_mat(sp, name):
    for p in sp.parts:
        if p['name'] == name: return p['mat']


def boots_detail(sp, names):
    for nm in names:
        for part in (nm, nm + 'Toe'):
            m_ = M(sp, part); ys, xs = np.nonzero(m_)
            for xx in set(xs.tolist()):
                yy = ys[xs == xx].max()
                if sp.parts_sorted[sp.pid[yy, xx]]['name'] == part: sp.px(xx, yy, R['boot'][0])
        tm = M(sp, nm + 'Toe'); ys, xs = np.nonzero(tm)
        sp.px(xs.min() + 2, ys.min() + 1, R['boot'][3]); sp.px(xs.min() + 3, ys.min() + 1, R['boot'][2])
        bm = M(sp, nm)                                                      # 腳踝綁帶＋金扣（背面也有）
        if bm is not None:
            ys2, xs2 = np.nonzero(bm); yy = ys2.min() + 3
            for xx in range(xs2.min() + 1, xs2.max()):
                if sp.parts_sorted[sp.pid[yy, xx]]['name'] == nm: sp.px(xx, yy, R['leather'][0])
            sp.px(xs2.min() + 1, yy, R['gold'][3])
        cm = M(sp, nm + 'Cuff')
        if cm is not None:
            ys, xs = np.nonzero(cm)
            for xx in set(xs.tolist()):
                col = ys[xs == xx]; sp.px(xx, col.min(), R['leather'][3] if xx < xs.mean() else R['leather'][2]); sp.px(xx, col.max(), R['leather'][0])


# ======================================================================
#  Eric：鼠尾草綠上衣、右肩護甲、右手劍（畫面左）、左手盾（畫面右，看到盾的正面）
# ======================================================================
EF_POSE = {
    'stand': dict(legR=[(21.5, 44), (21, 52.5), (20, 60.5)], legL=[(29, 44), (29.5, 52.5), (30, 60)],
                  bootR=(20, 0, 8.5), bootL=(30, 0, 8.4),
                  armR=([(16.5, 27), (14.8, 33.5), (14.5, 39.5)], 14), sw=((-.45, -.89), 22),
                  armL=([(34.5, 27), (37, 33), (36.5, 38)], 13.8), shield=(0, 0), shz=14.5),
    'run1': dict(legR=[(21.5, 44), (17, 49), (17.5, 55)], legL=[(29, 44), (31.5, 51.5), (35, 57)],
                 bootR=(17, -6, 8.5), bootL=(35, -2, 7.5),
                 armR=([(16.5, 27), (14.5, 33), (15.5, 38.5)], 14), sw=((-.55, -.83), 22),
                 armL=([(34.5, 27), (35.5, 32.5), (32, 35.5)], 14), shield=(-3, -1), shz=14.5),
    'run2': dict(legR=[(21.5, 44), (25.5, 51), (30.5, 56.5)], legL=[(29, 44), (23.5, 48.5), (23, 54.5)],
                 bootR=(31, -2, 7.5), bootL=(22.5, -7, 8.6),
                 armR=([(16.5, 27), (14, 32.5), (13.5, 38)], 14), sw=((-.35, -.94), 22),
                 armL=([(34.5, 27), (37.5, 32.5), (39.5, 31)], 9), shield=(3, -2), shz=8.8),
}


def eric_front(pose='stand'):
    c = EF_POSE[pose]
    sp = Sprite()
    def hairfn(d):
        d.ellipse(B(17, 5, 34.5, 20.5), fill=255)
        for (x, y) in ((17.5, 10), (17.5, 15), (19.5, 6), (24, 4.6), (29, 4.8), (33, 7.5), (34.5, 12), (34, 17)):
            d.ellipse(B(x - 1, y - 1, x + 1, y + 1), fill=255)                # 邊緣的小髮束（跟背面一樣）
    head34(sp, 'hairE', hairfn, [(17.4, 12.5), (17.4, 7), (21, 4.6), (26, 4), (31, 5), (33.6, 8.5), (33.6, 12),
                                 (32, 10.4), (30.2, 11.4), (28.4, 9.8), (26.4, 11.2), (24.4, 9.6), (22.4, 11.2), (20.4, 9.8), (18.6, 11)])
    # 上衣：V 領露出白色內衣＋綁繩，腰帶、裙甲片
    sp.poly('torso', 'green', 10, P([(17.5, 24), (33.5, 24), (36, 28), (35.5, 35), (34.5, 41), (17, 41), (16, 35), (15.5, 28)]))
    sp.poly('vneck', 'cream', 11, P([(20, 24), (26, 24), (23.5, 30.5)]), 'flat', light=.25)
    sp.poly('belt', 'leather', 13, P([(17, 39.2), (34.5, 39.2), (34.5, 41.6), (17, 41.6)]), 'cylv')
    sp.poly('pouch', 'leather', 13.5, P([(16, 38), (20, 38), (20, 44), (16, 44)]), light=.05)     # 腰包在右腰（畫面左）
    sp.poly('tassetR', 'green', 9.6, P([(17, 41), (24, 41), (24, 47), (17, 48), (16.5, 46)]), light=.1)
    sp.poly('tassetL', 'green', 9.5, P([(25, 41), (34.5, 41), (35, 46), (34.5, 48), (25, 47)]), light=-.15)
    sp.poly('hips', 'charcoal', 8.5, P([(18, 41), (33.5, 41), (33.5, 46), (18, 46)]), line=False)
    leg(sp, 'legR', *c['legR'], 8, light=.1, mat='charcoal', r=(3.7, 3.0, 2.5))
    leg(sp, 'legL', *c['legL'], 7.9, light=-.25, mat='charcoal', r=(3.7, 3.0, 2.5))
    boot_front(sp, 'bootR', c['bootR'][0], c['bootR'][2], light=.05, dy=c['bootR'][1])
    boot_front(sp, 'bootL', c['bootL'][0], c['bootL'][2], light=-.25, dy=c['bootL'][1])
    # 右肩護甲（畫面左）
    sp.ell('pauldron', 'metal', 15, B(12.5, 23, 21, 31), 'sphere')
    # 右手拿劍（畫面左，劍尖朝下前方）
    (s0, e0, w0), zR = c['armR']
    sp.cap('armU', 'green', zR, P([s0, e0]), 2.5, light=.2)
    sp.cap('armF', 'green', zR + .1, P([e0, w0]), 2.1, light=.2)
    bA = (e0[0] + (w0[0] - e0[0]) * .45, e0[1] + (w0[1] - e0[1]) * .45)
    sp.cap('bracer', 'leather', zR + .2, P([bA, w0]), 2.2, 'flat')
    (sdx, sdy), L = c['sw']
    hl = C.sword(sp, w0[0], w0[1], sdx, sdy, L, z=zR + 1)
    sp.ell('hand', 'skin', zR + 6, B(w0[0] - 2.4, w0[1] - 2.4, w0[0] + 2.4, w0[1] + 2.4), 'sphere')
    # 左手＋盾（畫面右，看到盾的正面：木板、鐵邊、中間圓釘）
    (s1, e1, w1), zL = c['armL']
    sp.cap('armLU', 'green', zL, P([s1, e1]), 2.5, light=-.15)
    sp.cap('armLF', 'green', zL + .1, P([e1, w1]), 2.2, light=-.15)
    dx_, dy_ = c['shield']
    shp = [(31 + dx_, 26 + dy_), (43 + dx_, 26 + dy_), (44 + dx_, 32 + dy_), (43 + dx_, 40 + dy_), (37 + dx_, 49 + dy_), (32 + dx_, 40 + dy_), (30.5 + dx_, 32 + dy_)]
    sp.poly('shield', 'shieldw', c['shz'], P(shp), 'cyl', light=-.05)
    sp.ell('boss', 'metal', c['shz'] + .2, B(35 + dx_, 31 + dy_, 39.5 + dx_, 35.5 + dy_), 'sphere', light=.2)
    sp.render()
    sp.line(P(hl), R['metal'][3], M(sp, 'blade'))
    C.hair_clumps(sp, 'hairBack', 'hairE', (26, 10), R_=8, curly=True, seed=3)
    C.hair_clumps(sp, 'bangs', 'hairE', (25, 3), R_=8, a0=25, a1=155, n=7, seed=5)
    Y = lambda y: y + OY
    face34(sp, glasses='#c98a2e', mouth='#b06a52')
    sm = M(sp, 'shield')                                                  # 盾：鐵邊（受光側亮）＋木板縫
    for y in range(C.H):
        for x in range(C.W):
            if sm[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == 'shield':
                edge = any(not sm[min(y + a, C.H - 1), min(x + b, C.W - 1)] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                if edge: sp.px(x, y, R['metal'][2] if x < 37 + dx_ else R['metal'][1])
                elif (x - dx_) in (34, 40): sp.px(x, y, R['shieldw'][0])
    for (x, y) in ((22, 25), (24, 25), (23, 27), (22, 27)): sp.px(x, Y(y), R['leather'][1])   # V 領綁繩
    g = R['green']
    fold(sp, 'torso', [(24, 31), (24, 38)], g[1], step=2)                  # 前中縫（背面是背中縫）
    for nm in ('tassetL', 'tassetR'):
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]
            if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] == nm: sp.px(xx, col.max(), g[0])
    sp.px(25, Y(40), R['gold'][3]); sp.px(26, Y(40), R['gold'][2])
    for nm in ('tassetL', 'tassetR'):                                      # 甲片：下緣暗＋奶油色縫線、中間褶（跟背面一樣）
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]
            if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] == nm and len(col) > 2 and xx % 2 == 0: sp.px(xx, col.max() - 1, R['cream'][2])
        fold(sp, nm, [((xs.min() + xs.max()) / 2, ys.min() - OY + 1), ((xs.min() + xs.max()) / 2 - 1, ys.max() - OY - 1)], g[1])
    pm = M(sp, 'pouch'); ys, xs = np.nonzero(pm)                         # 腰包蓋＋金扣
    for xx in range(xs.min(), xs.max() + 1): sp.px(xx, ys.min() + 2, R['leather'][0])
    sp.px((xs.min() + xs.max()) // 2, ys.min() + 3, R['gold'][3])
    fold(sp, 'pauldron', [(12.5, 27), (21, 27)], R['metal'][0])            # 護甲金屬帶＋鉚釘＋高光
    sp.px(14, Y(28), R['gold'][3]); sp.px(18, Y(28), R['gold'][3]); sp.px(15, Y(24), R['metal'][3]); sp.px(16, Y(24), R['metal'][3])
    back_like(sp, 'green', 'hairBack', pants='charcoal', drape=((23, 22), (30, 31)), lit=((21, 27), (19, 31)))
    boots_detail(sp, ('bootR', 'bootL'))
    sp.outline()
    return sp


# ======================================================================
#  Karen：長直髮垂在肩前、奶油白毛領披肩、玫瑰長袍、金色腰繩、右手法杖（畫面左）
# ======================================================================
KF_POSE = {
    'stand': dict(boots=((19.5, 0), (30, 0)), arm=([(16.5, 27), (14.5, 33), (13.5, 38)], 15), staffx=12.5, staffy=(14, 62),
                  armL=((34.5, 33), (36, 41), 13), hem=0),
    'run1': dict(boots=((17, -5), (34, -1)), arm=([(16.5, 27), (14, 32.5), (14, 37.5)], 15), staffx=13, staffy=(12, 60),
                 armL=((34.5, 31), (31.5, 36), 15), hem=-1),
    'run2': dict(boots=((31, -1), (22, -5)), arm=([(16.5, 27), (13.5, 33), (12, 37)], 15), staffx=11, staffy=(13, 61),
                 armL=((35.5, 31), (39, 32), 9), hem=1),
}


def karen_front(pose='stand'):
    c = KF_POSE[pose]
    sp = Sprite()
    def hairfn(d):
        d.ellipse(B(17, 4.5, 34.5, 20), fill=255)
    def tailfn(d):                                                          # 馬尾：從後腦往下垂，在畫面右邊（遠側）露出來
        d.polygon(P([(31, 15), (34, 14), (36.2, 19), (36.5, 26), (35.4, 31.5), (34, 33.5), (33.2, 30), (33.4, 24), (32, 19)]), fill=255)
    sp.mask('tail', 'hairK', 13.2, sp._mask(tailfn), 'cyl', light=-.05)
    head34(sp, 'hairK', hairfn, [(17.4, 13.5), (17.6, 7), (21, 4.8), (26, 4.2), (31, 5.2), (33.6, 8.5), (33.4, 13),
                                 (31.6, 10.6), (28.6, 9.4), (25, 8.6), (22, 9.6), (19.4, 11.4)])
    # 長袍＋裙襬
    sp.poly('torso', 'pink', 10, P([(19, 24), (32, 24), (35, 27), (34, 33), (32.5, 40), (19.5, 40), (17.5, 33), (16, 28)]))
    hm = c['hem']
    sp.poly('skirt', 'pink', 9, P([(19.5, 38), (32.5, 38), (35, 45), (37.5 + hm, 54), (38 + hm, 61), (30, 63), (22, 63), (14 + hm, 61), (14.5 + hm, 54), (17, 45)]))
    for k, (bx, dy) in enumerate(c['boots']):
        sp.poly('boot%d' % k, 'boot', 8.6 if dy < -2 else 6.5, P([(bx - 3, 61 + dy), (bx + 3, 61 + dy), (bx + 3.2, 66.5 + dy), (bx - 3.2, 66.5 + dy)]), 'cyl', light=-.1)
        sp.ell('boot%dToe' % k, 'boot', (8.6 if dy < -2 else 6.5) + .05, B(bx - 6, 64 + dy, bx + 2.5, 69 + dy), 'sphere')
    sp.cap('sash', 'gold', 12, P([(19.5, 39.5), (32.5, 39.5)]), 1.1, 'cylv')
    sp.ell('knot', 'gold', 12.6, B(28.3, 39.6, 30.9, 42))                  # 繩結在左腰（畫面右）
    sp.poly('tassel', 'gold', 12.5, P([(29.2, 43.5), (30, 43.5), (31.4, 48.5), (27.8, 48.5)]), 'cylv', light=-.05)
    sp.poly('cape', 'cream', 14, P([(18, 23), (33, 23), (36.5, 27), (36, 31), (29, 33.5), (22, 33.5), (15.5, 31), (15.5, 26)]))
    sp.poly('capeOpen', 'pink', 14.5, P([(23.5, 24.5), (27.5, 24.5), (26.5, 33.6), (24.5, 33.6)]), 'flat', light=.1)   # 披肩前面打開，露出長袍
    # 左手（畫面右）：寬袖
    (e1, w1, zl) = c['armL']
    C.sleeve(sp, 'sleeveL', 'pink', zl, e1, w1, r0=2.2, r1=3.2, droop=1.0, light=-.3)
    sp.ell('handL', 'skin', zl + .1, B(w1[0] - 1.6, w1[1] + .2, w1[0] + 1.8, w1[1] + 3.4), 'sphere', light=-.2)
    # 右手（畫面左）拿法杖
    (s0, e0, w0), z = c['arm']
    sp.cap('armU', 'pink', z, P([s0, e0]), 2.4)
    C.sleeve(sp, 'sleeve', 'pink', z + .5, e0, w0)
    sx = c['staffx']; t0, t1 = c['staffy']
    sp.cap('staff', 'wood', z + 1, P([(sx, t1), (sx + .5, t0)]), 1.0, 'cyl')
    sp.ell('orb', 'orb', z + 2.5, B(sx - 2.3, t0 - 7.5, sx + 3.3, t0 - 1.9), 'sphere')
    sp.cap('claw', 'gold', z + 2.2, P([(sx - 2.2, t0 - 2.5), (sx + .5, t0), (sx + 3.2, t0 - 2.5)]), .8, 'flat')
    sp.ell('hand', 'skin', z + 3, B(w0[0] - 1.8, w0[1] - 1.2, w0[0] + 2.2, w0[1] + 2.8), 'sphere')
    sp.render()
    C.hair_clumps(sp, 'bangs', 'hairK', (25, 3), R_=8, a0=25, a1=155, n=7, seed=6)
    C.hair_clumps(sp, 'hairBack', 'hairK', (26, 9), R_=9, a0=-175, a1=-5, n=8, seed=7)
    lm = M(sp, 'tail')                                                      # 馬尾的髮絲線
    for y in range(C.H):
        for x in range(C.W):
            if lm[y, x] and sp.parts_sorted[sp.pid[y, x]]['name'] == 'tail' and (x * 2 + y // 2) % 4 == 0: sp.px(x, y, R['hairK'][0])
    Y = lambda y: y + OY
    face34(sp, lash='#382216', blush='#efa59a', mouth='#c76a72')
    for x in (32, 33, 34): sp.px(x, Y(15), R['gold'][2])                    # 金色髮圈（跟背面一樣）
    for nm in ('cape',):                                                   # 披肩下緣金邊（跟背面一樣）
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        for xx in set(xs.tolist()):
            col = ys[xs == xx]
            if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] == nm: sp.px(xx, col.max(), R['gold'][2])
    m_ = M(sp, 'skirt'); ys, xs = np.nonzero(m_)                         # 裙襬金邊
    for xx in set(xs.tolist()):
        col = ys[xs == xx]
        if sp.parts_sorted[sp.pid[col.max(), xx]]['name'] == 'skirt':
            sp.px(xx, col.max(), R['cream'][3]); sp.px(xx, col.max() - 1, R['gold'][2])
    pk = R['pink']
    fold(sp, 'skirt', [(21, 46), (19, 58)], pk[1]); fold(sp, 'skirt', [(27, 46), (27.5, 58)], pk[1]); fold(sp, 'skirt', [(32, 46), (34, 57)], pk[0])
    sp.px(25, Y(28), R['gold'][3]); sp.px(25, Y(30), R['gold'][3])       # 長袍前扣
    fold(sp, 'cape', [(19, 25), (18, 31)], R['cream'][1]); fold(sp, 'cape', [(31, 25), (33, 30)], R['cream'][1])   # 披肩褶
    fold(sp, 'cape', [(20, 25), (19.5, 30)], R['cream'][3])
    for nm in ('sleeve', 'sleeveL'):                                       # 袖子皺摺
        m_ = M(sp, nm); ys, xs = np.nonzero(m_)
        cxm, cym = xs.mean(), ys.mean() - OY
        fold(sp, nm, [(cxm - 1, cym - 2), (cxm, cym + 1)], pk[0]); fold(sp, nm, [(cxm + 1, cym - 1), (cxm + 2, cym + 2)], pk[0])
    fold(sp, 'skirt', [(20, 44), (17.5, 58)], pk[3], step=2)               # 長袍受光條
    fold(sp, 'torso', [(19, 29), (21, 36)], pk[3])
    stm = M(sp, 'staff'); ys, xs = np.nonzero(stm)                       # 法杖金環
    for yy in (ys.min() + 6, ys.min() + 26):
        for xx in range(xs.min(), xs.max() + 1):
            if stm[yy, xx]: sp.px(xx, yy, R['gold'][2])
    om = M(sp, 'orb'); ys, xs = np.nonzero(om); sp.px(xs.min() + 1, ys.min() + 1, R['orb'][3])   # 寶珠高光
    hm = M(sp, 'hairBack')                                                 # 往後梳的髮流（往髮圈收）
    for p1 in ((19.5, 9), (21.5, 6.5), (27, 6), (19, 13)):
        im = Image.new('L', (C.W, C.H), 0); ImageDraw.Draw(im).line(P([p1, (33, 15)]), fill=255)
        for yy, xx in zip(*np.nonzero(np.array(im) > 127)):
            if hm[yy, xx] and sp.parts_sorted[sp.pid[yy, xx]]['name'] == 'hairBack': sp.px(xx, yy, R['hairK'][1])
    for k in (0, 1):                                                       # 靴子鞋底、腳尖高光
        for part in ('boot%d' % k, 'boot%dToe' % k):
            m_ = M(sp, part); ys, xs = np.nonzero(m_)
            for xx in set(xs.tolist()):
                yy = ys[xs == xx].max()
                if sp.parts_sorted[sp.pid[yy, xx]]['name'] == part: sp.px(xx, yy, R['boot'][0])
    back_like(sp, 'pink', 'hairBack', drape=(), lit=((19, 27), (21, 30)))
    sp.outline()
    return sp


if __name__ == '__main__':
    from PIL import Image
    S = 5
    import sys
    who = sys.argv[1] if len(sys.argv) > 1 else 'yulun'
    fn = {'yulun': yulun_front, 'eric': eric_front, 'karen': karen_front}[who]
    back = {'yulun': C.yulun34, 'eric': C.eric34, 'karen': C.karen34}[who]
    sps = [back('idle'), fn('stand'), fn('run1'), fn('run2')]
    c = Image.new('RGB', (64 * S * len(sps) + 20 * len(sps), 80 * S), (40, 50, 80))
    for i, sp in enumerate(sps):
        im = Image.fromarray(sp.rgb, 'RGBA').resize((64 * S, 80 * S), Image.NEAREST); c.paste(im, (i * (64 * S + 20), 0), im)
    c.save('/tmp/%sfront.png' % who[0] if who != 'yulun' else '/tmp/yfront.png')
