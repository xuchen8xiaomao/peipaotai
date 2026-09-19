import sys
sys.path.insert(0, r'C:/Users/24186/.workbuddy/binaries/python/pkgs')
from pypdf import PdfReader

src = r'D:/R/简历2026.pdf'
out = r'C:/Users/24186/WorkBuddy/2026-09-10-20-13-10/data/resume_raw.txt'

r = PdfReader(src)
parts = []
for i, p in enumerate(r.pages):
    parts.append('\n\n=== PAGE %d ===\n' % i)
    parts.append(p.extract_text() or '')
txt = ''.join(parts)
open(out, 'w', encoding='utf-8').write(txt)
print('pages', len(r.pages))
print('chars', len(txt))
