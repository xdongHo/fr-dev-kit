#!/usr/bin/env python3
"""
kfgj/sync_kb_index.py — 扫描知识库，自动生成 jcxt/data/_kb_index.yaml

用法:
    python kfgj/sync_kb_index.py

输出:
    jcxt/data/_kb_index.yaml  (大模型读取的机器可读索引)

规则:
    1. 扫描所有 .md 文件（排除 ckzl/bb/外部依赖与归档声明.md 和 FR_HEADLESS_GUIDE_Ver历史备份/）
    2. 解析文件顶部的 <!-- KB_INDEX: {...} --> 块提取元数据
    3. 无 KB_INDEX 块的文件从 H1 标题和文件名自动推断元数据
    4. 生成扁平化的知识节点列表 + 统计摘要
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
import json
import os
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

# v2: 中文 Windows 控制台默认 GBK，直接 print ✅ 等 Unicode 会崩溃 → 强制 UTF-8（errors=replace 兜底）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).parent.parent  # 脚本位于 kfgj/，知识库根目录上移一层

# 额外纳入的外部目录（绝对路径, 检索压力测试发现的盲区修复 2026-08-19）
# 2026-08-19 晚: notes 108 篇已整体入库 → ckzl/bb/外部依赖与归档声明.md官方插件逆向笔记/, 外部映射撤销防双重索引
EXTERNAL_DIRS = {}

# 排除目录
EXCLUDE_DIRS = {"_archive", "FR_HEADLESS_GUIDE_Ver历史备份", ".git", "node_modules", "site", "临时",
                "_runs", "__pycache__", ".claude"}  # v2: _runs 是 guard 闸门报告留痕, 非知识
# 排除文件
EXCLUDE_FILES = {"jcxt/data/_kb_index.yaml", "_kb_index.json"}

# KB_INDEX 块正则
KB_INDEX_RE = re.compile(
    r'<!--\s*KB_INDEX:\s*(\{.*?\})\s*-->',
    re.DOTALL
)
H1_RE = re.compile(r'^#\s+(.+)$', re.MULTILINE)

# 目录名 → stage 映射
DIR_STAGE_MAP = {
    "pipeline": "pipeline",
    "kfgj/tygs": "formatting",
    "kfgj/fzpy": "utility-scripts",
    "ckzl/zsk/tbcw": "error-analysis",
    "fr-agent": "gui-tracing",
    "ckzl/frapi/ex": "java-examples",
    "ckzl/frapi/doc": "api-reference",
    "ckzl/zsk/csff": "testing",
    "ckzl/zsk/xqfx": "requirements",
    "ckzl/zsk/sjfx": "data-analysis",
    "ckzl/zsk/frwd": "external-resources",
    "scwj/mb": "output",
    "参考模板": "reference-templates",
    "相关资源离线存储": "offline-resources",
    "ckzl/zsk/qdjk": "frontend",
    "ckzl/zsk/xtgt": "collaboration",
    "ckzl/zsk/xqfx": "requirements",
    "ckzl/zsk/csff": "testing",
    "scwj/mb": "output",
    "参考模板": "reference-templates",
    "ckzl/frapi/doc": "api-reference",
    "ckzl/frapi/ex": "java-examples",
}

# 顶层目录的权威入口 README（供生成 top-level 导航提示）
TOP_README_HINT = {
    "pipeline": "ckzl/lc/README.md",
    "kfgj/tygs": "kfgj/tygs/索引目录.md",
    "kfgj/fzpy": "kfgj/fzpy/README.md",
    "ckzl/zsk/tbcw": "ckzl/zsk/tbcw/README.md",
    "fr-agent": "fr-agent/README.md",
    "ckzl/frapi/doc": "ckzl/frapi/doc/README.md",
    "ckzl/frapi/ex": "ckzl/frapi/ex/README.md",
    "ckzl/zsk/csff": "ckzl/zsk/csff/README.md",
    "ckzl/zsk/xqfx": "ckzl/zsk/xqfx/README.md",
    "ckzl/zsk/sjfx": "ckzl/zsk/sjfx/README.md",
    "ckzl/zsk/frwd": "ckzl/zsk/frwd/资源索引.md",
    "scwj/mb": "scwj/mb/README.md",
    "参考模板": "ckzl/bb/外部依赖与归档声明.mdREADME.md",
    "相关资源离线存储": "相关资源离线存储/README.md",
    "ckzl/zsk/xtgt": "ckzl/zsk/xtgt/README.md",
    "ckzl/zsk/qdjk": "ckzl/zsk/qdjk/README.md",
}


def extract_metadata(filepath: Path, content: str) -> dict:
    """从文件内容提取或推断元数据。"""
    meta = {}

    # 1. 尝试解析 KB_INDEX 块
    m = KB_INDEX_RE.search(content[:2000])
    if m:
        try:
            meta = json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 2. 推断缺失字段
    if "title" not in meta:
        # 从 H1 标题提取
        h1 = H1_RE.search(content)
        meta["title"] = h1.group(1).strip() if h1 else filepath.stem

    if "stage" not in meta:
        try:
            rel = filepath.relative_to(BASE)
            top_dir = str(rel).split(os.sep)[0] if len(rel.parts) > 1 else "root"
            meta["stage"] = DIR_STAGE_MAP.get(top_dir, top_dir)
        except ValueError:
            # 外部目录文件
            for ext_dir, ext_stage in EXTERNAL_DIRS.items():
                try:
                    filepath.relative_to(ext_dir)
                    meta["stage"] = ext_stage
                    break
                except ValueError:
                    continue
            else:
                meta["stage"] = "external"

    if "tags" not in meta:
        meta["tags"] = []

    if "keywords" not in meta:
        # 从标题和文件名提取关键词
        words = re.findall(r'[\u4e00-\u9fff]+|[A-Z][a-z]+|[A-Z]+', meta["title"])
        meta["keywords"] = list(set(words))[:5]

    if "summary" not in meta:
        # 从第一段有意义的正文提取前 80 字
        # 跳过: 标题/注释/表格/引用/代码围栏/导航链接/分隔线/空行
        lines = content.split('\n')
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith(('#', '<!--', '|', '>', '```', '---', '*', '-', '←', '→', '[')):
                continue
            meta["summary"] = line[:80].rstrip()
            break
        else:
            meta["summary"] = ""

    meta["deprecated"] = meta.get("deprecated", False)

    return meta


def scan_file(filepath: Path, base_dir: Path = None) -> dict | None:
    """扫描单个 .md 文件，返回知识节点。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        try:
            content = filepath.read_text(encoding="gbk")
        except Exception:
            return None

    base_dir = base_dir or BASE
    rel_path = str(filepath.relative_to(base_dir)).replace("\\", "/")
    if base_dir != BASE:
        # 外部目录: 加前缀标识来源
        src_label = EXTERNAL_DIRS.get(base_dir, "external")
        rel_path = f"~{src_label}/{rel_path}"
    meta = extract_metadata(filepath, content)
    line_count = content.count('\n') + 1
    file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]

    return {
        "path": rel_path,
        "title": meta["title"],
        "stage": meta["stage"],
        "tags": meta["tags"],
        "keywords": meta["keywords"],
        "summary": meta["summary"],
        "deprecated": meta["deprecated"],
        "lines": line_count,
        "bytes": filepath.stat().st_size,
        "hash": file_hash,
        "has_kb_index": bool(KB_INDEX_RE.search(content[:2000])),
    }


