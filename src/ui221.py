"""v2.2.2 剩下的舊美術：清算頁付款箭頭（原本是文字「───▶」）、每週花費長條圖（原本平面漸層）、
右上角齒輪、月曆左右箭頭。ui22.apply 之後由 build_index 呼叫 apply(h)。"""
import math
import numpy as np
from PIL import Image, ImageDraw
from ui34 import im16, icon_from


def _mask(W, H, pts=None, ell=None, box=None):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    if pts: d.polygon(pts, fill=255)
    if ell: d.ellipse(ell, fill=255)
    if box: d.rectangle(box, fill=255)
    return np.array(im) > 127


def pay_arrow():
    """付款箭頭 40×12（UGOLD：1 外框、2 金、3 亮、4 暗）：三段虛線箭身＋實心箭頭，上亮下暗"""
    W, H = 40, 12
    m = np.zeros((H, W), bool)
    for x0 in (1, 8, 15):
        m |= _mask(W, H, box=(x0, 4, x0 + 4, 7))
    m |= _mask(W, H, box=(22, 4, 27, 7))
    m |= _mask(W, H, pts=[(26, 0), (38.5, 5.5), (26, 11)])
    g = [['.'] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if not m[y, x]: continue
            up = y == 0 or not m[y - 1, x]
            dn = y == H - 1 or not m[y + 1, x]
            g[y][x] = '3' if up else ('4' if dn or y >= 7 else '2')
    for y in range(H):
        for x in range(W):
            if not m[y, x] and any(0 <= y + dy < H and 0 <= x + dx < W and m[y + dy, x + dx] for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                g[y][x] = '1'
    return [''.join(r) for r in g]


def gear():
    """齒輪 32×32（GPAL：銅色 h/l/m/d、金色內圈 L/G/D、外框 o）：8 個一樣大的齒，左上受光"""
    N = 32; c = 15.5
    yy, xx = np.mgrid[0:N, 0:N] + .5
    r = np.hypot(xx - c - .5, yy - c - .5)
    ang = np.arctan2(yy - c - .5, xx - c - .5)
    body = r <= 10.6
    teeth = np.zeros((N, N), bool)
    for k in range(8):
        a = k * math.pi / 4
        dx, dy = math.cos(a), math.sin(a)
        along = (xx - c - .5) * dx + (yy - c - .5) * dy
        across = -(xx - c - .5) * dy + (yy - c - .5) * dx
        teeth |= (along > 8) & (along < 14.3) & (np.abs(across) < 2.9 - (along - 8) * .12)
    hole = r < 4.2
    ring = (r >= 4.2) & (r < 6.8)
    m = (body | teeth) & ~hole
    L = np.array([-.7, -.7])
    g = [['.'] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            if not m[y, x]: continue
            vx, vy = (x + .5 - c - .5), (y + .5 - c - .5)
            n = math.hypot(vx, vy) or 1
            d = (vx * L[0] + vy * L[1]) / n
            if ring[y, x]:
                d2 = -d                                                 # 內圈是凹進去的，光影反過來
                g[y][x] = 'L' if d2 > .35 else ('G' if d2 > -.35 else 'D')
            else:
                g[y][x] = 'h' if d > .45 else ('l' if d > -.05 else ('m' if d > -.55 else 'd'))
    for y in range(N):
        for x in range(N):
            if m[y, x]: continue
            if any(0 <= y + dy < N and 0 <= x + dx < N and m[y + dy, x + dx] for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))):
                g[y][x] = 'o'
    for y in range(N):                                                  # 金色內圈外緣一圈暗線，跟銅色分開
        for x in range(N):
            if m[y, x] and not ring[y, x] and r[y, x] < 7.9 and g[y][x] != 'o':
                g[y][x] = 'D' if g[y][x] in 'md' else 'm'
    return [''.join(r_) for r_ in g]


def arrow(left=True):
    """月曆左右箭頭 16×16（UGOLD）：圓潤一點的三角形，上緣亮、下緣暗"""
    pts = [(2.5, 8), (12.5, 1.5), (13.5, 3), (13.5, 13), (12.5, 14.5)]
    if not left: pts = [(15.9 - x, y) for x, y in pts]
    return icon_from([(im16(pts=pts), 1)])


CHART_CSS = """.chart{gap:7px}
.chart .b{background:#5a7ccc;box-shadow:0 0 0 var(--px) #0b0e1c,inset var(--px) var(--px) 0 #9ab8ec,inset calc(var(--px)*-1) calc(var(--px)*-1) 0 #34508f;min-height:0}
.chart .col.now .b{background:#d8b04a;box-shadow:0 0 0 var(--px) #0b0e1c,inset var(--px) var(--px) 0 #f6e2a8,inset calc(var(--px)*-1) calc(var(--px)*-1) 0 #9a7020}
.chart{border-bottom:var(--px) solid #4a5a90;padding-bottom:0}
.pay .ar{display:flex;justify-content:center;align-items:center;letter-spacing:0}
.pay .ar canvas{width:80px;height:24px}"""


def _fix_frames(h):
    """所有金框（.win 視窗、原本的 .stage）用的 border-image 是同一張畫錯的 12×12 小圖：右邊第 3～8 列少了金色和暗金兩格，
    所以每個視窗右邊的金框都不見。v2.1.2 只修了 .stage；這裡把整份 index 裡這張壞圖都換成修好的 stage-frame.png。"""
    import re, base64, io, os
    good = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stage-frame.png'), 'rb').read()).decode()
    bad = set()
    for b in re.findall(r'border-image:url\(data:image/png;base64,([A-Za-z0-9+/=]+)\)', h):
        im = Image.open(io.BytesIO(base64.b64decode(b))).convert('RGBA')
        if im.size == (12, 12) and im.getpixel((10, 5))[3] == 0 and im.getpixel((1, 5))[3] > 0:   # 右邊少金色 = 壞圖
            bad.add(b)
    for b in bad:
        h = h.replace(b, good)
    return h, len(bad)


def apply(h):
    import json, uiapply
    h, nbad = _fix_frames(h)
    assert nbad >= 1, 'no broken frame found'
    _, _, icon = uiapply._grab(h, 'ICON')
    icon['arrowL'] = arrow(True); icon['arrowR'] = arrow(False); icon['payArrow'] = pay_arrow()
    h = uiapply._put(h, 'ICON', icon)
    h = uiapply._put(h, 'GEAR', gear())
    old = "const ar = document.createElement('div'); ar.className = 'ar'; ar.textContent = '───▶';"
    assert old in h
    h = h.replace(old, "const ar = document.createElement('div'); ar.className = 'ar'; const pa = uic('payArrow', 80); pa.style.height = '24px'; ar.appendChild(pa);", 1)
    assert '</style>' in h
    h = h.replace('</style>', CHART_CSS + '\n</style>', 1)
    return h
