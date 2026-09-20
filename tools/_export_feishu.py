# -*- coding: utf-8 -*-
"""从飞书表导出并映射为云端表结构的 JSON。用法: python tools/_export_feishu.py <op_token>"""
import json, os, subprocess, sys, csv, io

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "data", "_migrate")
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("陪跑台·知识卡", "knowledge_cards", [("标题","title"),("类型","type"),("能力域","domains"),("核心概念","concept"),("对标产品","benchmark"),("落到你的项目","project"),("微练习","exercise"),("深度资料","deep_dive"),("日期","card_date")]),
    ("陪跑台·能力项", "capabilities", [("能力项","name"),("能力域","domain"),("当前等级","level"),("缺口","progress")]),
    ("陪跑台·学习记录", "study_logs", [("日期","log_date"),("任务段","kind"),("专注分钟","minutes"),("任务标题","content")]),
    ("陪跑台·打卡", "checkins", [("日期","checkin_date"),("用时分钟","minutes")]),
    ("陪跑台·素材库", "materials", [("标题","title"),("类型","kind"),("原文","content"),("来源","source")]),
    ("陪跑台·问答", "qa_records", [("我的提问","question"),("AI回答","answer")]),
    ("陪跑台·面试题库", "interview_questions", [("题目","question"),("答题框架","answer"),("对应能力域","domains")]),
    ("陪跑台·简历优化", "resumes", [("区块","version"),("优化后","content"),("优化点","suggestion")]),
]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=300)
    out = (p.stdout or "").strip()
    try:
        return json.loads(out)
    except Exception:
        return {"__error__": ((p.stderr or "") + "|" + out)[:300]}


summary = []
for fs_name, table, mapping in JOBS:
    tid = IDS.get(fs_name)
    if not tid:
        summary.append("%s -> NO_ID" % fs_name)
        continue
    r = run("get_database_content.py", "--database-id", tid)
    if "__error__" in r:
        summary.append("%s -> ERROR %s" % (fs_name, r["__error__"]))
        continue
    csv_txt = r.get("content", "") or r.get("csv", "") or ""
    rd = list(csv.reader(io.StringIO(csv_txt)))
    if not rd:
        summary.append("%s -> EMPTY" % fs_name)
        continue
    head = rd[0]
    idx = {h: i for i, h in enumerate(head)}
    rows = []
    for raw in rd[1:]:
        if not any((c or "").strip() for c in raw):
            continue
        obj = {}
        ok = False
        for fc, tc in mapping:
            i = idx.get(fc)
            v = raw[i].strip() if (i is not None and i < len(raw)) else ""
            if tc == "minutes":
                try:
                    v = int(float(v)) if v else None
                except Exception:
                    v = None
            else:
                v = v if v != "" else None
            if v is not None:
                ok = True
            obj[tc] = v
        if ok:
            rows.append(obj)
    open(os.path.join(OUT, table + ".json"), "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False))
    summary.append("%s -> %s : %d rows" % (fs_name, table, len(rows)))

open(os.path.join(ROOT, "tools", "_export_summary.txt"), "w", encoding="utf-8").write("\n".join(summary))
print("\n".join(summary))
