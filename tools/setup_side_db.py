#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, json
LIB = r'C:/Program Files/WorkBuddy/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/library'
sys.path.insert(0, LIB)
import _common

token = sys.argv[1]

def post(path, body):
    try:
        return _common.unwrap_data(_common.http_request("POST", _common.build_url(path), token, body=body, timeout=30))
    except Exception as e:
        return {"error": str(e)}

# 1) 知识卡表加「类型」字段（text，存：知识/模拟项目/简历包装）
r1 = post("/space/api/agent/v1/add-field", {
    "databaseId": "4zH7GK3VNQaBr9XHCE5sZH",
    "property": {"name": "类型", "config": {"text": {}}}
})
print("ADD_FIELD_CARD:", json.dumps(r1, ensure_ascii=False))

# 2) 新建「陪跑台·辅线知识库」表
schema = {
    "title": "陪跑台·辅线知识库",
    "properties": [
        {"name": "标题", "config": {"text": {}}},
        {"name": "分类", "config": {"text": {}}},
        {"name": "核心概念", "config": {"text": {}}},
        {"name": "深度资料", "config": {"text": {}}},
        {"name": "链接", "config": {"url": {}}},
        {"name": "日期", "config": {"date": {}}},
        {"name": "来源", "config": {"text": {}}}
    ]
}
r2 = post("/space/api/agent/v1/create-database", schema)
print("CREATE_SIDE:", json.dumps(r2, ensure_ascii=False))
