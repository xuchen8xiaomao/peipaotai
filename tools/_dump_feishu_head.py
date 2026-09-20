# -*- coding: utf-8 -*-
"""一次性：导出各飞书表的表头与样例行，用于设计字段映射。"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))

WANT = ["陪跑台·岗位JD", "陪跑台·知识卡", "陪跑台·能力项", "陪跑台·学习记录", "陪跑台·打卡",
        "陪跑台·素材库", "陪跑台·问答", "陪跑台·等级日志", "陪跑台·面试题库", "陪跑台·辅线知识库",
        "陪跑台·简历优化", "陪跑台·原始简历", "陪跑台·能力证据", "陪跑台·周报", "陪跑台·任务反馈"]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=240)
    out = (p.stdout or "").strip()
    try:
        return json.loads(out)
    except Exception:
        return {"__error__": ((p.stderr or "") + "|" + out)[:300]}


lines_out = []
for name in WANT:
    tid = IDS.get(name)
    if not tid:
        lines_out.append("=== %s : NO_ID" % name)
        continue
    r = run("get_database_content.py", "--database-id", tid)
    if "__error__" in r:
        lines_out.append("=== %s : ERROR %s" % (name, r["__error__"]))
        continue
    csv = r.get("content", "") or r.get("csv", "") or ""
    rows = [l for l in csv.splitlines() if l.strip()]
    lines_out.append("=== %s | data_rows=%d" % (name, max(0, len(rows) - 1)))
    if rows:
        lines_out.append("    HEAD: " + rows[0][:500])
    if len(rows) > 1:
        lines_out.append("    R1  : " + rows[1][:300])
        if len(rows) > 2:
            lines_out.append("    R2  : " + rows[2][:300])
    lines_out.append("")

open(os.path.join(ROOT, "tools", "_feishu_head.txt"), "w", encoding="utf-8").write("\n".join(lines_out))
print("WROTE", len(lines_out), "lines")
