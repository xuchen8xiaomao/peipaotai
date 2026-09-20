// 将 data/_migrate/*.json 导入 cloud-service 云端库（免登录 anon 直写）。
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = 'c:/Users/24186/WorkBuddy/2026-09-10-20-13-10';
const SDK_URL = 'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js';
const ENDPOINT = 'https://peipao-tai.app.workbuddy.host';
const PK = 'wbpk_iTGkwbktahAc8tjJawUTr9_hF8DbMgE7LS0ZVxUqBtd3NCUWrMdgW4Q';

(async () => {
  const js = await (await fetch(SDK_URL)).text();
  globalThis.window = globalThis;
  globalThis.self = globalThis;
  if (!globalThis.navigator) globalThis.navigator = { userAgent: 'node-import' };
  globalThis.location = {
    origin: ENDPOINT, href: ENDPOINT + '/',
    hostname: 'peipao-tai.app.workbuddy.host', protocol: 'https:'
  };
  const of = globalThis.fetch;
  globalThis.fetch = function (input, init) {
    init = init || {};
    try {
      const h = new Headers(init.headers || {});
      h.set('Origin', ENDPOINT);
      init = Object.assign({}, init, { headers: h });
    } catch (e) {}
    return of(input, init);
  };
  vm.runInThisContext(js);
  const cloud = globalThis.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: ENDPOINT, publishableKey: PK });

  const DIR = path.join(ROOT, 'data', '_migrate');
  const tables = fs.readdirSync(DIR).filter(function (f) { return f.endsWith('.json'); }).map(function (f) { return f.replace('.json', ''); });

  for (const t of tables) {
    const rows = JSON.parse(fs.readFileSync(path.join(DIR, t + '.json'), 'utf8'));
    if (!rows.length) { console.log(t, '| empty, skip'); continue; }

    const pre = await cloud.database.from(t).select('id', { count: 'exact', head: true });
    const cnt = pre.count || 0;
    if (cnt > 0) { console.log(t, '| already', cnt, 'rows, skip'); continue; }

    let ok = 0, errText = '';
    for (let i = 0; i < rows.length; i += 40) {
      const batch = rows.slice(i, i + 40);
      const r = await cloud.database.from(t).insert(batch).select();
      if (r.error) { errText = JSON.stringify(r.error).slice(0, 200); break; }
      ok += (r.data || []).length;
    }
    console.log(t, '| inserted', ok, '/', rows.length, errText ? ('ERR ' + errText) : '');
  }
})();
