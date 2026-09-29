#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
query_kb.py — 知识库检索入口（无向量·PageIndex 版，2026-09-29）

架构（参考 PageIndex：按文档结构建树索引 + 页级存储 + 导航式检索，向量路已整体归档）:
  1. 关键词检索（默认）: FTS5 BM25（jcxt/js/_kb_fts.db，由 build_fts_index.py 从 ckzl 直建）
  2. --tree [目录]     : 打印树索引目录（jcxt/data/_tree_index.json，由 build_tree_index.py 生成）
  3. --page <id|路径>  : 页级阅读——KB_INDEX 元数据 + 章节目录（--full 加印全文）
  4. --views / --view  : 多维视图目录（scenario 场景 / temperature 冷热 / practice 实战，
                         jcxt/data/_views.json，由 build_views.py 按 views.yaml 规则生成；
                         --hot / --cold / --warm 为冷热视图快捷方式）

用法（与 AGENTS.md 引用保持兼容）:
    python jcxt/js/query_kb.py "打开Excel 转 cpt" --mode keyword --top 3
    python jcxt/js/query_kb.py "冻结窗格" --full
    python jcxt/js/query_kb.py --tree ckzl/lc
    python jcxt/js/query_kb.py --page lc/10_Excel骨架正向工艺 [--full]
    python jcxt/js/query_kb.py --views                # 列全部视图
    python jcxt/js/query_kb.py --view 运维维护        # 支持中文名/英文 key（ops/hot/flow_f…）
    python jcxt/js/query_kb.py --hot                  # 等价 --view hot（--cold/--warm 同理）
    --mode hybrid / vector / --hybrid 已移除，会报错提示改用 keyword。
