// 数据通道探针：用官方 SDK 在本机模拟前端，验证免登录(anon)读写。
const vm = require('node:vm');
const SDK_URL = 'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js';
const ENDPOINT = 'https://peipao-tai.app.workbuddy.host';
const PK = 'wbpk_iTGkwbktahAc8tjJawUTr9_hF8DbMgE7LS0ZVxUqBtd3NCUWrMdgW4Q';

(async () => {
  let js;
  const r = await fetch(SDK_URL, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  js = await r.text();

  globalThis.window = globalThis;
  globalThis.self = globalThis;
  if (!globalThis.navigator) globalThis.navigator = { userAgent: 'node-probe' };
  globalThis.location = {
    origin: ENDPOINT, href: ENDPOINT + '/chat.html',
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

  try {
    const ins = await cloud.database.from('jd_records')
      .insert({ company: '__probe__', position: 'probe', requirement: 'probe row' }).select();
    console.log('INSERT err=', ins.error ? JSON.stringify(ins.error) : 'none', 'data=', JSON.stringify(ins.data || []).slice(0, 200));

    const sel = await cloud.database.from('jd_records').select('*').eq('company', '__probe__');
    console.log('SELECT err=', sel.error ? JSON.stringify(sel.error) : 'none', 'rows=', (sel.data || []).length);

    const del = await cloud.database.from('jd_records').delete().eq('company', '__probe__').select();
    console.log('DELETE err=', del.error ? JSON.stringify(del.error) : 'none', 'removed=', (del.data || []).length);
  } catch (e) {
    console.log('DB_EXC', e && e.message || String(e));
  }
})();
