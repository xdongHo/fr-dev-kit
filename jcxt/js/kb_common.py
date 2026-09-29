#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb_common.py — 无向量检索三件套（build_fts_index / build_tree_index / query_kb）共享底座。

2026-09-29 PageIndex 改造：向量路（embedding / vec0 / 余弦回退）整体归档到
~/.fr_dev_kit/kit_archive/removed_kb_20260929/jcxt/js/，本模块只保留纯本地能力：
  1. CJK bigram FTS5 分词（tokenize_for_fts，与被归档的 build_vector_index 逐字一致）
  2. KB_INDEX 头解析（<!-- KB_INDEX: {...} --> JSON 注释形态）
  3. Markdown 章节切分（## / ### / ####，代码围栏感知，带行号）
  4. ckzl 知识文件收集（跳过 _ 开头文件/目录与非 md）

不触网、不依赖任何 key、不读任何 .db 以外的二进制。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent          # jcxt/js/
DATA_DIR = TOOL_DIR.parent / "data"                 # jcxt/data/
KB_ROOT = TOOL_DIR.parent.parent                    # 套件根目录
CKZL_ROOT = KB_ROOT / "ckzl"                        # 知识库根
FTS_DB = TOOL_DIR / "_kb_fts.db"                    # FTS5 关键词库（本目录唯一写目标）
TREE_INDEX = DATA_DIR / "_tree_index.json"          # 树索引产物


def setup_console():
    """win GBK 控制台安全输出（UTF-8 + replace，缺 reconfigure 时静默跳过）。"""
    for s in (sys.stdout, sys.stderr):
        if s is not None and hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


# ---------------------------------------------------------------- FTS5 分词
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+")


def tokenize_for_fts(text):
    """FTS5 写入/查询共用的预分词：CJK 连续段展开 bigram，ASCII 字母数字段整词小写化。

    背景: FTS5 默认 unicode61 把整段连续中文当作单个 token，"冻结"查不到"冻结表头"。
    bigram 后 "冻结 表头 冻结表头" 逐对成词，BM25 区分度与子串召回都正常。
    单个 CJK 字符（孤字）直接保留，保证 G05 / A-AD 精确 token 也可命中。
    """
    out = []
    for m in _TOKEN_RE.finditer(text):
        s = m.group(0)
        if s[0] >= "\u4e00":
            if len(s) == 1:
                out.append(s)
            else:
                out.extend(s[i:i + 2] for i in range(len(s) - 1))
        else:
            out.append(s.lower())
    return " ".join(out)


def fts_match_expr(query):
    """自然语言查询 → FTS5 MATCH 表达式（token 双引号包裹后 AND 连接）。空查询返回 None。"""
    toks = tokenize_for_fts(query).split()
    if not toks:
        return None
    return " ".join('"%s"' % t for t in toks)


def fts_expr_prefix(question):
    """查询侧补丁（沿袭 BG-VA-06）：单字 CJK token 生成 prefix 查询 '"字" *'。
    索引侧 CJK 连续段只产 bigram，单字查询 token 在索引中几乎不存在 → AND 必零召回；
    prefix 查询命中以该字开头的 bigram（如 冻 → 冻结/冻结表头）。其余 token 保持原样。"""
    toks = tokenize_for_fts(question).split()
    if not toks:
        return None
    return " ".join('"%s" *' % t if len(t) == 1 and t >= "\u4e00" else '"%s"' % t
                    for t in toks)


