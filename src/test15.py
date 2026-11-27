"""v1.5 修正的流程測試：python3 src/test15.py（先跑 build_index.py 產生 src/index-test.html）"""
import pathlib
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
url = 'file://' + str(HERE / 'index-test.html')
ok = lambda c, m: print(('PASS ' if c else 'FAIL ') + m)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(url); pg.wait_for_timeout(1500)
    J = pg.evaluate
    J("go('enc')"); pg.wait_for_timeout(300)
    # --- 戰鬥打完不跳頁 ---
    J("$('btnRoll').click(); scrollTo(0,0)"); pg.wait_for_timeout(800)
    shop0 = J("$('shop').value")
    J("$('btnOk').click(); scrollTo(0,0)"); pg.wait_for_timeout(6500)
    st = J("({sec: document.querySelector('.scr.on').id, ok: $('btnOk').textContent, no: $('btnNo').textContent, shop: $('shop').value, foe: foeShop.name, talk: $('talk').textContent})")
    ok(st['sec'] == 's-enc', '打完停在遭遇畫面 ' + st['sec'])
    ok(st['ok'] == '記一筆' and st['no'] == '再抽一次', '按鈕變成 記一筆/再抽一次')
    ok(st['shop'] == st['foe'], '店名已填進記錄表單 ' + st['shop'])
    ok(shop0 != st['foe'] or shop0 == '', '抽店時不先覆蓋表單（抽完前=%r）' % shop0)
    r = J("(()=>{const a=$('stage').getBoundingClientRect(), c=$('btnNo').getBoundingClientRect();return [a.x,a.y,a.width,c.bottom-a.y]})()")
    pg.screenshot(path=str(HERE / 't15-decided.png'), clip={'x': r[0]-4, 'y': r[1]-4, 'width': r[2]+8, 'height': r[3]+10})
    J("$('btnOk').click()"); pg.wait_for_timeout(300)
    ok(J("document.querySelector('.scr.on').id") == 's-log', '按「記一筆」才去記錄頁')
    # --- 再抽一次會重設 ---
    J("go('enc'); $('btnNo').click()"); pg.wait_for_timeout(800)
    ok(J("$('btnOk').textContent") == '就這家', '再抽一次後按鈕恢復「就這家」')
    # --- 跳過動畫 ---
    J("$('btnOk').click(); scrollTo(0,0)"); pg.wait_for_timeout(700)
    box = J("(()=>{const a=$('stage').getBoundingClientRect();return [a.x+a.width/2,a.y+a.height/2]})()")
    pg.mouse.click(box[0], box[1]); pg.wait_for_timeout(250)
    st = J("({ok: $('btnOk').textContent, fx: document.querySelectorAll('#fx .fx, #stage .fx').length, tr: units.map(u=>u.d.style.transform).join('|'), rolling})")
    ok(st['ok'] == '記一筆' and st['fx'] == 0 and st['tr'] == '||' and not st['rolling'], '點畫面跳過 → 直接到結果 %s' % st)
    # --- 經典模式 ---
    J("S.cfg.enc='classic'; applyEncStyle(); $('btnRoll').click()"); pg.wait_for_timeout(1500)
    J("$('btnOk').click()"); pg.wait_for_timeout(300)
    ok(J("document.querySelector('.scr.on').id") == 's-enc' and J("$('btnOk').textContent") == '記一筆', '經典模式「就這家」也不跳頁')
    J("S.cfg.enc='battle'; applyEncStyle()")
    # --- 「改好了」 ---
    J("go('log'); resetForm(); $('shop').value='測試店'; $('amt0').value=100; $('btnSave').click()"); pg.wait_for_timeout(200)
    ok(J("$('toast').textContent") == '記好了', '新增 → 記好了')
    eid = J("alive(S.entries).find(e=>e.shop==='測試店').id")
    J("editEntry('%s'); $('amt0').value=120; $('btnSave').click()" % eid); pg.wait_for_timeout(200)
    ok(J("$('toast').textContent") == '改好了', '修改 → 改好了')
    # --- 關帳後鎖住 + 撤銷 ---
    J("go('settle'); $('btnClose').click()"); pg.wait_for_timeout(300)
    ok(J("!!alive(S.entries).find(e=>e.id==='%s').periodId" % eid), '關帳後紀錄有 periodId')
    J("editEntry('%s')" % eid); pg.wait_for_timeout(200)
    ok('關帳' in J("$('toast').textContent") and J("editing") is None, '已關帳的紀錄點了不能改：' + J("$('toast').textContent"))
    el = J("(()=>{const d=entryEl(alive(S.entries).find(e=>e.id==='%s'));return [d.classList.contains('locked'), d.innerHTML.includes('已關帳')]})()" % eid)
    ok(el == [True, True], '紀錄上有「已關帳」標籤')
    J("render(); go('settle'); scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(300)
    pr = J("(()=>{const r=$('periods').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
    pg.screenshot(path=str(HERE / 't15-periods.png'), clip={'x': pr[0]-14, 'y': pr[1]-60, 'width': pr[2]+28, 'height': pr[3]+74})
    ok(J("!!document.querySelector('#periods .undo')"), '關帳紀錄有「撤銷」按鈕')
    J("document.querySelector('#periods .undo').click()"); pg.wait_for_timeout(300)
    ok(J("!alive(S.entries).find(e=>e.id==='%s').periodId && alive(S.periods).length===0" % eid), '撤銷後紀錄回到本期：' + J("$('toast').textContent"))
    J("go('log'); scrollTo(0,0)"); pg.wait_for_timeout(200)
    print('ERR', errs)
    b.close()
