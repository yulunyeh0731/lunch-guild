"""v2.2.6 攻擊特效全面升級（像素風，跟馬賽克轉場同一路）。
共用一張蓋在舞台上的低解析度畫布 #pfx（1 格 = 3px，20fps 一格一格跳），特效都畫在上面：
- B 斬擊：Eric 的刀光改成程式畫的新月形像素刀光（3 格長出來、2 格收掉），取代原本半透明的 cleave 圖。
- B 命中火花：8 方向噴出的像素碎片＋十字閃光（Eric 白藍、Yulun 金、Karen 青），取代白色十字星（FX.slash／FX.magic）。
  Yulun 的箭飛行時後面拖一串金色像素尾巴。
- E 魔法：Karen 的魔法陣照舊，命中前從天上打下一道像素光柱（寬度 1→7→1），腳下冒青色光點往上飄。
- D 傷害數字：不再斷行（原本寬 68px，「初見！」會斷成兩行），置中、往上彈一下再落下（FF 風）；「初見！」用青色。
- A 打倒敵人：敵人圖示每 2×2 像素變成一顆碎片，往外噴、往下掉、最後閃爍消失（取代原本變灰）。
- 命中時敵人改成閃紅（原本閃白會蓋掉火花）。
- C 勝利姿勢：Eric 舉劍、Yulun 把弓舉在身體右側（改 chars34 姿勢點重畫，弓身和弦都看得到）、Karen 用原本的舉杖姿勢；三人依序跳一下，身邊冒金色光點，
  2.6 秒後回到待機。重抽時敵人和待機動畫會恢復。
build_index 在 idle22 之後呼叫 apply(h)。"""
import copy
import chars34 as C

