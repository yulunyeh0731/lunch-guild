"""v2.0 口袋名單整理：休息中、整理名單面板、記帳時勾選加入、改名合併。
build_index.py 在 app34.apply() 之後呼叫 apply(h)。"""
import re

MOON = ['................', '.............2..', '....111.....232.', '...12241.....2..', '..13241.........',
        '.133241.........', '.133241.........', '1333241.........', '1333241.........', '13332241........',
        '1332224411111...', '.1322222444441..', '.1322222222221..', '..12222222221...', '...122222221....',
        '....1111111.....']

CHECK = ['................', '................', '.............11.', '............1331', '...........13321',
         '.11.......13321.', '1331.....13321..', '13321...13321...', '.13321.13321....', '..1333333321....',
         '...133333321....', '....1333321.....', '.....13321......', '......121.......', '.......1........', '................']

CSS = r"""
/* ---- v2.0 口袋名單 ---- */
.pkhint{font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 0}
.mask.full{padding:0;align-items:stretch}
.mask.full .win{max-width:520px;height:100%;max-height:none;display:flex;flex-direction:column;padding-left:12px;padding-right:12px;
  padding-top:calc(env(safe-area-inset-top) + 12px);padding-bottom:calc(env(safe-area-inset-bottom) + 12px)}
.pkx{font-size:11px;color:var(--gold);padding:4px 10px;border:var(--px) solid var(--gold2);margin-left:6px;letter-spacing:1px;flex:none}
.pkx[aria-pressed=true]{background:var(--gold2);color:#1a1508}
.pktool{display:flex;flex-direction:column;gap:7px;margin-bottom:10px;flex:none}
.pktool .inp{font-size:16px}
.seg.row{display:flex;gap:6px}
.seg button small{font-size:11px;color:var(--dim);margin-left:3px}
.seg button[aria-pressed=true] small{color:var(--gold)}
.seg.sm button{font-size:11px;padding:6px 2px;letter-spacing:1px}
.pksort{display:flex;align-items:center;gap:8px}
.pksort .lbl{margin:0;flex:none}
.pksort .seg{flex:1}
.pkgrid{flex:1;overflow:auto;display:grid;grid-template-columns:1fr 1fr;gap:6px;align-content:start;
  margin:0 -6px;padding:4px 6px 8px;-webkit-overflow-scrolling:touch}
.pk{position:relative;display:flex;gap:6px;align-items:center;padding:7px 4px 6px 5px;
  background:#141b36;border:var(--px) solid #364268;text-align:left;min-width:0}
.pk canvas.f{width:24px;height:24px;flex:none}
.pk .t{flex:1;min-width:0}
.pk .n{font-size:22px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pk .s{font-size:11px;color:var(--dim);line-height:1.4;white-space:nowrap;overflow:hidden;padding-right:18px}
.pk .z{position:absolute;right:1px;bottom:1px;width:26px;height:24px;display:flex;align-items:center;justify-content:center}
.pk .z canvas{width:16px;height:16px;opacity:.3}
.pk .z span{display:none}
.pk.off{background:rgba(14,18,36,.9);border-style:dashed;border-color:#2c3558}
.pk.off .n{color:var(--dim)}
.pk.off canvas.f{opacity:.4;filter:grayscale(.85)}
.pk.off .z canvas{opacity:1}
.pk .ck{display:none;position:absolute;left:-5px;top:-5px;width:20px;height:20px;background:#0b0e1c;
  border:var(--px) solid #6a7aa8;z-index:2}
.pk .ck canvas{width:16px;height:16px;display:none}
.pkgrid.multi .pk .ck{display:block}
.pkgrid.multi .pk .z{display:none}
.pk.sel{border-color:var(--gold);border-style:solid;background:#26315a}
.pk.sel .ck{border-color:var(--gold)}
.pk.sel .ck canvas{display:block}
.pkbar{display:none;flex:none;gap:6px;align-items:center;padding-top:10px;margin-top:2px;
  border-top:var(--px) solid rgba(226,191,104,.3);font-size:11px;color:var(--dim)}
.pkbar.on{display:flex}
.pkbar b{color:var(--gold);font-size:22px;font-weight:normal;margin:0 2px}
.pkbar .sp{flex:1}
.pkbar .btn{width:auto;margin:0;padding:6px 10px}
.pkempty{grid-column:1/-1}
.pkchk{display:none;align-items:center;gap:8px;margin-top:7px;font-size:11px;color:var(--text);cursor:pointer}
.pkchk.on{display:flex}
.pkchk input{position:absolute;opacity:0;pointer-events:none}
.pkchk .bx{width:22px;height:22px;flex:none;background:#0b0e1c;border:var(--px) solid #6a7aa8;display:flex;align-items:center;justify-content:center}
.pkchk .bx canvas{width:16px;height:16px;display:none}
.pkchk input:checked+.bx{border-color:var(--gold)}
.pkchk input:checked+.bx canvas{display:block}
.pkchk small{color:var(--dim);font-size:11px}
.edstat{font-size:11px;color:var(--dim);margin:-4px 0 12px}
"""

