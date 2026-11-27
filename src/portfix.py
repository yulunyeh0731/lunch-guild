"""v2.1 頭像小改：保留原本的輪廓、眼神、髮型，只補光影（光從左上來）。
apply(PORTRAIT, PPAL) 回傳改好的 rows／palette。"""
GLEAM = {'yulun': [(7, 13), (20, 13)], 'eric': [(8, 13), (19, 13)], 'karen': []}
BLUSH = {'karen': [(8, 17), (9, 17), (21, 17), (22, 17)], 'yulun': [], 'eric': []}


def apply(P, PP):
    out, pal = {}, {}
    for k, rows in P.items():
        g = [list(r) for r in rows]
        p = dict(PP[k])
        p['T'] = p['h']            # 留個新色位
        # 1) 臉右側補一排陰影（第 10～18 列，最右邊的膚色像素）
        for y in range(10, 19):
            r = g[y]
            xs = [x for x in range(16, 32) if r[x] in 'sL']
            if xs:
                x = max(xs)
                if r[x + 1] in 'oghD':
                    r[x] = 'S'
        # 2) 頭髮右半邊加深：每列最右邊兩格 h → D（上半部頭頂）
        for y in range(3, 10):
            r = g[y]
            hs = [x for x in range(16, 32) if r[x] == 'h']
            for x in sorted(hs)[-2:]:
                r[x] = 'D'
        # 3) 頭髮左上加一道亮光（髮旋附近）
        for y in range(4, 8):
            r = g[y]
            hs = [x for x in range(4, 14) if r[x] == 'h']
            if hs:
                x0 = min(hs) + (2 if y < 6 else 1)
                if r[x0] == 'h':
                    r[x0] = 'H'
        # 4) 眼鏡左上角一點反光
        for (x, y) in GLEAM[k]:
            g[y][x] = 'G'
        # 5) Karen 腮紅
        if BLUSH[k]:
            p['b'] = '#efa59a'
            for (x, y) in BLUSH[k]:
                if g[y][x] == 's':
                    g[y][x] = 'b'
        # 6) 衣服左肩亮一點
        for y in range(26, 32):
            r = g[y]
            cs = [x for x in range(0, 14) if r[x] == 'c']
            if cs:
                r[min(cs)] = 'l'
        out[k] = [''.join(r) for r in g]
        pal[k] = p
    return out, pal
