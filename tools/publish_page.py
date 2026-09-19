# -*- coding: utf-8 -*-
"""把 index.html 重新导入空间页节点（覆盖更新），并声明所有数据表的 databaseRef。

⚠️ 关键：空间页要能读到某张表，必须 (a) 该表与页面建立 page↔database 绑定
   （见 tools/fix_page_binding.py），(b) 重导入时带上 --databases 声明。
   否则页面 db.query 该表永远返回空 —— 表现为「表里有数据，页面上却没有」。

用法：
    python tools/publish_page.py <op_token>
    PUB_TOKEN=<op_token> python tools/publish_page.py
"""
import json, os, subprocess, sys

TOKEN = (sys.argv[1] if len(sys.argv) > 1 else "") or os.environ.get("PUB_TOKEN", "")
if not TOKEN:
    print("缺少 op_token（参数或 PUB_TOKEN）")
    sys.exit(2)

PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Users\24186\.workbuddy\plugins\cache\workbuddy-builtin\skill-library\5.5.6-wb.38337834.g5f969292.h4918b5ced607"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
HTML = os.path.join(ROOT, "index.html")
PAGE = "3DxcmFIl7G2SGJjdPXvqH5"          # 陪跑台空间页节点（不要用 HTML 内部 data-page-node-id）
IDS = json.load(open(os.path.join(ROOT, "data", "_db_ids.json"), encoding="utf-8"))

# 页面 DB 对象里实际会查询的表，全部声明（含辅线知识库）
KEYS = ["陪跑台·能力项", "陪跑台·知识卡", "陪跑台·打卡", "陪跑台·能力证据", "陪跑台·学习记录",
        "陪跑台·问答", "陪跑台·等级日志", "陪跑台·素材库", "陪跑台·面试题库", "陪跑台·任务反馈",
        "陪跑台·简历优化", "陪跑台·岗位JD", "陪跑台·原始简历", "陪跑台·辅线知识库"]
dbs = json.dumps([{"id": IDS[k]} for k in KEYS], ensure_ascii=False)

p = subprocess.run(
    [PY, os.path.join(SKILL, "page", "import_html.py"), "--token-stdin",
     "--node-block-id", PAGE, "--databases", dbs, HTML],
    input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=300)
print("STDOUT:", (p.stdout or "").strip()[:800])
print("STDERR:", (p.stderr or "").strip()[:400])
print("RC:", p.returncode)