ENC_OLD = """    <div id="shops"></div>
    <button class="btn sm" id="moreShops" style="display:none"></button>"""
ENC_NEW = """    <button class="btn sm" id="btnPocket" style="margin-top:0">整理名單 ▸</button>
    <div class="pkhint" id="pkHint"></div>"""

SHEET = """<div class="mask full" id="mPocket"><div class="win">
  <div class="hd" data-ic="bowl"><span class="l">整理名單</span>
    <button class="pkx" id="pkMulti" aria-pressed="false">多選</button>
    <button class="pkx" id="pkDone">完成</button></div>
  <div class="pktool">
    <input class="inp" id="pkQ" placeholder="搜尋店名" enterkeyhint="search">
    <div class="seg row sm" id="pkF">
      <button data-v="on">抽籤中<small></small></button><button data-v="off">休息中<small></small></button><button data-v="all">全部<small></small></button>
    </div>
    <div class="pksort"><span class="lbl">排序</span>
      <div class="seg row sm" id="pkS"><button data-v="old">最久沒去</button><button data-v="freq">最常去</button><button data-v="name">店名</button></div>
    </div>
  </div>
  <div class="pkgrid" id="pkGrid"></div>
  <div class="pkbar" id="pkBar">已選<b id="pkN">0</b>家<span class="sp"></span>
    <button class="btn sm" id="pkRest">休息</button><button class="btn sm" id="pkWake">回抽籤</button>
    <button class="btn sm" id="pkDel" style="color:var(--loss)">移除</button></div>
</div></div>

"""

ED_OLD = """  <div class="hd" data-ic="bowl"><span class="l">編輯店家</span></div>
  <div class="field">
    <div class="lbl">名字</div>
    <input class="inp" id="edName">
  </div>"""
ED_NEW = """  <div class="hd" data-ic="bowl"><span class="l">編輯店家</span></div>
  <div class="edstat" id="edStat"></div>
  <div class="field">
    <div class="lbl">名字</div>
    <input class="inp" id="edName">
    <div class="note" id="edMerge" style="display:none;margin:8px 0 0"></div>
  </div>
  <div class="field">
    <div class="lbl">抽籤（休息中的店不會被抽到，紀錄照樣保留）</div>
    <div class="seg row" id="edOff"><button data-v="0">抽籤中</button><button data-v="1">休息中</button></div>
  </div>"""

LOG_OLD = """        <datalist id="shoplist"></datalist>
      </div>"""
LOG_NEW = """        <datalist id="shoplist"></datalist>
      </div>
      <label class="pkchk" id="pkChkRow"><input type="checkbox" id="fAddPk"><span class="bx"></span>
        <span>加入口袋名單 <small id="pkChkSub">（之後抽籤會抽到）</small></span></label>"""

# ---------- JS ----------
RENDER_RE = re.compile(r"  // 口袋名單：最久沒吃的排前面.*?\} else more\.style\.display = 'none';\n", re.S)

PICK_OLD = """  const all = alive(S.shops);
  if (!all.length) return null;
  const rec = lastEaten()"""
PICK_NEW = """  const all = alive(S.shops).filter(s => !+s.off);   // 休息中的不抽
  if (!all.length) return null;
  const rec = lastEaten()"""
ROLL_OLD = "if (!p) { toast('先在下面加幾家店'); return; }"
ROLL_NEW = "if (!p) { toast(alive(S.shops).length ? '名單上的店都在休息中' : '先在下面加幾家店'); return; }"

SAVE_OLD = "  if (!alive(S.shops).some(s => s.name === shop)) put('shops', { id: uid(), name: shop, icon: cur, by: S.me });\n  else {"
SAVE_NEW = ("  const typed = $('shop').value.trim();\n"
            "  if (!alive(S.shops).some(s => s.name === shop)) { if (typed && $('pkChkRow').classList.contains('on') && $('fAddPk').checked) put('shops', { id: uid(), name: shop, icon: cur, by: S.me, off: 0 }); }\n"
            "  else {")

