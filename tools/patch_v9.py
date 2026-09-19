# -*- coding: utf-8 -*-
import io
P = r"C:/Users/24186/WorkBuddy/2026-09-10-20-13-10/index.html"
s = io.open(P, encoding="utf-8").read()
def rep(old, new=1, n=1):
    global s
    c = s.count(old) if isinstance(old, str) else 0
    s = s.replace(old, new, n)
    assert s.count(old.replace(new, "", 1) if False else old) >= 0, "noop"
    assert c == n, ("count mismatch want", n, "got", c, "for", old[:60])
def slice_del(start_marker, end_marker, label):
    global s
    a = s.index(start_marker); b = s.index(end_marker)
    removed = s[a:b]
    s = s[:a] + s[b:]
    print("deleted", label, len(removed), "chars")

# 1) 删除无用 helper（overall/gaps/withEvidence/evOf），仅被总览/能力地图使用
slice_del("function overall(){", "function todayCard(){", "helpers(overall,gaps,withEvidence,evOf)")

# 2) 删除 viewOverview + viewMap 两个函数（合并进学习档案 / 删除）
slice_del("function viewOverview(){", "function viewToday(){", "viewOverview+viewMap")

# 3) 在学习档案前插入简化的能力地图 capMini()
capMini = '''function capMini(){
  var doms = domains();
  if(!doms.length) return '<div class="card"><h2 style="margin:0">能力地图（精简）</h2><div class="sub">从能力看板搬来的只读视图，按能力域归并，展示当前等级 / 目标等级。<br>暂无能力项数据——在能力看板校准等级后，这里会自动出现。</div></div>';
  var grid = doms.map(function(d){
    var cur=0,tg=0; d.items.forEach(function(c){ cur+=num(c["当前等级"]); tg+=num(c["目标等级"]); });
    var n=d.items.length||1, ratio=tg?Math.min(1,(cur/n)/(tg/n)):0;
    var cls=ratio>=0.95?"teal":(ratio>=0.6?"amber":"red");
    var items = d.items.map(function(c){
      return '<span class="tag">'+esc(c["能力项"]||"")+' <b>'+num(c["当前等级"])+'/'+num(c["目标等级"])+'</b></span>';
    }).join(" ");
    return '<div class="card"><div class="row-between" style="margin-bottom:6px"><b>'+esc(d.name)+'</b>'+
      '<span class="sub">'+(cur/n).toFixed(2)+' / '+(tg/n).toFixed(2)+'</span></div>'+
      '<div class="bar '+cls+'" style="margin-bottom:8px"><i style="width:'+Math.round(ratio*100)+'%"></i></div>'+
      '<div style="display:flex;flex-wrap:wrap;gap:5px">'+items+'</div></div>';
  }).join("");
  return '<div class="card"><h2 style="margin:0">能力地图（精简）</h2>'+
    '<div class="sub">从能力看板搬来的只读视图，按能力域归并，展示当前等级 / 目标等级。等级校准入口已随能力看板一并并入学习档案。</div></div>'+grid;
}

'''
assert s.count("function viewArch(){") == 1
s = s.replace("function viewArch(){", capMini + "function viewArch(){", 1)

# 4) 在简历优化前插入 fullResumeCard + copyText + fbCopy
resumeHelpers = '''function fullResumeCard(){
  var rec=null;
  for(var i=0;i<S.resume.length;i++){ if((S.resume[i]["区块"]||"").indexOf("优化版全文")>=0){ rec=S.resume[i]; break; } }
  if(!rec) return '';
  return '<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">'+
    '<div class="row-between"><h2 style="margin:0">\\u{1F4C4} 我的简历（优化版）</h2>'+
    '<button class="btn sm ghost" data-act="copyResume">复制全文</button></div>'+
    '<div class="sub">已按陪跑台宝典《简历相关》口径逐段优化，可直接复用。点「复制全文」粘贴到招聘平台 / 导出 PDF。需要更新时说「更新我的简历」即可。</div>'+
    '<div class="blk" style="margin-top:8px;white-space:pre-wrap;max-height:440px;overflow:auto;font-size:13px;line-height:1.6">'+esc(rec["优化后"]||"")+'</div></div>';
}
function copyText(t){
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(function(){ flashSaved(); }, function(){ fbCopy(t); });
  } else { fbCopy(t); }
}
function fbCopy(t){
  var ta=document.createElement("textarea"); ta.value=t; ta.style.position="fixed"; ta.style.left="-9999px";
  document.body.appendChild(ta); ta.select(); try{ document.execCommand("copy"); flashSaved(); }catch(e){ alert("复制失败，请手动选择文字复制"); } document.body.removeChild(ta);
}

'''
assert s.count("function viewResume(){") == 1
s = s.replace("function viewResume(){", resumeHelpers + "function viewResume(){", 1)

# 5) 学习档案 return 末尾追加 capMini()
rep('    \'<div class="card"><h2>学习记录（最近 15 条）</h2>\'+logList+\'</div>\';\n}',
    '    \'<div class="card"><h2>学习记录（最近 15 条）</h2>\'+logList+\'</div>\'+\n    capMini();\n}')

# 6) 简历优化 return 加入 fullResumeCard()
rep('  return rawForm + rawNow + jdForm + jdList + optHead + cards;',
    '  return rawForm + rawNow + jdForm + jdList + fullResumeCard() + optHead + cards;')

# 7) bind 中加入 copyResume 处理器（在 fbSubmit 之前）
copyHandler = '''    else if(a==="copyResume") el.onclick = function(){
      var t=""; for(var i=0;i<S.resume.length;i++){ if((S.resume[i]["区块"]||"").indexOf("优化版全文")>=0){ t=S.resume[i]["优化后"]||""; break; } }
      if(!t){ alert("还没生成优化版简历，先在 AI 对话里说「优化我的简历」。"); return; }
      copyText(t);
    };
'''
assert s.count('    else if(a==="fbSubmit") el.onclick = function(){') == 1
s = s.replace('    else if(a==="fbSubmit") el.onclick = function(){', copyHandler + '    else if(a==="fbSubmit") el.onclick = function(){', 1)

# 8) 删除导航里的 总览 / 能力地图 按钮
rep('  <button data-tab="overview" data-page-node-id="eqQKjmFFTGFYJ9N3pE0iN8">总览</button>\n  <button data-tab="map" data-page-node-id="Es1FT5DmsJVe1smiVFd8dM">能力地图</button>\n', "")

# 9) 删除 render() 里对这两个视图的调用
rep('  if(S.tab==="overview") m.innerHTML = viewOverview();\n  else if(S.tab==="map") m.innerHTML = viewMap();\n  else if(S.tab==="today") m.innerHTML = viewToday();\n',
    '  if(S.tab==="today") m.innerHTML = viewToday();\n')

io.open(P, "w", encoding="utf-8").write(s)
print("OK, new length", len(s))
