"""v2.0.3 加入公會：API 網址內建，只要打通關密語。build_index.py 在 appicon 之後呼叫 apply(h)。
網址放在公開的 repo 沒關係：沒有通關密語，後端一律回 bad key。"""

DEFAULT_URL = 'https://script.google.com/macros/s/AKfycbyfjMo1YNka--IyzYARuIWRHHW_OQZr2ZjOACI1sNKyKJ1Rd9tbSyB66VRLA-mLv5w70g/exec'

HTML_OLD = """    <div class="field">
      <div class="lbl">API 網址（Apps Script 部署後的 /exec）</div>
      <input class="inp s" id="setUrl" placeholder="https://script.google.com/macros/s/..../exec" autocapitalize="off" autocorrect="off" spellcheck="false">
    </div>
    <div class="field">
      <div class="lbl">通關密語（要和 Code.gs 裡的 SECRET 一樣）</div>
      <input class="inp s" id="setKey" autocapitalize="off" autocorrect="off" spellcheck="false">
    </div>
    <button class="btn gold" id="setGo">連線</button>"""
HTML_NEW = """    <div class="field">
      <div class="lbl">通關密語</div>
      <input class="inp s" id="setKey" autocapitalize="off" autocorrect="off" spellcheck="false" enterkeyhint="go">
    </div>
    <div class="field" id="setUrlBox" style="display:none">
      <div class="lbl">API 網址（Apps Script 部署後的 /exec）</div>
      <input class="inp s" id="setUrl" value="__URL__" autocapitalize="off" autocorrect="off" spellcheck="false">
    </div>
    <button class="btn gold" id="setGo">連線</button>
    <button class="btn sm" id="setUrlTgl" style="margin-top:8px">改用別的網址</button>"""

JS_OLD = """$('setGo').onclick = async () => {
  const u = $('setUrl').value.trim(), k = $('setKey').value.trim();
  if (!u || !k) { toast('兩格都要填'); return; }"""
JS_NEW = """const DEFAULT_URL = '__URL__';
$('setUrlTgl').onclick = () => { $('setUrlBox').style.display = ''; $('setUrlTgl').style.display = 'none'; };
$('setKey').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); $('setGo').click(); } });
$('setGo').onclick = async () => {
  const u = $('setUrl').value.trim() || DEFAULT_URL, k = $('setKey').value.trim();
  if (!k) { toast('先打通關密語'); return; }"""

ERR_OLD = "  } catch (e) { toast('連不上：' + e.message); setSync('bad', '連線失敗'); }"
ERR_NEW = "  } catch (e) { toast(e.message === 'bad key' ? '通關密語不對' : '連不上：' + e.message); setSync('bad', '連線失敗'); }"


def apply(h):
    for a, b in ((HTML_OLD, HTML_NEW), (JS_OLD, JS_NEW), (ERR_OLD, ERR_NEW)):
        assert h.count(a) == 1, a[:60]
        h = h.replace(a, b.replace('__URL__', DEFAULT_URL))
    return h
