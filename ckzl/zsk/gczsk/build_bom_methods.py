# -*- coding: utf-8 -*-
"""生成 类→方法 BOM 关系（METHOD_OF）：
对每个类级零件（name==class 短名），关联同 class_name 的所有方法零件
用法: python build_bom_methods.py [--rebuild]  # --rebuild 先清空 METHOD_OF 重建
"""
import sqlite3, sys
import os
BASE = os.path.dirname(os.path.abspath(__file__))

DB = os.path.join(BASE, "api_kb.sqlite")
REBUILD = "--rebuild" in sys.argv

conn = sqlite3.connect(DB)
cur = conn.cursor()

if REBUILD:
    cur.execute("DELETE FROM bom WHERE rel_type='METHOD_OF'")
    print("已清空旧 METHOD_OF 关系")

# 1. 找类级零件: name == class_name 最后一段, 且 class_name 具体(非通配)
rows = cur.execute("SELECT part_id, part_no, name, class_name FROM parts").fetchall()
cls_rep = {}   # class_name -> part_id（类代表零件）
for pid, pno, name, cls in rows:
    if not cls or cls.endswith("*") or "." not in cls:
        continue
    short = cls.split(".")[-1]
    if name == short:
        cls_rep.setdefault(cls, pid)

# 2. 对每个方法零件, 找所属类代表, 建立 METHOD_OF
methods = cur.execute("SELECT part_id, part_no, name, class_name FROM parts WHERE class_name NOT LIKE '%*%'").fetchall()
added = 0
skipped = 0
for pid, pno, name, cls in rows:
    if cls not in cls_rep:
        continue
    short = cls.split(".")[-1]
    if name == short:
        continue  # 类代表本身
    parent = cls_rep[cls]
    # 已有则跳过（去重）
    exists = cur.execute("SELECT 1 FROM bom WHERE parent_part_id=? AND child_part_id=? AND rel_type='METHOD_OF'", (parent, pid)).fetchone()
    if exists:
        skipped += 1
        continue
    cur.execute("INSERT INTO bom(parent_part_id, child_part_id, rel_type, note, qty) VALUES(?,?,?,?,1)",
                (parent, pid, "METHOD_OF", "组件方法归属"))
    added += 1

conn.commit()
total = cur.execute("SELECT count(*) FROM bom").fetchone()[0]
by_type = cur.execute("SELECT rel_type, count(*) FROM bom GROUP BY rel_type").fetchall()
print(f"新增 METHOD_OF: {added}, 跳过重复: {skipped}")
print(f"bom 总数: {total}, 按类型: {by_type}")
conn.close()
