import pathlib
from playwright.sync_api import sync_playwright
url = 'file://' + str((pathlib.Path(__file__).resolve().parent / 'index-test.html'))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
    pg.goto(url); pg.wait_for_timeout(1500); pg.evaluate("go('enc')"); pg.wait_for_timeout(400)
    pg.evaluate("document.getElementById('btnRoll').click(); window.scrollTo(0,0)"); pg.wait_for_timeout(1700)
    r = pg.evaluate("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
    pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent / 'test-stage.png'), clip={'x': r[0]-4, 'y': r[1]-4, 'width': r[2]+8, 'height': r[3]+8})
    foe = pg.evaluate("foeShop && foeShop.name")
    pg.evaluate("document.getElementById('btnOk').click()")
    pg.wait_for_timeout(7000)
    page = pg.evaluate("[...document.querySelectorAll('section')].filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id)")
    shopField = pg.evaluate("(()=>{const e=document.querySelector('#fShop, #shop, input[name=shop]');return e?e.value:null})()")
    print('foe', foe, '| visible sections', page, '| shop field', shopField)
    # classic mode
    pg.evaluate("S.cfg.enc='classic'; applyEncStyle(); go('enc')"); pg.wait_for_timeout(500)
    pg.evaluate("document.getElementById('btnRoll').click()"); pg.wait_for_timeout(1500)
    vis = pg.evaluate("[getComputedStyle(document.getElementById('stage')).display, getComputedStyle(document.getElementById('classicEnc')).display]")
    print('classic stage/classicEnc display', vis)
    print('ERR', errs)
    b.close()
