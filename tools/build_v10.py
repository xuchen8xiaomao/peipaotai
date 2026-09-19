# -*- coding: utf-8 -*-
"""v10：以「空间页线上版」为基底重建 index.html（线上版 UI 更完整），并补两处能力：
   1) 只读(非资料库环境，如固定网址 Site)下：不再隐藏导航、默认停在「简历优化」，
      且展示已固化的简历只读快照（div#resumeStatic + fullResumeCard fallback）。
   2) 保留线上版全部 UI（弹窗上传、JD 折叠表、只读 rovbanner）。
"""
import html
import os
import re
import shutil

BASE = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
LIVE = os.path.join(BASE, "data", "_live", "index.html")
OUT = os.path.join(BASE, "index.html")
MD = os.path.join(BASE, "data", "简历优化版.md")

src = open(LIVE, encoding="utf-8").read()
print("base(live) chars=%d" % len(src))


def rep(old, new, n=1):
    global src
    assert old in src, "未找到锚点：%s" % old[:80]
    src = src.replace(old, new, n)


# ---------- 1) 简历全文静态固化 ----------
md = open(MD, encoding="utf-8").read()
text = md[md.index("## 个人简介"):].strip()
out = []
for ln in text.split("\n"):
    s = re.sub(r"^#+\s*", "", ln)
    s = re.sub(r"^>\s?", "", s)
    s = re.sub(r"^\s*[-*]\s+", "• ", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"^---+$", "", s)
    if s.strip():
        out.append(s)
static_txt = html.escape("\n".join(out).strip())
div = '<div id="resumeStatic" hidden>\n' + static_txt + "\n</div>"
if '<div id="resumeStatic"' in src:
    src = re.sub(r'<div id="resumeStatic"[^>]*>.*?</div>', div, src, flags=re.S)
else:
    src = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + div, src, count=1)
assert '<div id="resumeStatic"' in src

# ---------- 2) fullResumeCard 只读 fallback ----------
rep(
    '  if(!rec) return \'\';\n  return \'<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">\'+',
    '  if(!rec){\n'
    '    var st=document.getElementById("resumeStatic");\n'
    '    var txt=st?st.textContent:"";\n'
    '    if(!txt) return \'\';\n'
    '    return \'<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">\'+\n'
    '      \'<div class="row-between"><h2 style="margin:0">\\u{1F4C4} 我的简历（优化版 · 只读快照）</h2>\'+\n'
    '      \'<a class="btn sm ghost" href="https://www.workbuddy.cn/space/d/3DxcmFIl7G2SGJjdPXvqH5" target="_blank">到空间页更新</a></div>\'+\n'
    '      \'<div class="sub">此固定网址为只读展示。上传 / 更新简历、看逐段优化，请点右上「到空间页更新」。</div>\'+\n'
    '      \'<div class="blk" style="margin-top:8px;white-space:pre-wrap;max-height:440px;overflow:auto;font-size:13px;line-height:1.6">\'+esc(txt)+\'</div></div>\';\n'
    '  }\n'
    '  return \'<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">\'+',
)

# ---------- 3) 只读环境下 viewResume 也展示简历快照 ----------
rep(
    "      + '</div>';\n  }\n  var uploadBtn",
    "      + '</div>'\n      + fullResumeCard();\n  }\n  var uploadBtn",
)

# ---------- 4) 只读环境：不隐藏导航、默认停在简历优化 ----------
rep(
    '    var tabs = document.getElementById("tabs"); if(tabs) tabs.style.display = "none";\n'
    '    var mn = document.getElementById("main");\n'
    '    if(mn) mn.innerHTML = \'<div class="card"><h2>AI 教练 · 实时对话</h2><div class="sub">这条链接用于陪跑台 AI 实时对话。任务 / 打卡 / 知识库请在 <a href="https://www.workbuddy.cn/space/d/3DxcmFIl7G2SGJjdPXvqH5" target="_blank">陪跑台空间页</a> 使用。点右下角「AI 教练」开始对话。</div></div>\';\n',
    '    S.tab = "resume";   /* 固定网址默认直接展示简历，省得找不到入口 */\n'
    '    var _m = document.getElementById("main");\n'
    '    if(_m) _m.innerHTML = \'<div class="card"><h2>AI 教练 · 实时对话</h2><div class="sub">这条固定网址为只读展示；实时写入请在 <a href="https://www.workbuddy.cn/space/d/3DxcmFIl7G2SGJjdPXvqH5" target="_blank">陪跑台空间页</a> 操作。点右下角「AI 教练」开始对话。</div></div>\';\n',
)

# ---------- 5) 只读横幅文案微调 ----------
rep(
    "b.innerHTML = '当前页面<b>未连接资料库</b>，任务 / 打卡 / 知识库为空、也不能写入；这些功能请在",
    "b.innerHTML = '固定网址为<b>只读展示</b>（已内置你的简历优化版全文，点「简历优化」可看）；任务 / 打卡 / 上传请在",
)

# ---------- 备份并写出 ----------
os.makedirs(os.path.join(BASE, "archive"), exist_ok=True)
shutil.copy2(OUT, os.path.join(BASE, "archive", "index_local_backup_20260919.html"))
open(OUT, "w", encoding="utf-8").write(src)
print("written index.html chars=%d  resumeStatic=%d  bytes=%d" % (
    len(src), src.count('id="resumeStatic"'), len(src.encode("utf-8"))))
