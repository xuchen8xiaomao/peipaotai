import io, sys

ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
svg_path = ROOT + r"\architecture_diagram.svg"
html_path = ROOT + r"\index.html"

with io.open(svg_path, encoding="utf-8") as f:
    raw = f.read()

# 转义为 JS 双引号字符串：先反斜杠，再双引号，再换行
esc = raw.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "\\n")
new_str = '"' + esc + '"'

with io.open(html_path, encoding="utf-8") as f:
    html = f.read()

start = html.find('"<svg')
end = html.find('</svg>"')
if start == -1 or end == -1:
    print("ANCHOR_NOT_FOUND start=%d end=%d" % (start, end))
    sys.exit(1)
end += len('</svg>"')
html2 = html[:start] + new_str + html[end:]

with io.open(html_path, "w", encoding="utf-8") as f:
    f.write(html2)

print("OK replaced %d chars -> %d chars" % (end - start, len(new_str)))
