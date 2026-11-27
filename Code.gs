/**
 * 午餐選困互助會 — 後端
 * 部署方式見 README。整份貼進 Apps Script 編輯器即可。
 *
 * 設計重點：
 *  - 逐列 upsert，同 id 比 updatedAt，大的贏 → 三人同時記帳不會互相蓋掉
 *  - 刪除是打墓碑（deleted=1），不是真的刪列 → 同步邏輯才單純
 *  - doPost 用 text/plain 收 JSON，避開 Apps Script 不回應 OPTIONS 預檢的問題
 */

// ⚠️ 改成你們自己的隨機字串，前端設定頁要填一樣的
var SECRET = 'CHANGE-ME-隨便打一串';
// 其他也能用的通關密語（例如換新密語時，舊的先留著，大家的手機才不會突然連不上）
var EXTRA_SECRETS = [];

var SHEETS = {
  members: ['id', 'name', 'portrait', 'cls', 'job', 'updatedAt', 'deleted'],
  shops:   ['id', 'name', 'icon', 'by', 'off', 'updatedAt', 'deleted'],   // off=1 休息中，不會被抽到
  entries: ['id', 'date', 'shop', 'icon', 'meal', 'payer', 'a1', 'a2', 'a3',
            'note', 'by', 'periodId', 'updatedAt', 'deleted'],
  periods: ['id', 'closedOn', 'fromDate', 'toDate', 'transfers', 'by', 'updatedAt', 'deleted']
};

// 這些欄位存成「純文字」，避免試算表把 7-11 變成日期、0800 變成數字
var TEXT_COLS = {
  members: ['id', 'name', 'portrait', 'cls', 'job', 'by'],
  shops:   ['id', 'name', 'icon', 'by'],
  entries: ['id', 'shop', 'icon', 'meal', 'payer', 'note', 'by', 'periodId'],
  periods: ['id', 'transfers', 'by']
};
var FMT_VER = '2';

var SEED_MEMBERS = [
  { id: 'm1', name: 'Yulun', portrait: 'yulun', cls: 'bow',    job: '友善時光獵人・電支專精' },
  { id: 'm2', name: 'Eric',  portrait: 'eric',  cls: 'shield', job: '課金戰士・滿手現金' },
  { id: 'm3', name: 'Karen', portrait: 'karen', cls: 'staff',  job: '先知・唯一知道午餐要吃什麼的人' }
];

function doGet(e)  { return handle_(e, null); }
function doPost(e) {
  var body = null;
  try { body = JSON.parse(e.postData.contents); } catch (err) { body = null; }
  return handle_(e, body);
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}

function handle_(e, body) {
  try {
    var k = e && e.parameter ? e.parameter.k : '';
    if (k !== SECRET && EXTRA_SECRETS.indexOf(k) < 0) return out_({ ok: false, error: 'bad key' });

    var lock = LockService.getScriptLock();
    if (!lock.tryLock(25000)) return out_({ ok: false, error: 'busy' });
    try {
      var ss = SpreadsheetApp.getActive();
      ensure_(ss);
      var wrote = 0;
      if (body) wrote = write_(ss, body);
      var data = readAll_(ss);
      data.ok = true;
      data.wrote = wrote;
      data.blocked = body ? body._blocked || 0 : 0;
      data.ts = Date.now();
      return out_(data);
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    return out_({ ok: false, error: String(err) });
  }
}

/* ---------- 建表 ---------- */
function ensure_(ss) {
  for (var name in SHEETS) {
    var sh = ss.getSheetByName(name);
    if (!sh) {
      sh = ss.insertSheet(name);
      sh.getRange(1, 1, 1, SHEETS[name].length).setValues([SHEETS[name]]);
      sh.setFrozenRows(1);
    } else if (sh.getLastRow() === 0) {
      sh.getRange(1, 1, 1, SHEETS[name].length).setValues([SHEETS[name]]);
      sh.setFrozenRows(1);
    } else {
      migrate_(sh, SHEETS[name]);
    }
  }
  var m = ss.getSheetByName('members');
  if (m.getLastRow() < 2) {
    var now = Date.now();
    var rows = SEED_MEMBERS.map(function (x) {
      return [x.id, x.name, x.portrait, x.cls, x.job, now, 0];
    });
    m.getRange(2, 1, rows.length, SHEETS.members.length).setValues(rows);
  }
  textFormat_(ss);
  var d = ss.getSheetByName('Sheet1') || ss.getSheetByName('工作表1');
  if (d && ss.getSheets().length > 1 && d.getLastRow() === 0) ss.deleteSheet(d);
}

/** 文字欄位設成純文字格式（只在第一次或欄位升級後做一次） */
function textFormat_(ss) {
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('fmt') === FMT_VER) return;
  for (var name in TEXT_COLS) {
    var sh = ss.getSheetByName(name);
    var cols = SHEETS[name];
    TEXT_COLS[name].forEach(function (c) {
      var i = cols.indexOf(c);
      if (i >= 0) sh.getRange(1, i + 1, sh.getMaxRows(), 1).setNumberFormat('@');
    });
  }
  props.setProperty('fmt', FMT_VER);
}

/**
 * 舊表升級：欄位有增減時，照欄名把每一列搬到新的位置。
 * 新欄位補空值，順序不同也會對齊。不會刪掉不認得的欄位以外的資料。
 */
