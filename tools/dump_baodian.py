import subprocess, json, os
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
TOKEN = os.environ["COACH_TOKEN"]
TID = "X6y2H6GmJA20l2lhT5x8he"
def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8")
    out=(p.stdout or "").strip()
    if not out:
        raise RuntimeError(script+" 无输出:"+(p.stderr or "")[:200])
    return json.loads(out)
rows=[]; cur=None
for _ in range(60):
    a=["--database-id",TID,"--page-size","200"]+(["--start-cursor",cur] if cur else [])
    r=run("query_database_record.py",*a)
    rows+=r.get("results",[])
    if not r.get("has_more") or not r.get("next_cursor") or r["next_cursor"]==cur: break
    cur=r["next_cursor"]
out=[]
for rec in rows:
    out.append(json.dumps({
        "章节":rec.get("章节",""),"小节":rec.get("小节",""),
        "对应能力域":rec.get("对应能力域",""),"来源":rec.get("来源",""),
        "内容":rec.get("内容",""),"record_id":rec.get("record_id","")
    }, ensure_ascii=False))
open(r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10\data\baodian_full.jsonl","w",encoding="utf-8").write("\n".join(out))
print(" dumped", len(out), "records to data/baodian_full.jsonl")
