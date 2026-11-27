"""v2.2.1 補畫剩下的區塊標題小圖示（跟 v2.1 選單圖示同一套畫法：ui34.icon_from 自動光影＋外框）：
scroll（冒險日誌／明細）、book（加入公會／關帳紀錄）、bowl（口袋名單／常去排行）、cal（行事曆）。
另外修月曆：一天 3 筆以上時「+N」多佔一行，格子是 aspect-ratio:1，內容一高就把格子撐寬，整個月曆往右爆出去。
改成「+N」放在圖示那一行，欄寬用 minmax(0,1fr) 鎖住。
uiapply.apply 之後由 build_index 呼叫 apply(h)。"""
from ui34 import im16, icon_from


def _g(shapes):
    return [list(r) for r in icon_from(shapes)]


def _s(g):
    return [''.join(r) for r in g]


def icon_scroll():
    """捲軸：上下兩根捲軸，中間紙上幾行字"""
    g = _g([(im16(box=(3, 3, 12, 12)), 1), (im16(ell=(1, 0.5, 15, 4.5)), 2), (im16(ell=(1, 11, 15, 15)), 2)])
    for y in (6, 8, 10):
        for x in range(5, 11 if y != 10 else 9):
            g[y][x] = '4'
    for (x, y) in [(2, 2), (2, 13)]: g[y][x] = '1'                          # 捲軸端的洞
    for x in range(4, 13): g[1][x] = '3'; g[12][x] = '3'
    return _s(g)


def icon_book():
    """攤開的帳本：兩頁、中間書背，頁上幾行字"""
    g = _g([(im16(pts=[(0, 3.5), (8, 5), (15.9, 3.5), (15.9, 14.5), (8, 16), (0, 14.5)]), 1),
            (im16(pts=[(1, 2), (7.4, 3.6), (7.4, 13.8), (1, 12.4)]), 2),
            (im16(pts=[(8.6, 3.6), (15, 2), (15, 12.4), (8.6, 13.8)]), 2)])
    for y in range(3, 15): g[y][8] = '1'
    for i, y in enumerate((5, 7, 9)):
        for x in range(2, 7): g[y + (1 if x > 4 else 0)][x] = '4'
        for x in range(10, 14): g[y + (1 if x < 12 else 0)][x] = '4'
    return _s(g)


def icon_bowl():
    """一碗白飯冒著熱氣"""
    body = im16(ell=(0.5, 0.5, 15.5, 15)); body[:8] = False
    rice = im16(ell=(2.5, 4, 13.5, 11)); rice[9:] = False
    g = _g([(im16(box=(5, 13, 10, 14.5)), 1), (rice, 2), (body, 3)])
    for (x, y) in [(5, 0), (6, 1), (5, 2), (10, 0), (11, 1), (10, 2)]: g[y][x] = '3'
    for (x, y) in [(5, 6), (8, 5), (10, 6), (7, 7)]:
        if g[y][x] == '2': g[y][x] = '3'
    for x in range(3, 13):
        if g[10][x] == '2': g[10][x] = '3'
    return _s(g)


def icon_cal():
    """日曆：上面兩個環、紅框標一天"""
    g = _g([(im16(box=(1, 3, 14, 15)), 1), (im16(box=(1, 3, 14, 6)), 2)])
    for x in (4, 11):
        g[1][x] = '1'; g[2][x] = '3'; g[3][x] = '3'; g[4][x] = '1'
        g[2][x - 1] = '1'; g[3][x - 1] = '1'; g[2][x + 1] = '1'; g[3][x + 1] = '1'
    for y in (9, 11, 13):
        for x in range(3, 13, 2): g[y][x] = '4'
    for (x, y) in [(8, 10), (9, 10), (10, 10), (8, 12), (10, 12), (8, 11), (10, 11), (9, 12)]: g[y][x] = '1'
    g[11][9] = '3'
    return _s(g)


ICONS = {'scroll': icon_scroll, 'book': icon_book, 'bowl': icon_bowl, 'cal': icon_cal}


def apply(h):
    import uiapply
    _, _, icon = uiapply._grab(h, 'ICON')
    for k, f in ICONS.items():
        icon[k] = f()
    h = uiapply._put(h, 'ICON', icon)
    old = "if (byDay[n].length > 2) { const m2 = document.createElement('div'); m2.className = 'more'; m2.textContent = '+' + (byDay[n].length - 2); d.appendChild(m2); }"
    assert old in h
    h = h.replace(old, "if (byDay[n].length > 2) { const m2 = document.createElement('span'); m2.className = 'more'; m2.textContent = '+' + (byDay[n].length - 2); ic.appendChild(m2); }", 1)
    old = ".cal{display:grid;grid-template-columns:repeat(7,1fr);gap:3px}"
    assert old in h
    h = h.replace(old, ".cal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px}\n.cal .d{min-width:0;overflow:hidden}\n.cal .d .ic{align-items:center}\n.cal .d .ic .more{font-size:10px;margin-left:1px}", 1)
    return h
