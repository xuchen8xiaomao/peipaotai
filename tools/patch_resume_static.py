# -*- coding: utf-8 -*-
"""把「简历优化版」全文静态固化进 index.html，让只读(Site)模式也能展示简历。
- 清理 markdown 为纯文本，转义后放进隐藏 <div id="resumeStatic">。
- fullResumeCard 在 LIVE=false 且无飞书记录时，改用静态 div 展示只读快照。
- rawForm 在 LIVE=false 时显示「只读，上传请到空间页」提示。
"""
import re, html

BASE = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
MD  = BASE + r"\data\简历优化版.md"
HTML= BASE + r"\index.html"

md = open(MD, encoding="utf-8").read()
lines = md.split("\n")
out = []
for ln in lines:
    s = ln
    s = re.sub(r"^#+\s*", "", s)            # 标题
    s = re.sub(r"^>\s?", "", s)             # 引用
    s = re.sub(r"^\s*[-*]\s+", "• ", s)     # 列表
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)  # 加粗
    s = re.sub(r"^---+$", "", s)            # 分隔线
    out.append(s)
text = "\n".join(out).strip()
text = html.escape(text)

src = open(HTML, encoding="utf-8").read()

# 1) 注入/替换隐藏静态简历 div
div = '<div id="resumeStatic" hidden>\n' + text + "\n</div>"
if '<div id="resumeStatic"' in src:
    src = re.sub(r'<div id="resumeStatic"[^>]*>.*?</div>', div, src, flags=re.S)
else:
    src = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + div, src, count=1)
assert '<div id="resumeStatic"' in src, "静态简历 div 注入失败"

# 2) fullResumeCard 增加只读 fallback
old_fb = '  if(!rec) return \'\';\n  return \'<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">\'+'
new_fb = (
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
'  return \'<div class="card" style="border-color:var(--blue);box-shadow:0 1px 0 var(--blueL)">\'+'
)
assert old_fb in src, "未找到 fullResumeCard 插入点"
src = src.replace(old_fb, new_fb, 1)

# 3) rawForm 只读提示
old_sub = ('<div class="sub">支持 PDF / Word / TXT，或直接把简历文字粘到下面。提交后存进「原始简历」库，可随时让我（AI）按某份 JD 重新逐段优化。</div>\'+')
new_sub = ('<div class="sub">支持 PDF / Word / TXT，或直接把简历文字粘到下面。提交后存进「原始简历」库，可随时让我（AI）按某份 JD 重新逐段优化。</div>\'+\n'
'    (LIVE?\'<div style="margin-top:8px;padding:6px 9px;border:1px solid var(--line);border-radius:8px;background:#fff7e6;color:#8a6d3b;font-size:12px">⚠️ 此固定网址为只读预览，不能直接上传。上传 / 更新简历请打开资料库空间页（见右上「到空间页更新」）。</div>\':\'\')+')
assert old_sub in src, "未找到 rawForm sub 插入点"
src = src.replace(old_sub, new_sub, 1)

open(HTML, "w", encoding="utf-8").write(src)
print("OK: 静态简历已固化，fullResumeCard fallback + 只读提示已加。")
