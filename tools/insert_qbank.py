# -*- coding: utf-8 -*-
"""把 data/qbank/*.json 批量写入「陪跑台·面试题库」表"""
import os, json, subprocess, glob

TOKEN = os.environ["COACH_TOKEN"]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL_DB = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))
DBID = IDS["陪跑台·面试题库"]


def lib(script, *args):
    cmd = [PY, os.path.join(SKILL_DB, script), "--token-stdin"] + list(args)
    r = subprocess.run(cmd, input=TOKEN, capture_output=True, text=True,
                       encoding="utf-8", timeout=180)
    out = (r.stdout or "").strip()
    if not out:
        raise RuntimeError("%s 无输出: %s" % (script, (r.stderr or "")[:500]))
    return json.loads(out)


records = []
for fp in sorted(glob.glob(os.path.join(ROOT, "data", "qbank", "*.json"))):
    data = json.load(open(fp, encoding="utf-8"))
    print("load", os.path.basename(fp), len(data))
    for r in data:
        rec = {}
        for k, v in r.items():
            if k in ("类别", "优先级", "状态"):
                rec[k] = {"select": v}
            else:
                rec[k] = {"text": v}
        records.append(rec)

# 顺序按题号排
records.sort(key=lambda x: x["题号"]["text"])
print("TOTAL", len(records))

ok = fail = 0
batch, blen = [], 0


def send(b):
    global ok, fail
    try:
        res = lib("batch_add_database_records.py", "--database-id", DBID,
                  "--records", json.dumps(b, ensure_ascii=False))
        s = sum(1 for x in res.get("results", []) if x.get("success"))
        ok += s
        fail += len(b) - s
        if len(b) - s:
            print("  partial fail:", [x.get("error") for x in res.get("results", []) if not x.get("success")][:2])
    except Exception as e:
        fail += len(b)
        print("BATCH ERR", str(e)[:300])


for rec in records:
    s = len(json.dumps(rec, ensure_ascii=False))
    if batch and blen + s + 50 > 24000:
        send(batch)
        batch, blen = [], 0
    batch.append(rec)
    blen += s
if batch:
    send(batch)

print("INSERTED ok=%d fail=%d" % (ok, fail))
