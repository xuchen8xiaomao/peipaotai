// 重试 interview_questions：逐条插入，带小延迟，记录被拦条目特征。
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = 'c:/Users/24186/WorkBuddy/2026-09-10-20-13-10';
const SDK_URL = 'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js';
const ENDPOINT = 'https://peipao-tai.app.workbuddy.host';
const PK = 'wbpk_iTGkwbktahAc8tjJawUTr9_hF8DbMgE7LS0ZVxUqBtd3NCUWrMdgW4Q';

function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }

(async () => {
  const js = await (await fetch(SDK_URL)).text();
  globalThis.window = globalThis;
  globalThis.self = globalThis;
  if (!globalThis.navigator) globalThis.navigator = { userAgent: 'node-import' };
  globalThis.location = { origin: ENDPOINT, href: ENDPOINT + '/', hostname: 'peipao-tai.app.workbuddy.host', protocol: 'https:' };
  const of = globalThis.fetch;
  globalThis.fetch = function (input, init) {
    init = init || {};
    try { const h = new Headers(init.headers || {}); h.set('Origin', ENDPOINT); init = Object.assign({}, init, { headers: h }); } catch (e) {}
    return of(input, init);
  };
  vm.runInThisContext(js);
  const cloud = globalThis.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: ENDPOINT, publishableKey: PK });

  const rows = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', '_migrate', 'interview_questions.json'), 'utf8'));
  const pre = await cloud.database.from('interview_questions').select('id', { count: 'exact', head: true });
  if ((pre.count || 0) > 0) { console.log('already', pre.count, 'rows'); return; }

  let ok = 0;
  const fails = [];
  for (let i = 0; i < rows.length; i++) {
    const r = await cloud.database.from('interview_questions').insert(rows[i]).select();
    if (r.error) {
      fails.push({ i: i, q: String(rows[i].question || '').slice(0, 40), err: String(r.error.message || r.error).slice(0, 80) });
    } else { ok++; }
    await sleep(120);
  }
  console.log('OK', ok, 'FAIL', fails.length);
  fails.slice(0, 10).forEach(function (f) { console.log('  fail#' + f.i, f.q, '|', f.err); });
})();
