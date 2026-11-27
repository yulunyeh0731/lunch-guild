"""v2.2.7 逃跑有意義＋逃跑動畫＋省電。
- 原本「逃跑」只是講一句台詞再重抽，跟「遭遇一家店」一樣，還可能又抽到同一家。
  改成：逃跑 = 這家今天先不要。逃過的店今天不會再被抽到（兩顆按鈕都一樣），隔天自動恢復；整份名單都逃光了就照常全抽。
  逃過的名單只存在這台手機（localStorage 'lunch-guild-fled'），不同步。
- 逃跑動畫：轉身換成正面斜角（面向左下）的站姿，再用正面跑步兩格交替，一步一步往左下（朝鏡頭）斜斜跑出畫面、邊跑邊彈，
  腳邊揚起像素煙塵（#pfx），接著馬賽克轉場抽下一家。正面圖在 `src/front22.py`（臉照頭像、細節照背面）。
  （試過：直接往左下移＝倒退跑；左右翻面往左跑＝還是背面）
- 省電：待機動畫只有在遭遇頁、而且 app 在前景時才每格重畫；其他時候每 0.4 秒看一次就好。
build_index 在 atk22 之後呼叫 apply(h)。"""

JS = r"""
/* ---- 逃跑：今天先不要這家 ---- */
const FLED_LS = 'lunch-guild-fled';
function fledList() {
  try { const o = JSON.parse(localStorage.getItem(FLED_LS) || '{}'); return o.d === today() ? (o.n || []) : []; } catch (_) { return []; }
}
function addFled(name) {
  const n = fledList(); if (!n.includes(name)) n.push(name);
  try { localStorage.setItem(FLED_LS, JSON.stringify({ d: today(), n })); } catch (_) {}
}
function pfxDust(cx, cy) {
  pfxInit(); const [x, y] = c2u(cx, cy);
  const ps = [...Array(5)].map(() => ({ dx: Math.random() * 8 - 4, v: .3 + Math.random() * .5, s: Math.random() < .5 ? 2 : 3 }));
  pfxAdd((g, t) => { const f = t / 50; ps.forEach(o => {
    const c = f < 2 ? '#e8e0d0' : f < 4 ? '#b8ae9c' : '#857c6c';
    px1(g, x + o.dx * (1 + f * .3), y - f * o.v, c, f < 3 ? o.s : o.s - 1); }); }, 320);
}
function runAway(done) {
  // 轉身（換成正面斜角站姿）→ 正面跑步兩格交替，一步一步往左下（朝鏡頭）斜斜跑出畫面、邊跑邊彈
  idleOn = false;
  units.forEach((u, i) => {
    setTimeout(() => {
      u.d.style.transition = 'none';
      if (SPR[u.k + '_fs']) draw(u.cv, SPR[u.k + '_fs'], SPAL[u.k]);
      for (let k = 1; k <= 8; k++) setTimeout(() => {
        const f = SPR[u.k + (k % 2 ? '_fr1' : '_fr2')]; if (f) draw(u.cv, f, SPAL[u.k]);
        u.d.style.transform = 'translate(' + (-32 * k) + 'px,' + (16 * k - (k % 2 ? 6 : 0)) + 'px)';
        const r = u.cv.getBoundingClientRect(); if (k % 2 === 0) pfxDust(r.left + r.width * .45, r.bottom - 6);
      }, 110 + k * 75);
    }, i * 70);
  });
  setTimeout(done, 860);
}
"""


def R(h, old, new):
    assert old in h, old[:70]
    return h.replace(old, new, 1)


def apply(h):
    import uiapply, idle22, front22
    _, _, spr = uiapply._grab(h, 'SPR'); _, _, spal = uiapply._grab(h, 'SPAL')
    for who, fn in (('yulun', front22.yulun_front), ('eric', front22.eric_front), ('karen', front22.karen_front)):
        for key, pose in (('_fs', 'stand'), ('_fr1', 'run1'), ('_fr2', 'run2')):
            spr[who + key] = idle22.rows_of(fn(pose).rgb, spal[who])
    h = uiapply._put(h, 'SPR', spr); h = uiapply._put(h, 'SPAL', spal)
    # pickShop：排除今天逃過的（全部逃光就不排除）
    h = R(h, "  let pool = all.filter(s => rec[s.name] == null || rec[s.name] >= cd);",
          "  const fled = fledList(), all0 = all.filter(s => !fled.includes(s.name));\n"
          "  let pool = (all0.length ? all0 : all).filter(s => rec[s.name] == null || rec[s.name] >= cd);")
    h = R(h, "  const relaxed = !pool.length; if (relaxed) pool = all;",
          "  const relaxed = !pool.length; if (relaxed) pool = all0.length ? all0 : all;")
    # 逃跑按鈕
    h = R(h, """  if (battleMode() && foeShop) {
    type($('talk'), RUNLINES[Math.floor(Math.random() * RUNLINES.length)]);
    rolling = true; setTimeout(() => { rolling = false; roll(); }, 700);
  } else roll();""", """  if (battleMode() && foeShop) {
    addFled(foeShop.name);
    type($('talk'), RUNLINES[Math.floor(Math.random() * RUNLINES.length)] + '\\u3000今天不會再遇到「' + foeShop.name + '」。');
    rolling = true; runAway(() => { rolling = false; roll(); });
  } else { if (foeShop && !decided) addFled(foeShop.name); roll(); }""")
    # 遇敵台詞標逃過幾家
    # 省電：不在遭遇頁或在背景時，待機動畫不重畫
    h = R(h, "(function idleTick(now) {\n  now = now || 0;",
          "(function idleTick(now) {\n  if (document.hidden || !$('s-enc').classList.contains('on')) { setTimeout(() => requestAnimationFrame(idleTick), 400); return; }\n  now = now || 0;")
    h = h.replace('/* ---- 抽籤 ---- */', JS + '\n/* ---- 抽籤 ---- */', 1)
    return h
