# -*- coding: utf-8 -*-
"""E-AUTORETRY-001 的 --redo 修复脚本：给 doc_target.md 补 KB_INDEX 元数据头。

guard 的 run_redo 以仓库根为 cwd 执行本脚本；路径基于 __file__ 推导，与 cwd 无关。
幂等：无论目标当前处于何状态，重写后必含 KB_INDEX 头。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "doc_target.md")

HEADER = """<!--
KB_INDEX: {
  "title": "auto-retry 闭环测试知识件",
  "stage": "evals",
  "tags": ["fixture", "auto-retry"],
  "keywords": ["G06", "guard"],
  "summary": "evals/fixtures/auto_retry 的 redo 闭环夹具，非产线知识"
}
-->

"""

body = ""
if os.path.isfile(TARGET):
    with io.open(TARGET, "r", encoding="utf-8", errors="replace") as f:
        body = f.read()
    if "KB_INDEX" in body[:2000]:
        print("fix_doc: 目标已含 KB_INDEX 头，无需修复")
        raise SystemExit(0)

with io.open(TARGET, "w", encoding="utf-8") as f:
    f.write(HEADER + body)
print("fix_doc: 已补 KB_INDEX 头 -> %s" % TARGET)
