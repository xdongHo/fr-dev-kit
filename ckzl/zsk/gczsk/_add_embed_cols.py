# -*- coding: utf-8 -*-
"""parts/materials 表加 embedding 列（float32 BLOB）"""
import re
import os
BASE = os.path.dirname(os.path.abspath(__file__))

def patch(fn, table, anchor_col, new_cols):
    src = open(fn, encoding="utf-8").read()
    # 在指定列后追加新列定义
    src = src.replace(anchor_col, anchor_col + "\n" + new_cols, 1)
    open(fn, "w", encoding="utf-8").write(src)
    print(f"{fn} 已加列")

BK = os.path.join(BASE, "build_kb.py")
B5 = os.path.join(BASE, "build_5m1e.py")

# parts 表: verified 列后加 embedding 三列
src = open(BK, encoding="utf-8").read()
old = "  verified    INTEGER DEFAULT 0       -- 1=实测, 0=文档推断\n)"
new = """  verified    INTEGER DEFAULT 0,      -- 1=实测, 0=文档推断
  embed_vec   BLOB,                    -- 语义检索向量 (float32, 1024/512 维)
  embed_dim   INTEGER DEFAULT 1024,
  embed_model TEXT                     -- 生成向量的模型名
)"""
if "embed_vec" not in src:
    src = src.replace(old, new, 1)
    open(BK, "w", encoding="utf-8").write(src)
    print("build_kb.py parts 表已加 embed_vec/embed_dim/embed_model")
else:
    print("build_kb.py 已有 embed 列")

# materials 表: source 列后加 embedding 三列
src5 = open(B5, encoding="utf-8").read()
old5 = "  source      TEXT,\n  UNIQUE(name, path)"
new5 = """  source      TEXT,
  embed_vec   BLOB,
  embed_dim   INTEGER DEFAULT 1024,
  embed_model TEXT,
  UNIQUE(name, path)"""
if "embed_vec" not in src5:
    src5 = src5.replace(old5, new5, 1)
    open(B5, "w", encoding="utf-8").write(src5)
    print("build_5m1e.py materials 表已加 embed 列")
else:
    print("build_5m1e.py 已有 embed 列")