def to_yaml(nodes: list, stats: dict) -> str:
    """手动序列化为可读的 YAML（不依赖 PyYAML）。"""
    lines = []
    lines.append("# 知识库索引 — 由 kfgj/sync_kb_index.py 自动生成，请勿手动编辑")
    lines.append(f"# 最后同步: {stats['generated_at']}")
    lines.append(f"# 大模型读取此文件来定位知识，不要直接读取细节文件")
    lines.append("")
    lines.append(f"version: \"{stats['generated_at'][:10]}\"")
    lines.append(f"total_files: {stats['total_files']}")
    lines.append(f"total_lines: {stats['total_lines']}")
    lines.append(f"total_bytes: {stats['total_bytes']}")
    lines.append("")
    lines.append("stages:")
    for stage, count in sorted(stats["stage_counts"].items()):
        lines.append(f"  {stage}: {count}")
    lines.append("")
    lines.append("nodes:")

    for n in nodes:
        # v3 修复(2026-08-25): title/tags/keywords 内含双引号(如 29 篇标题"最有趣代码片段")会破坏 YAML——统一转义
        def yq(s):
            return str(s).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f"  - path: \"{yq(n['path'])}\"")
        lines.append(f"    title: \"{yq(n['title'])}\"")
        lines.append(f"    stage: {n['stage']}")
        if n["tags"]:
            tags_str = ", ".join(f'"{yq(t)}"' for t in n["tags"])
            lines.append(f"    tags: [{tags_str}]")
        else:
            lines.append(f"    tags: []")
        if n["keywords"]:
            kw_str = ", ".join(f'"{yq(k)}"' for k in n["keywords"])
            lines.append(f"    keywords: [{kw_str}]")
        else:
            lines.append(f"    keywords: []")
        summary_escaped = n["summary"].replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    summary: "{summary_escaped}"')
        lines.append(f"    lines: {n['lines']}")
        if n["deprecated"]:
            lines.append(f"    deprecated: true")
        if n["has_kb_index"]:
            lines.append(f"    has_kb_index: true")
        lines.append("")

    return "\n".join(lines)


