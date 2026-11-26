# 素材原始碼

像素素材全部用程式畫，不是手繪圖檔。改角色、改背景都是改這裡的 Python，再重新產生 `index.html`。

需要：Python 3、`pip install pillow numpy`；跑測試另外要 `pip install playwright && playwright install chromium`。

## 檔案

| 檔案 | 用途 |
|---|---|
| `chars34.py` | 斜角戰鬥角色（64×80，顯示 2 倍）。`eric34(idle/atk/hit)`、`yulun34(idle/draw/rel)`、`karen34(idle/raise/cast)` |
| `bg34.py` | 戰鬥背景「午休商店街」192×230，輸出 `bg34.png` |
| `bg34.png` | 背景成品（`battle34.py` 會讀它） |
| `battle34.py` | 整合邏輯：把角色、背景、站位、攻擊動畫、魔法陣、影子寫進 html |
| `build_index.py` | 產生 `index.html`（輸入固定是根目錄的 `index-v1.3-backview.html`），同時產生本機測試版 `src/index-test.html` |
| `testindex.py` | 用假資料跑一次：抽店 → 攻擊 → 跳記帳頁，並檢查經典模式 |
| `chars.py` | 舊的背面版角色（v1.3），只留作參考 |

## 改完要做的事

```bash
python3 src/bg34.py          # 只有改了背景才需要
python3 src/build_index.py   # 重新產生 index.html
python3 src/testindex.py     # 確認流程沒壞（會輸出 src/test-stage.png）
```

`src/index-test.html`、`src/test-stage.png` 是本機測試用，不進 repo。

## 畫法規則

這些是調整過程中一路踩到的問題，新角色、新動作都要遵守（詳細見 CHANGELOG v1.4）：

- 膝蓋只往前彎：`leg()` 裡有 assert，膝蓋落在髖到踝連線的後方會直接報錯。
- 腿是一整塊錐形（髖最寬→膝→踝），明暗沿腿的方向算。不要用兩個零件拼，交界會出現內線。
- 靴子由 `boot_geo()` 從腳踝和小腿方向生成，靴筒跟著小腿走。
- 劍、箭沿同一條軸線生成，劍首、握柄、劍身成一直線。
- 弦、箭羽、光點在 `outline()` 之後畫，不加黑框；被身體擋住的部分不畫。
- 接近垂直的長物件不要只斜一點點（會出現不規律錯格、看起來像彎的），用完全垂直或規律斜率（法杖用 1:8）。
- 背面視角先想清楚每個部位離鏡頭的前後，再決定圖層順序。看不到的就藏起來。
