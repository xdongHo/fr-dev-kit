#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link_check.py — fr_dev_kit 知识库断链扫描器（CAR-011, 出处 R65/T14 lychee 等价实现）
====================================================================================

职责: 扫全仓 .md 中的仓库内相对路径引用, 校验目标存在性。**只报告, 不修改任何文档。**
输出清单: 引用文件:行号 → 断链目标; 有断链退出码 1。

提取范围:
    1) Markdown 链接/图片  [](...) 与 ![](...)  的目标
    2) 裸相对路径引用        `路径/文件.md` 形式(含 / 或 \\ 分隔且以 .md 结尾的连续 token)

跳过(不校验):
    - 锚点链接(#开头) / 纯 URL(http: https: mailto: 等带 scheme) / 协议相对(//)
    - 绝对路径(盘符 C:\\ 或以 / ~ 开头)
    - ``` / ~~~ 围栏代码块内的全部内容
    - 目标落在排除目录下的引用(--exclude-dir, 默认含 _runs/ = 会话产物, 生命周期短,
      如 jcxt/data/_kb_index.yaml/AGENTS.md 中对 _runs 的引用默认不判断链; 可用 --exclude-dir 追加)
    - 空目标 []()

解析约定:
    - 围栏代码块=代码块(跳过); 行内反引号 `...` 内的路径仍校验——本仓路由表/指南主体
      即反引号路径, 属有效引用而非代码
    - 相对目标按两个基准解析, 命中任一即算存在: ① 引用文件所在目录 ② 仓库根
      (本仓知识文档混用两种写法, 与 kfgj/check_refs.py 口径一致)
    - 中文路径按 UTF-8 读取; 链接目标 %20 解码、#锚点/#query 剥离; 裸路径 token 同样
      解码 %xx, 且支持向前回拼至多 3 个相邻 token 以还原含空格路径(如 `ckzl/frapi/doc/`)
    - Markdown 链接目标含空格时, 同时尝试"整串"与"首 token"两个候选

用法:
    python kfgj/fzpy/link_check.py                     # 扫全仓(脚本定位仓库根)
    python kfgj/fzpy/link_check.py <目录>              # 扫指定子树(自测用)
    python kfgj/fzpy/link_check.py --json              # JSON 输出(单对象, 无横幅)
    python kfgj/fzpy/link_check.py --exclude-dir 临时  # 追加排除目录名(可重复)

退出码: 0=无断链  1=存在断链  2=参数/根目录错误
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
import json
import os
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 扫描时剪枝的目录名(任意层级); 同时作为"目标落在其下→跳过校验"的前缀
DEFAULT_EXCLUDE_DIRS = {".git", "_runs", "node_modules", "__pycache__"}

# 裸路径 token 的非法字符(空白+常见中英文标点界定符); 注意 / \ . 与 _ 合法(路径分隔/扩展名/文件名常用)
_TOKEN_STOP = set(' \t`*#[]()<>{}"\'|~^，。；：！？、（）《》【】「」〔〕…—·＋－×＝\u3000')

MD_LINK_RE = re.compile(r'!?\[[^\]]*\]\(\s*([^)]*?)\s*\)')
SCHEME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9+.\-]*:')
ABS_RE = re.compile(r'^([A-Za-z]:[\\/]|[\\/]|~)')
FENCE_RE = re.compile(r'^\s{0,3}(`{3,}|~{3,})')


def _clean_link_target(raw):
    """清洗 Markdown 链接目标: 去标题/尖括号/引号, 解码 %xx, 剥 #锚 与 ?query。"""
    t = raw.strip()
    # 去掉尾部 "title" / 'title'
    t = re.sub(r'\s+("[^"]*"|\'[^\']*\')\s*$', '', t)
    if t.startswith('<') and t.endswith('>'):
        t = t[1:-1].strip()
    t = urllib.parse.unquote(t)
    for sep in ('#', '?'):
        i = t.find(sep)
        if i >= 0:
            t = t[:i]
    return t.strip()


def _line_tokens(line):
    """按界定符切一行成 token 列表(保留顺序, 供空格路径回拼)。"""
    out, buf = [], []
    for ch in line:
        if ch in _TOKEN_STOP or ch.isspace():
            if buf:
                out.append(''.join(buf))
                buf = []
        else:
            buf.append(ch)
    if buf:
        out.append(''.join(buf))
    return out


def _bare_md_paths(tokens):
    """从 token 列表筛裸相对路径引用(含分隔符且以 .md 结尾), 返回 (index, norm, display)。"""
    res = []
    for i, tok in enumerate(tokens):
        tok = tok.rstrip('.。')
        if not tok.endswith('.md'):
            continue
        norm = tok.replace('\\', '/')
        if '/' not in norm:      # 要求 路径/文件.md 形式, 同目录裸文件名不判
            continue
        res.append((i, norm, tok))
    return res


def _bare_candidates(idx, tokens):
    """一个裸 .md token 的存在性候选集:
    ① 原样 ② %xx 解码 ③ 向前回拼 1-3 个相邻 token(本仓路径含空格, 如 `ckzl/frapi/doc/`)。
    回拼在命中前一 token 已是 .md 引用时停止, 避免跨引用误拼。"""
    cands = [tokens[idx].rstrip('.。')]
    for k in range(1, 4):
        j = idx - k
        if j < 0 or tokens[j].lower().endswith('.md'):
            break
        cands.append(' '.join(tokens[j:idx + 1]).rstrip('.。'))
    out = []
    for c in cands:
        out.append(c)
        u = urllib.parse.unquote(c)
        if u != c:
            out.append(u)
    return out


