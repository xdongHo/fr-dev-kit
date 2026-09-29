#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_doc_id_registry.py — L3 白名单构建器（doc_id_registry）
=============================================================
设计依据：设计A-事前门禁.md §2 件3/件4＋铁律改造清单-A.md §3（白名单门禁设计）
＋闸门1裁决清单.md 裁决1：doc_id_registry 独立白名单（铁律区实测 76 个 doc-XXXX
＋ckzl/bb/外部依赖与归档声明.md 54 项「来源 doc」），字面量精确比对，零 embedding 零网络；
不与 api_kb.sqlite 混职责（清单B §3.2：该库 0 字节，职责是 FR Java API 知识）。

来源（只读，B 版带来源行号）：
    S1  ckzl/gf/FR_HEADLESS_GUIDE.md  「## 全局铁律」区（起始行至下一「## 」节前）
    S2  ckzl/bb/外部依赖与归档声明.md        全部表格的「来源 doc」列（多值格 doc-A/B 拆分）

输出：KIT3\\ckzl/zsk/gczsk\\doc_id_registry.json
    条目字段：src / verified / date（B 版另附 src_lines 来源行号）
幂等：同输入重跑仅 date（构建日）随之；只写本文件输出这一个新文件。
用法：python build_doc_id_registry.py [--guide <路径>] [--todo <路径>] [--out <路径>] [--check-only]
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import argparse
import datetime
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 脚本在 kfgj/fzpy/，根目录上跳三层
DOC_RE = re.compile(r"doc-\d+")
# 多值格实测形态：doc-3475/1383、doc-1269/1270——后续 ID 为裸数字（共用 doc- 前缀）
TOK_RE = re.compile(r"(?i)doc-\d+(?:\s*[/、,;]\s*\d+)*")
SRC_CELL_RE = re.compile(r"(?i)^doc-\d+(?:\s*[/、,;]\s*\d+)*\s*[;,.]?$")
EXPECTED = {"S1_unique": 76, "S2_rows": 54}  # 闸门1裁决1 实测锚，供对账


def expand_token(tok):
    """'doc-3475/1383' -> ['doc-3475', 'doc-1383']；单值原样。"""
    parts = re.split(r"\s*[/、,;]\s*", tok.strip().rstrip(";,."))
    out = [parts[0].lower()]
    for p in parts[1:]:
        if p.isdigit():
            out.append("doc-" + p)
    return out


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def extract_zone(lines, start_marker, end_marker):
    """取 start_marker 所在行至下一 end_marker 前一行（1-based 闭区间转 0-based）。"""
    start = end = None
    for i, l in enumerate(lines):
        if start is None and l.startswith(start_marker):
            start = i
        elif start is not None and l.startswith(end_marker):
            end = i
            break
    if start is None:
        raise SystemExit("[ERR] 未找到起始标记: %s" % start_marker)
    end = end if end is not None else len(lines)
    return start, end  # 0-based [start, end)