JS = r"""
/* ---- 像素戰鬥特效（#pfx） ---- */
const PFX = { U: 3, list: [], run: false };
function pfxInit() {
  const st = $('stage'), sc = st.querySelector('.sc');
  let cv = $('pfx'); if (!cv) { cv = document.createElement('canvas'); cv.id = 'pfx'; st.appendChild(cv); }
  Object.assign(cv.style, { left: sc.offsetLeft + 'px', top: sc.offsetTop + 'px', width: sc.offsetWidth + 'px', height: sc.offsetHeight + 'px' });
  const W = Math.ceil(sc.offsetWidth / PFX.U), H = Math.ceil(sc.offsetHeight / PFX.U);
  if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
  PFX.cv = cv; PFX.g = cv.getContext('2d'); PFX.W = W; PFX.H = H; PFX.R = sc.getBoundingClientRect();
}
const c2u = (x, y) => [(x - PFX.R.left) / PFX.U, (y - PFX.R.top) / PFX.U];
function pfxAdd(fn, dur, delay) {
  pfxInit(); PFX.list.push({ fn, t0: performance.now() + (delay || 0), dur });
  if (!PFX.run) { PFX.run = true; requestAnimationFrame(pfxLoop); }
}
function pfxLoop(now) {
  const g = PFX.g; g.clearRect(0, 0, PFX.W, PFX.H);
  PFX.list = PFX.list.filter(e => {
    const t = Math.floor((now - e.t0) / 50) * 50;          // 20fps：一格一格跳
    if (t > e.dur) return false;
    if (t >= 0) e.fn(g, t, t / e.dur);
    return true;
  });
  if (PFX.list.length) requestAnimationFrame(pfxLoop); else { PFX.run = false; g.clearRect(0, 0, PFX.W, PFX.H); }
}
const px1 = (g, x, y, c, s) => { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), s || 1, s || 1); };
// 命中火花：8 方向碎片＋十字閃光
function pfxSparks(cx, cy, pal, n) {
  pfxInit(); const [x, y] = c2u(cx, cy); n = n || 12;
  const ps = [...Array(n)].map((_, i) => ({ a: i / n * Math.PI * 2 + Math.random() * .35, v: 3 + Math.random() * 2.4 }));
  pfxAdd((g, t, p) => {
    const k = t / 50, c = pal[Math.min(pal.length - 1, Math.floor(p * pal.length))];
    ps.forEach(o => {
      const d = 4 + o.v * k, xx = x + Math.cos(o.a) * d, yy = y + Math.sin(o.a) * d + k * k * .12;
      px1(g, xx, yy, '#1a1020', p < .45 ? 3 : 2); px1(g, xx, yy, c, p < .45 ? 2 : 1);
      if (p < .5) px1(g, x + Math.cos(o.a) * (d - 2), y + Math.sin(o.a) * (d - 2), pal[0]);
    });
    if (p < .3) { const r = p < .15 ? 5 : 3; g.fillStyle = pal[0];
      g.fillRect(Math.round(x) - r, Math.round(y), r * 2 + 1, 1); g.fillRect(Math.round(x), Math.round(y) - r, 1, r * 2 + 1);
      if (p < .15) g.fillRect(Math.round(x) - 1, Math.round(y) - 1, 3, 3); }
  }, 480);
}
// 新月形刀光（從右上砍到左下）
function pfxSlash(cx, cy) {
  pfxInit(); const [x, y] = c2u(cx, cy); const R = 17, a0 = -1.25, a1 = 2.45;
  pfxAdd((g, t) => {
    const f = Math.round(t / 50), span = Math.min(1, (f + 1) / 3), cut = f >= 3 ? (f - 2) / 3 : 0;
    const th = [2, 3, 4, 4, 3, 2][f] || 1;
    for (let a = a0 + (a1 - a0) * cut; a <= a0 + (a1 - a0) * span; a += .025) {
      const tp = Math.sin(Math.PI * (a - a0) / (a1 - a0)), tt = Math.max(1, Math.round(th * tp + .4));
      for (let k = 0; k < tt; k++) {
        const r = R - k, c = tt === 1 ? '#bfeaff' : k === 0 ? '#4f86e0' : k === tt - 1 ? '#ffffff' : '#a8e4ff';
        px1(g, x + Math.cos(a) * r, y + Math.sin(a) * r * .78, c);
      }
    }
  }, 300);
}
// 箭的尾巴
function pfxDot(cx, cy) {
  pfxInit(); const [x, y] = c2u(cx, cy);
  pfxAdd((g, t) => { const f = t / 50; px1(g, x, y, f < 2 ? '#fff2c0' : f < 4 ? '#e2bf68' : '#9a7020', f < 2 ? 2 : 1); }, 260);
}
// 天降光柱＋往上飄的光點
function pfxPillar(cx, cyb) {
  pfxInit(); const [x, yb] = c2u(cx, cyb);
  pfxAdd((g, t) => {
    const f = Math.round(t / 50), w = [1, 2, 4, 6, 7, 7, 6, 4, 2, 1][f] || 0; if (!w) return;
    for (let dx = -w; dx <= w; dx++) { const ad = Math.abs(dx);
      g.fillStyle = ad <= w * .3 ? '#ffffff' : ad <= w * .7 ? '#9ff4ff' : '#3aa6d8'; g.fillRect(Math.round(x) + dx, 0, 1, Math.round(yb)); }
    g.fillStyle = '#ffffff'; g.fillRect(Math.round(x) - w - 3, Math.round(yb) - 1, (w + 3) * 2 + 1, 2);
    g.fillStyle = '#9ff4ff'; g.fillRect(Math.round(x) - w - 6, Math.round(yb), (w + 6) * 2 + 1, 1);
  }, 520);
  const ms = [...Array(16)].map(() => ({ x: x + (Math.random() * 34 - 17), y: yb - Math.random() * 5, v: .7 + Math.random() * 1.1, d: Math.random() * 350 }));
  pfxAdd((g, t) => ms.forEach(m => { const tt = t - m.d; if (tt < 0 || tt > 500) return;
    const yy = m.y - tt / 50 * m.v * 1.8; px1(g, m.x, yy, (tt / 50 | 0) % 2 ? '#9ff4ff' : '#ffffff'); if (tt < 250) px1(g, m.x, yy + 1, '#3aa6d8'); }), 900, -150);
}
// 打倒敵人：碎成像素
function pfxShatter() {
  const cv = $('foeIcon'); if (!cv.width) return; pfxInit();
  const r = cv.getBoundingClientRect(), N = cv.width, M = cv.height, s = r.width / N / PFX.U;
  const data = cv.getContext('2d').getImageData(0, 0, N, M).data, [ox, oy] = c2u(r.left, r.top);
  const cx = ox + N * s / 2, cy = oy + M * s / 2, ps = [];
  for (let y = 0; y < M; y += 2) for (let x = 0; x < N; x += 2) {
    const i = (y * N + x) * 4; if (data[i + 3] < 128) continue;
    const px = ox + (x + 1) * s, py = oy + (y + 1) * s, a = Math.atan2(py - cy, px - cx), d = Math.hypot(px - cx, py - cy);
    const v = .4 + Math.random() * 1.2 + d * .05;
    ps.push({ x: px - 1, y: py - 1, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 1.4 - Math.random() * 1.2,
      c: 'rgb(' + data[i] + ',' + data[i + 1] + ',' + data[i + 2] + ')', z: Math.random() < .3 ? 3 : 2, life: .55 + Math.random() * .45 });
  }
  $('foe').classList.add('gone');
  pfxAdd((g, t, p) => { const k = t / 50; ps.forEach(o => {
    if (p > o.life || (p > o.life * .6 && (Math.round(k) + o.z) % 2)) return;
    px1(g, o.x + o.vx * k, o.y + o.vy * k + .2 * k * k, o.c, o.z); }); }, 1000);
}
// 勝利：金色光點
function pfxGlitter(rect) {
  pfxInit(); const [x0, y0] = c2u(rect.left, rect.top), w = rect.width / PFX.U, h = rect.height / PFX.U;
  const ms = [...Array(9)].map(() => ({ x: x0 + w * (.2 + Math.random() * .6), y: y0 + h * (.15 + Math.random() * .6), d: Math.random() * 700 }));
  pfxAdd((g, t) => ms.forEach(m => { const tt = t - m.d; if (tt < 0 || tt > 450) return; const f = tt / 50 | 0, yy = m.y - f;
    if (f < 3) { px1(g, m.x, yy, '#fffbe0'); px1(g, m.x - 1, yy, '#e2bf68'); px1(g, m.x + 1, yy, '#e2bf68'); px1(g, m.x, yy - 1, '#e2bf68'); px1(g, m.x, yy + 1, '#e2bf68'); }
    else px1(g, m.x, yy, f % 2 ? '#e2bf68' : '#fffbe0'); }), 1300);
}
let winT = null;
function winPose() {
  idleOn = false;
  units.forEach((u, i) => {
    const k = SPR[u.k + '_win'] ? u.k + '_win' : u.k + '_1';
    setTimeout(() => {
      draw(u.cv, SPR[k], SPAL[u.k]); u.d.style.transition = 'transform .16s steps(3)'; u.d.style.transform = 'translateY(-14px)';
      setTimeout(() => { u.d.style.transform = ''; }, 170);
      pfxGlitter(u.cv.getBoundingClientRect());
    }, i * 110);
  });
  clearTimeout(winT);
  winT = setTimeout(() => { units.forEach(u => { u.d.style.transition = ''; }); idleOn = true; }, 2600);
}
"""

