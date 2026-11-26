"""三人斜角戰鬥預覽：新背景 + Eric/Yulun/Karen 斜角角色 + 依序攻擊。輸出 battle-preview-full.html（不動 index）"""
import json, re, base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import chars34 as C

POOL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789#$%&*+=?@!^~'


def breathe(rgb, keep=50):
    out = rgb.copy(); out[1:keep] = rgb[0:keep - 1]; out[0] = 0; return out


FRAMES = {
    'eric':  (C.eric34,  ['atk', 'hit']),
    'yulun': (C.yulun34, ['draw', 'rel']),
    'karen': (C.karen34, ['raise', 'cast']),
}
SPR = {}; SPAL = {}          # 只放斜角三人；舊的背面版 sprite 不再帶進來
meta = {}
for who, (fn, acts) in FRAMES.items():
    idle = fn('idle')
    fr = {'1': idle.rgb, '2': breathe(idle.rgb)}
    for a in acts:
        sp = fn(a); fr[a] = sp.rgb
        meta[who + '_' + a + '_shift'] = sp.shift
    cols = {}
    for a in fr.values():
        for y in range(C.H):
            for x in range(C.W):
                if a[y, x, 3]:
                    cols.setdefault(tuple(int(v) for v in a[y, x, :3]), None)
    assert len(cols) <= len(POOL), (who, len(cols))
    pal = {POOL[i]: '#%02x%02x%02x' % c for i, c in enumerate(cols)}
    inv = {v: k for k, v in pal.items()}
    SPAL[who] = pal
    for k, a in fr.items():
        SPR[who + '_' + k] = [''.join(inv['#%02x%02x%02x' % tuple(int(v) for v in a[y, x, :3])] if a[y, x, 3] else '.'
                                      for x in range(C.W)) for y in range(C.H)]
    print(who, len(cols), 'colours')

# 箭的出發點 = 拉弓時的弓把（換算成 sprite 內比例）
gx, gy = C.YULUN_POSE['draw']['bow'][1]
ARROW_FX = gx / C.W
ARROW_FY = (gy + C.OY + meta['yulun_draw_shift']) / C.H

# 魔法陣（敵人腳下）：橢圓雙環 + 符文刻點
MW, MH = 44, 18
grid = []
for y in range(MH):
    row = ''
    for x in range(MW):
        dx, dy = (x - (MW - 1) / 2) / (MW / 2), (y - (MH - 1) / 2) / (MH / 2)
        r = (dx * dx + dy * dy) ** .5
        ch = '.'
        if .9 <= r <= 1.0:
            ch = '2'
        elif .78 <= r < .86:
            ch = '1'
        elif r < .78 and (abs(dx) < .05 or abs(dy) < .1) and r > .3:
            ch = '1'
        elif .86 <= r < .9 and (x * 7 + y * 3) % 5 == 0:
            ch = '3'
        row += ch
    grid.append(row)
MCIRCLE = grid
MCPAL = ['', '#3aa6a3', '#86e4db', '#e6fffb']