def build(guide_path, todo_path, out_path):
    today = datetime.date.today().isoformat()
    ids = {}   # docid -> {"src": [...], "src_lines": {srcfile: [lines]}, "src_sections": {...}}
    report = {"S1": {}, "S2": {}}

    # ---- S1: ckzl/gf/FR_HEADLESS_GUIDE.md 全局铁律区 ----
    g_lines = read_lines(guide_path)
    s, e = extract_zone(g_lines, "## 全局铁律", "## ")
    occurrences = 0
    for i in range(s, e):
        for m in DOC_RE.findall(g_lines[i]):
            docid = m.lower()
            occurrences += 1
            ent = ids.setdefault(docid, {"src": [], "src_lines": {}, "src_sections": {}})
            lst = ent["src_lines"].setdefault("ckzl/gf/铁律速查.md", [])
            if (i + 1) not in lst:
                lst.append(i + 1)
    src1 = "ckzl/gf/铁律速查.md" % ()
    for docid in [d for d in ids if "ckzl/gf/铁律速查.md" in ids[d]["src_lines"]]:
        if src1 not in ids[docid]["src"]:
            ids[docid]["src"].append(src1)
    report["S1"] = {"zone": "L%d-L%d" % (s + 1, e), "occurrences": occurrences,
                    "unique": sum(1 for d in ids if "ckzl/gf/FR_HEADLESS_GUIDE.md" in ids[d]["src_lines"])}

    # ---- S2: ckzl/bb/外部依赖与归档声明.md 表格「来源 doc」列 ----
    # 稳健解析：①逻辑行缓冲（表格行内嵌真实换行，如 L32-35 官方模板路径断行，
    # 续行并入上一逻辑行）；②来源格按内容识别（整格仅为 doc-ID 列表，可多值
    # doc-A/B、可带尾分号），不依赖列位移——防内容格里 raw「|」致列号漂移。
    t_lines = read_lines(todo_path) if todo_path and os.path.isfile(todo_path) else []
    section = ""
    in_table = False
    row_buf = None  # 当前逻辑行 (start_line, text)
    src_cell_re = SRC_CELL_RE

    def flush(buf, ids, section, acc):
        """解析一个逻辑表格行（buf=(start_line,text)）；返回是否为数据行。"""
        if buf is None:
            return False
        start_line, text = buf
        cells = [c.strip() for c in text.strip().strip("|").split("|")]
        if not cells or all(re.fullmatch(r"[:\-\s]*", c) for c in cells):
            return False  # 表头分隔行
        found = []
        for c in cells:
            if src_cell_re.match(c):
                found = []
                for tok in TOK_RE.findall(c):
                    found.extend(expand_token(tok))
                break
        if not found:
            return True  # 数据行但来源格无 doc-ID（如实计数）
        for m in found:
            docid = m.lower()
            ent = ids.setdefault(docid, {"src": [], "src_lines": {}, "src_sections": {}})
            lst = ent["src_lines"].setdefault("ckzl/bb/外部依赖与归档声明.md", [])
            if start_line not in lst:
                lst.append(start_line)
            ent["src_sections"].setdefault("ckzl/bb/外部依赖与归档声明.md", [])
            if section and section not in ent["src_sections"]["ckzl/bb/外部依赖与归档声明.md"]:
                ent["src_sections"]["ckzl/bb/外部依赖与归档声明.md"].append(section)
        acc.append((start_line, found))
        return True

    rows = 0
    row_buf = None
    for i0, line in enumerate(t_lines):
        i = i0 + 1  # 1-based 行号
        if line.startswith("## "):
            flush(row_buf, ids, section, [])
            row_buf = None
            in_table = False
            section = line[3:].strip()
            continue
        if not line.lstrip().startswith("|"):
            if row_buf is not None and line.strip():
                row_buf = (row_buf[0], row_buf[1].rstrip("\n") + " " + line.strip())
                continue
            if row_buf is not None:
                if flush(row_buf, ids, section, []):
                    rows += 1
                row_buf = None
            in_table = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "来源 doc" in cells:
            if row_buf is not None:
                if flush(row_buf, ids, section, []):
                    rows += 1
                row_buf = None
            in_table = True
            continue
        if not in_table:
            continue
        if all(re.fullmatch(r"[:\-\s]*", c) for c in cells):  # 分隔行
            row_buf = None
            continue
        if row_buf is not None:
            if flush(row_buf, ids, section, []):
                rows += 1
        row_buf = (i, line)
    if row_buf is not None:
        if flush(row_buf, ids, section, []):
            rows += 1
    src2 = "ckzl/bb/外部依赖与归档声明.md#来源doc列"
    for docid in [d for d in ids if "ckzl/bb/外部依赖与归档声明.md" in ids[d]["src_lines"]]:
        if src2 not in ids[docid]["src"]:
            ids[docid]["src"].append(src2)
    report["S2"] = {"rows": rows, "unique": sum(
        1 for d in ids if "ckzl/bb/外部依赖与归档声明.md" in ids[d]["src_lines"])}

    # ---- 组装 registry（字段：src/verified/date，B 版附 src_lines 行号）----
    for docid, ent in ids.items():
        ent["verified"] = False  # 一期保守：核验状态以文档核验待办销项为准（设计A §6.3 开放依赖）
        ent["date"] = today
        ent["src_lines"]["ckzl/gf/FR_HEADLESS_GUIDE.md"] = sorted(
            ent["src_lines"].get("ckzl/gf/FR_HEADLESS_GUIDE.md", []))
        ent["src_lines"]["ckzl/bb/外部依赖与归档声明.md"] = sorted(
            ent["src_lines"].get("ckzl/bb/外部依赖与归档声明.md", []))

    registry = {
        "meta": {
            "name": "doc_id_registry",
            "purpose": "R5 写前白名单门禁数据源：只防『编造从未存在的 doc-ID』，不防真 ID 引错内容（清单B §3.2）",
            "method": "正则抽取 doc-\\d+ → 归一（小写）→ 字面量精确比对；零 embedding 零网络",
            "builder": "kfgj/fzpy/build_doc_id_registry.py",
            "built_at": today,
            "sources": {
                "S1": {"file": "ckzl/gf/FR_HEADLESS_GUIDE.md", "zone": report["S1"]["zone"],
                       "marker": "## 全局铁律 → 下一 ## 节前",
                       "unique": report["S1"]["unique"],
                       "occurrences": report["S1"]["occurrences"]},
                "S2": {"file": "ckzl/bb/外部依赖与归档声明.md", "column": "来源 doc",
                       "rows": report["S2"]["rows"], "unique": report["S2"]["unique"],
                       "note": "多值格 doc-A/B 拆分；行号=B 版可溯源锚"}
            },
            "counts": {"total_unique": len(ids)},
            "verification": {"verified_false_all": True,
                             "note": "verified 联动销项规则属设计A §6.3 开放依赖，一期全部 false"},
            "expected_anchors": EXPECTED,
            "anchor_check": {
                "S1_unique_ok": report["S1"]["unique"] == EXPECTED["S1_unique"],
                "S2_rows_ok": report["S2"]["rows"] == EXPECTED["S2_rows"]},
            "boundary": "独立于 api_kb.sqlite（闸门1裁决1：不混职责）"
        },
        "ids": dict(sorted(ids.items())),
    }
    return registry, report


