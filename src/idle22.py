"""v2.2.5 人物待機動畫改版。
原本：兩格（原樣／腰以上整塊往下 1px，切在腰帶附近）每 520ms 硬切，三人同步 → 有截斷感、像一起抽動。
改成：
- 身體：自動找「上下兩排最像」的那一排（三人都在大腿，第 60～61 排）拿掉，上面整個往下 1px → 像膝蓋微彎往下沉，看不出切口。
  站 640ms、沉 520ms，三人速度不同（Eric 1.08、Yulun 1、Karen 1.18 倍）、起點錯開。
- 小動作（跟身體各自計時）：Eric 劍身一道反光從劍柄滑到劍尖；Karen 法杖寶珠發光閃一下；Yulun 不時調整一下持弓（弓往前傾、手抬 1 格，用 chars34 姿勢重畫，不是搬像素）。
  用 chars34 的零件 mask（含外框）做在每一格上，所以下沉時小動作也跟著下沉。
idle 用 SPR[who + '_i' + 身體格 + 小動作格]；攻擊動畫還是用原本的 _1／_2。
build_index 在 fx222 之後呼叫 apply(h)。"""
import numpy as np
import chars34 as C

FN = {'eric': C.eric34, 'yulun': C.yulun34, 'karen': C.karen34}
ROW = {'eric': 60, 'yulun': 60, 'karen': 61}
ACC = {'eric': ('blade',), 'karen': ('orb',)}
NACC = {'eric': 5, 'karen': 3, 'yulun': 3}
# Yulun 的小動作用重畫姿勢（不是搬像素）：1 = 弓往前傾一點，2 = 再加上持弓的手抬 1 格
YULUN_VAR = {1: dict(bow=[(42.5, 21), (39.5, 40), (34.5, 59)]),
             2: dict(armR=[(35, 28), (37, 33.5), (38.5, 39)], bow=[(42.5, 20), (40, 39), (34.5, 58)])}


def yulun_var(k):
    import copy
    base = C.YULUN_POSE['idle']
    if k == 0: return C.yulun34('idle').rgb
    p = copy.deepcopy(base); p.update(YULUN_VAR[k]); C.YULUN_POSE['idle'] = p
    try:
        return C.yulun34('idle').rgb
    finally:
        C.YULUN_POSE['idle'] = base


