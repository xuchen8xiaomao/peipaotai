# -*- coding: utf-8 -*-
"""创建「陪跑台·岗位JD」和「陪跑台·原始简历」两张表，打印 database_id。"""
import json, os, subprocess, sys

TOKEN = sys.argv[1]
PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
SKILL = r"C:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library\database"

schemas = {
    "陪跑台·岗位JD": [
        {"name": "公司", "config": {"text": {}}},
        {"name": "岗位", "config": {"text": {}}},
        {"name": "JD原文", "config": {"text": {}}},
        {"name": "链接", "config": {"url": {}}},
        {"name": "关联能力域", "config": {"text": {}}},
        {"name": "入库日期", "config": {"date": {}}},
        {"name": "状态", "config": {"text": {}}},
    ],
    "陪跑台·原始简历": [
        {"name": "版本", "config": {"text": {}}},
        {"name": "内容", "config": {"text": {}}},
        {"name": "字数", "config": {"number": {}}},
        {"name": "入库日期", "config": {"date": {}}},
        {"name": "状态", "config": {"text": {}}},
    ],
}

for title, props in schemas.items():
    schema = {"title": title, "properties": props}
    p = subprocess.run(
        [PY, os.path.join(SKILL, "create_database.py"), "--token-stdin", "--schema", json.dumps(schema, ensure_ascii=False)],
        input=TOKEN, capture_output=True, text=True, encoding="utf-8", timeout=60)
    out = (p.stdout or "").strip()
    print("=== %s ===" % title)
    print("STDOUT:", out)
    if p.stderr.strip():
        print("STDERR:", p.stderr.strip()[:600])
    print()