def main():
    ap = argparse.ArgumentParser(description="构建 doc_id_registry 白名单")
    ap.add_argument("--guide", default=os.path.join(KIT_ROOT, "ckzl/gf/FR_HEADLESS_GUIDE.md"))
    ap.add_argument("--todo", default="")  # comm 版：S2 源文件已随个人组件移除，缺省跳过 S2
    ap.add_argument("--out", default=os.path.join(KIT_ROOT, "ckzl/zsk/gczsk", "doc_id_registry.json"))
    ap.add_argument("--check-only", action="store_true", help="只对账不落盘")
    args = ap.parse_args()

    registry, rep = build(args.guide, args.todo, args.out)
    print("=" * 62)
    print("  doc_id_registry 构建对账")
    print("=" * 62)
    print("  S1 铁律区:      区间=%s  出现=%d 次  唯一=%d (期望 %d)"
          % (rep["S1"]["zone"], rep["S1"]["occurrences"], rep["S1"]["unique"],
             EXPECTED["S1_unique"]))
    print("  S2 来源doc列:   行=%d (期望 %d)  唯一=%d"
          % (rep["S2"]["rows"], EXPECTED["S2_rows"], rep["S2"]["unique"]))
    print("  合计唯一 doc-ID: %d" % registry["meta"]["counts"]["total_unique"])
    ok = all(registry["meta"]["anchor_check"].values())
    print("  锚核对账:       %s" % ("✅ 76/54 全符" if ok else "❌ 与裁决1锚不符"))
    print("=" * 62)
    if args.check_only:
        return 0 if ok else 2
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print("  落盘: %s" % args.out)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
