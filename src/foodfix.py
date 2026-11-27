"""v2.2 食物圖示小改款：保留原本 16×16 的粗像素和外框，只補光影（光從左上）。
apply(FOOD, FPAL) → (FOOD, FPAL)。調色盤從陣列改成字典（index 的 draw() 兩種都吃）。"""

OUT = '#191322'


def _hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, t):
    a, b = _hx(a), _hx(b)
    return '#%02x%02x%02x' % tuple(round(x * (1 - t) + y * t) for x, y in zip(a, b))


def _light(c):
    return _mix(c, '#fff6dc', .28)          # 偏暖的亮面


def _dark(c):
    return _mix(c, '#2a1638', .30)          # 偏紫的暗面（像素畫常見做法，不會髒）


def fix_one(rows, pal):
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
            if ch in '.1' or ch not in lt:
                continue
            same = sum(1 for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
                       if 0 <= y + dy < H and 0 <= x + dx < W and rows[y + dy][x + dx] == ch)
            if same < 2:                      # 細線（蒸氣、筷子）不動，保留原本的味道
                continue
            if edge(y - 1, x) or edge(y, x - 1):
                g[y][x] = lt[ch]
            elif edge(y + 1, x) or edge(y, x + 1):
                g[y][x] = dk[ch]
    return [''.join(r) for r in g], newpal


def apply(F, FP):
    out, pal = {}, {}
    for k in F:
        out[k], pal[k] = fix_one(F[k], FP[k])
    return out, pal


# ---- 手工細節（只在幾個試畫的圖示上）：反光、米粒、紋理，數量少、點到為止 ----
TOUCH = {
    'ramen': [(4, 7, '#ff9a86'), (5, 7, '#ff9a86'), (5, 4, '#c9a868'), (8, 5, '#c9a868'), (10, 4, '#c9a868'),
              (6, 6, '#fff3c8'), (9, 3, '#fff3c8')],
    'bento': [(3, 2, '#ffffff'), (4, 2, '#ffffff'), (9, 3, '#fff1b8'), (4, 6, '#9fdc8a'), (9, 6, '#fff1b8'),
              (4, 9, '#ffb08a'), (10, 9, '#c79368'), (11, 7, '#c88f2a')],
    'luroufan': [(4, 3, '#ffffff'), (5, 3, '#ffffff'), (8, 4, '#dcd4c2'), (11, 4, '#dcd4c2'), (6, 4, '#dcd4c2'),
                 (6, 6, '#f0b070'), (7, 6, '#f0b070'), (9, 7, '#6fc07a'), (5, 7, '#6fc07a'), (10, 6, '#5a2c16'),
                 (3, 10, '#a9c6ee')],
    'friedchicken': [(2, 4, '#ffe6a0'), (7, 4, '#ffe6a0'), (12, 4, '#ffe6a0'), (3, 5, '#a86a28'), (8, 6, '#a86a28'),
                     (13, 5, '#a86a28'), (5, 9, '#5aa04a'), (6, 9, '#3f7d2a'), (10, 9, '#d94f3d'), (3, 11, '#fffaf0')],
    'boba': [(5, 5, '#ffffff'), (5, 6, '#ffffff'), (5, 8, '#e6b88a'), (6, 11, '#7a5a48'), (8, 10, '#7a5a48'),
             (10, 11, '#7a5a48'), (7, 12, '#7a5a48'), (11, 1, '#ffe08a')],
    'sushi': [(5, 3, '#ffb49a'), (7, 4, '#fde2d2'), (8, 5, '#fde2d2'), (10, 4, '#fde2d2'), (11, 5, '#fde2d2'),
              (4, 8, '#e4ddcb'), (7, 7, '#e4ddcb'), (10, 8, '#e4ddcb'), (3, 7, '#ffffff')],
}


def touch(rows, pal, pts):
    g = [list(r) for r in rows]
    inv = {v: k for k, v in pal.items()}
    pool = iter('qrstuvwxyzQRSTUVWXYZ!#$%&*+-')
    for x, y, col in pts:
        if col not in inv:
            ch = next(c for c in pool if c not in pal)
            pal[ch] = col; inv[col] = ch
        if g[y][x] not in '.1':
            g[y][x] = inv[col]
    return [''.join(r) for r in g], pal


def apply_touch(F, FP, keys=None):
    for k in (keys or TOUCH):
        if k in TOUCH:
            F[k], FP[k] = touch(F[k], dict(FP[k]), TOUCH[k])
    return F, FP