def integrate(src, PREVIEW=False):
    global h
    h = src


    def patch(a, b, regex=False):
        global h
        if regex:
            h2 = re.sub(a, b, h, count=1, flags=re.S)
            assert h2 != h, a[:70]
            h = h2
        else:
            assert a in h, a[:70]
            h = h.replace(a, b, 1)


    h = re.sub(r'const SPR=.*?;\n', lambda m: 'const SPR=%s;\n' % json.dumps(SPR), h, count=1, flags=re.S)
    h = re.sub(r'const SPAL=.*?;\n', lambda m: 'const SPAL=%s;\n' % json.dumps(SPAL), h, count=1, flags=re.S)

    # ---- 新背景 ----
    b64 = base64.b64encode(open(os.path.join(HERE, 'bg34.png'), 'rb').read()).decode()
    h = re.sub(r'<img class="bgi" src="data:image/png;base64,[^"]*"', '<img class="bgi" src="data:image/png;base64,' + b64 + '"', h, count=1)
    patch('.stage .bgi{position:absolute;left:50%;top:-56%;transform:translateX(-50%);height:214%;width:auto;min-width:100%}',
          '.stage .bgi{position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:384px;height:460px;image-rendering:pixelated}')
    patch('rgba(10,14,32,.04),rgba(10,14,32,.5) 80%', 'rgba(10,14,32,0),rgba(10,14,32,.28) 85%')
    patch(r'(\.stage\{[^}]*?)height:\d+px', r'\1height:460px', regex=True)

    # ---- 版面：敵人站在右上的石板路上；隊伍三角陣（Eric 前排、Yulun 左上後排、Karen 右下後排）----
    patch('#foe{position:absolute;left:50%;top:3%;', '#foe{position:absolute;left:69%;top:64px;')
    patch(r'#bparty\{position:absolute;left:0;right:0;bottom:4px;display:flex;justify-content:[a-z-]+;(padding-left:\d+px;)?',
          '#bparty{position:absolute;inset:0;display:block;', regex=True)
    patch(r'(#bparty\{[^}]*?)z-index:\d+', r'\1z-index:4', regex=True)
    patch(r'#bparty \.u\{width:\d+px;height:\d+px;position:relative;', '#bparty .u{width:128px;height:160px;position:absolute;', regex=True)
    patch(r'#bparty \.u canvas\{width:\d+px;height:\d+px;', '#bparty .u canvas{width:128px;height:160px;', regex=True)
    patch(r"cv\.style\.width = '\d+px'; cv\.style\.height = '\d+px';", "cv.style.width = '128px'; cv.style.height = '160px';", regex=True)
    patch("    d.append(cv, sh); box.appendChild(d);\n    units.push({ k, d, cv, frame: 0 });",
          "    const SLOT = { eric: [150, 134, 2], yulun: [20, 160, 2], karen: [188, 262, 3] }[k] || [0, 0, 1];\n"
          "    d.style.left = SLOT[0] + 'px'; d.style.top = SLOT[1] + 'px'; d.style.zIndex = SLOT[2];\n"
          "    d.append(cv, sh); box.appendChild(d);\n    units.push({ k, d, cv, frame: 0 });")

    # ---- 人物影子：放在腳底下（框底往下露 7px）、加寬加深 ----
    patch(r'#bparty \.u \.sh\{position:absolute;left:50%;bottom:4px;transform:translateX\(-50%\);\s*width:46px;height:18px;opacity:\.45;z-index:1\}',
          '#bparty .u .sh{position:absolute;left:47%;bottom:-8px;transform:translateX(-50%);width:76px;height:24px;opacity:.48;z-index:1}', regex=True)
    patch('#bparty .u .sh canvas{width:46px;height:18px}', '#bparty .u .sh canvas{width:76px;height:24px}')
    patch("shadowInto(sh, 46, 18)", "shadowInto(sh, 76, 24)")

    # ---- 攻擊 ----
    i = h.index('function attackOne(u, done) {')
    j = h.index('/* ---- 抽籤 ---- */')
    JS = '''const ARROW_FX = %.4f, ARROW_FY = %.4f;
    function bump() { const st = $('stage'); st.classList.remove('shake'); void st.offsetWidth; st.classList.add('shake'); }
    function attackOne(u, done) {
      idleOn = false;
      const f = $('foeIcon').getBoundingClientRect(), s = u.cv.getBoundingClientRect();
      const fin = (ms) => setTimeout(() => { draw(u.cv, SPR[u.k + '_1'], SPAL[u.k]); idleOn = true; if (done) done(); }, ms);
      if (u.k === 'eric') {
        // 衝刺 → 舉劍 → 揮下（劍尖剛好砍到敵人）→ 跳回
        const dx = (f.left + f.width * 0.38) - (s.left + s.width * 0.95);
        const dy = (f.top + f.height * 0.78) - (s.top + s.height * 0.78);
        $('plate').style.transition = 'opacity .12s'; $('plate').style.opacity = '.25';
        u.d.style.zIndex = 9;
        u.d.style.transition = 'transform .24s steps(5)';
        u.d.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
        setTimeout(() => draw(u.cv, SPR.eric_atk, SPAL.eric), 120);
        setTimeout(() => {
          draw(u.cv, SPR.eric_hit, SPAL.eric);
          fxDraw('cleave', 150, 150, f.left + f.width / 2 - 75, f.top + f.height / 2 - 75);
          hitFoe(); bump();
        }, 380);
        setTimeout(() => { u.d.style.transition = 'transform .26s steps(5)'; u.d.style.transform = ''; draw(u.cv, SPR.eric_1, SPAL.eric); $('plate').style.opacity = ''; }, 820);
        setTimeout(() => { u.d.style.transition = ''; u.d.style.zIndex = 2; }, 1100);
        fin(1120);
      } else if (u.k === 'yulun') {
        // 拉弓（轉正）→ 放箭：箭走淺拋物線，避開 Eric 頭頂
        draw(u.cv, SPR.yulun_draw, SPAL.yulun);
        setTimeout(() => {
          draw(u.cv, SPR.yulun_rel, SPAL.yulun);
          const x0 = s.left + s.width * ARROW_FX, y0 = s.top + s.height * ARROW_FY;
          const x1 = f.left + f.width * 0.45, y1 = f.top + f.height * 0.55;
          const cx = (x0 + x1) / 2, cy = Math.min(y0, y1) - 46;
          const d = document.createElement('div'); d.className = 'fx';
          const cv = document.createElement('canvas'); draw(cv, FX.arrow, FXPAL.arrow);
          cv.style.width = '24px'; cv.style.height = '66px'; d.appendChild(cv); $('fx').appendChild(d);
          const N = 8;
          for (let k = 0; k <= N; k++) setTimeout(() => {
            const t = k / N, x = (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * cx + t * t * x1, y = (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * cy + t * t * y1;
            const tx = 2 * (1 - t) * (cx - x0) + 2 * t * (x1 - cx), ty = 2 * (1 - t) * (cy - y0) + 2 * t * (y1 - cy);
            d.style.left = (x - 12) + 'px'; d.style.top = (y - 33) + 'px';
            d.style.transform = 'rotate(' + (Math.atan2(tx, -ty) * 180 / Math.PI) + 'deg)';
            if (k === N) { d.remove(); fxDraw('slash', 96, 96, x1 - 48, y1 - 48); hitFoe(); bump(); }
          }, k * 45);
        }, 460);
        fin(1250);
      } else {
        // 舉杖蓄力（寶珠亮）→ 施法：敵人腳下出現魔法陣 → 爆開
        draw(u.cv, SPR.karen_raise, SPAL.karen);
        setTimeout(() => {
          draw(u.cv, SPR.karen_cast, SPAL.karen);
          // 魔法陣是地上的圖案：畫在舞台地面層（人物和敵人下面）
          const sh = $('foeShadow').getBoundingClientRect(), st = $('stage'), sr = st.getBoundingClientRect();
          const d = document.createElement('div'); d.className = 'fx mcircle';
          const cv = document.createElement('canvas'); draw(cv, FX.mcircle, FXPAL.mcircle);
          cv.style.width = '176px'; cv.style.height = '72px'; d.appendChild(cv);
          d.style.left = (sh.left + sh.width / 2 - 88 - sr.left - st.clientLeft) + 'px';
          d.style.top = (sh.top + sh.height / 2 - 38 - sr.top - st.clientTop) + 'px';
          d.style.zIndex = 2; st.appendChild(d); void d.offsetWidth; d.classList.add('go');
          setTimeout(() => d.remove(), 1000);
        }, 420);
        setTimeout(() => {
          fxDraw('magic', 122, 128, f.left + f.width / 2 - 61, f.top + f.height / 2 - 64);
          hitFoe(); bump();
        }, 980);
        fin(1450);
      }
    }

    ''' % (ARROW_FX, ARROW_FY)
    h = h[:i] + JS + h[j:]

    # 依序攻擊：Eric → Yulun → Karen，一個做完再換下一個
    i = h.index("  units.forEach((u, i) => setTimeout(() => attackOne(u, i === units.length - 1 ? () => {")
    j = h.index("function applyEncStyle()")
    END_PREVIEW = "type($('talk'), '決定吃「' + foeShop.name + '」！\\u3000（預覽：再按一次「就這家」可重播）', () => { rolling = false; });"
    END_INDEX = "type($('talk'), '決定吃「' + foeShop.name + '」！\\u3000隊伍朝店家前進。', () => { rolling = false; setTimeout(() => go('log'), 500); });"
    h = h[:i] + """  const order = ['eric', 'yulun', 'karen'].map(k => units.find(u => u.k === k)).filter(Boolean);
      units.forEach(u => { if (!order.includes(u)) order.push(u); });
      const next = (n) => {
        if (n >= order.length) { %s return; }
        attackOne(order[n], () => setTimeout(() => next(n + 1), 260));
      };
      setTimeout(() => next(0), 200);
    };
    """ % (END_PREVIEW if PREVIEW else END_INDEX) + h[j:]

    # 魔法陣 FX + 動畫
    h = h.replace('const FX=', 'const FX0=', 1)
    h = h.replace('const FXPAL=', 'const FXPAL0=', 1)
    h = h.replace('/* ---- 抽籤 ---- */', 'const FX = Object.assign({}, FX0, { mcircle: %s }); const FXPAL = Object.assign({}, FXPAL0, { mcircle: %s });\n/* ---- 抽籤 ---- */'
                  % (json.dumps(MCIRCLE), json.dumps(MCPAL)), 1)
    patch('.fx.magic.go{', '.fx.mcircle.go{animation:bmc .95s steps(6) 1 forwards}\n'
          '@keyframes bmc{0%{opacity:0;transform:scale(.25)}25%{opacity:1;transform:scale(1)}50%{opacity:.75}70%{opacity:1}100%{opacity:0;transform:scale(1.08)}}\n.fx.magic.go{')

    # 店名牌移到左上角（不擋隊伍）
    h = h.replace('</body>', '''<script>
    (() => { const st = $('stage'), pl = $('plate'); st.appendChild(pl);
      Object.assign(pl.style, { position: 'absolute', left: '10px', top: '10px', right: 'auto', bottom: 'auto', transform: 'none', margin: '0', zIndex: 6 }); })();
    </script>
    </body>''', 1)

    return h
