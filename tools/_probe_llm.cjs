// 一次性诊断探针：用官方 SDK 在本机复现前端调用，抓真实错误码。
// 用法: node tools/_probe_llm.cjs
const vm = require('node:vm');

const SDK_URL = 'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js';
const ENDPOINT = 'https://peipao-tai.app.workbuddy.host';
const PK = 'wbpk_iTGkwbktahAc8tjJawUTr9_hF8DbMgE7LS0ZVxUqBtd3NCUWrMdgW4Q';

(async () => {
  let js;
  try {
    const r = await fetch(SDK_URL, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    js = await r.text();
    console.log('SDK_HTTP', r.status, 'len', js.length);
  } catch (e) {
    console.log('SDK_FETCH_ERR', String(e && e.message || e));
    return;
  }

  // browser-ish shims
  globalThis.window = globalThis;
  globalThis.self = globalThis;
  if (!globalThis.navigator) globalThis.navigator = { userAgent: 'node-probe' };
  globalThis.location = {
    origin: ENDPOINT, href: ENDPOINT + '/chat.html',
    hostname: 'peipao-tai.app.workbuddy.host', protocol: 'https:'
  };

  const origFetch = globalThis.fetch;
  globalThis.fetch = function (input, init) {
    const u = (typeof input === 'string') ? input : (input && input.url);
    const m = (init && init.method) || 'GET';
    let finalInit = init || {};
    try {
      const h = new Headers(finalInit.headers || {});
      h.set('Origin', ENDPOINT);           // 模拟浏览器自动带上的 Origin
      finalInit = Object.assign({}, finalInit, { headers: h });
    } catch (e) { /* ignore */ }
    console.log('FETCH>', m, u, '| Origin=', (finalInit.headers && finalInit.headers.get && finalInit.headers.get('Origin')));
    return origFetch(input, finalInit)
      .then(res => { console.log('FETCH<', res.status, u); return res; })
      .catch(e => { console.log('FETCH_ERR', u, String(e && e.message || e)); throw e; });
  };

  try { vm.runInThisContext(js); } catch (e) { console.log('SDK_EVAL_ERR', String(e && e.message || e)); return; }
  console.log('HAS_WBC', typeof globalThis.WorkBuddyCloud);
  if (!globalThis.WorkBuddyCloud) { console.log('NO_GLOBAL'); return; }

  let cloud;
  try {
    cloud = globalThis.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: ENDPOINT, publishableKey: PK });
  } catch (e) { console.log('INIT_ERR', String(e && e.message || e)); return; }

  try {
    const models = await cloud.llm.models.list();
    console.log('MODELS_OK count=', (models && models.length));
    if (models && models.length) {
      const first = models.find(m => m.disabled !== true) || models[0];
      console.log('FIRST=', JSON.stringify({ id: first.id, name: first.name, supportsImages: first.supportsImages }));
    }
  } catch (e) {
    console.log('MODELS_ERR', e && e.error ? JSON.stringify(e.error) : String(e && e.message || e));
    console.log('STATUS', e && e.status, 'REQID', e && e.requestId);
  }
})();