def main():
    # 收集所有 .md 文件
    all_files = []  # (filepath, base_dir)
    for filepath in BASE.rglob("*.md"):
        rel = filepath.relative_to(BASE)
        parts = rel.parts
        # 排除
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if filepath.name in EXCLUDE_FILES:
            continue
        all_files.append((filepath, BASE))

    # 外部目录（notes 等）
    for ext_dir, _stage in EXTERNAL_DIRS.items():
        if ext_dir.exists():
            for filepath in ext_dir.rglob("*.md"):
                if filepath.name in EXCLUDE_FILES:
                    continue
                all_files.append((filepath, ext_dir))

    all_files.sort(key=lambda t: str(t[0]))

    # 扫描
    nodes = []
    for f, b in all_files:
        node = scan_file(f, b)
        if node:
            nodes.append(node)

    # 统计
    stage_counts = {}
    total_lines = 0
    total_bytes = 0
    for n in nodes:
        stage_counts[n["stage"]] = stage_counts.get(n["stage"], 0) + 1
        total_lines += n["lines"]
        total_bytes += n["bytes"]

    stats = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": len(nodes),
        "total_lines": total_lines,
        "total_bytes": total_bytes,
        "stage_counts": stage_counts,
    }

    # 生成 YAML
    yaml_str = to_yaml(nodes, stats)

    # 写入
    out_path = BASE / "jcxt" / "data" / "_kb_index.yaml"
    out_path.write_text(yaml_str, encoding="utf-8")

    # 打印摘要
    print(f"✅ 索引已生成: {out_path.name}")
    print(f"   文件数: {stats['total_files']}")
    print(f"   总行数: {stats['total_lines']:,}")
    print(f"   总大小: {stats['total_bytes']:,} bytes ({stats['total_bytes']/1024:.1f} KB)")
    print(f"")
    print(f"   阶段分布:")
    for stage, count in sorted(stage_counts.items(), key=lambda x: -x[1]):
        print(f"     {stage:25s} {count:3d} 文件")

    # 检查无 KB_INDEX 的文件
    no_index = [n for n in nodes if not n["has_kb_index"]]
    if no_index:
        print(f"\n   ⚠️ {len(no_index)} 个文件缺少 KB_INDEX 元数据（已自动推断）:")
        for n in no_index:
            print(f"     {n['path']}")


if __name__ == "__main__":
    main()
