"""v2.0 程式邏輯修正（純前端）。build_index.py 在 pocket34.apply() 之後呼叫 apply(h)。"""

EATERS = "Math.max(1, {L}.reduce((s, e) => s + ({M} < 0 ? AK.filter(k => +e[k] > 0).length : 1), 0))"

FIXES = [
    # 逃跑連點：跑台詞那 0.7 秒也算抽籤中，避免抽兩次
    ("    setTimeout(roll, 700);\n",
     "    rolling = true; setTimeout(() => { rolling = false; roll(); }, 700);\n"),
    # roll() 裡重複的判斷
    ("  if (!p) { toast(alive(S.shops).length ? '名單上的店都在休息中' : '先在下面加幾家店'); return; }\n  if (rolling) return;\n",
     "  if (!p) { toast(alive(S.shops).length ? '名單上的店都在休息中' : '先在下面加幾家店'); return; }\n"),
    # decide()：先確認有店再算戰果
    ("function decide() {\n  setDecided(true);\n  const st_ = shopStats(foeShop.name);",
     "function decide() {\n  if (!foeShop) return;\n  setDecided(true);\n  const st_ = shopStats(foeShop.name);"),
    # 刪除按取消時不要清掉表單（delEntry 刪成功才會 resetForm）
    ("$('btnDel').onclick = () => { if (editing) { const id = editing; resetForm(); delEntry(id); render(); } };",
     "$('btnDel').onclick = () => { if (editing) { delEntry(editing); render(); } };"),
    # 每人每餐：除以實際有吃的人次，不是固定 3
    ("nt(tot / lun.length / per2)", "nt(tot / " + EATERS.format(L='lun', M='mi2') + ")"),
    ("nt(wsum / rs.length / per)", "nt(wsum / " + EATERS.format(L='rs', M='mi') + ")"),
    # 匯出不帶密鑰
    ("const b = new Blob([JSON.stringify(S, null, 1)]",
     "const b = new Blob([JSON.stringify(Object.assign({}, S, { cfg: Object.assign({}, S.cfg, { key: '' }) }), null, 1)]"),
    # 同步失敗：還有沒送出的，30 秒後自動再試
    ("let syncing = false, retry = false;", "let syncing = false, retry = false, syncRetryT = 0;"),
    ("    syncing = false; setSync('bad', '同步失敗');\n",
     "    syncing = false; setSync('bad', '同步失敗');\n"
     "    clearTimeout(syncRetryT); if (S.outbox.length) syncRetryT = setTimeout(() => sync(true), 30000);\n"),
    # 伺服器擋下「把已關帳的紀錄拉回本期」時，提示一下（資料會自動還原成關帳版本）
    ("    mergeAll(j);\n    S.lastSync = Date.now(); save(); render();\n",
     "    mergeAll(j);\n    S.lastSync = Date.now(); save(); render();\n"
     "    if (j.blocked) toast('有 ' + j.blocked + ' 筆已關帳的紀錄沒改成功，已還原');\n"),
]


def apply(h):
    for a, b in FIXES:
        assert h.count(a) == 1, ('pattern count', h.count(a), a[:70])
        h = h.replace(a, b)
    return h
