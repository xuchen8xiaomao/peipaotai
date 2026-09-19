# -*- coding: utf-8 -*-
"""创建「陪跑台·简历优化」表，返回 database_id。用法：python tools/create_resume_db.py <op_token>"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"

schema = json.load(open(os.path.join(ROOT, "data", "schema_resume.json"), encoding="utf-8"))
p = subprocess.run(
    [PY, os.path.join(SKILL, "create_database.py"), "--token-stdin", "--schema", json.dumps(schema, ensure_ascii=False)],
    input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=60)
out = (p.stdout or "").strip()
print("STDOUT:", out)
if p.stderr.strip():
    print("STDERR:", p.stderr.strip()[:600])
