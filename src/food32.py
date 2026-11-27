"""v2.2 食物圖示 32×32 小改款：16×16 原圖 → Scale2x（像素畫放大法，斜邊變順、輪廓不變）
→ 外框修成一格寬 → 光影（左上亮、右下暗）→ 手點細節。apply(FOOD, FPAL) → (FOOD, FPAL)，調色盤用字典。"""
from foodfix import _light, _dark


def scale2x(rows):
    H, W = len(rows), len(rows[0])
    P = lambda y, x: rows[y][x] if 0 <= y < H and 0 <= x < W else '.'
    out = [[''] * (W * 2) for _ in range(H * 2)]
    for y in range(H):
        for x in range(W):
            p, a, b, c, d = P(y, x), P(y - 1, x), P(y, x + 1), P(y, x - 1), P(y + 1, x)
            e0 = a if (c == a and c != d and a != b) else p
            e1 = b if (a == b and a != c and b != d) else p
            e2 = c if (d == c and d != b and c != a) else p
            e3 = d if (b == d and b != a and d != c) else p
            out[2 * y][2 * x], out[2 * y][2 * x + 1], out[2 * y + 1][2 * x], out[2 * y + 1][2 * x + 1] = e0, e1, e2, e3
    return [''.join(r) for r in out]


def thin_outline(rows):
    """外框原本放大後變兩格寬：內側那格換成旁邊的顏色，只留最外一格"""
    H, W = len(rows), len(rows[0])
    g = [list(r) for r in rows]
    out = lambda y, x: not (0 <= y < H and 0 <= x < W) or rows[y][x] == '.'
    for y in range(H):
        for x in range(W):
            if rows[y][x] != '1':
                continue
            n4 = [(y + dy, x + dx) for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))]
            if any(out(yy, xx) for yy, xx in n4):
                continue
            near = any(out(y + dy, x + dx) for dy in (-2, -1, 0, 1, 2) for dx in (-2, -1, 0, 1, 2))
            if not near:
                continue
            fills = [rows[yy][xx] for yy, xx in n4 if 0 <= yy < H and 0 <= xx < W and rows[yy][xx] not in '.1']
            if fills:
                g[y][x] = max(set(fills), key=fills.count)
    return [''.join(r) for r in g]


def light(rows, pal):
    H, W = len(rows), len(rows[0])
    g = [list(r) for r in rows]
    newpal = {str(i): c for i, c in enumerate(pal) if c}
    lt, dk = {}, {}
    for i, c in enumerate(pal):
        if i >= 2 and c:
            lt[str(i)] = 'abcdefghijklmnop'[i]; newpal[lt[str(i)]] = _light(c)
            dk[str(i)] = 'ABCDEFGHIJKLMNOP'[i]; newpal[dk[str(i)]] = _dark(c)
    edge = lambda y, x: not (0 <= y < H and 0 <= x < W) or rows[y][x] in '.1'
    for y in range(H):
        for x in range(W):
            ch = rows[y][x]
            if ch not in lt:
                continue
            same = sum(1 for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
                       if 0 <= y + dy < H and 0 <= x + dx < W and rows[y + dy][x + dx] == ch)
            if same < 3:
                continue
            if edge(y - 1, x) or edge(y, x - 1):
                g[y][x] = lt[ch]
            elif edge(y + 1, x) or edge(y, x + 1) or edge(y + 1, x + 1):
                g[y][x] = dk[ch]
    return [''.join(r) for r in g], newpal


def base(rows, pal):
    return light(thin_outline(scale2x(rows)), pal)


def apply(F, FP):
    out, pal = {}, {}
    for k in F:
        out[k], pal[k] = base(F[k], FP[k])
    return out, pal


# ---------------- 手點細節（32 格座標） ----------------
class Pen:
    def __init__(self, rows, pal):
        self.g = [list(r) for r in rows]; self.pal = dict(pal)
        self.inv = {v: k for k, v in self.pal.items()}
        self.pool = iter('qrstuvwxyzQRSTUVWXYZ!#$%&*+-/:;<=>?@^_~')

    def c(self, col):
        if col not in self.inv:
            ch = next(x for x in self.pool if x not in self.pal)
            self.pal[ch] = col; self.inv[col] = ch
        return self.inv[col]

    def px(self, x, y, col, force=False):
        if 0 <= y < 32 and 0 <= x < 32 and (force or self.g[y][x] not in '.1'):
            self.g[y][x] = self.c(col)

    def pts(self, lst, col, force=False):
        for x, y in lst:
            self.px(x, y, col, force)

    def ell(self, x0, y0, x1, y1, col, outline=None):
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
        inside = lambda x, y: ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if inside(x, y):
                    edge = outline and not all(inside(x + dx, y + dy) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)))
                    self.px(x, y, outline if edge else col, force=True)

    def done(self):
        return [''.join(r) for r in self.g], self.pal