ED_SAVE_RE = re.compile(r"\$\('edSave'\)\.onclick = \(\) => \{.*?\n\};\n", re.S)
ED_SAVE_NEW = r"""$('edSave').onclick = () => {
  if (!edShop) return;
  const newName = $('edName').value.trim() || edShop.name;
  const oldName = edShop.name, oldIcon = edShop.icon;
  const twin = newName !== oldName && alive(S.shops).find(s => s.name === newName && s.id !== edShop.id);
  if (twin) {                                   // 改成已經有的店名 → 合併
    if (!confirm('已經有「' + newName + '」了。\n要把「' + oldName + '」合併進去嗎？以前的紀錄會全部算到「' + newName + '」。')) return;
    put('shops', Object.assign({}, edShop, { deleted: 1 }));
    const hit = alive(S.entries).filter(e => e.shop === oldName);
    if (hit.length) putMany('entries', hit.map(e => Object.assign({}, e, { shop: newName, icon: twin.icon })));
    $('mShop').classList.remove('on'); edShop = null; toast('合併好了'); return;
  }
  put('shops', Object.assign({}, edShop, { name: newName, icon: edIcon, off: edOff }));
  // 連動：這家店已記過的紀錄一起換圖／改名
  if (newName !== oldName || edIcon !== oldIcon) {
    const hit = alive(S.entries).filter(e => e.shop === oldName);
    if (hit.length) putMany('entries', hit.map(e => Object.assign({}, e, { shop: newName, icon: edIcon })));
  }
  $('mShop').classList.remove('on'); edShop = null; toast('改好了');
};
"""

OPEN_OLD = """  edShop = s; edIcon = ic(s.icon);
  $('edName').value = s.name;"""
OPEN_NEW = """  edShop = s; edIcon = ic(s.icon); edOff = +s.off ? 1 : 0;
  $('edName').value = s.name; edMergeNote(); paintOff();
  const st = pkStats()[s.name];
  $('edStat').textContent = st ? '去過 ' + st.n + ' 次・上次' + (st.last === 0 ? '今天' : st.last === 1 ? '昨天' : ' ' + st.last + ' 天前') : '還沒記過這家';"""

ADD_OLD = "  if (alive(S.shops).some(s => s.name === v)) { toast('已經有這家了'); return; }"
ADD_NEW = "  const ex = alive(S.shops).find(s => s.name === v);\n  if (ex) { toast(+ex.off ? '已經有這家了（休息中，到整理名單打開）' : '已經有這家了'); return; }"

MORE_OLD = "$('moreShops').onclick = () => { shopsOpen = !shopsOpen; render(); };"

