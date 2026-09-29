# -*- coding: utf-8 -*-
"""从 _overnight_extract.json 生成 overnight_parts.py（增量零件 EXTRA_PARTS）"""
import re, json
import os
BASE = os.path.dirname(os.path.abspath(__file__))

EXTRACT = os.path.join(BASE, "_overnight_extract.json")
OUT = os.path.join(BASE, "overnight_parts.py")
BUILD = os.path.join(BASE, "build_kb.py")

build_src = open(BUILD, encoding="utf-8").read()
# 现有 (part_no, name, class_name) 三元组
existing_triples = set(re.findall(r'\(\"(P-\d+)\",\s*\"([\w$]+)\",\s*\"(com\.fr\.[^\"]+)\"', build_src))
existing_classes = {t[2] for t in existing_triples}
existing_name_cls = {(t[1], t[2]) for t in existing_triples}
print(f"现有零件: {len(existing_triples)}  现有类: {len(existing_classes)}")

def map_category(cls):
    if ".form.ui.container" in cls: return "CONTAINER"
    if ".form.ui" in cls: return "WIDGET"
    if ".form." in cls or ".form" in cls: return "FORM_BUILD"
    if ".report." in cls and "Style" in cls: return "STYLE"
    if ".report." in cls: return "CPT_BUILD"
    if ".data." in cls: return "DATASET"
    if ".js." in cls or "Hyperlink" in cls: return "LINK"
    if ".io." in cls: return "IO"
    if ".chart." in cls: return "CHART"
    if ".plugin." in cls: return "PLUGIN"
    if ".web" in cls: return "WEB"
    return "OTHER"

data = json.load(open(EXTRACT, encoding="utf-8"))

extra = []
next_no = 71
for o in data:
    cls = o["class"]
    core_docs = o["core_docs"]
    all_docs = o["all_docs"]
    src = "夜学:" + ",".join(core_docs or all_docs)
    # 1. 类级零件（类名未登记过）
    if cls not in existing_classes:
        cat = map_category(cls)
        extra.append((f"P-{next_no:04d}", cls.split(".")[-1], cls,
                      "new " + cls.split(".")[-1] + "() 或静态入口",
                      cat, f"夜学文档涉及的类（{'核心类' if core_docs else '顺带提及'}）",
                      "-", "-", "文档推断，使用前核对 jar", src, 0))
        next_no += 1
    # 2. 方法级零件（仅核心类的方法，按 (方法名,类) 去重）
    for mm in o["methods"]:
        if (mm, cls) in existing_name_cls:
            continue
        cat = map_category(cls)
        extra.append((f"P-{next_no:04d}", mm, cls, f"{mm}(...)",
                      cat, f"{cls.split('.')[-1]} 的方法（夜学 {','.join(core_docs)}）",
                      "-", "-", "文档推断，使用前核对 jar", src, 0))
        next_no += 1

lines = ['# -*- coding: utf-8 -*-',
         '"""夜学文档增量零件（自动生成自 _overnight_extract.json；重跑 _parse_overnight.py + _gen_extra_parts.py 即可再生成）"""',
         '',
         'EXTRA_PARTS = [']
for p in extra:
    lines.append(f'    {p!r},')
lines.append(']')
lines.append('')
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"生成增量零件: {len(extra)} 条 -> {OUT}")
print(f"编号范围: P-0071 .. P-{next_no-1:04d}")

if "from overnight_parts import EXTRA_PARTS" not in build_src:
    build_src = build_src.replace("# ---------- 零件表（物料主数据）----------",
        "from overnight_parts import EXTRA_PARTS\n\n# ---------- 零件表（物料主数据）----------")
    build_src = build_src.replace("    cur.executemany(\"INSERT INTO parts(",
        "    PARTS_ALL = PARTS + EXTRA_PARTS\n    cur.executemany(\"INSERT INTO parts(")
    build_src = build_src.replace("[(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10]) for p in PARTS])",
        "[(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10]) for p in PARTS_ALL])")
    open(BUILD, "w", encoding="utf-8").write(build_src)
    print("build_kb.py 已引入 EXTRA_PARTS")
else:
    print("build_kb.py 已包含引入")
