#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_fts_index.py — FTS5 关键词索引库构建器（无向量版，2026-09-29 重构）

用途:
    直接扫描 ckzl/ 全部 .md（跳过 _ 开头文件/目录与非 md，规则与 build_tree_index.py 一致），
    按 ## / ### / #### 章节分块，写入独立库 jcxt/js/_kb_fts.db，供 query_kb.py 关键词检索。

    - 纯本地运行：不调 embedding API、不触网、不依赖（已归档的）向量库
    - FTS 可检索字段 = 页标题 + KB_INDEX(title/summary/keywords/tags) + 章节路径 + 正文
      （沿袭压测 2026-08-19 建议②：专名/元数据拼进 fts_text，关键词不失明）
    - chunk_text 原文存 UNINDEXED 列（--full 展示用）；page_id / n_sections 等
      页级信息存 UNINDEXED 列（query_kb 命中结果展示"页 id + 章节数"用）

用法:
    python build_fts_index.py                # 全量重建（删除旧库重写，秒级~分钟级）
    python build_fts_index.py --verify       # 对账: 页数/块数/抽样查询
    python build_fts_index.py --query "冻结窗格" [--top 8] [--full]   # 建库后快速试查
"""

# --- console-safe guard (win GBK 控制台) ---
from kb_common import setup_console
setup_console()
# --- end guard ---
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (CKZL_ROOT, FTS_DB, fts_expr_prefix, fts_match_expr,
                       iter_md_files, page_id_of, parse_kb_index, rel_posix,
                       split_long, split_sections, tokenize_for_fts)

MAX_CHARS = 1200       # 单块正文上限（与被归档版 chunking.max_chars 一致）
OVERLAP = 150          # 相邻块重叠
MIN_CHARS = 20         # 短于该值的节丢弃（沿袭旧版 min_chunk_chars）


# ---------------------------------------------------------------- 建库
def do_build():
    if not FTS_DB.parent.exists():
        FTS_DB.parent.mkdir(parents=True, exist_ok=True)
    if FTS_DB.exists():
        FTS_DB.unlink()  # 重建式：删旧库，杜绝脏块/旧 schema 残留

    started = time.time()
    files = iter_md_files()
    if not files:
        raise SystemExit(f"[错误] {CKZL_ROOT} 下未扫描到任何待索引 md，请检查知识库目录")
    print(f"↺ 扫描 {CKZL_ROOT.name}/ 知识库: {len(files)} 个 md（跳过 _ 开头与非 md）")

    # 本地 sqlite 缺 FTS5 编译时优雅报错
    dst = sqlite3.connect(FTS_DB)
    try:
        dst.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                fts_text,
                file_path UNINDEXED,
                section_path UNINDEXED,
                chunk_text UNINDEXED,
                page_id UNINDEXED,
                page_title UNINDEXED,
                keywords UNINDEXED,
                n_sections UNINDEXED
            )""")
        dst.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")

        batch, n, n_pages, n_sections_total = [], 0, 0, 0
        for p in files:
            try:
                content = p.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                content = p.read_text(encoding="utf-8", errors="replace")
            meta = parse_kb_index(content)
            title = meta["title"] or p.stem
            kw_str = ", ".join(meta["keywords"])
            meta_str = " ".join([title, meta["summary"], kw_str, " ".join(meta["tags"])])
            sections = split_sections(content)
            n_sec = sum(1 for h1, sec, ln, t in sections if sec.strip())
            n_sections_total += n_sec
            n_pages += 1
            pid = page_id_of(p)

            page_chunks = []
            for h1, sec, ln, text in sections:
                if not sec.strip():
                    continue  # 丢弃无章节归属的杂散块（KB_INDEX 注释等）
                for part in split_long(text, MAX_CHARS, OVERLAP):
                    head = f"[章节] {sec}\n"
                    if kw_str:
                        head += f"[关键词] {kw_str}\n"
                    page_chunks.append((sec, head + part))
            if not page_chunks:  # 无章节正文页（如极简 README）→ 保底整页一块
                body = meta_str.strip() or p.stem
                page_chunks.append((title, body))

            for sec, text in page_chunks:
                fts_text = tokenize_for_fts(f"{title} {meta_str} {sec} {text}")
                batch.append((fts_text, rel_posix(p), sec, text, pid, title,
                              kw_str, str(n_sec)))
                if len(batch) >= 500:
                    _flush(dst, batch)
                    n += len(batch)
                    batch = []
                    print(f"   已写入 {n} 块（{n_pages} 页）")
        if batch:
            _flush(dst, batch)
            n += len(batch)

        for kv in (("built_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                   ("n_chunks", str(n)),
                   ("n_pages", str(n_pages)),
                   ("n_sections", str(n_sections_total)),
                   ("source", "ckzl md direct scan (vector-free, PageIndex)"),
                   ("tokenizer", "kb_common.tokenize_for_fts (CJK bigram)"),
                   ("fields", "title+summary+keywords+tags+section+body")):
            dst.execute("INSERT INTO meta(key, value) VALUES(?, ?)", kv)
        dst.commit()
        check = dst.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
    except sqlite3.OperationalError as e:
        if "fts5" in str(e).lower():
            raise SystemExit(f"[错误] 本机 SQLite 未编译 FTS5: {e}")
        raise
    finally:
        dst.close()

    print()
    print(f"✅ FTS 索引完成  {FTS_DB.name}")
    print(f"   块数: {check} | 页数: {n_pages} | 章节数: {n_sections_total}")
    print(f"   分词: CJK bigram | 检索字段: 标题+摘要+关键词+标签+章节+正文")
    print(f"   耗时: {time.time() - started:.1f}s | 下一步: python jcxt/js/query_kb.py \"关键词\" --top 5")


def _flush(dst, batch):
    dst.executemany(
        "INSERT INTO chunks_fts(fts_text, file_path, section_path, chunk_text, "
        "page_id, page_title, keywords, n_sections) VALUES(?,?,?,?,?,?,?,?)", batch)


# ---------------------------------------------------------------- 对账
def do_verify():
    started = time.time()
    if not FTS_DB.exists():
        raise SystemExit(f"[错误] 找不到 {FTS_DB.name}，请先运行: python jcxt/js/build_fts_index.py")
    f = sqlite3.connect(f"file:{FTS_DB}?mode=ro", uri=True)
    try:
        n = f.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
        n_pages_db = f.execute("SELECT value FROM meta WHERE key='n_pages'").fetchone()[0]
        n_pages_real = len(iter_md_files())
        ids_db = {r[0] for r in f.execute("SELECT DISTINCT page_id FROM chunks_fts")}
        print(f"对账: _kb_fts.db vs ckzl 实时扫描")
        print(f"  页数:  库 {n_pages_db} / 实扫 {n_pages_real}  "
              f"{'✓' if int(n_pages_db) == n_pages_real else '✗ 不一致（知识库有增删，请重跑本脚本）'}")
        print(f"  块数:  {n} | 覆盖页: {len(ids_db)}")
        samples = ["冻结窗格", "级联参数", "提交属性", "参数面板", "G05", "填报",
                   "决策报表", "Excel转cpt"]
        ok_all = True
        for q in samples:
            expr = fts_expr_prefix(q)
            if not expr:
                continue
            rows = f.execute(
                "SELECT page_id, page_title FROM chunks_fts WHERE chunks_fts MATCH ? "
                "ORDER BY bm25(chunks_fts) LIMIT 5", (expr,)).fetchall()
            status = f"{len(rows)} 命中, 首位 {rows[0][0]}" if rows else "零命中"
            ok_all &= bool(rows)
            print(f"    - {q}: {status}")
    finally:
        f.close()
    print(f"\n{'✅ verify PASS' if ok_all else '❌ verify FAIL'}（{time.time() - started:.1f}s）")
    raise SystemExit(0 if ok_all else 1)


# ---------------------------------------------------------------- 快速试查
def do_query(question, topn=5, full=False):
    """独立快速试查（与 query_kb.py 检索路同逻辑，供建库后冒烟）。"""
    if not FTS_DB.exists():
        raise SystemExit(f"[错误] 找不到 {FTS_DB.name}，请先运行: python jcxt/js/build_fts_index.py")
    f = sqlite3.connect(f"file:{FTS_DB}?mode=ro", uri=True)
    try:
        total = f.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
        expr = fts_expr_prefix(question)
        rows = []
        if expr:
            rows = f.execute(
                "SELECT bm25(chunks_fts), file_path, section_path, chunk_text, "
                "page_id, page_title, keywords, n_sections "
                "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY 1 LIMIT ?",
                (expr, topn)).fetchall()
            if not rows:
                toks = tokenize_for_fts(question).split()
                expr_or = " OR ".join('"%s"' % t for t in toks)
                if expr_or:
                    rows = f.execute(
                        "SELECT bm25(chunks_fts), file_path, section_path, chunk_text, "
                        "page_id, page_title, keywords, n_sections "
                        "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY 1 LIMIT ?",
                        (expr_or, topn)).fetchall()
    finally:
        f.close()
    print(f"问题: {question}")
    print(f"模式: keyword(独立FTS库) | 命中 top {len(rows)} / 共 {total} 个知识块\n")
    for i, (bm, fp, sp, text, pid, ptitle, kws, nsec) in enumerate(rows, 1):
        print(f" {i}. [{-bm:.2f} kw] {fp}  >  {sp}")
        print(f"    页: {pid} | 章节 {nsec} | {ptitle}")
        print(f"    {text.replace(chr(10), ' ')[:120]}")
        if full:
            print("-" * 60)
            print(text)
        print()
    print("提示: 完整入口用 query_kb.py（同库同路），支持 --tree / --page 导航。")


def main():
    setup_console()
    if "--verify" in sys.argv:
        do_verify()
        return
    if "--query" in sys.argv:
        i = sys.argv.index("--query")
        q = sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--") else ""
        if not q:
            raise SystemExit('[错误] --query 需要查询词: python build_fts_index.py --query "冻结窗格"')
        topn = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 5
        do_query(q, topn, "--full" in sys.argv)
        return
    do_build()


if __name__ == "__main__":
    main()
