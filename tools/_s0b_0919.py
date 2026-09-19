# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coach as C

mt = C.load_all("rLcH92l8foVxGRWizDbTJA")
for r in mt:
    t = str(r.get("标题") or "")
    if "JD" in t or "面试真题" in t or "私有化" in t:
        print("=" * 20, t)
        print((r.get("原文") or r.get("摘要") or "")[:3500])
        print()
