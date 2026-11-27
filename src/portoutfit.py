"""v2.1 頭像衣服換成戰鬥同款（照原頭像的粗像素畫法：平塗、三色、粗外框）。
接在 portfix.apply 之後：apply(P, PP) → (P, PP)。只改第 23 列以下（衣服），臉和頭髮不動。"""

EXTRA = {
    'r': '#8a5a34', 'R': '#5e3a1f',      # 皮革
    'y': '#e2bf68', 'Y': '#a8822f',      # 金色
    'M': '#aab3c2', 'N': '#e3e8ef', 'K': '#6c7484',   # 金屬
    'k': '#f1e8d0', 'q': '#cdbf9c',      # 奶油白披肩
}


def _line(g, x0, y0, x1, y1, ch, under='ch'):
    n = max(abs(x1 - x0), abs(y1 - y0)) * 3
    for i in range(n + 1):
        t = i / n
        x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
        if 0 <= y < 32 and 0 <= x < 32 and g[y][x] not in '.o':
            g[y][x] = ch


def strap21(g, x0, y0, n, buckle=None):
    """規則的 2:1 斜帶：每往下一格往右兩格，上排亮皮、下排暗皮，階梯整齊"""
    for j in range(n):
        for dx in (0, 1):
            x = x0 + 2 * j + dx
            for y, ch in ((y0 + j, 'r'), (y0 + j + 1, 'R')):
                if 0 <= y < 32 and 0 <= x < 32 and g[y][x] not in '.o' and not (ch == 'R' and g[y][x] == 'r'):
                    g[y][x] = ch
    if buckle is not None:
        j = buckle; x = x0 + 2 * j; y = y0 + j
        g[y][x] = 'y'; g[y][x + 1] = 'y'; g[y + 1][x] = 'Y'; g[y + 1][x + 1] = 'Y'


def strap_v(g, x0, y0, y1, buckle=None):
    """掛在肩上往下的背帶：每 3 格往右 1 格，2 格寬（左亮右暗）"""
    for y in range(y0, y1 + 1):
        x = x0 + (y - y0) // 3
        if g[y][x] not in '.o': g[y][x] = 'r'
        if g[y][x + 1] not in '.o': g[y][x + 1] = 'R'
    if buckle is not None:
        x = x0 + (buckle - y0) // 3
        g[buckle][x] = 'y'; g[buckle][x + 1] = 'Y'


VARIANT = {'yulun': 'A', 'eric': 'B'}    # 使用者選：Yulun 規則斜帶、Eric 只留肩甲


def _v(who):
    return VARIANT if isinstance(VARIANT, str) else VARIANT[who]


def yulun(g):
    # 紅領帶 → 米色 T 恤；丹寧外套的亮邊改成金色明線；斜背箭袋背帶（他的右肩 → 左腰）
    for y in range(24, 32):
        for x in range(32):
            if g[y][x] == 'a':
                g[y][x] = 'w'
            elif g[y][x] == 'l':
                g[y][x] = 'y'
    for x in range(13, 19):
        g[25][x] = 'q' if g[25][x] == 'w' else g[25][x]     # T 恤領口
    if _v('yulun') == 'A':
        strap21(g, 6, 26, 6, buckle=3)
    else:
        strap_v(g, 8, 25, 31, buckle=29)                       # 背帶扣


def eric(g):
    # 領帶 → 米色內衫＋皮繩交叉；右肩（畫面左）金屬肩甲；斜背皮帶
    for y in range(24, 32):
        for x in range(32):
            if g[y][x] == 'a':
                g[y][x] = 'w'
    for (x, y) in [(15, 26), (16, 27), (15, 28), (16, 29), (15, 30), (16, 31)]:    # 領口綁繩（之字形）
        g[y][x] = 'R'
    # 下巴下面原本一整條白（舊襯衫領）→ 露出脖子，內衫從第 26 列才開始
    for x in range(12, 20):
        if g[24][x] == 'w': g[24][x] = 'S'
        if g[25][x] == 'w': g[25][x] = 'S' if x in (12, 19) else 's'
    pauld = {27: (5, 9), 28: (4, 10), 29: (4, 10), 30: (4, 10), 31: (5, 9)}
    for y, (a, b) in pauld.items():
        for x in range(a, b + 1):
            if g[y][x] != '.':
                g[y][x] = 'M'
        if g[y][a] != '.': g[y][a] = 'o'
        if g[y][b] != '.': g[y][b] = 'o'
    for x in range(5, 10):
        if g[26][x] != '.': g[26][x] = 'o'
    for x in range(6, 9):
        g[28][x] = 'N'
    g[29][5] = 'N'; g[30][8] = 'K'; g[31][7] = 'K'; g[29][7] = 'K'; g[30][9] = 'K'
    if _v('eric') == 'A':
        strap21(g, 11, 27, 5)


def karen(g):
    # 粉色上衣 → 奶油白披肩蓋住肩膀＋金色繩結，下面露出玫瑰色長袍
    shawl = {24: (12, 19), 25: (11, 20), 26: (11, 20), 27: (11, 20)}
    for y, (a, b) in shawl.items():
        for x in range(a, b + 1):
            if g[y][x] in 'cClw':
                g[y][x] = 'k'
        if g[y][a] == 'k': g[y][a] = 'q'
    for x in range(12, 20):
        if g[27][x] == 'k':
            g[27][x] = 'q'
    for (x, y) in [(15, 26), (16, 26), (15, 27), (16, 27), (15, 28), (16, 29), (15, 30)]:
        g[y][x] = 'y'
    g[26][15] = 'Y'
    for y in range(28, 32):
        for x in range(12, 20):
            if g[y][x] == 'l':
                g[y][x] = 'c'


def apply(P, PP):
    out, pal = {}, {}
    for k, f in (('yulun', yulun), ('eric', eric), ('karen', karen)):
        g = [list(r) for r in P[k]]
        f(g)
        out[k] = [''.join(r) for r in g]
        p = dict(PP[k]); p.update(EXTRA); pal[k] = p
    return out, pal