function migrate_(sh, cols) {
  var width = sh.getLastColumn();
  var head = sh.getRange(1, 1, 1, Math.max(width, cols.length)).getValues()[0];
  var same = true;
  for (var i = 0; i < cols.length; i++) {
    if (String(head[i] || '') !== cols[i]) { same = false; break; }
  }
  if (same && width === cols.length) return;

  var map = {};
  for (var c = 0; c < head.length; c++) {
    if (head[c]) map[String(head[c])] = c;
  }
  var last = sh.getLastRow();
  var body = last >= 2 ? sh.getRange(2, 1, last - 1, Math.max(width, 1)).getValues() : [];
  var out = [];
  for (var r = 0; r < body.length; r++) {
    if (!body[r][map['id'] === undefined ? 0 : map['id']]) continue;
    var row = [];
    for (var k = 0; k < cols.length; k++) {
      var src = map[cols[k]];
      row.push(src === undefined ? '' : body[r][src]);
    }
    out.push(row);
  }
  sh.clear();
  PropertiesService.getScriptProperties().deleteProperty('fmt');   // 清表會清掉格式，等下重設
  sh.getRange(1, 1, 1, cols.length).setValues([cols]);
  if (out.length) sh.getRange(2, 1, out.length, cols.length).setValues(out);
  sh.setFrozenRows(1);
}

/* ---------- 讀 ---------- */
function readAll_(ss) {
  var res = {};
  for (var name in SHEETS) {
    res[name] = readSheet_(ss, name);
  }
  return res;
}

function readSheet_(ss, name) {
  var sh = ss.getSheetByName(name);
  var cols = SHEETS[name];
  var last = sh.getLastRow();
  if (last < 2) return [];
  var vals = sh.getRange(2, 1, last - 1, cols.length).getValues();
  var out = [];
  for (var i = 0; i < vals.length; i++) {
    if (!vals[i][0]) continue;
    var o = {};
    for (var c = 0; c < cols.length; c++) o[cols[c]] = vals[i][c];
    o.updatedAt = Number(o.updatedAt) || 0;
    o.deleted = Number(o.deleted) ? 1 : 0;
    if (name === 'entries') {
      o.meal = o.meal || 'lunch';
      o.a1 = Number(o.a1) || 0;
      o.a2 = Number(o.a2) || 0;
      o.a3 = Number(o.a3) || 0;
      o.date = fmtDate_(o.date);
    }
    if (name === 'shops') o.off = Number(o.off) ? 1 : 0;
    if (name === 'periods') {
      o.fromDate = fmtDate_(o.fromDate);
      o.toDate = fmtDate_(o.toDate);
      o.closedOn = fmtDate_(o.closedOn);
    }
    out.push(o);
  }
  return out;
}

function fmtDate_(v) {
  if (v instanceof Date) return Utilities.formatDate(v, 'Asia/Taipei', 'yyyy-MM-dd');
  return String(v || '');
}

/* ---------- 寫（逐列 upsert） ---------- */
function write_(ss, body) {
  var n = 0, ctx = { blocked: 0, undone: undonePeriods_(ss, body) };
  for (var name in SHEETS) {
    var incoming = body[name];
    if (!incoming || !incoming.length) continue;
    n += upsert_(ss, name, incoming, ctx);
  }
  body._blocked = ctx.blocked;
  return n;
}

/** 已撤銷（刪除）的關帳 id：表上的 + 這次一起送來的 */
function undonePeriods_(ss, body) {
  var set = {};
  readSheet_(ss, 'periods').forEach(function (p) { if (p.deleted) set[String(p.id)] = 1; });
  (body.periods || []).forEach(function (p) { if (p && Number(p.deleted)) set[String(p.id)] = 1; });
  return set;
}

function upsert_(ss, name, rows, ctx) {
  var sh = ss.getSheetByName(name);
  var cols = SHEETS[name];
  var last = sh.getLastRow();
  var index = {};
  var existing = [];
  if (last >= 2) {
    existing = sh.getRange(2, 1, last - 1, cols.length).getValues();
    for (var i = 0; i < existing.length; i++) {
      if (existing[i][0]) index[String(existing[i][0])] = i;
    }
  }

  var updates = [];   // [rowNumber, values]
  var appends = [];
  var wrote = 0;

  for (var r = 0; r < rows.length; r++) {
    var row = rows[r];
    if (!row || !row.id) continue;
    var id = String(row.id);
    var vals = cols.map(function (c) {
      var v = row[c];
      if (v === undefined || v === null) return '';
      if (c === 'deleted') return Number(v) ? 1 : 0;
      if (c === 'updatedAt') return Number(v) || 0;
      return v;
    });

    if (index.hasOwnProperty(id)) {
      var i2 = index[id];
      var curTs = Number(existing[i2][cols.indexOf('updatedAt')]) || 0;
      if ((Number(row.updatedAt) || 0) <= curTs) continue;   // 舊的不覆蓋新的
      if (name === 'entries') {
        // 已關帳的紀錄不能被「還沒同步到關帳的手機」改回本期或刪掉，除非那次關帳被撤銷了
        var pi = cols.indexOf('periodId');
        var curPid = String(existing[i2][pi] || '');
        if (curPid && curPid !== String(row.periodId || '') && !ctx.undone[curPid]) {
          var keep = existing[i2].slice();
          keep[cols.indexOf('updatedAt')] = Math.max(Number(row.updatedAt) || 0, Date.now()) + 1;   // 讓各手機改回關帳版本
          updates.push([i2 + 2, keep]);
          existing[i2] = keep;
          ctx.blocked++;
          continue;
        }
      }
      updates.push([i2 + 2, vals]);
      existing[i2] = vals;
      wrote++;
    } else {
      appends.push(vals);
      index[id] = existing.length;
      existing.push(vals);
      wrote++;
    }
  }

  for (var u = 0; u < updates.length; u++) {
    sh.getRange(updates[u][0], 1, 1, cols.length).setValues([updates[u][1]]);
  }
  if (appends.length) {
    sh.getRange(sh.getLastRow() + 1, 1, appends.length, cols.length).setValues(appends);
  }
  return wrote;
}