JS = r"""
/* ================= v2.0 口袋名單 ================= */
ICON.moon = __MOON__;
ICON.check = __CHECK__;
let edOff = 0;
const pk = { q: '', f: 'on', sort: 'old', multi: false, sel: new Set() };
function pkStats() {
  const r = {};
  alive(S.entries).forEach(e => {
    if (!e.shop) return;
    const o = r[e.shop] || (r[e.shop] = { n: 0, last: null });
    o.n++; const d = dayDiff(e.date, today());
    if (o.last == null || d < o.last) o.last = d;
  });
  return r;
}
const pkWhen = d => d == null ? '沒去過' : d === 0 ? '今天' : d === 1 ? '昨天' : d + '天前';
function renderPocket() {
  const all = alive(S.shops), off = all.filter(s => +s.off).length;
  $('shopCnt').textContent = all.length ? all.length + ' 家' + (off ? '・休息中 ' + off + ' 家' : '') : '';
  $('pkHint').textContent = all.length
    ? '抽籤會跳過「休息中」的店' + (+S.cfg.cool ? '，和 ' + S.cfg.cool + ' 天內吃過的。' : '。')
    : '還沒有店家。加幾家常吃的進來。';
  if (!$('mPocket').classList.contains('on')) return;
  const st = pkStats(), q = pk.q.trim().toLowerCase();
  const cnt = { on: all.length - off, off, all: all.length };
  $$('#pkF button').forEach(b => { b.setAttribute('aria-pressed', b.dataset.v === pk.f); b.querySelector('small').textContent = cnt[b.dataset.v]; });
  $$('#pkS button').forEach(b => b.setAttribute('aria-pressed', b.dataset.v === pk.sort));
  $('pkMulti').setAttribute('aria-pressed', pk.multi);
  let list = all.filter(s => pk.f === 'all' || (pk.f === 'off') === !!+s.off)
    .filter(s => !q || s.name.toLowerCase().includes(q));
  const L = s => (st[s.name] || {}).last, Nn = s => (st[s.name] || {}).n || 0;
  if (pk.sort === 'old') list.sort((a, b) => (L(b) == null ? 9e9 : L(b)) - (L(a) == null ? 9e9 : L(a)));
  else if (pk.sort === 'freq') list.sort((a, b) => Nn(b) - Nn(a) || (L(a) ?? 9e9) - (L(b) ?? 9e9));
  else list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'));
  const g = $('pkGrid'); g.innerHTML = ''; g.classList.toggle('multi', pk.multi);
  if (!list.length) g.innerHTML = '<div class="zero pkempty">' + (q ? '找不到「' + esc(pk.q.trim()) + '」' : pk.f === 'off' ? '沒有休息中的店。' : '這裡是空的。') + '</div>';
  list.forEach(s => {
    const d = document.createElement('button');
    d.className = 'pk' + (+s.off ? ' off' : '') + (pk.sel.has(s.id) ? ' sel' : '');
    const ck = document.createElement('i'); ck.className = 'ck'; ck.appendChild(uic('check', 16));
    const f = pxc('f', s.icon || 'bento', 24); f.classList.add('f');
    const t = document.createElement('div'); t.className = 't';
    const o = st[s.name];
    t.innerHTML = '<div class="n">' + esc(s.name) + '</div><div class="s">' + (o ? o.n + '次・' + pkWhen(o.last) : '沒去過') + '</div>';
    const z = document.createElement('span'); z.className = 'z';
    z.appendChild(uic('moon', 16, +s.off ? UGOLD : UDIM));
    const zl = document.createElement('span'); zl.textContent = +s.off ? '休息中' : '抽籤中'; z.appendChild(zl);
    z.onclick = ev => {
      ev.stopPropagation();
      const now = +s.off ? 0 : 1;
      put('shops', Object.assign({}, s, { off: now }));
      toast(now ? '「' + s.name + '」休息中，不會被抽到' : '「' + s.name + '」回到抽籤');
    };
    d.append(ck, f, t, z);
    d.onclick = () => {
      if (pk.multi) { pk.sel.has(s.id) ? pk.sel.delete(s.id) : pk.sel.add(s.id); renderPocket(); }
      else openShop(s);
    };
    g.appendChild(d);
  });
  [...pk.sel].forEach(id => { if (!all.some(s => s.id === id)) pk.sel.delete(id); });
  $('pkBar').classList.toggle('on', pk.multi);
  $('pkN').textContent = pk.sel.size;
  ['pkRest', 'pkWake', 'pkDel'].forEach(id => $(id).disabled = !pk.sel.size);
}
$('btnPocket').onclick = () => { pk.multi = false; pk.sel.clear(); pk.q = ''; $('pkQ').value = ''; $('mPocket').classList.add('on'); renderPocket(); $('pkGrid').scrollTop = 0; };
$('pkDone').onclick = () => { $('mPocket').classList.remove('on'); render(); };
$('pkQ').oninput = () => { pk.q = $('pkQ').value; renderPocket(); };
$$('#pkF button').forEach(b => b.onclick = () => { pk.f = b.dataset.v; renderPocket(); });
$$('#pkS button').forEach(b => b.onclick = () => { pk.sort = b.dataset.v; renderPocket(); });
$('pkMulti').onclick = () => { pk.multi = !pk.multi; pk.sel.clear(); renderPocket(); };
const pkPick = () => alive(S.shops).filter(s => pk.sel.has(s.id));
$('pkRest').onclick = () => { const l = pkPick(); if (!l.length) return; putMany('shops', l.map(s => Object.assign({}, s, { off: 1 }))); pk.sel.clear(); toast(l.length + ' 家改成休息中'); };
$('pkWake').onclick = () => { const l = pkPick(); if (!l.length) return; putMany('shops', l.map(s => Object.assign({}, s, { off: 0 }))); pk.sel.clear(); toast(l.length + ' 家回到抽籤'); };
$('pkDel').onclick = () => {
  const l = pkPick(); if (!l.length) return;
  if (!confirm('把這 ' + l.length + ' 家從名單移除？（已記過的帳不受影響）')) return;
  putMany('shops', l.map(s => Object.assign({}, s, { deleted: 1 }))); pk.sel.clear(); toast('移除了 ' + l.length + ' 家');
};
// 編輯店家：抽籤開關、改名撞名提示
function paintOff() { $$('#edOff button').forEach(b => b.setAttribute('aria-pressed', +b.dataset.v === edOff)); }
$$('#edOff button').forEach(b => b.onclick = () => { edOff = +b.dataset.v; paintOff(); });
function edMergeNote() {
  const v = $('edName').value.trim(), n = $('edMerge');
  const twin = edShop && v && v !== edShop.name && alive(S.shops).find(s => s.name === v && s.id !== edShop.id);
  n.style.display = twin ? '' : 'none';
  if (twin) n.textContent = '已經有「' + v + '」了，儲存會把兩家合併，紀錄全部算到「' + v + '」。';
  $('edSave').textContent = twin ? '合併' : '儲存';
}
$('edName').addEventListener('input', edMergeNote);
// 記錄頁：新店名才出現「加入口袋名單」
function updPkChk() {
  const v = $('shop').value.trim(), row = $('pkChkRow');
  const isNew = !!v && !alive(S.shops).some(s => s.name === v);
  if (!isNew) { row.classList.remove('on'); row.dataset.v = ''; return; }
  if (row.dataset.v !== v || row.dataset.m !== mealId()) {     // 換了店名或餐別才重設預設值
    const gone = (S.shops || []).some(s => s.deleted && s.name === v);
    $('fAddPk').checked = !editing && !gone && mealId() === 'lunch';
    $('pkChkSub').textContent = gone ? '（之前移除過）' : mealId() === 'lunch' ? '（之後抽籤會抽到）' : '（點心、晚餐預設不加）';
    row.dataset.v = v; row.dataset.m = mealId();
  }
  row.classList.add('on');
}
$('shop').addEventListener('input', updPkChk);
document.querySelector('#pkChkRow .bx').appendChild(uic('check', 16));
$('fMeal').addEventListener('click', () => setTimeout(updPkChk, 0));
"""