CSS = """#foe.hit canvas{animation:bhitR .3s steps(2) 3!important}
@keyframes bhitR{0%,100%{filter:none}50%{filter:brightness(.9) sepia(1) saturate(7) hue-rotate(-38deg)}}
#pfx{position:absolute;z-index:8;pointer-events:none;image-rendering:pixelated}
#foe.gone canvas{visibility:hidden}
.dmg{width:auto!important;white-space:nowrap;animation:bdmg2 1.1s steps(22) 1 forwards!important}
.dmg .nw{color:#8ff0ff}
@keyframes bdmg2{0%{transform:translate(-50%,10px) scale(.6);opacity:0}10%{transform:translate(-50%,-16px) scale(1.2);opacity:1}20%{transform:translate(-50%,0) scale(1)}28%{transform:translate(-50%,-6px)}36%{transform:translate(-50%,0)}80%{opacity:1;transform:translate(-50%,0)}100%{transform:translate(-50%,-12px);opacity:0}}"""


def _swap(D, fn, upd):
    base = D['idle']; p = copy.deepcopy(base); p.update(upd); D['idle'] = p
    try:
        return fn('idle').rgb
    finally:
        D['idle'] = base


def win_frames():
    return {'eric_win': _swap(C.ERIC_POSE, C.eric34, dict(arm=[(35, 28), (38.5, 21.5), (39, 15)], sw=[(0.08, -1), 21])),
            'yulun_win': _swap(C.YULUN_POSE, C.yulun34, dict(armR=[(35, 28), (41, 24.5), (46.5, 19)], bow=[(42, 0), (47.5, 19), (43, 38)])),   # 弓舉在身體右側：弓背朝外（敵人那邊）、弦在身體這側
            'karen_win': C.karen34('raise').rgb}