"""

# --- console-safe guard (win GBK 控制台打印特殊字符不再 UnicodeEncodeError) ---
from kb_common import setup_console
setup_console()
# --- end guard ---
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (DATA_DIR, FTS_DB, KB_ROOT, TREE_INDEX, fts_expr_prefix,
                       fts_match_expr, tokenize_for_fts)

VIEWS_INDEX = DATA_DIR / "_views.json"   # 多维视图产物（build_views.py 生成）


# ================================================================ 关键词检索（FTS5 BM25）
def do_search(question, topn, full=False):
    """纯 FTS5 关键词检索。AND 零命中时同 token OR 降级重试一次（沿袭旧版策略）。"""
    if not FTS_DB.exists():
        raise SystemExit("[错误] 找不到 _kb_fts.db，请先运行: python jcxt/js/build_fts_index.py")
    try:
        conn = sqlite3.connect(f"file:{FTS_DB}?mode=ro", uri=True)
        total = conn.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
        n_pages = int(conn.execute(
            "SELECT value FROM meta WHERE key='n_pages'").fetchone()[0])
    except (sqlite3.DatabaseError, sqlite3.OperationalError):
        raise SystemExit("[错误] _kb_fts.db 损坏或无效，请重建: python jcxt/js/build_fts_index.py")

    expr = fts_expr_prefix(question)
    rows = []
    if expr:
        rows = conn.execute(
            "SELECT bm25(chunks_fts), file_path, section_path, chunk_text, "
            "page_id, page_title, keywords, n_sections "
            "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY 1 LIMIT ?",
            (expr, topn)).fetchall()
        degraded_or = False
        if not rows:  # H5 同款降级: 同 token 集 OR 重试一次
            degraded_or = True
            toks = tokenize_for_fts(question).split()
            expr_or = " OR ".join('"%s"' % t for t in toks)
            if expr_or:
                rows = conn.execute(
                    "SELECT bm25(chunks_fts), file_path, section_path, chunk_text, "
                    "page_id, page_title, keywords, n_sections "
                    "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY 1 LIMIT ?",
                    (expr_or, topn)).fetchall()
    conn.close()

    print(f"问题: {question}")
    if degraded_or:
        print("⚠ AND 零命中，已降级为 OR 匹配（结果可能只含部分关键词）")
    print(f"模式: keyword | 命中 top {len(rows)} / 共 {total} 个知识块 / {n_pages} 页\n")
    for i, (bm, fp, sp, text, pid, ptitle, kws, nsec) in enumerate(rows, 1):
        # bm25 越负越相关 → 输出正分数（越大越相关），保持旧版 "[分数] 路径 > 章节" 风格
        print(f" {i}. [{-bm:.2f} kw] {fp}  >  {sp}")
        kws_show = (kws or "")[:80]
        print(f"    页: {pid} | 章节 {nsec} | {ptitle}"
              + (f" | 关键词: {kws_show}" if kws_show else ""))
        print(f"    {text.replace(chr(10), ' ')[:120]}")
        if full:
            print("-" * 60)
            print(text)
        print()
    print("提示: 加 --full 打印命中块全文；--tree 看目录导航；--page <id> 整页精读（--page <id> --full 全文）。")


# ================================================================ 树导航（--tree）
def _load_tree():
    if not TREE_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {TREE_INDEX}，请先运行: python jcxt/js/build_tree_index.py")
    try:
        return json.loads(TREE_INDEX.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise SystemExit(f"[错误] {TREE_INDEX.name} 损坏，请重建: python jcxt/js/build_tree_index.py")


def _norm_dir(filt):
    """"lc" / "ckzl/lc" / "ckzl/lc/" / ".\\ckzl\\lc" → "ckzl/lc" 归一。"""
    f = filt.strip().replace("\\", "/").strip("/")
    while f.startswith("./"):
        f = f[2:]
    if f == "ckzl":
        return "ckzl"
    if not f.startswith("ckzl/"):
        f = "ckzl/" + f
    return f.rstrip("/")


def _print_tree(node, prefix, is_last, lines_out):
    kids = node.get("children", [])
    connector = "└── " if is_last else "├── "
    if "children" in node:
        n_pages = sum(1 for k in kids if "children" not in k)
        n_dirs = sum(1 for k in kids if "children" in k)
        label = f"{node['title']}/  ({n_pages} 页" + (f", {n_dirs} 子目录" if n_dirs else "") + ")"
    else:
        label = f"{node['title']}  [{node.get('lines', '?')} 行]"
    lines_out.append(prefix + connector + label)
    child_prefix = prefix + ("    " if is_last else "│   ")
    for j, k in enumerate(kids):
        _print_tree(k, child_prefix, j == len(kids) - 1, lines_out)


def do_tree(filt=""):
    doc = _load_tree()
    root = doc.get("root", [])
    print(f"知识库目录树  (生成于 {doc.get('generated_at', '?')} | 共 {doc.get('page_count', '?')} 页)")
    if filt:
        target = _norm_dir(filt)
        nodes = [n for n in root if n.get("path") == target]
        if not nodes:  # 允许更深层目录过滤，如 ckzl/lc/fr10_deep_learn
            def walk(ns):
                for n in ns:
                    if n.get("path") == target:
                        yield n
                    yield from walk(n.get("children", []))
            nodes = list(walk(root))
        if not nodes:
            tops = ", ".join(n["path"] for n in root)
            raise SystemExit(f"[错误] 目录不存在: {filt}（归一为 {target}）。顶层可选: {tops}")
        root = nodes
    out = []
    for j, n in enumerate(root):
        _print_tree(n, "", j == len(root) - 1, out)
    print("\n".join(out))
    print("\n提示: --page <id> 阅读某页（id 见树叶标注路径去 .md），加 --full 打印整页全文。")


# ================================================================ 页级阅读（--page）
def _find_page(key):
    """按 id / 路径 / 关键词定位页。返回 (page_dict, doc)。"""
    doc = _load_tree()
    pages = doc.get("pages", [])
    k = key.strip().replace("\\", "/")
    if k.lower().endswith(".md"):
        k_md, k_noext = k, k[:-3]
    else:
        k_md, k_noext = k + ".md", k

    def hit(p):  # 命中优先级: id → 完整路径 → 去扩展路径 → 后缀 → 包含
        pid, pp = p["id"], p["path"]
        if k == pid or k_noext == pid:
            return 0
        if k == pp or k_md == pp or ("ckzl/" + k_md) == pp or ("ckzl/" + k_noext) == pp:
            return 1
        if pp.endswith(k_md) or pp.endswith(k_noext) or pp.endswith(k):
            return 2
        if pid.endswith(k) or pid.endswith(k_noext):
            return 3
        if k_noext in pid or k_noext in pp or k_noext in p.get("title", ""):
            return 4
        return 99

    cands = sorted((hit(p), p) for p in pages if hit(p) != 99)
    if not cands:
        raise SystemExit(f"[错误] 未找到页: {key}\n"
                         f"提示: 先 --tree 浏览目录拿页 id，或用关键词子串（命中多页时会列出候选）。")
    best = cands[0][0]
    exact = [p for h, p in cands if h == best]
    if len(exact) > 1 and best >= 3:
        print(f"⚠ \"{key}\" 模糊命中 {len(exact)} 页，请用更精确的 id：")
        for p in exact[:10]:
            print(f"   - {p['id']}  {p['title']}")
        raise SystemExit(1)
    return exact[0], doc


def do_page(key, full=False):
    pg, _ = _find_page(key)
    fp = KB_ROOT / pg["path"]
    print(f"页 ID: {pg['id']}")
    print(f"路径: {pg['path']}  ({pg['lines']} 行 | {len(pg['sections'])} 个章节)")
    print(f"标题: {pg['title']}")
    if pg.get("tags"):
        print(f"标签: {', '.join(pg['tags'])}")
    if pg.get("keywords"):
        print(f"关键词: {', '.join(pg['keywords'])}")
    if pg.get("summary"):
        print(f"摘要: {pg['summary']}")
    print("\n章节目录:")
    for s in pg["sections"]:
        print(f"  L{s['line']:>5}  {s['title']}")
    if not pg["sections"]:
        print("  （无标题章节）")
    if full:
        if not fp.exists():
            raise SystemExit(f"\n[错误] 文件已不存在: {fp}（知识库有变动，请重跑 build_tree_index.py）")
        print("\n" + "=" * 70)
        print(fp.read_text(encoding="utf-8-sig", errors="replace"))
    else:
        print(f"\n提示: 加 --full 打印整页全文；直接精读: {fp}")


# ================================================================ 多维视图（--views / --view / --hot / --cold）
def _load_views():
    if not VIEWS_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {VIEWS_INDEX}，视图数据缺失，请先运行: "
                         f"python jcxt/js/build_views.py")
    try:
        return json.loads(VIEWS_INDEX.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise SystemExit(f"[错误] {VIEWS_INDEX.name} 损坏，请重建: python jcxt/js/build_views.py")


def _resolve_view(views, key):
    """视图名解析：完整 key → 中文名 → 英文短名（scenario_ops→ops）→ 中文名/短名前缀。
    返回视图 dict；歧义/未命中时列出候选并退出。"""
    k = key.strip()
    if not k:
        raise SystemExit("[错误] --view 需要视图名，如: --view 运维维护 / ops / hot。--views 可列全部。")
    kl = k.lower()
    exact = [v for v in views.values() if k == v["key"] or k == v["name"]
             or kl == v["key"].lower()]
    if len(exact) == 1:
        return exact[0]
    short = [v for v in views.values()
             if v["key"].split("_", 1)[-1].lower() == kl
             or f"{v['dim']}/{v['key'].split('_', 1)[-1]}".lower() == kl]
    if len(short) == 1:
        return short[0]
    fuzzy = [v for v in views.values()
             if v["name"].startswith(k) or v["key"].split("_", 1)[-1].lower().startswith(kl)]
    seen, cands = set(), []
    for v in exact + short + fuzzy:
        if v["key"] not in seen:
            seen.add(v["key"])
            cands.append(v)
    if len(cands) == 1:
        return cands[0]
    if not cands:
        raise SystemExit(f"[错误] 未找到视图: {key}。可先用 --views 查看全部视图名。")
    print(f"⚠ \"{key}\" 模糊命中 {len(cands)} 个视图，请用更精确的名称：")
    for v in cands:
        print(f"   - {v['key']}  {v['name']}  ({v['count']} 页)")
    raise SystemExit(1)


def do_views():
    doc = _load_views()
    views = doc.get("views", {})
    print(f"多维视图目录  (生成于 {doc.get('generated_at', '?')} | 树索引 "
          f"{doc.get('tree_generated_at', '?')} | 全库 {doc.get('page_count', '?')} 页)\n")
    cur = None
    for v in views.values():
        if v["dim"] != cur:
            cur = v["dim"]
            label = {"scenario": "场景", "temperature": "冷热", "practice": "实战"}.get(cur, cur)
            print(f"[{cur} · {label}]")
        print(f"  {v['key']:<20} {v['name']:<12} {v['count']:>3} 页  {v['desc']}")
    print("\n提示: --view <名> 查看某视图页清单（支持中文名/英文 key，如 运维维护 / ops / hot / flow_f）；"
          "--hot / --cold / --warm 为冷热快捷方式。")


def do_view(key):
    doc = _load_views()
    v = _resolve_view(doc.get("views", {}), key)
    print(f"视图: {v['name']}  [{v['dim']}/{v['key']}]  共 {v['count']} 页")
    if v.get("desc"):
        print(f"说明: {v['desc']}")
    if v.get("rules_summary"):
        print(f"规则: {v['rules_summary']}")
    if v.get("external"):
        print("外置指针:")
        for e in v["external"]:
            print(f"  - {e}")
    print()
    for i, p in enumerate(v["pages"], 1):
        line = (f"{i:>3}. {p['title']}  [{p['lines']}行] — "
                f"{(p.get('summary') or '')[:60]}  | {p['path']}")
        if "hot_score" in p:
            line += f"  🔥{p['hot_score']}"
        print(line)
    print("\n提示: --page <id> 精读某页；--views 列全部视图。")


# ================================================================ CLI
def main():
    ap = argparse.ArgumentParser(
        prog="query_kb.py",
        description="知识库检索（无向量·PageIndex 版）: FTS5 关键词 + 目录树导航 + 页级阅读 + 多维视图")
    ap.add_argument("question", nargs="?", default="",
                    help="查询问题，如 \"冻结表头怎么配置\"（默认模式 keyword）")
    ap.add_argument("--mode", choices=["keyword", "hybrid", "vector"], default="keyword",
                    help="检索模式（无向量版仅 keyword 可用）")
    ap.add_argument("--top", type=int, default=5, help="返回条数（默认 5）")
    ap.add_argument("--full", action="store_true",
                    help="检索时打印命中块全文；--page 时打印整页全文")
    ap.add_argument("--tree", nargs="?", const="", default=None, metavar="目录",
                    help="打印目录树，可选目录过滤如 --tree ckzl/lc")
    ap.add_argument("--page", default=None, metavar="id或路径",
                    help="页级阅读: id/路径/关键词，如 lc/10_Excel骨架正向工艺")
    ap.add_argument("--views", action="store_true",
                    help="列出全部多维视图（场景/冷热/实战）及页数")
    ap.add_argument("--view", default=None, metavar="视图名",
                    help="打印某视图页清单，支持中文名/英文 key，如 运维维护 / ops / flow_f")
    ap.add_argument("--hot", action="store_true", help="等价 --view hot（热视图）")
    ap.add_argument("--cold", action="store_true", help="等价 --view cold（冷视图）")
    ap.add_argument("--warm", action="store_true", help="等价 --view warm（温视图）")
    ap.add_argument("--hybrid", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--mock", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--engine", default=None, help=argparse.SUPPRESS)
    args, unknown = ap.parse_known_args()
    if unknown:
        print(f"⚠ WARN: 忽略未知参数: {' '.join(unknown)}")

    if args.hybrid or args.mode in ("hybrid", "vector"):
        raise SystemExit("[错误] 向量/混合检索已移除（2026-09-29 PageIndex 无向量改造，组件归档于 "
                         "~/.fr_dev_kit/kit_archive/removed_kb_20260929/）。"
                         "请改用 --mode keyword（默认即是），导航用 --tree / --page。")
    if args.mock:
        print("⚠ --mock 已无效果：向量路已移除，关键词检索零 key 零配置。")
    if args.engine:
        print("⚠ --engine 已无效果：向量路已移除。")
    if args.top <= 0:
        raise SystemExit(f"[错误] --top 必须为正整数，收到: {args.top}")

    # 优先级: --views > --view/--hot/--cold/--warm > --page > --tree > 关键词检索
    if args.views:
        do_views()
        return
    view_key = args.view or ("hot" if args.hot else None) or ("cold" if args.cold else None) \
        or ("warm" if args.warm else None)
    if view_key is not None:
        do_view(view_key)
        return
    if args.page is not None:
        if not args.page.strip():
            raise SystemExit('[错误] --page 需要页 id/路径，如: --page lc/10_Excel骨架正向工艺')
        do_page(args.page, full=args.full)
        return
    if args.tree is not None:
        do_tree(args.tree)
        return
    if not args.question.strip():
        ap.print_help()
        raise SystemExit("\n[错误] 请提供查询词，或使用 --tree / --page / --view 导航。"
                         '示例: python jcxt/js/query_kb.py "冻结窗格" --top 5')
    do_search(args.question, args.top, full=args.full)


if __name__ == "__main__":
    main()
