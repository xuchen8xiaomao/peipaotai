#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建陪跑台 index.html：5 sheet 重构（架构/主线/辅线/简历/学习档案）+ 隐性活跃计时。
只替换 nav 区块与主 <script> 块，保留 style / header / footer / 第二个聊天脚本。"""
import os, io, json

ROOT = r'C:\Users\24186\WorkBuddy\2026-09-10-20-13-10'
HTML = os.path.join(ROOT, 'index.html')
SVG  = os.path.join(ROOT, 'architecture_diagram.svg')
OUT  = HTML

src = open(HTML, encoding='utf-8').read()
svg = open(SVG, encoding='utf-8').read()

# ---------- 1) 替换 nav 为 5 个 tab ----------
nav_old_start = src.index('<nav data-page-node-id="vOAU3invfDfdxsRKvZy8PP"')
nav_old_end = src.index('</nav>', nav_old_start) + len('</nav>')
nav_new = (
'<nav data-page-node-id="vOAU3invfDfdxsRKvZy8PP" class="tabs" id="tabs">\n'
'  <button data-tab="arch">陪跑台架构</button>\n'
'  <button data-tab="main" class="on">主线</button>\n'
'  <button data-tab="side">辅线</button>\n'
'  <button data-tab="resume">简历</button>\n'
'  <button data-tab="study">学习档案</button>\n'
'</nav>'
)
src = src[:nav_old_start] + nav_new + src[nav_old_end:]

# ---------- 2) 替换主 script 块 ----------
script_tag = '<script data-page-node-id="IDWL0IYBJ8EImxvj0yVne5" data-pnid-children="ut620vmrj4IpD34OTz2nhj">'
i = src.index(script_tag)
j = src.index('</script>', i) + len('</script>')

NEW_SCRIPT = r'''
var DB = {
  cap:   "lmO6iKZKy7pQ0a8tuqxq19",
  card:  "4zH7GK3VNQaBr9XHCE5sZH",
  check: "RqgVNlZGB49XuKvLLQ7hvf",
  ev:    "HwXYvz3bF3Hhw1Z7oxctc2",
  log:   "D0qAeD4rB0L28FL0e5inQZ",
  ask:   "kSQ6FwMN7moypXY4RExhee",
  lvl:   "YI5gA3JiABu5sWTVNUfhee",
  mat:   "rLcH92l8foVxGRWizDbTJA",
  qb:    "pQ4o8ka8XxhAaeE3M3JKLm",
  fb:    "4moVqTqT7JRxYIkKEmvS7b",
  resume:"X9WGdVETyOPGE4KDMAghP3",
  jd:    "48W3D38yJk7RKzo5V9pRL3",
  raw:   "X8FBew1mW66tVKy3Qj6FJu",
  side:  "KYgCXpyPwSbMWW2eVtrXBz"
};
var db = (window.__SMART_PAGE__ && window.__SMART_PAGE__.database) || null;
var LIVE = !!db;

var S = {caps:[],cards:[],checks:[],logs:[],asks:[],lvls:[],qbs:[],qbOpen:{},qbCat:"",qbStat:"全部",deepOpen:false,mats:[],resume:[],kbOpen:{},jds:[],raws:[],side:[],tab:"main",loaded:false,fbs:[]};

function todayStr(){var d=new Date();return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
function dayOf(v){return String(v||"").slice(0,10);}
function num(v){var n=parseFloat(v);return isNaN(n)?0:n;}
function ridOf(r){ return (r && (r.record_id || r._id || r.id)) || ""; }
function fmt(s){ return esc(s||"").replace(/\n/g,"<br>"); }
function links(s){ if(!s) return ""; var ps=String(s).split(/\s+/).filter(Boolean); return ps.map(function(u){ return '<a href="'+esc(u)+'" target="_blank" style="color:var(--blue)">'+esc(u)+'</a>'; }).join(" "); }
function flashSaved(){ var h=document.getElementById("saveHint"); if(!h) return; h.textContent="已保存 ✓"; setTimeout(function(){ h.textContent=""; },1800); }

/* ---------- 活跃计时（页面前台可见才计） ---------- */
var AT = { on:false, sec:0, day:todayStr(), last:Date.now() };
function atStatus(){ var el=document.getElementById("todayLabel"); if(el) el.textContent="今日学习 "+Math.floor(AT.sec/60)+" 分钟"+(AT.on?" · 计时中":" · 暂停"); }
function atStart(){ AT.on=true; AT.last=Date.now(); atStatus(); }
function atStop(){ if(AT.on){ AT.sec += Math.floor((Date.now()-AT.last)/1000); AT.last=Date.now(); AT.on=false; atFlush(); atStatus(); } }
function atTick(){ if(AT.on){ AT.sec += 1; if(AT.sec % 60 === 0) atFlush(); atStatus(); } }
function atLoad(){ try{ var v=JSON.parse(localStorage.getItem("at_"+AT.day)||"{}"); if(v.sec) AT.sec=v.sec; }catch(e){} }
function atSave(){ try{ localStorage.setItem("at_"+AT.day, JSON.stringify({sec:AT.sec})); }catch(e){} }
function atFlush(){ atSave(); if(!LIVE) return; var mins=Math.floor(AT.sec/60); if(mins<=0) return;
  var rec=null; S.checks.forEach(function(r){ if(dayOf(r["日期"])===AT.day && (r["任务段"]||"")==="自动计时") rec=r; });
  if(rec){ db.updateRecord({databaseId:DB.check, recordId:ridOf(rec), properties:{"专注分钟":mins}}); }
  else { db.addRecord({databaseId:DB.check, properties:{"日期":AT.day,"任务段":"自动计时","任务标题":"页面浏览学习","专注分钟":mins,"建议分钟":0,"达标":false,"状态":"自动"}}); }
}
document.addEventListener("visibilitychange", function(){ if(document.visibilityState==="visible" && document.hasFocus()) atStart(); else atStop(); });
window.addEventListener("focus", atStart);
window.addEventListener("blur", atStop);
setInterval(atTick, 1000);

/* ---------- 读取 ---------- */
function loadAll(id, startCursor, acc, guard){
  acc = acc || []; guard = guard || 0;
  if(!LIVE) return Promise.resolve([]);
  if(guard > 60) return Promise.resolve(acc);
  return db.query({databaseId:id, pageSize:200, startCursor:startCursor}).then(function(r){
    acc = acc.concat(r.results || []);
    var next = r.nextCursor;
    if(r.hasMore && next && next !== startCursor && (r.results||[]).length) return loadAll(id, next, acc, guard+1);
    return acc;
  });
}
function refresh(){
  if(!LIVE){ S.loaded = true; safeRender(); return Promise.resolve(); }
  return Promise.all([loadAll(DB.cap), loadAll(DB.card), loadAll(DB.check),
                      loadAll(DB.log), loadAll(DB.ask), loadAll(DB.lvl), loadAll(DB.qb), loadAll(DB.mat), loadAll(DB.fb), loadAll(DB.resume),
                      loadAll(DB.jd), loadAll(DB.raw), loadAll(DB.side)])
    .then(function(r){
      S.caps=r[0]; S.cards=r[1]; S.checks=r[2];
      S.logs=r[3]; S.asks=r[4]; S.lvls=r[5]; S.qbs=r[6]; S.mats=r[7]; S.fbs=r[8]; S.resume=r[9];
      S.jds=r[10]; S.raws=r[11]; S.side=r[12];
      S.cards.sort(function(a,b){return dayOf(a["日期"])<dayOf(b["日期"])?1:-1;});
      S.side.sort(function(a,b){return dayOf(a["日期"])<dayOf(b["日期"])?1:-1;});
      S.qbs.sort(function(a,b){return String(a["题号"]||"").localeCompare(String(b["题号"]||""));});
      S.loaded = true; safeRender();
    }).catch(function(e){
      document.getElementById("main").innerHTML = '<div class="card"><b>数据读取失败</b><div class="hint">'+esc(String(e&&e.message||e))+'</div></div>';
    });
}

/* ---------- 渲染分发 ---------- */
function setTabOn(){ document.querySelectorAll("nav.tabs button").forEach(function(b){ b.classList.toggle("on", b.dataset.tab===S.tab); }); }
function safeRender(){ render(); }
function render(){
  if(!S.loaded){ document.getElementById("main").innerHTML='<div class="loading">正在从数据库读取…</div>'; return; }
  setTabOn();
  var m=document.getElementById("main");
  var f=document.getElementById("footer");
  if(S.tab==="arch") m.innerHTML=viewArch();
  else if(S.tab==="main") m.innerHTML=viewMain();
  else if(S.tab==="side") m.innerHTML=viewSide();
  else if(S.tab==="resume") m.innerHTML=viewResume();
  else m.innerHTML=viewStudy();
  bind();
  atStatus();
}

/* ---------- 架构说明页 ---------- */
function viewArch(){
  return '<div class="card arch-top"><h2 style="margin:0">陪跑台是什么 · 怎么用</h2>'+
    '<div class="sub">这是你的个人成长系统。所有数据存在资料库在线表格（手机/电脑同一份），你只通过一个网址使用。</div></div>'+
    ARCH_SVG +
    '<div class="grid g3" style="margin-top:12px">'+
      '<div class="card"><h3 style="margin:0">① 主线</h3><div class="sub">围绕你的目标岗位：模拟项目、岗位知识、面试题、简历包装。你在这上传，AI 帮你按岗位打磨。</div></div>'+
      '<div class="card"><h3 style="margin:0">② 辅线</h3><div class="sub">AI 行业动向 / 知识 / 产品 / 技术。随手记，拓宽视野。</div></div>'+
      '<div class="card"><h3 style="margin:0">③ 简历</h3><div class="sub">上传简历，AI 逐段优化并给建议，左看最新版、右看优化点。</div></div>'+
    '</div>'+
    '<div class="card"><h3 style="margin:0">④ 学习档案</h3><div class="sub">系统自动记录你浏览本页面的时长（仅当前台可见才计时），呈现日历、累计学习分钟、知识数、核心概念数、能力等级变化。</div></div>'+
    '<div class="card"><h3 style="margin:0">怎么运转</h3><div class="sub">空间页=你唯一入口（数据读写）。AI 聊天的后端挂在 Site，被空间页内嵌调用，你不用单独打开。本地文件、旧网页只是制作材料，不是入口。</div></div>';
}

/* ---------- 主线 ---------- */
function viewMain(){
  var jd = S.jds[0];
  var jdCard = jd ? ('<div class="card" style="border-color:var(--blue)"><div class="row-between"><b>🎯 当前目标岗位</b>'+
      (jd["链接"]&&jd["链接"].link?'<a class="btn sm ghost" href="'+esc(jd["链接"].link)+'" target="_blank">JD 链接</a>':'')+'</div>'+
      '<div class="sub" style="margin-top:6px"><span class="tag blue">'+esc(jd["公司"]||"")+'</span> '+esc(jd["岗位"]||"")+(jd["关联能力域"]?' · '+esc(jd["关联能力域"]):'')+'</div>'+
      (jd["JD原文"]?'<div class="blk" style="margin-top:8px;max-height:180px;overflow:auto">'+esc(jd["JD原文"])+'</div>':'<div class="sub">（未填 JD 原文）</div>')):'<div class="card"><b>🎯 目标岗位</b><div class="sub">还没设定。去「简历」页录入岗位 JD，主线就围绕它展开。</div></div>';

  var upForm = '<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)"><h2 style="margin:0">📥 上传到主线知识库</h2>'+
    '<div class="sub">登记一个知识 / 模拟项目 / 简历包装素材（围绕目标岗位）。AI 后续可据此出题、优化简历。</div>'+
    '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px">'+
      '<input id="cTitle" placeholder="标题（必填）" style="flex:1;min-width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
      '<select id="cType" style="width:150px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
        '<option>知识</option><option>模拟项目</option><option>简历包装</option></select>'+
    '</div>'+
    '<div style="margin-top:8px"><textarea id="cCore" rows="2" placeholder="核心概念（选填，一段精要）" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
    '<div style="margin-top:8px"><textarea id="cDeep" rows="3" placeholder="深度资料 / 你的项目落地（选填）" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
    '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px">'+
      '<input id="cUrl" placeholder="链接（选填）" style="flex:1;min-width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
      '<input id="cDom" placeholder="能力域（选填）" style="width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
    '</div>'+
    '<div style="margin-top:8px"><button class="btn sm" data-act="cardAdd">入库</button><span class="hint" style="margin-left:8px" id="cMsg"></span></div></div>';

  var filters = ['全部','知识','模拟项目','简历包装'];
  var fhtml = '<div class="sub" style="margin:10px 0 4px">按类型筛选：'+filters.map(function(f){ return '<span class="tag'+(S.mFilter===f?' on':'')+'" data-act="mFilter" data-f="'+esc(f)+'">'+esc(f)+'</span>'; }).join(' ')+'</div>';

  var list = S.cards.slice();
  if(S.mFilter && S.mFilter!=="全部") list = list.filter(function(c){ return (c["类型"]||"知识")===S.mFilter; });
  var cardsHtml = list.map(function(c){
    var t=(c["类型"]||"知识");
    var body = (c["核心概念"]?'<div class="sec"><span class="sh">核心概念</span><div class="blk">'+fmt(c["核心概念"])+'</div></div>':'')+
               (c["深度资料"]?'<div class="sec"><span class="sh t">深度资料</span><div class="blk">'+fmt(c["深度资料"])+'</div></div>':'')+
               (c["对标产品"]?'<div class="sec"><span class="sh a">对标产品</span><div class="blk">'+fmt(c["对标产品"])+'</div></div>':'')+
               (c["落到你的项目"]?'<div class="sec"><span class="sh g">落到你的项目</span><div class="blk">'+fmt(c["落到你的项目"])+'</div></div>':'')+
               (c["延伸阅读"]?'<div class="sec"><span class="sh">延伸阅读</span>'+links(c["延伸阅读"])+'</div>':'');
    return '<div class="wfc" data-act="kbExpand" data-rid="'+esc(ridOf(c))+'"><div class="wt">'+esc(c["标题"]||"（无标题）")+'</div>'+
      '<div class="wm"><span class="tag">'+esc(t)+'</span>'+(c["能力域"]?'<span class="tag">'+esc(c["能力域"])+'</span>':'')+'<span class="chev">▾</span></div>'+
      '<div class="wb">'+(body||'<div class="sub">（暂无内容）</div>')+'</div></div>';
  }).join("");
  if(!list.length) cardsHtml='<div class="card"><div class="sub">该类型还没有内容。用上方表单上传第一条'+(S.mFilter&&S.mFilter!=="全部"?"（"+esc(S.mFilter)+"）":"")+'。</div></div>';

  var qbHtml = S.qbs.length ? ('<div class="card"><h2 style="margin:0">面试题（'+S.qbs.length+' 道）</h2><div class="sub">由 AI 出题，按岗位考察点准备。</div></div>'+S.qbs.slice(0,12).map(function(r){
    var body='<div class="sec"><span class="sh">考察点</span><div class="blk">'+fmt(r["考察点"])+'</div></div>'+
             '<div class="sec"><span class="sh t">答题框架</span><div class="blk">'+fmt(r["答题框架"])+'</div></div>'+
             (r["你的素材"]?'<div class="sec"><span class="sh a">你的素材</span><div class="blk">'+fmt(r["你的素材"])+'</div></div>':'');
    return '<div class="wfc" data-act="kbExpand" data-rid="'+esc(ridOf(r))+'"><div class="wt">'+esc((r["题号"]||"")+" "+(r["题目"]||""))+'</div>'+
      '<div class="wm"><span class="tag teal">面试题</span>'+(r["类别"]?'<span class="tag">'+esc(r["类别"])+'</span>':'')+'<span class="chev">▾</span></div>'+
      '<div class="wb">'+(body||'<div class="sub">（暂无内容）</div>')+'</div></div>';
  }).join("")) : '';

  var matHtml = S.mats.length ? ('<div class="card"><h2 style="margin:0">素材投喂（'+S.mats.length+' 条）</h2><div class="sub">你投喂的原始资料，是知识卡 / 面试题的引用来源。</div></div>'+S.mats.slice().sort(function(a,b){return dayOf(b["入库日期"])<dayOf(a["入库日期"])?-1:1;}).slice(0,20).map(function(r){
    var link=r["链接"]||{}; var lh=link.link||"";
    return '<div class="row-between" style="padding:8px 0;border-bottom:1px solid var(--line)"><div style="flex:1;min-width:0"><span class="tag blue">'+esc(r["类型"]||"")+'</span> '+esc(r["标题"]||"")+(lh?' <a href="'+esc(lh||"#")+'" target="_blank" style="color:var(--blue)">🔗</a>':'')+'<div class="sub" style="font-size:11px;margin-top:2px">'+esc(dayOf(r["入库日期"]))+'</div></div></div>';
  }).join("")) : '';

  return jdCard + upForm + '<div class="card"><h2 style="margin:0">主线知识库（'+S.cards.length+' 条）</h2><div class="sub">知识 / 模拟项目 / 简历包装，围绕目标岗位沉淀。</div></div>'+fhtml+'<div class="wf">'+cardsHtml+'</div>'+qbHtml+matHtml;
}

/* ---------- 辅线 ---------- */
function viewSide(){
  var upForm = '<div class="card" style="border-color:var(--amber);box-shadow:0 1px 0 var(--amberL)"><h2 style="margin:0">📥 记录一条 AI 动向 / 知识</h2>'+
    '<div class="sub">AI 行业、产品、技术、方法论——随手记，拓宽视野。</div>'+
    '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px">'+
      '<input id="sTitle" placeholder="标题（必填）" style="flex:1;min-width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
      '<select id="sCat" style="width:150px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
        '<option>动向</option><option>知识</option><option>产品</option><option>技术</option><option>其他</option></select>'+
    '</div>'+
    '<div style="margin-top:8px"><textarea id="sCore" rows="2" placeholder="核心概念（选填）" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
    '<div style="margin-top:8px"><textarea id="sDeep" rows="3" placeholder="深度资料（选填）" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
    '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px">'+
      '<input id="sUrl" placeholder="链接（选填）" style="flex:1;min-width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px">'+
    '</div>'+
    '<div style="margin-top:8px"><button class="btn sm" data-act="sideAdd">入库</button><span class="hint" style="margin-left:8px" id="sMsg"></span></div></div>';

  var cardsHtml = S.side.map(function(c){
    var body=(c["核心概念"]?'<div class="sec"><span class="sh">核心概念</span><div class="blk">'+fmt(c["核心概念"])+'</div></div>':'')+
               (c["深度资料"]?'<div class="sec"><span class="sh t">深度资料</span><div class="blk">'+fmt(c["深度资料"])+'</div></div>':'')+
               (c["链接"]&&c["链接"].link?'<div class="sec"><span class="sh a">链接</span><div class="blk"><a href="'+esc(c["链接"].link)+'" target="_blank" style="color:var(--blue)">'+esc(c["链接"].link)+'</a></div></div>':'');
    return '<div class="wfc" data-act="kbExpand" data-rid="'+esc(ridOf(c))+'"><div class="wt">'+esc(c["标题"]||"（无标题）")+'</div>'+
      '<div class="wm"><span class="tag amber">'+esc(c["分类"]||"其他")+'</span><span class="chev">▾</span></div>'+
      '<div class="wb">'+(body||'<div class="sub">（暂无内容）</div>')+'</div></div>';
  }).join("");
  if(!S.side.length) cardsHtml='<div class="card"><div class="sub">还没有辅线内容。看到值得记的 AI 动向 / 知识，用上方表单记一条。</div></div>';

  return upForm + '<div class="card"><h2 style="margin:0">辅线知识库（'+S.side.length+' 条）</h2><div class="sub">AI 行业 / 产品 / 技术 / 方法论，随手积累。</div></div><div class="wf">'+cardsHtml+'</div>';
}

/* ---------- 简历（两栏） ---------- */
function fullResumeCard(){
  var rec=null;
  for(var i=0;i<S.resume.length;i++){ if((S.resume[i]["区块"]||"").indexOf("优化版全文")>=0){ rec=S.resume[i]; break; } }
  if(!rec){
    var st=document.getElementById("resumeStatic"); var txt=st?st.textContent:"";
    if(!txt) return '<div class="card"><div class="sub">还没有简历。点上方「上传简历」投喂第一份。</div></div>';
    return '<div class="card" style="border-color:var(--blue)"><div class="row-between"><h2 style="margin:0">📄 我的简历（优化版 · 只读快照）</h2>'+
      '<a class="btn sm ghost" href="https://www.workbuddy.cn/space/d/3DxcmFIl7G2SGJjdPXvqH5" target="_blank">到空间页更新</a></div>'+
      '<div class="blk" style="margin-top:8px;white-space:pre-wrap;max-height:520px;overflow:auto;font-size:13px;line-height:1.6">'+esc(txt)+'</div></div>';
  }
  return '<div class="card" style="border-color:var(--blue)"><div class="row-between"><h2 style="margin:0">📄 我的简历（优化版）</h2>'+
    '<button class="btn sm ghost" data-act="copyResume">复制全文</button></div>'+
    '<div class="blk" style="margin-top:8px;white-space:pre-wrap;max-height:520px;overflow:auto;font-size:13px;line-height:1.6">'+esc(rec["优化后"]||"")+'</div></div>';
}
function copyText(t){ if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(function(){ flashSaved(); }, function(){ fbCopy(t); }); } else { fbCopy(t); } }
function fbCopy(t){ var ta=document.createElement("textarea"); ta.value=t; ta.style.position="fixed"; ta.style.left="-9999px"; document.body.appendChild(ta); ta.select(); try{ document.execCommand("copy"); flashSaved(); }catch(e){ alert("复制失败，请手动选择文字复制"); } document.body.removeChild(ta); }
function openUpload(){ var m=document.getElementById("uploadMask"); if(m) m.classList.remove("hidden"); }
function closeUpload(){ var m=document.getElementById("uploadMask"); if(m) m.classList.add("hidden"); }
function viewResume(){
  if(!LIVE){
    return '<div class="robanner" style="padding:14px 16px;font-size:13.5px;line-height:1.7"><b>⚠️ 当前是只读预览，不能上传 / 保存。</b><br>请在 WorkBuddy 资料库里打开「陪跑台-数据版」节点（或下方按钮在已登录浏览器新标签打开）上传并永久保存：<br>'+
      '<a class="robtn" href="https://www.workbuddy.cn/space/d/3DxcmFIl7G2SGJjdPXvqH5" target="_blank" style="margin-top:10px">↗ 在资料库打开可写版</a></div>'+fullResumeCard();
  }
  var uploadBtn='<button class="btn" data-act="openUpload" style="width:100%;padding:10px;font-size:13.5px">📥 上传简历 / 录入 JD</button>'+
    '<div class="sub" style="margin-top:6px;margin-bottom:12px">支持 PDF / Word / TXT，或粘贴文字；JD 填公司、岗位与要求。点上方按钮在弹窗填写。</div>';

  var jdSec = (!S.jds.length) ? '<div class="card"><h2 style="margin:0">💼 岗位 JD</h2><div class="sub">还没有 JD。点上方按钮录入，主线就围绕它展开。</div></div>' :
    '<div class="card"><h2 style="margin:0">💼 岗位 JD（'+S.jds.length+' 条）</h2>'+S.jds.slice().sort(function(a,b){return dayOf(b["入库日期"])<dayOf(a["入库日期"])?-1:1;}).map(function(r){
      return '<div style="padding:8px 0;border-bottom:1px solid var(--line)"><span class="tag blue">'+esc(r["公司"]||"")+'</span> '+esc(r["岗位"]||"")+(r["关联能力域"]?' · '+esc(r["关联能力域"]):'')+'<div class="sub" style="font-size:11px;margin-top:2px">'+esc(dayOf(r["入库日期"]))+'</div></div>';
    }).join("")+'</div>';

  var segs = S.resume.filter(function(r){ return (r["区块"]||"").indexOf("优化版全文")<0; });
  var optHead='<div class="card"><h2 style="margin:0">简历优化建议（'+segs.length+' 段）</h2><div class="sub">每段「原始 → 优化后 → 为什么 → 面试增益」。</div></div>';
  var cards=segs.map(function(r){
    var sec=function(t,c){ return c?('<div class="sec"><span class="sh">'+t+'</span><div class="blk">'+fmt(c)+'</div></div>'):''; };
    return '<div class="card" style="border-color:var(--blue)"><h2 style="margin:0">'+esc(r["区块"]||"简历优化")+'</h2>'+
      sec("原始简历",r["原始简历"])+sec("优化后",r["优化后"])+sec("优化点",r["优化点"])+
      sec("背后知识（为什么这么改）",r["背后知识（为什么这么改）"])+sec("面试视角增益",r["面试视角增益"])+sec("关联能力域",r["关联能力域"])+
      (r["状态"]?'<div class="sub" style="margin-top:6px">状态：'+esc(r["状态"])+'</div>':'')+'</div>';
  }).join("");
  if(!segs.length) cards='<div class="card"><div class="sub">还没有优化对照。上传简历后，让 AI 逐段优化即可生成。</div></div>';

  var modal='<div class="modal-mask hidden" id="uploadMask" data-act="closeUpload"><div class="modal"><div class="modal-head"><b>📥 上传简历 / 录入 JD</b><button class="modal-close" data-act="closeUpload" aria-label="关闭">×</button></div>'+
    '<div class="modal-body"><div class="xsec"><h3>① 上传你的简历</h3>'+
      '<div style="margin-top:8px"><input id="rawFile" type="file" accept=".pdf,.doc,.docx,.txt" style="font-size:13px"> <span class="hint">PDF/Word 自动提取文字</span></div>'+
      '<div style="margin-top:8px"><textarea id="rawText" rows="4" placeholder="或在此粘贴简历全文" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
      '<div style="margin-top:8px"><button class="btn sm" data-act="rawAdd">提交并收录</button><span class="hint" style="margin-left:8px" id="rawMsg"></span></div></div>'+
      '<div class="xsec"><h3>② 录入岗位 JD</h3>'+
      '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px"><input id="jdCo" placeholder="公司（必填）" style="flex:1;min-width:140px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"><input id="jdPos" placeholder="岗位（必填）" style="flex:1;min-width:140px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></div>'+
      '<div style="margin-top:8px"><textarea id="jdText" rows="3" placeholder="JD 原文 / 核心要求" style="width:100%;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></textarea></div>'+
      '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px"><input id="jdUrl" placeholder="JD 链接（选填）" style="flex:1;min-width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"><input id="jdDom" placeholder="关联能力域（选填）" style="width:160px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:#fcfcfa;color:var(--tx);font-size:13px"></div>'+
      '<div style="margin-top:8px"><button class="btn sm" data-act="jdAdd">入库</button><span class="hint" style="margin-left:8px" id="jdMsg"></span></div></div></div></div></div>';

  return uploadBtn +
    '<div class="r2col"><div class="col">'+fullResumeCard()+'</div>'+
    '<div class="col">'+jdSec+optHead+cards+'</div></div>' + modal;
}

/* ---------- 学习档案 ---------- */
function capMini(){
  var doms=domains(); if(!doms.length) return '';
  var grid=doms.map(function(d){
    var cur=0,tg=0; d.items.forEach(function(c){ cur+=num(c["当前等级"]); tg+=num(c["目标等级"]); });
    var n=d.items.length||1, ratio=tg?Math.min(1,(cur/n)/(tg/n)):0;
    var cls=ratio>=0.95?"teal":(ratio>=0.6?"amber":"red");
    var items=d.items.map(function(c){ return '<span class="tag">'+esc(c["能力项"]||"")+' <b>'+num(c["当前等级"])+'/'+num(c["目标等级"])+'</b></span>'; }).join(" ");
    return '<div class="card"><div class="row-between" style="margin-bottom:6px"><b>'+esc(d.name)+'</b><span class="sub">'+(cur/n).toFixed(2)+' / '+(tg/n).toFixed(2)+'</span></div>'+
      '<div class="bar '+cls+'" style="margin-bottom:8px"><i style="width:'+Math.round(ratio*100)+'%"></i></div><div style="display:flex;flex-wrap:wrap;gap:5px">'+items+'</div></div>';
  }).join("");
  return '<div class="card"><h2 style="margin:0">能力地图（精简）</h2><div class="sub">按能力域归并，展示当前 / 目标等级。</div></div>'+grid;
}
function domains(){ var m={}; S.caps.forEach(function(c){ var d=c["能力域"]||"其他"; (m[d]=m[d]||{name:d,items:[]}).items.push(c); }); return Object.keys(m).map(function(k){return m[k];}); }
function viewStudy(){
  var totalMin=0; S.checks.forEach(function(r){ totalMin+=num(r["专注分钟"]); });
  totalMin += Math.floor(AT.sec/60);
  var coreN = S.cards.filter(function(c){ return (c["核心概念"]||"").trim(); }).length;
  var knowN = S.cards.length + S.side.length;
  var lvN = S.lvls.length;
  // 日历：最近 35 天
  var byDay={}; S.checks.forEach(function(r){ var d=dayOf(r["日期"]); byDay[d]=(byDay[d]||0)+num(r["专注分钟"]); });
  var dt=new Date(); dt.setDate(dt.getDate()-34); var cells="";
  for(var i=0;i<35;i++){ var k=dt.getFullYear()+"-"+String(dt.getMonth()+1).padStart(2,"0")+"-"+String(dt.getDate()).padStart(2,"0");
    var v=Math.round(byDay[k]||0); cells+='<div class="cal'+(v?' on':'')+'" title="'+k+' · '+v+' 分钟">'+(dt.getDate())+'</div>'; dt.setDate(dt.getDate()+1); }
  // 近14天
  var byDay2={}; S.checks.forEach(function(r){ var d=dayOf(r["日期"]); byDay2[d]=(byDay2[d]||0)+num(r["专注分钟"]); });
  var dt2=new Date(); dt2.setDate(dt2.getDate()-13); var days=[],maxV=1;
  for(var x=0;x<14;x++){ var k2=dt2.getFullYear()+"-"+String(dt2.getMonth()+1).padStart(2,"0")+"-"+String(dt2.getDate()).padStart(2,"0"); var v2=Math.round(byDay2[k2]||0); days.push({k:k2,v:v2}); if(v2>maxV)maxV=v2; dt2.setDate(dt2.getDate()+1); }
  var bars=days.map(function(d){ return '<div class="b '+(d.v?'':'zero')+'" style="height:'+Math.max(2,Math.round(d.v/maxV*78))+'px" title="'+d.k+' · '+d.v+' 分钟"></div>'; }).join("");
  var barLbl='<div class="bx">'+days.map(function(d,i){ return '<div style="flex:1;text-align:center;overflow:hidden">'+(i%3===0||i===13?String(d.k).slice(5):"")+'</div>'; }).join("")+'</div>';
  var lvList=S.lvls.slice(0,10).map(function(r){ var up=num(r["新等级"])>num(r["旧等级"]); return '<div class="row-between" style="padding:7px 0;border-bottom:1px solid var(--line)"><div><span class="tag blue">'+esc(r["能力项ID"]||"")+'</span> '+esc(r["能力项"]||"")+'<div class="sub" style="font-size:11px;margin-top:2px">'+esc(dayOf(r["日期"]))+'</div></div><span class="tag '+(up?'ok':'bad')+'">'+num(r["旧等级"])+' → '+num(r["新等级"])+'</span></div>'; }).join("")||'<div class="sub">还没有等级变化。</div>';
  var logList=S.logs.slice(0,12).map(function(r){ return '<div style="padding:9px 0;border-bottom:1px solid var(--line)"><div class="row-between"><div><span class="tag blue">'+esc(r["任务段"]||"")+'</span> '+esc(r["任务标题"]||"")+'<div class="sub" style="font-size:11px;margin-top:2px">'+esc(dayOf(r["日期"]))+'</div></div><span class="tag '+(r["达标"]?'ok':'warn')+'">'+num(r["专注分钟"])+' 分钟</span></div>'+(r["我的产出"]?'<div class="hint" style="margin-top:6px">产出：'+esc(r["我的产出"])+'</div>':'')+(r["AI总结"]?'<div class="hint" style="margin-top:4px;color:var(--teal)">教练总结：'+esc(r["AI总结"])+'</div>':'')+'</div>'; }).join("")||'<div class="sub">还没有学习记录。</div>';
  return '<div class="card" style="border-color:var(--green)"><div class="row-between"><b>⏱ 学习计时</b><span class="tag '+(AT.on?'ok':'')+'">'+(AT.on?'● 计时中（页面在前台）':'○ 暂停')+'</span></div>'+
    '<div class="sub" style="margin-top:6px">系统在你打开本页面且置于前台时自动累加学习分钟；切到后台或最小化不计时。数据实时写入打卡表。</div></div>'+
    '<div class="grid g4" style="margin:12px 0"><div class="kpi"><div class="n">'+Math.floor(totalMin)+'</div><div class="l">累计学习（分钟）</div></div>'+
      '<div class="kpi"><div class="n">'+(AT.on?'进行中':Math.floor(AT.sec/60))+'</div><div class="l">今日（分钟）</div></div>'+
      '<div class="kpi"><div class="n">'+knowN+'</div><div class="l">知识数（主+辅）</div></div>'+
      '<div class="kpi"><div class="n">'+coreN+'</div><div class="l">核心概念数</div></div></div>'+
    '<div class="card"><h2>近 35 天打卡日历</h2><div class="calgrid">'+cells+'</div><div class="sub" style="margin-top:6px">高亮 = 当天有学习记录</div></div>'+
    '<div class="card"><h2>近 14 天专注时长</h2><div class="bars">'+bars+'</div>'+barLbl+'</div>'+
    '<div class="card"><h2>能力等级变化（'+lvN+' 次）</h2>'+lvList+'</div>'+
    '<div class="card"><h2>学习记录（最近 12 条）</h2>'+logList+'</div>'+
    capMini();
}

/* ---------- 事件 ---------- */
function bind(){
  document.querySelectorAll("[data-act]").forEach(function(el){
    var a=el.dataset.act;
    if(a==="kbExpand"){ el.onclick=function(){ var rid=el.dataset.rid; S.kbOpen[rid]=!S.kbOpen[rid]; var wb=el.querySelector(".wb"); if(wb) wb.classList.toggle("open"); }; }
    else if(a==="mFilter"){ el.onclick=function(){ S.mFilter=el.dataset.f; render(); }; }
    else if(a==="copyResume"){ el.onclick=function(){ var rec=null; for(var i=0;i<S.resume.length;i++){ if((S.resume[i]["区块"]||"").indexOf("优化版全文")>=0){ rec=S.resume[i]; break; } } if(rec) copyText(rec["优化后"]||""); }; }
    else if(a==="openUpload"){ el.onclick=openUpload; }
    else if(a==="closeUpload"){ el.onclick=closeUpload; }
    else if(a==="rawAdd"){ el.onclick=rawAdd; }
    else if(a==="jdAdd"){ el.onclick=jdAdd; }
    else if(a==="cardAdd"){ el.onclick=cardAdd; }
    else if(a==="sideAdd"){ el.onclick=sideAdd; }
  });
  document.querySelectorAll("nav.tabs button").forEach(function(b){ b.onclick=function(){ document.querySelectorAll("nav.tabs button").forEach(function(x){ x.classList.remove("on"); }); b.classList.add("on"); S.tab=b.dataset.tab; render(); }; });
}
function rawAdd(){
  var f=document.getElementById("rawFile"), t=document.getElementById("rawText"), msg=document.getElementById("rawMsg");
  var txt=t?t.value.trim():"";
  if(f && f.files && f.files[0]){ /* PDF/Word 提取简化：交给 AI 处理，这里存文件链接逻辑省略，提示用户粘贴 */ msg.textContent="PDF/Word 提取请在 AI 对话中说「读取并优化我的简历」"; return; }
  if(!txt){ msg.textContent="请粘贴简历文字，或在 AI 对话中上传文件"; return; }
  if(!LIVE){ msg.textContent="只读环境不能保存"; return; }
  db.addRecord({databaseId:DB.raw, properties:{"内容":txt,"版本":"简历","状态":"待优化"}}).then(function(){ S.raws.push({"内容":txt}); msg.textContent="已收录，去 AI 对话说「优化我的简历」"; closeUpload(); refresh(); });
}
function jdAdd(){
  var co=document.getElementById("jdCo"), pos=document.getElementById("jdPos"), tx=document.getElementById("jdText"), url=document.getElementById("jdUrl"), dom=document.getElementById("jdDom"), msg=document.getElementById("jdMsg");
  if(!co.value.trim()||!pos.value.trim()){ msg.textContent="公司和岗位必填"; return; }
  if(!LIVE){ msg.textContent="只读环境不能保存"; return; }
  var props={"公司":co.value.trim(),"岗位":pos.value.trim(),"JD原文":tx.value.trim(),"关联能力域":dom.value.trim(),"状态":"已收录"};
  if(url.value.trim()) props["链接"]={link:url.value.trim()};
  db.addRecord({databaseId:DB.jd, properties:props}).then(function(){ msg.textContent="已录入"; closeUpload(); refresh(); });
}
function cardAdd(){
  var ti=document.getElementById("cTitle"), ty=document.getElementById("cType"), co=document.getElementById("cCore"), de=document.getElementById("cDeep"), ur=document.getElementById("cUrl"), dm=document.getElementById("cDom"), msg=document.getElementById("cMsg");
  if(!ti.value.trim()){ msg.textContent="标题必填"; return; }
  if(!LIVE){ msg.textContent="只读环境不能保存"; return; }
  var props={"标题":ti.value.trim(),"类型":ty.value,"核心概念":co.value.trim(),"深度资料":de.value.trim(),"能力域":dm.value.trim(),"日期":todayStr(),"状态":"未读"};
  if(ur.value.trim()) props["延伸阅读"]=ur.value.trim();
  db.addRecord({databaseId:DB.card, properties:props}).then(function(){ msg.textContent="已入库"; refresh(); });
}
function sideAdd(){
  var ti=document.getElementById("sTitle"), ca=document.getElementById("sCat"), co=document.getElementById("sCore"), de=document.getElementById("sDeep"), ur=document.getElementById("sUrl"), msg=document.getElementById("sMsg");
  if(!ti.value.trim()){ msg.textContent="标题必填"; return; }
  if(!LIVE){ msg.textContent="只读环境不能保存"; return; }
  var props={"标题":ti.value.trim(),"分类":ca.value,"核心概念":co.value.trim(),"深度资料":de.value.trim(),"日期":todayStr(),"来源":"页面上传"};
  if(ur.value.trim()) props["链接"]={link:ur.value.trim()};
  db.addRecord({databaseId:DB.side, properties:props}).then(function(){ msg.textContent="已入库"; refresh(); });
}

/* ---------- 启动 ---------- */
function injectCSS(){ var st=document.createElement("style"); st.textContent=
  ".r2col{display:flex;gap:16px;flex-wrap:wrap}.r2col .col{flex:1;min-width:300px}"+
  ".calgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}.cal{border:1px solid var(--line);border-radius:6px;text-align:center;padding:7px 0;font-size:12px;color:var(--tx2)}.cal.on{background:var(--greenL);border-color:var(--green);color:var(--green);font-weight:600}"+
  ".tag.on{background:var(--blueL);border-color:var(--blue);color:var(--blue)}"+
  ".arch-top{background:linear-gradient(0deg,var(--blueL),transparent)}"+
  ".col h2,.col .card h2{font-size:14px}"; document.head.appendChild(st); }
(function init(){
  injectCSS(); atLoad(); atStatus();
  var btns=document.querySelectorAll("nav.tabs button"); btns.forEach(function(b){ if(b.dataset.tab===S.tab) b.classList.add("on"); });
  refresh();
})();
'''

# 注入架构图 SVG（转义为合法 JS 字符串字面量，避免多行/引号破坏语法）
svg_inline = svg.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()
svg_js = json.dumps(svg_inline, ensure_ascii=False)
NEW_SCRIPT = NEW_SCRIPT.replace('ARCH_SVG', svg_js)

src = src[:i] + '<script data-page-node-id="IDWL0IYBJ8EImxvj0yVne5" data-pnid-children="ut620vmrj4IpD34OTz2nhj">\n' + NEW_SCRIPT + '\n</script>' + src[j:]

open(OUT, 'w', encoding='utf-8').write(src)
print("written", OUT, len(src))