# ---------------------------------------------------------------- KB_INDEX 头
def parse_kb_index(content):
    """解析文件头部 <!-- KB_INDEX: {...} --> 注释块，返回 dict（无则各字段取默认空值）。

    兼容 BOM；JSON 损坏时静默返回空结构（不中断建库）。"""
    body = content.lstrip("\ufeff")
    meta = {}
    m = re.search(r"KB_INDEX:\s*(\{.*?\})\s*-->", body, re.S)
    if m:
        try:
            meta = json.loads(m.group(1)) or {}
        except Exception:
            meta = {}

    def _slist(v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        if isinstance(v, (list, tuple)):
            return [str(x).strip() for x in v if str(x).strip()]
        return [str(v).strip()]

    return {
        "title": str(meta.get("title") or "").strip(),
        "stage": str(meta.get("stage") or "").strip(),
        "tags": _slist(meta.get("tags")),
        "keywords": _slist(meta.get("keywords")),
        "summary": str(meta.get("summary") or "").strip(),
    }


# ---------------------------------------------------------------- 文件收集
# 沿袭被归档 build_vector_index 的排除规则（comm 版 ckzl 实际生效子集），
# 另按本任务铁律：任何路径段以 _ 开头一律跳过。
EXCLUDE_DIRS = {"_archive", "_studies", "__pycache__", ".git", "node_modules",
                "references_preview", "_qa_fixtures"}
# GVS1 批次05 方案C 沿袭：fr10_deep_learn/docs 子树与 fr11_knowledge 同源重复约 88%，不入库
EXCLUDE_PREFIXES = ("ckzl/lc/fr10_deep_learn/docs/",)


def rel_posix(p: Path) -> str:
    """相对套件根的 posix 路径，如 ckzl/lc/03_报表构建.md。"""
    return p.relative_to(KB_ROOT).as_posix()


def page_id_of(p: Path) -> str:
    """页 id = 相对 ckzl 的路径去 .md，如 lc/03_报表构建。"""
    return p.relative_to(CKZL_ROOT).with_suffix("").as_posix()


def iter_md_files():
    """收集 ckzl/ 全部待索引 .md，返回 [Path]（按路径排序）。

    跳过：非 md；文件名或任一路径段以 _ 开头；EXCLUDE_DIRS 命名目录；EXCLUDE_PREFIXES 子树。
    """
    files = []
    for p in CKZL_ROOT.rglob("*.md"):
        parts = p.relative_to(KB_ROOT).parts
        if any(part.startswith("_") for part in parts):
            continue
        if any(part in EXCLUDE_DIRS for part in parts):
            continue
        if rel_posix(p).startswith(EXCLUDE_PREFIXES):
            continue
        files.append(p)
    files.sort(key=lambda x: rel_posix(x))
    return files


# ---------------------------------------------------------------- Markdown 章节切分
_HEADING_RE = re.compile(r"^(#{1,4}) (.+?)\s*$")


def split_sections(content):
    """按 #/##/###/#### 切分章节（代码围栏 ``` ~~~ 内的行不参与标题解析）。

    返回 [(h1, sec_title, line_no, body_text)]：
      h1        文件首个一级标题（无则空串）
      sec_title 当前最近的小节标题（无则空串）
      line_no   该章起始标题所在行（1 基；正文块则为其起始行）
      body_text 归属该节的正文（不含标题行本身；KB_INDEX 注释等标题前杂散行归属行 1 块）
    """
    h1, cur_title, cur_lines, cur_line = "", "", [], 1
    sections = []
    in_fence = False

    def flush(end_default):
        nonlocal cur_lines, cur_line
        if not cur_lines:
            return
        text = "\n".join(cur_lines).strip()
        if text:
            section = f"{h1} / {cur_title}" if (cur_title and h1) else (cur_title or h1)
            sections.append((h1, section, cur_line, text))
        cur_lines = []
        cur_line = end_default

    for i, line in enumerate(content.split("\n"), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            cur_lines.append(line)
            continue
        if in_fence:
            cur_lines.append(line)
            continue
        m = _HEADING_RE.match(s)
        if m:
            flush(i)
            if m.group(1) == "#":
                h1 = m.group(2).strip()
                cur_title = ""
            else:
                cur_title = m.group(2).strip()
            cur_line = i
        else:
            if not cur_lines:
                cur_line = i
            cur_lines.append(line)
    flush(len(content.split("\n")) + 1)
    return sections


def list_headings(content):
    """树索引用：列出全部标题 [(line_no(1基), 原样标题行含#号)]，代码围栏内忽略。"""
    out = []
    in_fence = False
    for i, line in enumerate(content.split("\n"), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _HEADING_RE.match(s):
            out.append((i, s))
    return out


# ---------------------------------------------------------------- 超长块切分（FTS 建库用）
def split_long(text, max_chars=1200, overlap_chars=150):
    """超长块按段落贪心切分，相邻块保留尾部重叠（沿袭被归档 build_vector_index.split_long）。"""
    if len(text) <= max_chars:
        return [text]
    ov = min(overlap_chars, max_chars // 4)

    # 1) 段落单元化：单段超限（代码块/表格无空行）按行硬切，超长行按字符斩
    units = []
    for p in (x.strip() for x in text.split("\n\n")):
        if not p:
            continue
        if len(p) <= max_chars:
            units.append(p)
            continue
        cur = ""
        for ln in p.split("\n"):
            while len(ln) > max_chars:
                if cur:
                    units.append(cur)
                    cur = ""
                units.append(ln[:max_chars])
                ln = ln[max_chars:]
            cand = (cur + "\n" + ln) if cur else ln
            if len(cand) > max_chars and cur:
                units.append(cur)
                cur = ln
            else:
                cur = cand
        if cur:
            units.append(cur)

    # 2) 贪心合并 + 上一块尾部重叠
    out, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 2 > max_chars:
            out.append(cur.strip())
            tail = cur[-ov:] if ov and len(cur) > ov else (cur if ov else "")
            if tail and len(tail) + len(u) + 2 <= max_chars:
                cur = tail + "\n" + u
            else:
                cur = u
        else:
            cur = (cur + "\n\n" + u) if cur else u
    if cur.strip():
        out.append(cur.strip())
    return out
