# -*- coding: utf-8 -*-
"""一次性发布编排：先把所有数据表绑定到空间页节点，再重新导入 index.html（带 14 表声明）。
token 从临时文件读取，避免出现在命令行/日志里。
用法：python tools/_deploy.py   （需先写 token 到 OP_TOKEN_FILE，默认指向用户目录下的临时文件）
"""
import json, os, subprocess, sys

PY = r"C:\Users\24186\.workbuddy\binaries\python\versions\3.13.12\python.exe"
ROOT = r"C:\Users\24186\WorkBuddy\2026-09-10-20-13-10"
TOKEN_FILE = os.environ.get("OP_TOKEN_FILE", r"C:\Users\24186\.workbuddy\tmp_op_token")

try:
    TOKEN = open(TOKEN_FILE, "r", encoding="utf-8").read().strip()
except Exception as e:
    print("读取 token 失败:", e); sys.exit(2)
if not TOKEN:
    print("token 为空"); sys.exit(2)

print("== 1) 绑定数据表到空间页 ==")
bp = subprocess.run([PY, os.path.join(ROOT, "tools", "fix_page_binding.py"), TOKEN],
                    capture_output=True, text=True, encoding="utf-8", timeout=180)
print(bp.stdout[-2200:])
print("ERR:", bp.stderr[-300:])

print("== 2) 重新发布空间页（14 表） ==")
env = dict(os.environ); env["PUB_TOKEN"] = TOKEN
pp = subprocess.run([PY, os.path.join(ROOT, "tools", "publish_page.py")],
                    capture_output=True, text=True, encoding="utf-8", timeout=300, env=env)
print(pp.stdout[-2200:])
print("ERR:", pp.stderr[-300:])
