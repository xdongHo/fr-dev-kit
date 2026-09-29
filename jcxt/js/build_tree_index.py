#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tree_index.py — 知识库树索引构建器（PageIndex 思路·无向量改造，2026-09-29）

用途:
    扫描 ckzl/ 全部 .md（跳过 _ 开头文件/目录与非 md），生成 jcxt/data/_tree_index.json：
      - pages: 扁平全量页表（检索用）——每页 id / path / title / summary / keywords /
        tags / lines / sections（全部标题+行号）
      - root:  按目录层级组织的导航树（导航用）——目录节点含 children，页为叶子
    与 build_fts_index.py 互不依赖、可独立重跑；改知识后两个都要跑（见 README）。

用法:
    python jcxt/js/build_tree_index.py            # 全量重建 _tree_index.json
    python jcxt/js/build_tree_index.py --verify   # 自检: JSON 可解析/页数一致/抽样页字段完整
"""

# --- console-safe guard (win GBK 控制台) ---
from kb_common import setup_console
setup_console()
# --- end guard ---
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (CKZL_ROOT, TREE_INDEX, iter_md_files, list_headings,
                       parse_kb_index, rel_posix, page_id_of)


def build_pages():
    """扫描全部知识页，返回 (pages, n_skip)。"""
    pages = []
    for p in iter_md_files():
        try:
            content = p.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            content = p.read_text(encoding="utf-8", errors="replace")
        meta = parse_kb_index(content)
        lines = content.count("\n") + (0 if content.endswith("\n") or not content else 1)
        sections = [{"title": s, "line": ln} for ln, s in list_headings(content)]
        pages.append({
            "id": page_id_of(p),
            "path": rel_posix(p),
            "title": meta["title"] or p.stem,
            "summary": meta["summary"],
            "keywords": meta["keywords"],
            "tags": meta["tags"],
            "lines": lines,
            "sections": sections,
        })
    return pages


def build_tree(pages):
    """按目录层级组织导航树；目录节点 {title:目录名, path:"ckzl/lc", children:[...]}，
    页叶子 {title:页title, path, id, lines}。"""
    root = []
    dir_nodes = {}  # "ckzl/lc" -> node

    def dir_node(rel_dir):
        """rel_dir 形如 'ckzl/lc'；逐级挂到 root，返回最深层节点。"""
        node = None
        parts = rel_dir.split("/")
        for i in range(1, len(parts) + 1):
            key = "/".join(parts[:i])
            if key not in dir_nodes:
                node = {"title": parts[i - 1], "path": key, "children": []}
                dir_nodes[key] = node
                parent_key = "/".join(parts[:i - 1])
                (dir_nodes[parent_key] if parent_key in dir_nodes else
                 {"children": root})["children"].append(node)
            node = dir_nodes[key]
        return node

    for pg in pages:
        rel = pg["path"]              # ckzl/lc/03_报表构建.md
        rel_dir = rel.rsplit("/", 1)[0]
        node = dir_node(rel_dir)
        node["children"].append({
            "title": pg["title"],
            "path": rel,
            "id": pg["id"],
            "lines": pg["lines"],
        })

    def sort_children(n):
        n["children"].sort(key=lambda c: (("children" not in c), c["title"]))
        for c in n["children"]:
            if "children" in c:
                sort_children(c)

    root.sort(key=lambda n: n["title"])
    for n in root:
        sort_children(n)
    # 规格对齐：root 顶层直接列知识子目录（path 形如 "ckzl/lc"），
    # 不包 "ckzl" 外壳；仅当 ckzl 根下散落 .md 时才保留壳节点承载它们。
    if len(root) == 1 and root[0]["path"] == "ckzl":
        only = root[0]
        stray = [c for c in only["children"] if "children" not in c]
        root = [c for c in only["children"] if "children" in c]
        root.sort(key=lambda n: n["title"])
        if stray:  # 理论不出现（当前 ckzl 根下无散页），防御性保留
            root.append({"title": "ckzl", "path": "ckzl", "children": stray})
    return root


def do_build():
    pages = build_pages()
    doc = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "page_count": len(pages),
        "root": build_tree(pages),
        "pages": pages,
    }
    TREE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    TREE_INDEX.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    n_sec = sum(len(p["sections"]) for p in pages)
    n_kw = sum(1 for p in pages if p["keywords"])
    n_sum = sum(1 for p in pages if p["summary"])
    size_kb = TREE_INDEX.stat().st_size / 1024
    print(f"✅ 树索引完成  {TREE_INDEX}")
    print(f"   页数: {len(pages)} | 章节标题: {n_sec} | 有 keywords: {n_kw} | 有 summary: {n_sum}")
    print(f"   顶层目录: {', '.join(n['title'] for n in doc['root'])}")
    print(f"   文件大小: {size_kb:.0f} KB | 下一步: python jcxt/js/query_kb.py --tree")

    # 抽样打印 3 页便于人工核对
    print("\n抽样页（前 3）:")
    for pg in pages[:3]:
        print(f"   - {pg['id']}  [{pg['lines']} 行 / {len(pg['sections'])} 章节]  {pg['title']}")
    return 0


def do_verify():
    if not TREE_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {TREE_INDEX}，请先运行: python jcxt/js/build_tree_index.py")
    doc = json.loads(TREE_INDEX.read_text(encoding="utf-8"))
    pages, root = doc.get("pages", []), doc.get("root", [])
    ok = True

    def walk(nodes):
        for n in nodes:
            yield n
            yield from walk(n.get("children", []))

    tree_pages = [n for n in walk(root) if "children" not in n]
    print(f"页表: {len(pages)} | 树叶子: {len(tree_pages)} | "
          f"{'✓ 一致' if len(pages) == len(tree_pages) else '✗ 不一致!'}")
    ok &= len(pages) == len(tree_pages) and len(pages) > 0
    ids = {p["id"] for p in pages}
    ok &= all(t["id"] in ids for t in tree_pages)
    bad = [p["id"] for p in pages if not p.get("path") or p.get("lines", 0) <= 0
           or not isinstance(p.get("sections"), list)]
    if bad:
        print(f"✗ 字段异常页: {bad[:5]}")
        ok = False
    sample = next((p for p in pages if "03" in p["id"] and "lc" in p["id"]), pages[0])
    print(f"抽样: {sample['id']} → {sample['title']} ({len(sample['sections'])} 章节)")
    print(f"\n{'✅ verify PASS' if ok else '❌ verify FAIL'}")
    raise SystemExit(0 if ok else 1)


def main():
    setup_console()
    ap = argparse.ArgumentParser(description="知识库树索引构建器（无向量·PageIndex）")
    ap.add_argument("--verify", action="store_true", help="自检 _tree_index.json")
    args = ap.parse_args()
    if args.verify:
        do_verify()
    else:
        raise SystemExit(do_build())


if __name__ == "__main__":
    main()
