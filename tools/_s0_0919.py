# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coach as C

IDS = C.IDS
print("=== FEEDBACK 4moVqTqT7JRxYIkKEmvS7b ===")
try:
    fb = C.load_all("4moVqTqT7JRxYIkKEmvS7b")
    print("count", len(fb))
    for r in fb:
        print(json.dumps({k: v for k, v in r.items() if k not in ("record_id",)}, ensure_ascii=False)[:500])
except Exception as e:
    print("ERR fb", e)

print("\n=== CARDS ===")
try:
    cards = C.load_all(IDS["陪跑台·知识卡"])
    print("count", len(cards))
    days = []
    for r in cards:
        days.append((C.day(r.get("日期")), C.n(r.get("Day")), str(r.get("能力域"))[:24], str(r.get("标题"))[:30]))
    days.sort()
    for d in days[-12:]:
        print(d)
except Exception as e:
    print("ERR cards", e)

print("\n=== 素材库 rLcH92l8foVxGRWizDbTJA ===")
try:
    mt = C.load_all("rLcH92l8foVxGRWizDbTJA")
    print("count", len(mt))
    for r in mt:
        print("-", str(r.get("标题"))[:60], "|", str(r.get("类型"))[:10], "|", str(r.get("关联能力域"))[:30])
except Exception as e:
    print("ERR mt", e)
