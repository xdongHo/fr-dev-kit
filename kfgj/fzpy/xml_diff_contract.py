"""
XML 变更白名单校验 — 修改类任务的"改了什么"机检（吸收官方 skill 包 regression_contract 思路）。

场景: 修改模板后, 声明"只改了 X"——本工具把两份 cpt/frm XML 投影成 {路径: 值} 平面,
diff 出全部变化, 白名单(glob)之外还有差异 = 任务越界, 不许交付。
与 file_lock.py 的整文件 md5 互补: md5 回答"变没变", 本工具回答"变了哪些字段"。

用法:
  python xml_diff_contract.py --baseline 原.cpt --candidate 改.cpt \
      --allow "/WorkBook/TableDataMap/TableData[0]#text" \
      --allow "/WorkBook/Report[0]/CellElementList/*"        # glob 可重复

  路径键格式: /根tag[0]/子tag[i]...  后缀 #tag(标签名) #text(元素文本) @属性名
  glob 语法: '[*]'=任意序号段, '*'=任意串, '?'=单字符, 其余字面, 例:
    /WorkBook/Report[0]/*                 该节点下全部子项
    /WorkBook/TableDataMap/TableData[*]@* 任意数据集的任意属性
    /WorkBook/Report[0]/CellElementList[*]/C[*]/O[*]#text  任意单元格富文本

退出码: 0=全部变化在白名单内  1=白名单外存在差异(越界)  2=读取/解析失败
注: 只处理纯 XML cpt/frm; 压缩 cpt(zip) 先解包取包内 XML 再比对。
"""

# --- console-safe guard ---
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def glob_to_re(glob: str):
    """白名单 glob → 正则。语义: '[*]'=任意序号段(如 C[*] 匹配 C[0]/C[13]), '*'=任意串, '?'=单字符, 其余字面。"""
    out, i = [], 0
    while i < len(glob):
        if glob[i:i + 3] == "[*]":
            out.append(r"\[\d+\]")
            i += 3
        elif glob[i] == "*":
            out.append(".*")
            i += 1
        elif glob[i] == "?":
            out.append(".")
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def path_allowed(key: str, globs) -> bool:
    return any(glob_to_re(g).match(key) for g in globs)


def load_root(path: str) -> ET.Element:
    with open(path, "rb") as f:
        head = f.read(4)
    if head[:2] == b"PK":
        raise ValueError(f"{path} 是压缩 cpt(zip): 先解包取包内 XML 再比对")
    return ET.parse(path).getroot()


def xml_projection(root: ET.Element) -> dict:
    """顺序敏感、空白不敏感的 XML 投影: {路径键: 值}。键含 #tag/#text/@attr 三种后缀。"""
    projection = {}

    def visit(element, current_path):
        projection[f"{current_path}#tag"] = element.tag
        text = (element.text or "").strip()
        if text:
            projection[f"{current_path}#text"] = text
        for attr, value in sorted(element.attrib.items()):
            projection[f"{current_path}@{attr}"] = value
        occurrences = {}
        for child in list(element):
            idx = occurrences.get(child.tag, 0)
            occurrences[child.tag] = idx + 1
            visit(child, f"{current_path}/{child.tag}[{idx}]")

    visit(root, f"/{root.tag}[0]")
    return projection


def classify(key: str, before, after) -> str:
    if key.endswith("#tag"):
        return "结构"
    if after is None:
        return "删除"
    if before is None:
        return "新增"
    return "值变"


def compare(baseline_path: str, candidate_path: str, allowed_globs):
    baseline = xml_projection(load_root(baseline_path))
    candidate = xml_projection(load_root(candidate_path))
    changes, rejected = [], []
    for key in sorted(set(baseline) | set(candidate)):
        before, after = baseline.get(key), candidate.get(key)
        if before == after:
            continue
        kind = classify(key, before, after)
        in_scope = path_allowed(key, allowed_globs)
        changes.append({"path": key, "kind": kind, "baseline": before,
                        "candidate": after, "allowed": in_scope})
        if not in_scope:
            rejected.append(key)
    return {
        "status": "passed" if not rejected else "failed",
        "baseline": str(Path(baseline_path).resolve()),
        "candidate": str(Path(candidate_path).resolve()),
        "total_changes": len(changes),
        "rejected_count": len(rejected),
        "changes": changes,
        "allowed_globs": list(allowed_globs),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="XML 变更白名单校验（修改类任务机检）")
    ap.add_argument("--baseline", required=True, help="基线(改前) cpt/frm")
    ap.add_argument("--candidate", required=True, help="候选(改后) cpt/frm")
    ap.add_argument("--allow", action="append", default=[],
                    help="允许变化的路径键 glob，可多次指定")
    ap.add_argument("--json", action="store_true", help="输出完整 JSON(默认人读摘要)")
    args = ap.parse_args()

    try:
        result = compare(args.baseline, args.candidate, args.allow)
    except (OSError, ET.ParseError, ValueError) as e:
        print(f"[FAIL] 读取/解析失败: {e}")
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "passed" else 1

    # 人读摘要
    tag = "✅ PASS" if result["status"] == "passed" else "❌ FAIL"
    print(f"{tag}  变化 {result['total_changes']} 处, 白名单外 {result['rejected_count']} 处")
    for ch in result["changes"]:
        mark = "✔" if ch["allowed"] else "✘"
        b = (ch["baseline"] or "∅")
        a = (ch["candidate"] or "∅")
        b, a = b[:40] + ("…" if len(b) > 40 else ""), a[:40] + ("…" if len(a) > 40 else "")
        print(f"  {mark} [{ch['kind']}] {ch['path']}")
        if ch["kind"] == "值变":
            print(f"       {b!r} → {a!r}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
