# -*- coding: utf-8 -*-
"""0920 step0: 读任务反馈 + 素材库 + 最近卡片"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import coach

out = {}
fb = coach.load_all("4moVqTqT7JRxYIkKEmvS7b")
out["反馈_全量"] = [{k: v for k, v in r.items() if k in
                 ("record_id", "日期", "评分", "反馈内容", "状态", "关联卡片", "能力域")} for r in fb]

mat = coach.load_all("rLcH92l8foVxGRWizDbTJA")
out["素材库"] = [{k: v for k, v in r.items() if k in
                ("record_id", "标题", "类型", "来源", "摘要", "关联能力域", "入库日期", "状态")} for r in mat]

cards = coach.load_all(coach.IDS["陪跑台·知识卡"])
cards.sort(key=lambda r: str(r.get("日期") or ""))
out["最近卡片"] = [{"日期": str(r.get("日期"))[:10], "Day": r.get("Day"),
                 "能力域": r.get("能力域"), "标题": r.get("标题")} for r in cards[-8:]]
out["Day最大"] = max([r.get("Day") or 0 for r in cards] or [0])

qa = [r for r in coach.load_all(coach.IDS["陪跑台·问答"]) if (r.get("状态") or "待回答") == "待回答"]
out["待回答"] = [{"日期": str(r.get("日期"))[:10], "提问": r.get("我的提问"),
                "能力项ID": r.get("能力项ID")} for r in qa[-10:]]

json.dump(out, open(os.path.join(coach.ROOT, "data", "_step0.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("反馈条数", len(out["反馈_全量"]), "素材条数", len(out["素材库"]))
for f in out["反馈_全量"]:
    print("  FB:", f)
print("Day最大", out["Day最大"])
for c in out["最近卡片"]:
    print("  CARD:", c["日期"], "Day", c["Day"], c["能力域"], c["标题"])
print("待回答:", len(out["待回答"]))
for q in out["待回答"]:
    print("  Q:", q["日期"], str(q["提问"])[:100])
print("=== 素材库标题 ===")
for m in out["素材库"]:
    print("  -", m.get("标题"), "|", m.get("类型"), "|", str(m.get("关联能力域"))[:40])
