"""v2.2.4 進戰鬥轉場改版（試作三種：螺旋方格 spiral／馬賽克 mosaic／漩渦 swirl）。
原本是 9 條斜黑帶用 CSS scaleX 平滑縮掉（不像像素、中間留一條直的殘影）＋白閃，約 0.3 秒。
做法：把舞台上的圖片和像素圖合成到一張低解析度畫布（snapStage），在上面做效果，蓋在舞台上（#bfx）。
全黑的那一刻換上敵人（onCover），再用新畫面做反向效果打開。
ui221 之後由 build_index 呼叫 apply(h, kind)。"""

JS = r"""
/* ---- 進戰鬥轉場 ---- */
let FXKIND = '%KIND%';
function snapStage(U) {
  const st = $('stage'), sc = st.querySelector('.sc'), R = sc.getBoundingClientRect();
  const W = Math.ceil(R.width / U), H = Math.ceil(R.height / U);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
  g.fillStyle = '#0b0e1c'; g.fillRect(0, 0, W, H);
  st.querySelectorAll('img, canvas').forEach(el => {
    if (el.id === 'bfx') return;
    const r = el.getBoundingClientRect(); if (r.width < 1) return;
    let op = 1, e = el; while (e && e !== st) { op *= +getComputedStyle(e).opacity; e = e.parentElement; }
    if (op < .02) return;
    g.globalAlpha = op;
    try { g.drawImage(el, (r.left - R.left) / U, (r.top - R.top) / U, r.width / U, r.height / U); } catch (_) {}
    g.globalAlpha = 1;
  });
  return c;
}
function encFx(onCover) {
  const st = $('stage'), sc = st.querySelector('.sc');
  let cv = $('bfx');
  if (!cv) { cv = document.createElement('canvas'); cv.id = 'bfx'; st.appendChild(cv); }
  Object.assign(cv.style, { left: sc.offsetLeft + 'px', top: sc.offsetTop + 'px', width: sc.offsetWidth + 'px', height: sc.offsetHeight + 'px', display: 'block' });
  const kind = FXKIND, U = kind === 'swirl' ? 2 : 4;
  const W = Math.ceil(sc.offsetWidth / U), H = Math.ceil(sc.offsetHeight / U);
  cv.width = W; cv.height = H;
  const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
  const DK = '#0b0e1c';
  let snap = snapStage(U), covered = false, t0 = performance.now();
  const cover = () => { if (covered) return; covered = true; onCover && onCover(); requestAnimationFrame(() => { snap = snapStage(U); }); };
  const flash = (t, T) => { const k = Math.floor(t / (T / 4)); if (k === 0 || k === 2) { g.fillStyle = k ? 'rgba(255,255,255,.7)' : '#fff'; g.fillRect(0, 0, W, H); } };

  // ---- 螺旋方格：從四周順時針一圈圈繞進中心蓋滿，再從中心沿原路繞出去打開 ----
  const B = 6, cols = Math.ceil(W / B), rows = Math.ceil(H / B);
  const ord = [];
  { let x0 = 0, y0 = 0, x1 = cols - 1, y1 = rows - 1;
    while (x0 <= x1 && y0 <= y1) {
      for (let x = x0; x <= x1; x++) ord.push([x, y0]);
      for (let y = y0 + 1; y <= y1; y++) ord.push([x1, y]);
      if (y0 < y1) for (let x = x1 - 1; x >= x0; x--) ord.push([x, y1]);
      if (x0 < x1) for (let y = y1 - 1; y > y0; y--) ord.push([x0, y]);
      x0++; y0++; x1--; y1--; } }
  const tile = (c, r, s) => { if (s <= 0) return; const x = c * B + (B - s) / 2, y = r * B + (B - s) / 2;
    g.fillStyle = DK; g.fillRect(x, y, s, s); if (s >= 4) { g.fillStyle = '#1e2850'; g.fillRect(x, y, s, 1); g.fillRect(x, y, 1, s); } };
  const grow = p => [0, 2, 4, 6, 6][Math.max(0, Math.min(4, Math.floor(p * 4)))];
  const spiral = (p, out) => { const n = ord.length;
    ord.forEach(([c, r], i) => { const d = out ? 1 - i / n : i / n, k = (p - d * .8) / .2; tile(c, r, out ? B - grow(k) : grow(k)); }); };
  // ---- 馬賽克：格子越變越粗＋越來越暗 ----
  const tmp = document.createElement('canvas'), tg = tmp.getContext('2d');
  const mosaic = (blk, dark) => { const w = Math.max(1, Math.ceil(W / blk)), h = Math.max(1, Math.ceil(H / blk));
    tmp.width = w; tmp.height = h; tg.imageSmoothingEnabled = true; tg.drawImage(snap, 0, 0, w, h);
    g.drawImage(tmp, 0, 0, w * blk, h * blk); if (dark > 0) { g.fillStyle = 'rgba(11,14,28,' + dark + ')'; g.fillRect(0, 0, W, H); } };
  const MS = [1, 2, 3, 4, 6, 8, 12, 16];
  // ---- 漩渦：往中心扭轉吸進去 ----
  let src = null, srcFor = null; const out = g.createImageData(W, H);
  const swirl = (k, dark) => {
    if (srcFor !== snap) { src = snap.getContext('2d').getImageData(0, 0, W, H).data; srcFor = snap; }
    const cx = W / 2, cy = H / 2, Rm = Math.hypot(cx, cy), o = out.data;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const dx = x - cx, dy = y - cy, r = Math.hypot(dx, dy), f = 1 - r / Rm;
      const a = Math.atan2(dy, dx) + k * 9 * f * f, rr = r * (1 + k * 1.6);
      let sx = Math.round(cx + Math.cos(a) * rr), sy = Math.round(cy + Math.sin(a) * rr), i = (y * W + x) * 4;
      if (sx < 0 || sy < 0 || sx >= W || sy >= H) { o[i] = 11; o[i + 1] = 14; o[i + 2] = 28; o[i + 3] = 255; continue; }
      const j = (sy * W + sx) * 4, m = 1 - dark;
      o[i] = src[j] * m + 11 * dark; o[i + 1] = src[j + 1] * m + 14 * dark; o[i + 2] = src[j + 2] * m + 28 * dark; o[i + 3] = 255;
    }
    g.putImageData(out, 0, 0);
  };
  const q = (p, n) => Math.floor(Math.max(0, Math.min(.999, p)) * n) / n;   // 動畫一格一格跳（像素風）

  const T = { spiral: [110, 420, 60, 380], mosaic: [90, 380, 70, 360], swirl: [90, 440, 60, 380] }[kind];
  (function f(now) {
    const t = now - t0, [a, b, c, d] = T;
    g.clearRect(0, 0, W, H);
    if (t < a) { if (kind !== 'spiral') g.drawImage(snap, 0, 0); flash(t, a); }
    else if (t < a + b) { const p = (t - a) / b;
      if (kind === 'spiral') spiral(p, false);
      else if (kind === 'mosaic') { const i = Math.floor(q(p, MS.length) * MS.length); mosaic(MS[i], Math.max(0, (p - .55) / .45)); }
      else swirl(q(p, 12), Math.max(0, (p - .5) / .5)); }
    else if (t < a + b + c) { g.fillStyle = DK; g.fillRect(0, 0, W, H); cover(); }
    else if (t < a + b + c + d) { cover(); const p = (t - a - b - c) / d;
      if (kind === 'spiral') spiral(p, true);
      else if (kind === 'mosaic') { snap = snapStage(U); const i = MS.length - 1 - Math.floor(q(p, MS.length) * MS.length); mosaic(MS[i], Math.max(0, 1 - p / .45)); }   // 打開時每格重拍，敵人落下、隊伍進場會透過馬賽克看到
      else swirl(-q(1 - p, 10) * .8, Math.max(0, 1 - p / .5)); }
    else { cv.style.display = 'none'; return; }
    requestAnimationFrame(f);
  })(t0);
}
"""

CSS = "#bfx{position:absolute;z-index:7;pointer-events:none;image-rendering:pixelated;display:none}\n#bwipe,#bflash{display:none!important}"


def apply(h, kind='spiral'):
    old = "    ['bflash', 'bwipe'].forEach(id => { $(id).classList.remove('go'); void $(id).offsetWidth; $(id).classList.add('go'); });\n"
    assert old in h
    h = h.replace(old, "", 1)
    old2 = """      setTimeout(() => u.classList.add('in'), 240 + i * 70);
    });
    setTimeout(() => {"""
    assert old2 in h
    h = h.replace(old2, """      setTimeout(() => u.classList.add('in'), 680 + i * 70);
    });
    encFx(() => {""", 1)
    old3 = """      rolling = false;
    }, 330);"""
    assert old3 in h
    h = h.replace(old3, """      rolling = false;
    });""", 1)
    h = h.replace('/* ---- 抽籤 ---- */', JS.replace('%KIND%', kind) + '\n/* ---- 抽籤 ---- */', 1)
    h = h.replace('</style>', CSS + '\n</style>', 1)
    return h
