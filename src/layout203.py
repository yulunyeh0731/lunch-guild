"""v2.0.4 遭遇頁塞進一個螢幕：按鈕只留一排、矮螢幕自動把戰鬥畫面上方裁掉一點。
build_index.py 在 join20 之後呼叫 apply(h)。"""

CSS = r"""
/* ---- v2.0.4 遭遇頁一屏 ---- */
.stage .sc{position:absolute;left:0;right:0;bottom:0;height:436px}
/* 戰鬥框內側原本透出舞台底色（淺藍）：底色只鋪在框內，跟其他視窗一樣 */
.stage{background-clip:padding-box;border-image:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAUUlEQVR4XmPk4hH7z0ACYAGpvbE5iCgtGr7rIBpAYMaSE3g1ZcRYgOXhGkCgbe4FRmy6qpIN4M5mwmssFjAcNKCEEnJo4AJwDbBwJgQYSU0aAHvaD3+FHo9SAAAAAElFTkSuQmCC) 4 repeat}
/* ↑ 原本的框圖右邊少了金色和暗金兩格（只剩黑線），右側金框一直不見；補齊成左右對稱 */
/* 螢幕比背景圖寬時（iPhone 16 Pro Max 寬 440），左右兩邊原本露出淺藍底色：改成圖片左右接續鋪滿 */
.stage .sc,#bg{background-repeat:repeat-x;background-position:center bottom;image-rendering:pixelated}
.stage .sc{background-size:384px auto}
#bg{background-size:432px auto}
/* 間距縮小、按鈕扁一點 */
#s-enc .stage{margin-bottom:8px}
#s-enc > .win{padding-top:10px;padding-bottom:10px;margin-bottom:8px}
#s-enc .btn{padding-top:6px;padding-bottom:6px}
#s-enc #btnRoll{margin-top:0}
#s-enc #encRow .btn{margin-top:8px}
/* 還是放不下（較矮的手機）才改成一排：抽到之後收起「遭遇一家店」 */
#s-enc.onerow.hasfoe #btnRoll{display:none}
#s-enc.onerow:not(.hasfoe) #encRow{display:none}
"""

JS = r"""
/* ================= v2.0.4 遭遇頁一屏 ================= */
// 舞台內容包進一層、貼齊底部：舞台變矮時只裁掉上方（店家屋頂），人物、敵人位置不變
(function () {
  const st = $('stage'), w = document.createElement('div'); w.className = 'sc';
  while (st.firstChild) w.appendChild(st.firstChild);
  st.appendChild(w);
  $('btnOk').parentElement.id = 'encRow';
  const bgi = st.querySelector('.bgi'); if (bgi) w.style.backgroundImage = 'url(' + bgi.src + ')';
  const pg = document.querySelector('#bg img'); if (pg) $('bg').style.backgroundImage = 'url(' + pg.src + ')';
})();
// 還沒抽之前只有「遭遇一家店」；抽到之後換成「就這家／逃跑」（逃跑就是再抽一次）
function encButtons() { $('s-enc').classList.toggle('hasfoe', !!foeShop); }
// 按鈕被底部選單蓋住時，把舞台變矮（最多裁 60px，敵人在上方 64px 處，不會被切到）
function fitStage() {
  const st = $('stage'), enc = $('s-enc');
  if (!st.offsetParent) return;
  st.style.height = ''; enc.classList.remove('onerow');
  const navH = document.querySelector('nav').getBoundingClientRect().height;
  const overBy = () => { const last = enc.classList.contains('onerow') && !foeShop ? $('btnRoll') : $('encRow');
    return last.getBoundingClientRect().bottom + scrollY + 8 - (innerHeight - navH); };
  let over = overBy();
  if (over > 60) { enc.classList.add('onerow'); over = overBy(); }
  if (over > 0) st.style.height = Math.max(400, 460 - Math.ceil(over)) + 'px';
}
addEventListener('resize', fitStage);
"""

HOOKS = [
    ("function showFoe(s, rec, relaxed) {\n  foeShop = s;",
     "function showFoe(s, rec, relaxed) {\n  foeShop = s; encButtons();"),
]

GO_WRAP = """
{ const _go = go; go = function (k) { const r = _go.apply(this, arguments); if (k === 'enc') { encButtons(); requestAnimationFrame(fitStage); } return r; }; }
encButtons();
"""


def apply(h):
    assert h.count('</style>') == 1
    h = h.replace('</style>', CSS + '</style>')
    for a, b in HOOKS:
        assert h.count(a) == 1, a
        h = h.replace(a, b)
    mark = '/* ================= 啟動 ================= */'
    assert h.count(mark) == 1
    return h.replace(mark, JS + GO_WRAP + '\n' + mark)
