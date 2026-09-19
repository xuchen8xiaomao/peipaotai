# -*- coding: utf-8 -*-
"""只读诊断：读 陪跑台·知识卡 全量记录，按 日期 找当天/最近3天卡片，
判定「深度资料(≥1000字+四节齐全)」与「问题三问(含【答法要点】)」是否达标。
绝不写库、绝不覆盖。调用方通过 COACH_TOKEN 环境变量传入 token。
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library"
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))
TOKEN = os.environ.get("COACH_TOKEN", "")
DBID = IDS["陪跑台·知识卡"]

SECTIONS = ["【一、知识本身】", "【二、在工作里怎么用】", "【三、面试会怎么考】", "【四、生动案例】"]


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, "database", script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8")
    out = (p.stdout or "").strip()
    if not out:
        raise RuntimeError("%s 无输出：%s" % (script, (p.stderr or "")[:300]))
    return json.loads(out)


def load_all():
    rows, cur = [], None
    for _ in range(50):
        a = ["--database-id", DBID, "--page-size", "200"] + (["--start-cursor", cur] if cur else [])
        r = run("query_database_record.py", *a)
        rows += r.get("results", [])
        if not r.get("has_more") or not r.get("next_cursor") or r["next_cursor"] == cur:
            break
        cur = r["next_cursor"]
    return rows


def text_of(v):
    """多维表字段可能是 {"text": "..."} 或 {"type":..., "text":...} 等，做兼容提取。"""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        if "text" in v:
            return str(v["text"])
        # 有的结构把值放在内部
        for k in ("value", "content"):
            if k in v:
                return text_of(v[k])
        return ""
    if isinstance(v, list):
        return "\n".join(text_of(x) for x in v)
    return str(v)


def get_questions(rec):
    """兼容：问题 可能是 字段 问题1/问题2/问题3，或 问题(数组)。返回 3 元组文本列表。"""
    # 优先 问题1/问题2/问题3
    q1, q2, q3 = rec.get("问题1"), rec.get("问题2"), rec.get("问题3")
    if q1 is not None or q2 is not None or q3 is not None:
        return [text_of(q1), text_of(q2), text_of(q3)]
    q = rec.get("问题")
    if isinstance(q, list):
        return [text_of(x) for x in q[:3]] + [""] * max(0, 3 - len(q))
    if q is not None:
        return [text_of(q), "", ""]
    return ["", "", ""]


def judge(rec):
    dd = text_of(rec.get("深度资料"))
    dd_len = len(dd)
    miss_sec = [s for s in SECTIONS if s not in dd]
    dd_ok = dd_len >= 1000 and not miss_sec
    qs = get_questions(rec)
    q_status = []
    for q in qs:
        has = ("【答法要点】" in q) and len(q.strip()) > 0
        q_status.append(has)
    q_ok = all(q_status) and any(q.strip() for q in qs)
    return dd_len, miss_sec, dd_ok, qs, q_status, q_ok


def main():
    today = sys.argv[1] if len(sys.argv) > 1 else "2026-09-18"
    rows = load_all()
    # 找当天
    cand = [r for r in rows if str(r.get("日期", ""))[:10] == today]
    scope_note = "当天 %s" % today
    if not cand:
        # 最近3天
        from datetime import datetime, timedelta
        t = datetime.strptime(today, "%Y-%m-%d")
        days = [(t - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 4)]
        cand = [r for r in rows if str(r.get("日期", ""))[:10] in days]
        scope_note = "最近3天 %s" % days
    print("范围：%s | 命中卡片数：%d | 库总记录：%d" % (scope_note, len(cand), len(rows)))
    need = []
    for r in cand:
        rid = r.get("record_id") or r.get("_id")
        title = text_of(r.get("标题"))
        dd_len, miss_sec, dd_ok, qs, q_status, q_ok = judge(r)
        flag = "需补" if (not dd_ok or not q_ok) else "达标"
        print("-" * 60)
        print("RID=%s | %s" % (rid, str(r.get("日期", ""))[:10]))
        print("标题：%s" % title[:40])
        print("深度资料：%d字 %s | 缺节：%s" % (dd_len, "OK" if dd_ok else "缺", "/".join(miss_sec) or "无"))
        print("问题：%s | 含答法要点：%s" % ("OK" if q_ok else "需补", ["Y" if x else "N" for x in q_status]))
        if not dd_ok or not q_ok:
            need.append((rid, r, dd_ok, q_ok, dd_len, miss_sec, qs, q_status))
    print("=" * 60)
    print("需补卡片数：%d" % len(need))
    return need


if __name__ == "__main__":
    main()
