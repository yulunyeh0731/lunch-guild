# 午餐選困互助會 — 更新紀錄

> 給 Claude 讀的：每次改版都往上加一節。記「改了什麼、為什麼、動到哪個檔案的哪一段」，
> 不要只寫「修 bug」。程式碼在 `app.html`（樣板）→ `build.py` 注入資源 → 產出 `index.html`。
> 像素素材在 `/home/claude/px/`：`art2.py`（食物圖鑑+關鍵字）、`faces.py`（32×32 頭像）、
> `ui.py`（UI 圖示）、`scene2.py`（背景場景）。

---

## v1.0.2 — 2026-08-11

**換 App 圖示：拉麵**

舊的金色碗+筷子（`ui.py` 的 `crest`）只有 16×16 又是單色金，在手機桌面上看不出是什麼。
重畫成 32×32、22 色的拉麵，檔案在 `px/ramen.py`。提了三案給使用者挑：
A 正面碗、B 筷子夾麵、C 俯視碗。**選 B，並要求蒸氣加多**。

B 定稿的重點（之後要改記得維持這幾點）：
- **筷子一定要兩支**。第一版用一條 3px 斜線，在 60px 下就是一根棍子。現在是兩組 2px
  斜線中間留 2px 空隙。
- 蒸氣三道，用交錯鋸齒讓它有飄動感，不要三條直線。
- 從筷子垂下的麵條只能 1–2px 波浪。第一版畫成實心柱狀，糊成一團看不出是麵。
- 右側原本整片都是麵，顏色太空，補了魚板和蔥花。

用在兩個地方：`apple-touch-icon`（`build.py` 的 `RM.appicon()` 合成 180px 深藍圓角底 +
金框）、標題列 crest（32×32 原尺寸，1:1 不縮放）。JS 端變數是 `RAMEN` / `RPAL`。

**月曆箭頭改像素風**

原本用文字 `◀ ▶`。改成 16×16 手繪像素箭頭（`ui.py` 的 `arrowL` / `arrowR`），
以 32px 顯示（2 倍，整數倍才不會糊）。

---

## v1.0.1 — 2026-08-11

**修：iOS 安全區域露出底色，各分頁選單位置不一致**

症狀：真機上「隊伍」分頁（內容短、不用捲）選單下方會露出一條淺藍色，且選單位置比其他
分頁高。原因是 `viewport-fit=cover` 在部分情況沒生效，版面視口底部在 home indicator 之上，
下方區域顯示的是 canvas 背景色。

`app.html` 改動：
- `html{background:#0f1530}` — 只設在 html，**不能同時設在 body**。body 有自己的背景時
  會蓋掉 `#bg`（負 z-index 的子元素畫在 root 背景之上、但在 body 背景之下）。第一次改的
  時候踩到這個，整張背景場景消失。
- `nav::after` 往下鋪 160px 的 `#0b0e1c`，保證選單下方永遠是深色。
- `body` 和 `main` 加 `min-height`，用 `dvh`（`vh` 當退路），讓長短頁面的選單位置一致。
- `#bg` 從 `inset:0` 改成 `top/left/right:0 + height:100dvh`。

---

## v1.0 — 2026-08-11 首版上線

**架構**
- 前端：單一 `index.html`（約 616 KB），字型、場景、所有像素圖都用 base64 內嵌，無外部相依。
  放在 GitHub Pages `yulunyeh0731/lunch-guild`。
- 後端：Google Apps Script 綁定在試算表「午餐選困互助會 — 帳本」
  （fileId `148CEVfN3jLCSWnZhPVIwVyxW8-Rr_mjPF_d5e2BZ_No`），對外只有 `doGet` / `doPost` 兩支。
- 同步：逐列 upsert，同 id 比 `updatedAt` 大的贏。刪除打墓碑（`deleted=1`）不真的刪列。
  離線寫入排進 `S.outbox`，連上自動送出。

**Sheet 欄位**
```
members : id, name, portrait, cls, job, updatedAt, deleted
shops   : id, name, icon, by, updatedAt, deleted
entries : id, date, shop, icon, payer, a1, a2, a3, note, by, periodId, updatedAt, deleted
periods : id, closedOn, fromDate, toDate, transfers, by, updatedAt, deleted
```
`a1/a2/a3` 對應 members 的前三列（m1/m2/m3），順序固定。

**踩過的坑（別再犯）**
- Apps Script 不回應 OPTIONS 預檢，POST 一定要用 `Content-Type: text/plain;charset=utf-8`。
- 同步進行中排隊的變更會被 `S.outbox = []` 清掉。關帳要一次寫 6 筆會觸發，資料會消失。
  已改成只清「這一批實際送出的」，並在結束後檢查 outbox 是否還有東西、有的話再送一輪。
- 像素圖縮放必須是整數倍（16→32、24→48），非整數倍會糊。
- Cubic 11 是 11×11 點陣字，字級只能用 11 的倍數（11/22/33px）。

**部署設定**
- Apps Script 部署：執行身分「我」、存取權「任何人」。選「擁有 Google 帳戶的任何使用者」
  一樣會失敗，因為 `fetch()` 跨網域是匿名請求。
- 改了 `Code.gs` 要「管理部署作業 → 編輯 → 版本選新版本 → 部署」，存檔不會生效。

**除錯備忘**
- Claude 的 web_fetch 打 Apps Script `/exec` 一律回 404（推測是沒跟隨 302 到
  googleusercontent）。**這是假警報，不要當成部署有問題的證據。**
  要驗證後端請改用：讀試算表看分頁/資料有沒有出現，或請使用者用無痕視窗開網址。