def part_mask(sp, names):
    pn = [p['name'] for p in sp.parts_sorted]
    pid = sp.pid; H, W = pid.shape
    m = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if pid[y, x] >= 0 and pn[pid[y, x]] in names: m[y, x] = True
    a = sp.rgb[:, :, 3] > 0
    mm = m.copy()
    for y in range(H):
        for x in range(W):
            if a[y, x] and pid[y, x] < 0 and any(0 <= y + dy < H and 0 <= x + dx < W and m[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                mm[y, x] = True
    return m, mm


def drop_row(arr, row):
    out = arr.copy(); out[1:row + 1] = arr[0:row]; out[0] = 0; return out


def accessory(who, rgb, m, mm, k):
    out = rgb.copy()
    if k == 0: return out
    if who == 'karen':                                       # 寶珠發光：亮一階／亮兩階＋四角星
        amt = 45 if k == 1 else 90
        for y, x in zip(*np.nonzero(m)):
            out[y, x, :3] = np.minimum(255, out[y, x, :3].astype(int) + amt)
        if k == 2:
            ys, xs = np.nonzero(m); cy, cx = ys.min() - 2, xs.max() + 2
            for dy, dx in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                y, x = cy + dy, cx + dx
                if 0 <= y < out.shape[0] and 0 <= x < out.shape[1]: out[y, x] = (255, 255, 255, 255) if (dy, dx) == (0, 0) else (190, 250, 255, 255)
    elif who == 'eric':                                      # 劍身反光：沿著劍身從柄滑到尖
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0)
        u, s, vt = np.linalg.svd(pts - c); ax = vt[0]
        if ax[1] > 0: ax = -ax                               # 往上（劍尖）為正
        pr = (pts - c) @ ax; lo, hi = pr.min(), pr.max()
        pos = lo + (hi - lo) * (k - .5) / (NACC[who] - 1)
        for (x, y), p in zip(pts.astype(int), pr):
            if abs(p - pos) < 1.3: out[y, x, :3] = (255, 255, 255)
            elif abs(p - pos) < 2.4: out[y, x, :3] = np.minimum(255, out[y, x, :3].astype(int) + 50)
    return out


def frames(who):
    if who == 'yulun':
        res = {}
        for k in range(NACC[who]):
            v = yulun_var(k)
            res['i1%d' % k] = v; res['i2%d' % k] = drop_row(v, ROW[who])
        return res
    sp = FN[who]('idle')
    m, mm = part_mask(sp, ACC[who])
    res = {}
    for b in ('1', '2'):
        base = sp.rgb if b == '1' else drop_row(sp.rgb, ROW[who])
        bm, bmm = (m, mm) if b == '1' else (drop_row(m, ROW[who]), drop_row(mm, ROW[who]))
        for k in range(NACC[who]):
            res['i%s%d' % (b, k)] = accessory(who, base, bm, bmm, k)
    return res


EXTRA = 'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'


def rows_of(rgb, pal):
    inv = {v: k for k, v in pal.items()}
    out = []
    for y in range(rgb.shape[0]):
        r = ''
        for x in range(rgb.shape[1]):
            if not rgb[y, x, 3]: r += '.'; continue
            col = '#%02x%02x%02x' % tuple(int(v) for v in rgb[y, x, :3])
            if col not in inv:
                ch = next(c for c in EXTRA if c not in pal); pal[ch] = col; inv[col] = ch
            r += inv[col]
        out.append(r)
    return out


JS_OLD = """setInterval(() => {
  if (!idleOn || !units.length) return;
  units.forEach(u => { u.frame ^= 1; draw(u.cv, SPR[u.k + '_' + (u.frame ? 2 : 1)], SPAL[u.k]); });
}, 520);"""
JS_NEW = """const IDLE_BODY = [['1', 640], ['2', 520]];
const IDLE_ACC = { eric: [[0, 2600], [1, 70], [2, 70], [3, 70], [4, 70]], karen: [[0, 1100], [1, 140], [2, 220], [1, 140]], yulun: [[0, 2100], [1, 110], [2, 650], [1, 110]] };
const IDLE_TEMPO = { eric: 1.08, yulun: 1, karen: 1.18 };
const idleAt = (seq, t, k) => { const per = seq.reduce((s, x) => s + x[1], 0) * k; t %= per; for (const [n, d] of seq) { if (t < d * k) return n; t -= d * k; } return seq[0][0]; };
(function idleTick(now) {
  now = now || 0;
  if (!idleOn) units.forEach(u => { u.idleF = null; });
  else units.forEach((u, i) => {
    const k = IDLE_TEMPO[u.k] || 1;
    const f = 'i' + idleAt(IDLE_BODY, now + i * 430, k) + (IDLE_ACC[u.k] ? idleAt(IDLE_ACC[u.k], now + i * 777, 1) : 0);
    if (u.idleF !== f && SPR[u.k + '_' + f]) { u.idleF = f; draw(u.cv, SPR[u.k + '_' + f], SPAL[u.k]); }
  });
  requestAnimationFrame(idleTick);
})();"""


def apply(h):
    import uiapply
    _, _, spr = uiapply._grab(h, 'SPR'); _, _, spal = uiapply._grab(h, 'SPAL')
    for who in FN:
        for k, rgb in frames(who).items():
            spr[who + '_' + k] = rows_of(rgb, spal[who])
    h = uiapply._put(h, 'SPR', spr); h = uiapply._put(h, 'SPAL', spal)
    assert JS_OLD in h
    return h.replace(JS_OLD, JS_NEW, 1)
