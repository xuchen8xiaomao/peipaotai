# -*- coding: utf-8 -*-
"""陪跑台命令行工具。每日自动化用，避免每次重新拼脚本参数。

  python tools/coach.py gaps            按 缺口×权重 列出最该补的能力项
  python tools/coach.py check           今天有没有打卡
  python tools/coach.py week            最近 7 天的打卡与证据概况
  python tools/coach.py addcard --file card.json    写入一张知识卡
  python tools/coach.py evidence 能力项ID "证据内容" [强|中|弱]

首次运行需要资料库 token：由自动化调用方通过环境变量 COACH_TOKEN 传入。
本脚本只做读写，不打印 token。
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library"
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))
TOKEN = os.environ.get("COACH_TOKEN", "")


def run(script, *args):
    p = subprocess.run([PY, os.path.join(SKILL, "database", script), "--token-stdin"] + list(args),
                       input=TOKEN, capture_output=True, text=True, encoding="utf-8")
    out = (p.stdout or "").strip()
    if not out:
        raise RuntimeError("%s 无输出：%s" % (script, (p.stderr or "")[:200]))
    return json.loads(out)


def load_all(dbid):
    rows, cur = [], None
    for _ in range(50):
        a = ["--database-id", dbid, "--page-size", "200"] + (["--start-cursor", cur] if cur else [])
        r = run("query_database_record.py", *a)
        rows += r.get("results", [])
        if not r.get("has_more") or not r.get("next_cursor") or r["next_cursor"] == cur:
            break
        cur = r["next_cursor"]
    return rows


def n(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def day(v):
    return str(v or "")[:10]


def cmd_gaps(a):
    caps = load_all(IDS["陪跑台·能力项"])
    rows = [{"id": c.get("能力项ID"), "域": c.get("能力域"), "项": c.get("能力项"),
             "当前": n(c.get("当前等级")), "目标": n(c.get("目标等级")),
             "权重": n(c.get("权重")), "判定": c.get("判定依据"),
             "缺口": n(c.get("目标等级")) - n(c.get("当前等级")),
             "分": (n(c.get("目标等级")) - n(c.get("当前等级"))) * n(c.get("权重"))}
            for c in caps]
    rows = [r for r in rows if r["缺口"] > 0]
    rows.sort(key=lambda r: -r["分"])
    print(json.dumps(rows[:a.limit], ensure_ascii=False, indent=2))


def cmd_check(a):
    d = a.date or __import__("datetime").date.today().isoformat()
    ck = [c for c in load_all(IDS["陪跑台·打卡"]) if day(c.get("日期")) == d]
    if not ck:
        print("NO_CHECKIN")
        return
    c = ck[0]
    done = [k for k in ("概念卡", "对标补给", "案例拆写", "对话盘点") if c.get(k)]
    print(json.dumps({"日期": d, "已完成段": done, "段数": len(done),
                      "回答": [c.get("回答1"), c.get("回答2"), c.get("回答3")]},
                     ensure_ascii=False, indent=2))


def cmd_week(a):
    import datetime
    today = datetime.date.today()
    lo = (today - datetime.timedelta(days=6)).isoformat()
    ck = [c for c in load_all(IDS["陪跑台·打卡"]) if day(c.get("日期")) >= lo]
    ev = [e for e in load_all(IDS["陪跑台·能力证据"]) if day(e.get("日期")) >= lo]
    days = [c for c in ck if any(c.get(k) for k in ("概念卡", "对标补给", "案例拆写", "对话盘点"))]
    print(json.dumps({"区间": lo + " ~ " + today.isoformat(), "打卡天数": len(days),
                      "打卡记录": len(ck), "新增证据": len(ev),
                      "证据": [{"项": e.get("能力项ID"), "内容": e.get("证据内容"), "强度": e.get("强度")} for e in ev]},
                     ensure_ascii=False, indent=2))


def cmd_addcard(a):
    card = json.load(open(a.file, encoding="utf-8"))
    rec = {
        "日期": {"date": card["日期"]}, "Day": {"number": card.get("Day", 0)},
        "能力域": {"text": card.get("能力域", "")}, "标题": {"text": card.get("标题", "")},
        "核心概念": {"text": card.get("核心概念", "")}, "对标产品": {"text": card.get("对标产品", "")},
        "落到你的项目": {"text": card.get("落到你的项目", "")}, "微练习": {"text": card.get("微练习", "")},
        "延伸阅读": {"text": card.get("延伸阅读", "")},
        "深度资料": {"text": card.get("深度资料", "")},
        "概念卡分钟": {"number": card.get("概念卡分钟", 13)},
        "对标分钟": {"number": card.get("对标分钟", 14)},
        "拆写分钟": {"number": card.get("拆写分钟", 23)},
        "盘点分钟": {"number": card.get("盘点分钟", 10)},
        "问题1": {"text": (card.get("问题") or ["", "", ""])[0]},
        "问题2": {"text": (card.get("问题") or ["", "", ""])[1]},
        "问题3": {"text": (card.get("问题") or ["", "", ""])[2]},
        "状态": {"select": "未读"},
    }
    r = run("batch_add_database_records.py", "--database-id", IDS["陪跑台·知识卡"],
            "--records", json.dumps([rec], ensure_ascii=True))
    print(json.dumps(r, ensure_ascii=False))


TEXT_FIELDS = ["标题", "能力域", "核心概念", "对标产品", "落到你的项目", "微练习",
               "问题1", "问题2", "问题3", "延伸阅读"]
NUM_FIELDS = ["Day", "概念卡分钟", "对标分钟", "拆写分钟", "盘点分钟"]


def cmd_updatecard(a):
    """按日期更新已有知识卡的字段（只更新 JSON 里给出的字段）。"""
    card = json.load(open(a.file, encoding="utf-8"))
    date = day(card.get("日期") or a.date)
    rows = [r for r in load_all(IDS["陪跑台·知识卡"]) if day(r.get("日期")) == date]
    if not rows:
        print(json.dumps({"error": "未找到该日期的卡片", "日期": date}, ensure_ascii=False))
        return
    rec = rows[0]
    rid = rec.get("record_id") or rec.get("_id") or rec.get("id")
    if not rid:
        print(json.dumps({"error": "记录缺少 id", "keys": list(rec.keys())[:12]}, ensure_ascii=False))
        return
    props = {}
    for f in TEXT_FIELDS:
        if f in card:
            props[f] = {"text": card[f]}
    for f in NUM_FIELDS:
        if f in card:
            props[f] = {"number": card[f]}
    if not props:
        print(json.dumps({"error": "没有可更新字段", "可用字段": TEXT_FIELDS + NUM_FIELDS},
                         ensure_ascii=False))
        return
    r = run("batch_update_database_records.py", "--database-id", IDS["陪跑台·知识卡"],
            "--records", json.dumps([{"record_id": rid, "properties": props}], ensure_ascii=True))
    print(json.dumps({"ok": True, "日期": date, "更新字段": list(props.keys()), "结果": r},
                     ensure_ascii=False, indent=2))


def _add(dbid, rec):
    return run("batch_add_database_records.py", "--database-id", dbid,
               "--records", json.dumps([rec], ensure_ascii=True))


def _upd(dbid, rid, props):
    return run("batch_update_database_records.py", "--database-id", dbid,
               "--records", json.dumps([{"record_id": rid, "properties": props}], ensure_ascii=True))


def _find(dbid, pred):
    return [r for r in load_all(dbid) if pred(r)]


def cmd_asks(a):
    """列出待回答的提问。"""
    rows = _find(IDS["陪跑台·问答"], lambda r: (r.get("状态") or "待回答") == "待回答")
    out = [{"id": r.get("record_id"), "日期": day(r.get("日期")), "任务段": r.get("任务段"),
            "能力项ID": r.get("能力项ID"), "上下文": r.get("上下文"), "提问": r.get("我的提问")}
           for r in rows]
    print(json.dumps({"待回答": len(out), "列表": out}, ensure_ascii=False, indent=2))


def cmd_answer(a):
    """回答一条提问：--id 记录id --text 回答内容"""
    print(json.dumps(_upd(IDS["陪跑台·问答"], a.id, {"AI回答": {"text": a.text}, "状态": {"select": "已回答"}}),
                     ensure_ascii=False))


def cmd_logs(a):
    """列出待总结的学习记录。"""
    rows = [r for r in load_all(IDS["陪跑台·学习记录"]) if (r.get("状态") or "待总结") == "待总结"]
    rows.sort(key=lambda r: day(r.get("日期")))
    out = [{"id": r.get("record_id"), "日期": day(r.get("日期")), "任务段": r.get("任务段"),
            "任务标题": r.get("任务标题"), "能力项ID": r.get("能力项ID"),
            "建议分钟": n(r.get("建议分钟")), "专注分钟": n(r.get("专注分钟")),
            "达标": r.get("达标"), "我的产出": r.get("我的产出"), "我的疑问": r.get("我的疑问")}
           for r in rows]
    print(json.dumps({"待总结": len(out), "列表": out}, ensure_ascii=False, indent=2))


def cmd_summarize(a):
    """给一条学习记录写 AI 总结：--id 记录id --text 总结内容"""
    print(json.dumps(_upd(IDS["陪跑台·学习记录"], a.id,
                          {"AI总结": {"text": a.text}, "状态": {"select": "已总结"}}), ensure_ascii=False))


def cmd_addlog(a):
    """补写一条学习记录（--file JSON）。页面通常直接写库，此命令供 Agent 补录。"""
    d = json.load(open(a.file, encoding="utf-8"))
    rec = {"日期": {"date": d.get("日期")}, "Day": {"number": d.get("Day", 0)},
           "能力项ID": {"text": d.get("能力项ID", "")}, "能力域": {"text": d.get("能力域", "")},
           "任务段": {"select": d.get("任务段", "")}, "任务标题": {"text": d.get("任务标题", "")},
           "建议分钟": {"number": d.get("建议分钟", 0)}, "专注分钟": {"number": d.get("专注分钟", 0)},
           "达标": {"checkbox": bool(d.get("达标"))}, "我的产出": {"text": d.get("我的产出", "")},
           "我的疑问": {"text": d.get("我的疑问", "")}, "AI总结": {"text": d.get("AI总结", "")},
           "状态": {"select": d.get("状态", "待总结")}}
    print(json.dumps(_add(IDS["陪跑台·学习记录"], rec), ensure_ascii=False))


def cmd_level(a):
    """记一条等级变化日志：level 能力项ID 新等级 --old 旧等级 --why 触发原因"""
    name = ""
    for c in load_all(IDS["陪跑台·能力项"]):
        if c.get("能力项ID") == a.item:
            name = c.get("能力项", "")
    import datetime
    rec = {"日期": {"date": a.date or datetime.date.today().isoformat()},
           "能力项ID": {"text": a.item}, "能力项": {"text": name},
           "旧等级": {"number": a.old}, "新等级": {"number": a.new},
           "触发": {"text": a.why or ""}}
    print(json.dumps(_add(IDS["陪跑台·等级日志"], rec), ensure_ascii=False))


def cmd_stats(a):
    """量化档案：专注时长、完成任务、覆盖能力项、等级变化。"""
    import datetime
    today = datetime.date.today()
    lo = (today - datetime.timedelta(days=a.days - 1)).isoformat()
    logs = [r for r in load_all(IDS["陪跑台·学习记录"]) if day(r.get("日期")) >= lo]
    evs = [r for r in load_all(IDS["陪跑台·能力证据"]) if day(r.get("日期")) >= lo]
    lv = [r for r in load_all(IDS["陪跑台·等级日志"]) if day(r.get("日期")) >= lo]
    by_day = {}
    for r in logs:
        by_day[day(r.get("日期"))] = by_day.get(day(r.get("日期")), 0) + n(r.get("专注分钟"))
    by_seg = {}
    for r in logs:
        k = r.get("任务段") or "其他"
        by_seg[k] = round(by_seg.get(k, 0) + n(r.get("专注分钟")), 1)
    ids = sorted({r.get("能力项ID") for r in logs if r.get("能力项ID")})
    print(json.dumps({
        "区间": lo + " ~ " + today.isoformat(),
        "累计专注分钟": round(sum(n(r.get("专注分钟")) for r in logs), 1),
        "完成任务数": len(logs),
        "达标数": len([r for r in logs if r.get("达标")]),
        "待总结": len([r for r in logs if (r.get("状态") or "待总结") == "待总结"]),
        "覆盖能力项": len(ids), "能力项列表": ids,
        "新增证据": len(evs), "等级变化次数": len(lv),
        "等级变化": [{"项": r.get("能力项ID"), "旧": n(r.get("旧等级")), "新": n(r.get("新等级")),
                      "日期": day(r.get("日期")), "触发": r.get("触发")} for r in lv],
        "每日专注分钟": by_day, "分任务段分钟": by_seg,
    }, ensure_ascii=False, indent=2))


def cmd_evidence(a):
    caps = load_all(IDS["陪跑台·能力项"])
    name = ""
    for c in caps:
        if c.get("能力项ID") == a.item:
            name = c.get("能力项", "")
    import datetime
    rec = {"日期": {"date": a.date or datetime.date.today().isoformat()},
           "能力项ID": {"text": a.item}, "能力项": {"text": name},
           "证据内容": {"text": a.content}, "来源": {"select": a.source}, "强度": {"select": a.strength}}
    r = run("batch_add_database_records.py", "--database-id", IDS["陪跑台·能力证据"],
            "--records", json.dumps([rec], ensure_ascii=True))
    print(json.dumps(r, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("gaps"); p.add_argument("--limit", type=int, default=6); p.set_defaults(f=cmd_gaps)
    p = sub.add_parser("check"); p.add_argument("--date", default=""); p.set_defaults(f=cmd_check)
    p = sub.add_parser("week"); p.set_defaults(f=cmd_week)
    p = sub.add_parser("addcard"); p.add_argument("--file", required=True); p.set_defaults(f=cmd_addcard)
    p = sub.add_parser("updatecard"); p.add_argument("--file", required=True)
    p.add_argument("--date", default=""); p.set_defaults(f=cmd_updatecard)
    p = sub.add_parser("asks"); p.set_defaults(f=cmd_asks)
    p = sub.add_parser("answer"); p.add_argument("--id", required=True)
    p.add_argument("--text", required=True); p.set_defaults(f=cmd_answer)
    p = sub.add_parser("logs"); p.set_defaults(f=cmd_logs)
    p = sub.add_parser("summarize"); p.add_argument("--id", required=True)
    p.add_argument("--text", required=True); p.set_defaults(f=cmd_summarize)
    p = sub.add_parser("addlog"); p.add_argument("--file", required=True); p.set_defaults(f=cmd_addlog)
    p = sub.add_parser("level"); p.add_argument("item"); p.add_argument("new", type=float)
    p.add_argument("--old", type=float, default=0.0); p.add_argument("--why", default="")
    p.add_argument("--date", default=""); p.set_defaults(f=cmd_level)
    p = sub.add_parser("stats"); p.add_argument("--days", type=int, default=30); p.set_defaults(f=cmd_stats)
    p = sub.add_parser("evidence"); p.add_argument("item"); p.add_argument("content")
    p.add_argument("--strength", default="中"); p.add_argument("--source", default="对话盘点")
    p.add_argument("--date", default=""); p.set_defaults(f=cmd_evidence)
    a = ap.parse_args()
    if not a.cmd:
        ap.print_help(); sys.exit(1)
    if not TOKEN:
        print("缺少 COACH_TOKEN 环境变量"); sys.exit(2)
    a.f(a)


if __name__ == "__main__":
    main()