def d_ramen(p):
    for y in (8, 11):                                  # 麵條暗紋
        for x in range(8, 24):
            if (x + y) % 5 < 3 and p.g[y][x] in 'b2': p.px(x, y + (x % 4 == 0), '#c9a868')
    p.ell(17, 7, 23, 12, '#fbf6ea', outline='#c9bfae')   # 半顆溏心蛋
    p.ell(19, 8.5, 22, 11, '#f4a33a')
    p.px(20, 9, '#ffd27a', True)
    p.pts([(10, 6), (11, 7), (13, 6)], '#f6c3ac')        # 叉燒肥邊
    p.pts([(9, 10), (14, 12), (21, 13), (12, 9)], '#6fc07a')  # 蔥花
    p.pts([(7, 15), (8, 15), (9, 15)], '#ff9a86')        # 碗口反光


def d_bento(p):
    for x, y in [(13, 5), (14, 9), (13, 14), (14, 19), (25, 5), (24, 12), (25, 20), (13, 22), (24, 23)]:
        p.px(x, y, '#e4ddcb')                            # 白飯米粒
    p.pts([(13, 7), (14, 16), (25, 9)], '#2a1c15')       # 黑芝麻
    for x in range(16, 22, 2):                           # 烤肉焦痕
        p.px(x, 19, '#5e3a1f'); p.px(x + 1, 20, '#5e3a1f')
    p.pts([(17, 13), (18, 13), (19, 14), (20, 13)], '#d99a2a')   # 玉子燒捲紋
    p.pts([(7, 13), (8, 14), (9, 13)], '#9fdc8a')        # 青菜葉脈
    p.pts([(7, 7), (8, 7)], '#ffb4a0')                   # 鮭魚油光


def d_luroufan(p):
    for x, y in [(8, 7), (11, 6), (14, 7), (18, 6), (21, 7), (9, 9), (23, 9)]:
        p.px(x, y, '#ddd5c3')                            # 米粒
    p.ell(17, 11, 23, 16, '#9a5a2a', outline='#5e3218')  # 滷蛋
    p.ell(18.5, 12, 21.5, 14.5, '#e9a43a'); p.px(19, 12, '#ffd27a', True)
    p.pts([(8, 12), (10, 13), (12, 12), (14, 14), (9, 15)], '#f0cf9a')   # 肥肉丁
    p.pts([(7, 11), (11, 11)], '#e8a060')                # 油亮反光
    p.pts([(13, 11), (15, 13), (11, 16)], '#6fc07a')     # 蔥花


def d_friedchicken(p):
    for x0 in (4, 14, 24):                               # 三塊炸雞的酥脆顆粒
        for (dx, dy) in [(1, 5), (3, 7), (2, 10), (4, 12), (1, 13)]:
            p.px(x0 + dx, dy, '#a86a28')
        for (dx, dy) in [(2, 6), (4, 9), (1, 11)]:
            p.px(x0 + dx, dy, '#ffe6a0')
    p.ell(9, 17, 13, 20, '#4f9a3c', outline='#2f5e22')   # 九層塔
    p.ell(19, 17, 22, 19.5, '#3f8a30', outline='#2f5e22')
    p.pts([(15, 18), (16, 18), (17, 19)], '#d94f3d')     # 辣椒


def d_boba(p):
    for (x, y) in [(10, 21), (14, 22), (18, 21), (12, 24), (16, 24), (20, 23)]:    # 珍珠
        p.ell(x - 1, y - 1, x + 1.2, y + 1.2, '#2a1c15')
        p.px(x - 1, y - 1, '#8a6a58', True)
    for y in range(11, 24):                              # 杯身反光
        if y % 6 != 5: p.px(10, y, '#f4e2c8')
    p.pts([(11, 14), (12, 14), (14, 15)], '#e8c08e')     # 奶茶漸層


def d_sushi(p):
    for k in range(4):                                   # 鮭魚油花
        for t in range(5):
            p.px(9 + k * 4 + t, 7 + t, '#fde2d2')
    for x, y in [(8, 15), (12, 16), (16, 15), (20, 16), (24, 15), (10, 20), (22, 20), (14, 21)]:
        p.px(x, y, '#e4ddcb')                            # 飯粒
    p.pts([(7, 6), (8, 6)], '#ffc2ac')


DETAIL = {'ramen': d_ramen, 'bento': d_bento, 'luroufan': d_luroufan,
          'friedchicken': d_friedchicken, 'boba': d_boba, 'sushi': d_sushi}


def full(rows, pal, k):
    r, p = base(rows, pal)
    if k in DETAIL:
        pen = Pen(r, p); DETAIL[k](pen); r, p = pen.done()
    return r, p