FORM_HOOKS = [
    ("if (!editing && foeShop) { $('shop').value = foeShop.name; paint(ic(foeShop.icon), false); }",
     "if (!editing && foeShop) { $('shop').value = foeShop.name; paint(ic(foeShop.icon), false); updPkChk(); }"),
    # resetForm / editEntry / decide 之後更新勾選列
    ("  $('editRow').style.display = 'none'; paint('bento', false); setMeal('lunch');\n}",
     "  $('editRow').style.display = 'none'; paint('bento', false); setMeal('lunch');\n  if ($('pkChkRow')) updPkChk();\n}"),
    ("  $('editRow').style.display = ''; scrollTo(0, 0);\n}",
     "  $('editRow').style.display = ''; scrollTo(0, 0); updPkChk();\n}"),
]


def rep(h, a, b, n=1):
    assert h.count(a) == n, ('pattern count', h.count(a), a[:80])
    return h.replace(a, b)


def apply(h):
    h = rep(h, '</style>', CSS + '</style>')
    h = rep(h, ENC_OLD, ENC_NEW)
    h = rep(h, '<div class="mask" id="mShop">', SHEET + '<div class="mask" id="mShop">')
    h = rep(h, ED_OLD, ED_NEW)
    h = rep(h, LOG_OLD, LOG_NEW)
    assert len(RENDER_RE.findall(h)) == 1
    h = RENDER_RE.sub('  renderPocket();\n', h)
    h = rep(h, PICK_OLD, PICK_NEW)
    h = rep(h, ROLL_OLD, ROLL_NEW)
    h = rep(h, SAVE_OLD, SAVE_NEW)
    assert len(ED_SAVE_RE.findall(h)) == 1
    h = ED_SAVE_RE.sub(lambda m: ED_SAVE_NEW, h)
    h = rep(h, OPEN_OLD, OPEN_NEW)
    h = rep(h, ADD_OLD, ADD_NEW)
    h = rep(h, MORE_OLD, '')
    for a, b in FORM_HOOKS:
        h = rep(h, a, b)
    js = JS.replace('__MOON__', repr(MOON)).replace('__CHECK__', repr(CHECK))
    h = rep(h, '/* ================= 啟動 ================= */', js + '\n/* ================= 啟動 ================= */')
    return h
