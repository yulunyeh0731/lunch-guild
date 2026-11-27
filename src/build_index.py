"""把斜角戰鬥整合進 index.html。
用法：python3 src/bg34.py（改了背景才需要）→ python3 src/build_index.py → 檢查 src/index-test.html → commit index.html
輸入固定是 index-v1.3-backview.html（v1.3 背面版），輸出覆蓋 index.html。"""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battle34, app34, pocket34, fix20, appicon, join20, layout203, uiapply, food22, ui22, ui221
REPO = os.path.dirname(HERE) + os.sep
BASE = REPO + 'index-v1.3-backview.html'
if not os.path.exists(BASE):
    shutil.copy(REPO + 'index.html', BASE)
src = open(BASE, encoding='utf-8').read()
assert 'ARROW_FX' not in src, '輸入檔已經是整合過的版本'
h = battle34.integrate(src, PREVIEW=False)
h = app34.apply(h)                     # v1.5 起的 app 修正
h = pocket34.apply(h)                  # v2.0 口袋名單整理
h = fix20.apply(h)                     # v2.0 邏輯修正
h = appicon.apply(h)                   # v2.0 App 圖示
h = join20.apply(h)                    # v2.0.3 網址內建，只打通關密語
h = layout203.apply(h)                 # v2.0.4 遭遇頁塞進一個螢幕
h = uiapply.apply(h)                   # v2.1 選單／職業圖示、頭像（光影＋戰鬥服裝）
h = food22.apply(h)                    # v2.2 食物圖示 32×32 重畫、熱炒→甜點
h = ui22.apply(h)                      # v2.2.1 標題小圖示補畫、月曆爆版修正
h = ui221.apply(h)                     # v2.2.2 付款箭頭、長條圖、齒輪、月曆箭頭
open(REPO + 'index.html', 'w', encoding='utf-8').write(h)

# 本機測試版（假資料、獨立儲存，不進 repo）：python3 src/testindex.py 會用它跑一次完整流程
DEMO = """
const __DB = { members: [
  {id:'m1',name:'Yulun',portrait:'yulun',cls:'bow',job:'友善時光獵人・電支專精',updatedAt:1,deleted:0},
  {id:'m2',name:'Eric',portrait:'eric',cls:'shield',job:'課金戰士・滿手現金',updatedAt:1,deleted:0},
  {id:'m3',name:'Karen',portrait:'karen',cls:'staff',job:'先知・唯一知道午餐要吃什麼的人',updatedAt:1,deleted:0}],
  shops: [['巷口自助餐','buffet'],['一蘭拉麵','ramen'],['阿婆滷味','luwei'],['甜點工房','dessert'],['麥當勞','mcd'],
          ['越南河粉','pho'],['池上便當','bento']].map((s,i)=>({id:'s'+i,name:s[0],icon:s[1],by:'m1',updatedAt:1,deleted:0})),
  entries: [], periods: [] };
window.fetch = async (u, opt) => {
  if (opt && opt.method === 'POST') {
    const b = JSON.parse(opt.body);
    ['members','shops','entries','periods'].forEach(k => (b[k]||[]).forEach(r => {
      const i = __DB[k].findIndex(x => x.id === r.id);
      if (i < 0) __DB[k].push(r); else __DB[k][i] = r;
    }));
  }
  return { json: async () => Object.assign({ ok: true }, JSON.parse(JSON.stringify(__DB))) };
};
"""
t = h.replace("const LS = 'lunch-guild-v1';", "const LS = 'lunch-guild-test';", 1)
t = t.replace('<script>\n', '<script>\n' + DEMO, 1)
t = t.replace("S.cfg = Object.assign({ url: '', key: '', cool: 5, enc: 'battle' }, S.cfg || {});",
              "S.cfg = Object.assign({ url: '', key: '', cool: 5, enc: 'battle' }, S.cfg || {});\nS.cfg.url = 'demo'; S.cfg.key = 'demo'; S.cfg.enc = 'battle'; if (!S.me) S.me = 'm1';", 1)
open(os.path.join(HERE, 'index-test.html'), 'w', encoding='utf-8').write(t)
print('index.html', len(src), '->', len(h))
