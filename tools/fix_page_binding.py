# -*- coding: utf-8 -*-
"""把陪跑台空间页缺失的数据表绑定补上（页面查不到数据 = 表没绑到页面）。
   用法：python tools/fix_page_binding.py <op_token>
"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Users\24186\.workbuddy\plugins\cache\workbuddy-builtin\skill-library\5.5.6-wb.38337834.g5f969292.h4918b5ced607"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
PAGE = "3DxcmFIl7G2SGJjdPXvqH5"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))

# 页面代码实际会查询的表（DB 对象里的 13 张）
WANT = [
    ("能力项", IDS["陪跑台·能力项"]),
    ("知识卡", IDS["陪跑台·知识卡"]),
    ("打卡", IDS["陪跑台·打卡"]),
    ("能力证据", IDS["陪跑台·能力证据"]),
    ("学习记录", IDS["陪跑台·学习记录"]),
    ("问答", IDS["陪跑台·问答"]),
    ("等级日志", IDS["陪跑台·等级日志"]),
    ("素材库", IDS["陪跑台·素材库"]),
    ("面试题库", IDS["陪跑台·面试题库"]),
    ("任务反馈", IDS["陪跑台·任务反馈"]),
    ("简历优化", IDS["陪跑台·简历优化"]),
    ("岗位JD", IDS["陪跑台·岗位JD"]),
    ("原始简历", IDS["陪跑台·原始简历"]),
    ("辅线知识库", IDS["陪跑台·辅线知识库"]),
]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, "page", script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=180)
    return json.loads((p.stdout or "{}").strip() or "{}")


def current():
    r = run("page_database_relation.py", "--action", "list", "--page-id", PAGE)
    rel = (((r.get("data") or {}).get("relations")) or [])
    return {x["databaseId"] for x in rel}


have = current()
print("绑定前：%d 张 -> %s" % (len(have), sorted(have)))

added, skipped = [], []
for name, tid in WANT:
    if tid in have:
        skipped.append(name)
        continue
    r = run("page_database_relation.py", "--action", "link", "--page-id", PAGE, "--database-id", tid)
    ok = r.get("code") == 0
    print("  link %-6s %s -> %s" % (name, tid, "OK" if ok else "FAIL " + str(r)[:160]))
    (added if ok else skipped).append(name)

have2 = current()
print("绑定后：%d 张；本次新增=%s；仍缺=%s" % (
    len(have2), added, [n for n, t in WANT if t not in have2]))