def _resolve(target, src_dir, root):
    """返回解析成功的候选路径; 都失败返回 None。
    基准: ① 引用文件所在目录 ② 其父目录(SKILL 包内文档常以包根视角写 notes/x.md)
    ③ 仓库根——命中任一即算存在。"""
    bases = [src_dir, os.path.dirname(src_dir), root]
    cands = []
    for base in bases:
        cands.append(os.path.normpath(os.path.join(base, target)))
    # 链接目标含空格时追加"首 token"候选(非规范写法的兜底)
    if ' ' in target:
        cands.append(os.path.normpath(os.path.join(src_dir, target.split(' ', 1)[0])))
    for p in cands:
        if os.path.exists(p):
            return p
    return None


def _is_skipped_target(norm, exclude_prefixes):
    return any(norm == p or norm.startswith(p + '/') for p in exclude_prefixes)


def scan(root, exclude_dirs, as_json=False):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        if as_json:
            print(json.dumps({"error": "root not found: %s" % root}, ensure_ascii=False))
        else:
            print("[FAIL] 根目录不存在: %s" % root)
        return 2
    exclude_prefixes = {d.replace('\\', '/').strip('/') for d in exclude_dirs}

    broken = []          # {source, line, target, kind}
    n_files = n_refs = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.lower().endswith('.md'):
                continue
            src = os.path.join(dirpath, fn)
            rel_src = os.path.relpath(src, root).replace('\\', '/')
            n_files += 1
            try:
                with open(src, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except OSError:
                continue
            in_fence = False
            fence_mark = ''
            for lineno, line in enumerate(lines, 1):
                m = FENCE_RE.match(line)
                if m:
                    mark = m.group(1)
                    if not in_fence:
                        in_fence, fence_mark = True, mark[0] * 3
                    elif mark[0] == fence_mark[0]:
                        in_fence = False
                    continue
                if in_fence:
                    continue
                targets = []
                for lm in MD_LINK_RE.finditer(line):
                    t = _clean_link_target(lm.group(1))
                    if t:
                        targets.append((t, 'link'))
                line_tokens = _line_tokens(line)
                bare = _bare_md_paths(line_tokens)
                seen = set()
                for t, kind in targets:
                    norm = t.replace('\\', '/')
                    if norm in seen:
                        continue
                    seen.add(norm)
                    n_refs += 1
                    if (norm.startswith('#') or SCHEME_RE.match(norm)
                            or norm.startswith('//') or ABS_RE.match(norm)
                            or not norm.strip('.')):
                        continue
                    if _is_skipped_target(norm, exclude_prefixes):
                        continue
                    if _resolve(t, dirpath, root) is None:
                        broken.append({"source": rel_src, "line": lineno,
                                       "target": norm, "kind": kind})
                for idx, norm, _disp in bare:
                    if norm in seen:
                        continue
                    seen.add(norm)
                    n_refs += 1
                    if SCHEME_RE.match(norm) or norm.startswith('//') or ABS_RE.match(norm):
                        continue
                    if _is_skipped_target(norm, exclude_prefixes):
                        continue
                    if not any(_resolve(c, dirpath, root)
                               for c in _bare_candidates(idx, line_tokens)):
                        broken.append({"source": rel_src, "line": lineno,
                                       "target": urllib.parse.unquote(norm), "kind": "bare"})

    broken.sort(key=lambda b: (b["source"], b["line"], b["target"]))
    if as_json:
        print(json.dumps({"root": root, "scanned_files": n_files,
                          "refs_checked": n_refs, "broken_count": len(broken),
                          "broken": broken}, ensure_ascii=False, indent=1))
    else:
        n_link = sum(1 for b in broken if b["kind"] == "link")
        print("=" * 62)
        print("  link_check 断链扫描  root=%s" % root)
        print("  .md 文件: %d | 引用: %d | 断链: %d (md链接 %d / 裸路径 %d)"
              % (n_files, n_refs, len(broken), n_link, len(broken) - n_link))
        print("  排除目录(不扫源/不校目标): %s" % ", ".join(sorted(exclude_prefixes)))
        print("-" * 62)
        for b in broken:
            print("  %s:%d → %s   [%s]"
                  % (b["source"], b["line"], b["target"],
                     "md链接" if b["kind"] == "link" else "裸路径"))
        if broken:
            print("-" * 62)
            print("  [FAIL] 存在断链 %d 处 (只报告不修改; 修复或登记 ckzl/bb/外部依赖与归档声明.md)" % len(broken))
        else:
            print("  [PASS] 无断链")
        print("=" * 62)
    return 1 if broken else 0


def main():
    ap = argparse.ArgumentParser(description="知识库断链扫描器(只报告不修改)")
    ap.add_argument("root", nargs="?", default=KIT_ROOT,
                    help="扫描根目录(缺省=仓库根)")
    ap.add_argument("--json", action="store_true", help="JSON 输出(仅对象)")
    ap.add_argument("--exclude-dir", action="append", default=[],
                    metavar="目录名", help="追加排除目录名(可重复); 默认已含 .git/_runs/node_modules/__pycache__")
    args = ap.parse_args()
    if args.json and args.root == KIT_ROOT:
        pass  # json 模式无横幅, 由 scan 内保证
    return scan(args.root, set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir), args.json)


if __name__ == "__main__":
    sys.exit(main())
