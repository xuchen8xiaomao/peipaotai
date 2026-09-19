# -*- coding: utf-8 -*-
"""把 data/简历优化版.md 的简历正文作为「优化版全文」记录写入「陪跑台·简历优化」表。
   若已存在则跳过，避免重复。用法：python tools/insert_resume_full.py <op_token>
"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))
RESUME = IDS["陪跑台·简历优化"]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=240)
    out = (p.stdout or "").strip()
    if not out:
        raise RuntimeError("%s 无输出：%s" % (script, (p.stderr or "")[:600]))
    return json.loads(out)


# 提取简历正文（从「## 个人简介」起）
md = open(os.path.join(ROOT, "data", "简历优化版.md"), encoding="utf-8").read()
start = md.index("## 个人简介")
body = md[start:].strip()

# 查现有内容，避免重复插入
csv_out = run("get_database_content.py", "--database-id", RESUME)
csv_text = csv_out.get("content", "") or ""
if "优化版全文" in csv_text:
    print("已存在「优化版全文」记录，跳过插入。如需刷新请先删除旧记录。")
else:
    record = {
        "区块": {"text": "📄 我的简历（优化版全文）"},
        "优化后": {"text": body},
        "状态": {"text": "已优化·可更新"},
    }
    r = run("batch_add_database_records.py", "--database-id", RESUME,
            "--records", json.dumps([record], ensure_ascii=False))
    ok = sum(1 for x in r.get("results", []) if x.get("success"))
    print("简历全文 INSERT ok=%d 结果=%s" % (ok, str(r)[:300]))

print("DONE body_chars=%d" % len(body))
