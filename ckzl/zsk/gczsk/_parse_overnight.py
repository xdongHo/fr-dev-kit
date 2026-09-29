# -*- coding: utf-8 -*-
"""v3 精准提取：识别文档核心类，方法只归属核心类，顺带类仅登记
产出 _overnight_extract.json
"""
import re, json
import os
BASE = os.path.dirname(os.path.abspath(__file__))

DOC = os.path.join(os.path.dirname(BASE), "ckzl/frapi/doc", "JavaAPI构建速查.md")
text = open(DOC, encoding="utf-8").read()

sections = re.split(r"^## (doc-\d+) ", text, flags=re.M)
docs = []
for i in range(1, len(sections), 2):
    docs.append((sections[i], sections[i+1].split("\n",1)[0].strip(), sections[i+1]))

CLS_RE = re.compile(r"com\.fr\.[A-Za-z0-9_$]+(?:\.[A-Za-z0-9_$]+)+")
METHOD_RE = re.compile(r"\b(set[A-Z]\w*|get[A-Z]\w*|add[A-Z]\w*|create[A-Z]\w*|remove[A-Z]\w*|put[A-Z]\w*)\s*\(")

def clean_class(c):
    """类名清洗: 仅当 倒数第二段大写(类名) + 最后一段小写(方法) 时砍掉方法段"""
    parts = c.split(".")
    if len(parts) >= 4 and parts[-1][:1].islower() and parts[-2][:1].isupper():
        return ".".join(parts[:-1])
    return c

def is_valid_cls(c):
    parts = c.split(".")
    if len(parts) < 3: return False
    if c.endswith("."): return False
    last = parts[-1]
    return bool(last) and last[0].isupper()

def find_core_class(seg):
    m = re.search(r"核心类\s*`?(com\.fr\.[A-Za-z0-9_.$]+)`?", seg)
    if m:
        c = clean_class(m.group(1))
        if is_valid_cls(c): return c
    return None

cls_methods = {}
cls_core_docs = {}
cls_all_docs = {}
for docid, title, body in docs:
    m = re.search(r"Java API 构建要点:(.*?)(?:- 最小 Java 示例|$)", body, re.S)
    seg = m.group(1) if m else body
    if "无(纯理解级内容)" in seg or "无 Java API" in seg:
        continue
    core = find_core_class(seg)
    for c in CLS_RE.findall(seg):
        cc = clean_class(c)
        if is_valid_cls(cc):
            cls_all_docs.setdefault(cc, set()).add(docid)
    if core:
        cls_core_docs.setdefault(core, set()).add(docid)
        for mm in METHOD_RE.findall(seg):
            cls_methods.setdefault(core, set()).add(mm)

out = []
for cls in sorted(cls_all_docs):
    methods = sorted(cls_methods.get(cls, set()))
    out.append({"class": cls, "methods": methods,
                "core_docs": sorted(cls_core_docs.get(cls, set())),
                "all_docs": sorted(cls_all_docs[cls])})

with open(os.path.join(BASE, "_overnight_extract.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

core_n = sum(1 for o in out if o["core_docs"])
print(f"有效类: {len(out)}  核心类(挂方法): {core_n}")
for o in out:
    if o["core_docs"]:
        print(f"★ {o['class']}  [{','.join(o['core_docs'])}]")
        print(f"    方法({len(o['methods'])}): {', '.join(o['methods'][:24]) or '-'}")