def R(h, old, new):
    assert old in h, old[:60]
    return h.replace(old, new, 1)


def apply(h):
    import uiapply, idle22
    _, _, spr = uiapply._grab(h, 'SPR'); _, _, spal = uiapply._grab(h, 'SPAL')
    for k, rgb in win_frames().items():
        spr[k] = idle22.rows_of(rgb, spal[k.split('_')[0]])
    h = uiapply._put(h, 'SPR', spr); h = uiapply._put(h, 'SPAL', spal)
    # B：Eric 刀光＋火花
    h = R(h, "fxDraw('cleave', 150, 150, f.left + f.width / 2 - 75, f.top + f.height / 2 - 75);",
          "pfxSlash(f.left + f.width / 2, f.top + f.height / 2); pfxSparks(f.left + f.width * .42, f.top + f.height * .55, ['#ffffff', '#bfeaff', '#6aa0ff', '#3a5ab0']);")
    # B：箭尾巴＋金色火花
    h = R(h, "d.style.left = (x - 12) + 'px'; d.style.top = (y - 33) + 'px';",
          "d.style.left = (x - 12) + 'px'; d.style.top = (y - 33) + 'px'; if (k > 0 && k < N) pfxDot(x, y);")
    h = R(h, "fxDraw('slash', 96, 96, x1 - 48, y1 - 48);",
          "pfxSparks(x1, y1, ['#ffffff', '#ffe27a', '#f0a030', '#b5501a'], 14);")
    # E：光柱＋青色火花
    h = R(h, """        bt(() => {
          fxDraw('magic', 122, 128, f.left + f.width / 2 - 61, f.top + f.height / 2 - 64);""",
          """        bt(() => { const sh2 = $('foeShadow').getBoundingClientRect(); pfxPillar(f.left + f.width / 2, sh2.top + sh2.height / 2); }, 800);
        bt(() => {
          pfxSparks(f.left + f.width / 2, f.top + f.height / 2, ['#ffffff', '#c8fbff', '#7ff0ff', '#3aa6d8'], 16);""")
    # D：傷害數字置中、不斷行
    h = R(h, "'</small>' + (v == null ? '初見！' : '$' + nt(v));", "'</small>' + (v == null ? '<span class=\"nw\">初見！</span>' : '$' + nt(v));")
    h = R(h, "d.style.left = (f.left + f.width / 2 - sr.left - st.clientLeft - 34 + (Math.random() * 20 - 10)) + 'px';",
          "d.style.left = (f.left + f.width / 2 - sr.left - st.clientLeft + (Math.random() * 20 - 10)) + 'px';")
    # A＋C：打倒敵人碎掉、勝利姿勢
    h = R(h, "st.appendChild(v); $('foe').classList.add('down');",
          "v.style.visibility = 'hidden'; st.appendChild(v); hitFoe(); setTimeout(pfxShatter, 130); setTimeout(() => { v.style.visibility = ''; winPose(); }, 520);")
    # 重抽：敵人、待機恢復
    h = R(h, "    st.classList.remove('shake'); void st.offsetWidth; st.classList.add('shake');\n    $('foe').classList.remove('on');",
          "    st.classList.remove('shake'); void st.offsetWidth; st.classList.add('shake');\n    clearTimeout(winT); idleOn = true; units.forEach(u => { u.d.style.transition = ''; u.d.style.transform = ''; });\n    $('foe').classList.remove('on', 'gone', 'down');")
    h = h.replace('/* ---- 抽籤 ---- */', JS + '\n/* ---- 抽籤 ---- */', 1)
    h = h.replace('</style>', CSS + '\n</style>', 1)
    return h
