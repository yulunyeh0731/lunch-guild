"""v2.0 App 圖示（A3 金框拉麵）。圖由 icon34.py 產生：icon_A3.png → src/icon-180.png、repo 根目錄 icon-192/512.png。"""
import base64, re, pathlib

BASE = 'https://yulunyeh0731.github.io/lunch-guild/'


def apply(h):
    b64 = base64.b64encode((pathlib.Path(__file__).parent / 'icon-180.png').read_bytes()).decode()
    n = 0
    for rel in ('apple-touch-icon', 'icon'):
        h, k = re.subn(r'<link rel="%s" href="data:image/png;base64,[^"]+">' % rel,
                       '<link rel="%s" href="data:image/png;base64,%s">' % (rel, b64), h)
        n += k
    assert n == 2, n
    old = '%22start_url%22%3A%22./%22%7D'
    icons = ('%22icons%22%3A%5B'
             '%7B%22src%22%3A%22' + BASE + 'icon-192.png%22%2C%22sizes%22%3A%22192x192%22%2C%22type%22%3A%22image/png%22%7D%2C'
             '%7B%22src%22%3A%22' + BASE + 'icon-512.png%22%2C%22sizes%22%3A%22512x512%22%2C%22type%22%3A%22image/png%22%7D%5D')
    assert h.count(old) == 1
    h = h.replace(old, '%22start_url%22%3A%22./%22%2C' + icons + '%7D')
    # 桌面名稱：iPhone 用 apple-mobile-web-app-title，Android 用 manifest short_name
    a = '<meta name="apple-mobile-web-app-title" content="午餐互助會">'
    assert h.count(a) == 1
    h = h.replace(a, '<meta name="apple-mobile-web-app-title" content="午餐選困互助會">')
    a = '%22short_name%22%3A%22%E5%8D%88%E9%A4%90%E4%BA%92%E5%8A%A9%E6%9C%83%22'      # 午餐互助會
    assert h.count(a) == 1
    h = h.replace(a, '%22short_name%22%3A%22%E5%8D%88%E9%A4%90%E9%81%B8%E5%9B%B0%E4%BA%92%E5%8A%A9%E6%9C%83%22')
    # 標題列小圖示：換成新圖示的碗（54×50，顯示 36px → 3 倍螢幕剛好 2 倍放大）
    cb = base64.b64encode((pathlib.Path(__file__).parent / 'icon-crest.png').read_bytes()).decode()
    a = '<canvas id="crest"></canvas>'
    assert h.count(a) == 1
    h = h.replace(a, '<img id="crest" src="data:image/png;base64,' + cb + '" alt="" style="width:36px;height:auto;flex:none;image-rendering:pixelated">')
    a = "draw($('crest'), RAMEN, RPAL); $('crest').style.width = '32px'; $('crest').style.height = '32px';"
    assert h.count(a) == 1
    return h.replace(a, '')
