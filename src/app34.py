"""app 本身的修正（v1.5 起）：套在 battle34.integrate() 之後。每個 patch 都 assert 找得到原文，對不上就直接報錯。"""
import os, re, base64
HERE = os.path.dirname(os.path.abspath(__file__))


def apply(h):
    def patch(a, b, n=1):
        nonlocal h
        assert h.count(a) >= 1, a[:80]
        h = h.replace(a, b, n)

    # 1. 「改好了」：存檔前先記下是不是在編輯，resetForm() 會把 editing 清掉
    patch("  resetForm(); render(); toast(editing ? '改好了' : '記好了');",
          "  const wasEditing = !!editing;\n  resetForm(); render(); toast(wasEditing ? '改好了' : '記好了');")

    # 2. 已關帳的紀錄不能改、不能刪；最近一次關帳可以撤銷
    patch("function editEntry(id) {\n  const e = alive(S.entries).find(x => x.id === id); if (!e) return;\n",
          "function editEntry(id) {\n  const e = alive(S.entries).find(x => x.id === id); if (!e) return;\n"
          "  if (e.periodId) { toast('這筆已經關帳了；要改請先到「清算」撤銷那次關帳'); return; }\n")
    patch("function delEntry(id) {\n  const e = alive(S.entries).find(x => x.id === id); if (!e) return;\n",
          "function delEntry(id) {\n  const e = alive(S.entries).find(x => x.id === id); if (!e) return;\n"
          "  if (e.periodId) { toast('這筆已經關帳了，不能刪'); return; }\n")
    patch("  const tag = (e.meal || 'lunch') !== 'lunch' ? '<span style=\"color:var(--gold)\">［' + mealName(e.meal) + '］</span>' : '';",
          "  const tag = (e.periodId ? '<span class=\"lk\">已關帳</span>' : '') +\n"
          "    ((e.meal || 'lunch') !== 'lunch' ? '<span style=\"color:var(--gold)\">［' + mealName(e.meal) + '］</span>' : '');\n"
          "  if (e.periodId) d.classList.add('locked');")
    patch("    d.append(t, a); pb.appendChild(d);\n  });",
          "    if (x === pd[0]) {                       // 只有最近一次關帳可以撤銷\n"
          "      const u = document.createElement('button'); u.className = 'btn sm undo'; u.textContent = '撤銷';\n"
          "      u.onclick = () => undoPeriod(x); a.appendChild(u);\n"
          "    }\n"
          "    d.append(t, a); pb.appendChild(d);\n  });")
    patch("/* ================= 統計 ================= */",
          "function undoPeriod(x) {\n"
          "  const list = alive(S.entries).filter(e => e.periodId === x.id);\n"
          "  if (!confirm('撤銷 ' + md(x.fromDate) + '–' + md(x.toDate) + ' 這次關帳？\\n這 ' + list.length + ' 筆會回到本期，可以再修改。')) return;\n"
          "  put('periods', Object.assign({}, x, { deleted: 1 }));\n"
          "  if (list.length) putMany('entries', list.map(e => Object.assign({}, e, { periodId: '' })));\n"
          "  render(); toast('撤銷了，' + list.length + ' 筆回到本期');\n"
          "}\n\n/* ================= 統計 ================= */")
    patch("</style>",
          ".e.locked{opacity:.72}\n.e .lk{display:inline-block;font-size:11px;line-height:1;padding:2px 4px;margin-right:4px;"
          "border:1px solid var(--dim,#8a8fa8);color:var(--dim,#8a8fa8);vertical-align:1px}\n"
          ".e .a .undo{display:block;margin:6px 0 0 auto;width:auto;padding:4px 10px;font-size:11px}\n</style>")

    # 3. 戰鬥結束（或經典模式按「就這家」）不跳頁：停在遭遇畫面，按鈕變成「記一筆／再抽一次」
    #    抽店時不再覆蓋記錄表單；決定之後才把店名填進去（正在改別筆時不填）
    patch("  $('shop').value = s.name; paint(key, false);\n  if (navigator.vibrate) navigator.vibrate(16);",
          "  if (navigator.vibrate) navigator.vibrate(16);")
    patch("let rolling = false, foeShop = null;",
          "let rolling = false, foeShop = null, decided = false;\n"
          "function setDecided(on) {\n"
          "  decided = on;\n"
          "  if (!on) { document.querySelectorAll('.vic, .dmg').forEach(x => x.remove()); $('foe').classList.remove('down'); }\n"
          "  $('btnOk').textContent = on ? '記一筆' : '就這家';\n"
          "  $('btnNo').textContent = on ? '再抽一次' : (battleMode() ? '逃跑' : '再抽一次');\n"
          "}\n"
          "function decide() {\n"
          "  setDecided(true);\n"
          "  const st_ = shopStats(foeShop.name);\n"
          "  if (!editing && foeShop) { $('shop').value = foeShop.name; paint(ic(foeShop.icon), false); }\n"
          "  $('foeSub').textContent = '今天就吃這家'; $('encSub').textContent = '今天就吃這家';\n"
          "  let msg;\n"
          "  if (!st_.n) msg = '第一次挑戰這家！\\u3000店名先幫你填好了，吃完再記也可以。';\n"
          "  else {\n"
          "    const days = Math.round((new Date(today()) - new Date(st_.last)) / 864e5);\n"
          "    const when = days <= 0 ? '今天' : days === 1 ? '昨天' : days + ' 天前';\n"
          "    const per = M().map((m, i) => st_.per[i] == null ? null : m.name + ' ' + nt(st_.per[i])).filter(Boolean).join('／');\n"
          "    msg = '戰果：平均每人 $' + nt(st_.avg) + '（' + per + '）\\u3000第 ' + (st_.n + 1) + ' 次來，上次是' + (days > 1 ? ' ' : '') + when + '。';\n"
          "  }\n"
          "  type($('talk'), msg);\n"
          "}")
    patch("function roll() {\n  const p = pickShop();",
          "function roll() {\n  if (rolling) return;\n  setDecided(false);\n  const p = pickShop();")
    patch("$('btnNo').onclick = () => {\n  if (rolling) return;\n  if (battleMode() && foeShop) {",
          "$('btnNo').onclick = () => {\n  if (rolling) return;\n  if (decided) { roll(); return; }\n  if (battleMode() && foeShop) {")
    patch("  if (!foeShop) { toast('先抽一家'); return; }\n  if (!battleMode()) { go('log'); return; }",
          "  if (!foeShop) { toast('先抽一家'); return; }\n  if (decided) { go('log'); return; }\n  if (!battleMode()) { decide(); return; }")
    patch("  type($('talk'), '隊伍發動攻擊！');", "  type($('talk'), '隊伍發動攻擊！（點畫面可以跳過）');")
    # applyEncStyle 會重設按鈕文字：保持決定後的狀態
    patch("  $('btnNo').textContent = b ? '逃跑' : '再抽一次';",
          "  $('btnNo').textContent = decided ? '再抽一次' : (b ? '逃跑' : '再抽一次');")

    # 4. 離線也能開：註冊 Service Worker（只在 https 下；本機測試檔不註冊）
    patch("</body>",
          "<script>\nif ('serviceWorker' in navigator && location.protocol === 'https:') {\n"
          "  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => { }));\n}\n</script>\n</body>")
    # 5. 一般頁面的背景換成「午休商店街」（src/bgtown.py street），整數 2 倍、貼齊底部
    b64 = base64.b64encode(open(os.path.join(HERE, 'bgtown_street.png'), 'rb').read()).decode()
    h2 = re.sub(r'(<div id="bg"><img src="data:image/png;base64,)[^"]*', lambda m: m.group(1) + b64, h, count=1)
    assert h2 != h, 'page bg'
    h = h2
    patch("#bg img{position:absolute;left:50%;top:0;transform:translateX(-50%);height:100%;width:auto;min-width:100%}",
          "#bg img{position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:432px;height:auto;image-rendering:pixelated}")
    return h
