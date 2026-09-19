# -*- coding: utf-8 -*-
"""诊断：查「简历优化 / 岗位JD / 原始简历 / 知识卡」四张表在飞书侧的真实记录数与字段。
   用法：python tools/_check_tables.py <op_token>
"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))

TARGETS = [
    ("陪跑台·简历优化", IDS["陪跑台·简历优化"], "X9WGdVETyOPGE4KDMAghP3"),
    ("陪跑台·岗位JD", IDS["陪跑台·岗位JD"], "48W3D38yJk7RKzo5V9pRL3"),
    ("陪跑台·原始简历", IDS["陪跑台·原始简历"], "X8FBew1mW66tVKy3Qj6FJu"),
    ("陪跑台·知识卡", IDS["陪跑台·知识卡"], "4zH7GK3VNQaBr9XHCE5sZH"),
]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=240)
    out = (p.stdout or "").strip()
    if not out:
        return {"__error__": (p.stderr or "")[:800]}
    try:
        return json.loads(out)
    except Exception as e:
        return {"__error__": "json解析失败: %s | raw=%s" % (e, out[:500])}


for name, tid, expect in TARGETS:
    print("=" * 60)
    print("%s  配置ID=%s  (期望=%s)  一致=%s" % (name, tid, expect, tid == expect))
    r = run("get_database_content.py", "--database-id", tid)
    if "__error__" in r:
        print("  ERROR:", r["__error__"][:400])
        continue
    csv = r.get("content", "") or r.get("csv", "") or ""
    lines = [l for l in csv.splitlines() if l.strip()]
    print("  CSV行数(含表头)=%d" % len(lines))
    for l in lines[:3]:
        print("   >", l[:300])
print("=" * 60)
