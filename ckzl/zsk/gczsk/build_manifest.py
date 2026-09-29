# -*- coding: utf-8 -*-
"""build_manifest.py — kit 脚本工具清单(registry 式 manifest)生成器（P1-7）。

背景（07-审计启示 P1-7）: 对齐 MCP Registry 思路, 为 kit 内 python 脚本工具建立
机器可读清单: 名称/路径/用途/哈希/大小/mtime, 供 kernel 只驻"精简工具目录"、
脚本正文按需加载, 并为"描述版本化+哈希钉住"防 rug-pull 打底。

用法（仓库根执行）:
  python ckzl/zsk/gczsk/build_manifest.py                 # 重建 script_manifest.json
  python ckzl/zsk/gczsk/build_manifest.py --check        # 校验清单与现状是否一致(drift 检测)
  python ckzl/zsk/gczsk/build_manifest.py --dirs a,b     # 指定扫描目录（仓库内相对路径, 逗号分隔; 拒绝绝对路径与含 .. 目录）

扫描范围(默认): 仓库根目录顶层 *.py(不递归) + kfgj/fzpy/ + ckzl/zsk/gczsk/ +
与 *.bak*。资料型目录(ckzl/frapi/ex 等)不扫——清单只收"工具脚本"。

退出码: 0=正常(check=无漂移)  1=check 有漂移(哈希/doc)  2=用法错误(--dirs 非法/写模式空扫描拒写)
"""
import argparse
import hashlib
import io
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ckzl/zsk/gczsk/ 的上级 = 仓库根
OUT = os.path.join(KIT, "ckzl/zsk/gczsk", "script_manifest.json")
DEFAULT_DIRS = ["(root)", "kfgj/fzpy", "ckzl/zsk/gczsk", "jcxt/js", "dsl", "evals"]
SKIP_PARTS = {"__pycache__", ".git", "build", "_archive", "_parsed", "_runs"}
MANIFEST_VER = 1


def _mkitem(full, d):
    rel = os.path.relpath(full, KIT).replace("\\", "/")
    raw = open(full, "rb").read()
    head = raw[:4000].decode("utf-8", errors="replace")
    doc = ""
    if '"""' in head:
        seg = head.split('"""', 2)
        if len(seg) >= 2:
            doc = " ".join(seg[1].split())[:160]
    return {"name": os.path.basename(full)[:-3], "path": rel, "dir": d,
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()[:16],
            "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full))),
            "doc": doc, "has_argparse": ("argparse" in head) or ("sys.argv" in head)}


def scan(dirs):
    items = []
    for d in dirs:
        base = KIT if d == "(root)" else os.path.join(KIT, d)
        if not os.path.isdir(base):
            # BG-EV-04: 未知/不存在目录不再静默跳过
            print("[WARN] 目录不存在, 跳过: %r" % d)
            continue
        if d == "(root)":
            for fn in sorted(os.listdir(base)):
                full = os.path.join(base, fn)
                if os.path.isfile(full) and fn.endswith(".py") and ".bak" not in fn.lower():
                    try:
                        items.append(_mkitem(full, d))
                    except OSError:
                        pass
            continue
        for root, ds, fs in os.walk(base):
            ds[:] = [x for x in ds if x not in SKIP_PARTS and not x.startswith(".")]
            for fn in sorted(fs):
                if not fn.endswith(".py") or ".bak" in fn.lower():
                    continue
                full = os.path.join(root, fn)
                try:
                    items.append(_mkitem(full, d))
                except OSError as e:
                    items.append({"name": fn[:-3], "dir": d, "error": repr(e)})
    items.sort(key=lambda x: x.get("path", ""))
    return items


def main():
    ap = argparse.ArgumentParser(description="kit 脚本工具 manifest 生成器(P1-7)")
    ap.add_argument("--check", action="store_true", help="校验现有清单是否与现状一致")
    ap.add_argument("--dirs", default=None, help="逗号分隔的扫描目录, (root)=仓库根顶层")
    a = ap.parse_args()

    dirs = [x.strip() for x in a.dirs.split(",")] if a.dirs else DEFAULT_DIRS
    # BG-EV-04: 拒绝空条目/绝对路径/含 .. 的目录, 防清单被仓库外路径污染或手误清零
    bad_dirs = [d for d in dirs
                if not d or (d != "(root)" and (os.path.isabs(d) or ".." in d.replace("\\", "/").split("/")))]
    if bad_dirs:
        print("用法错误: --dirs 仅接受仓库内相对目录(逗号分隔), 拒绝空条目/绝对路径/含 ..: %s"
              % "; ".join(repr(x) for x in bad_dirs))
        return 2
    items = scan(dirs)
    if a.check:
        if not os.path.isfile(OUT):
            print("清单不存在: %s (先不带 --check 跑一次生成)" % OUT)
            return 2
        # BG-EV-09: utf-8-sig 抗外部编辑器保存带入的 BOM
        old = json.load(io.open(OUT, encoding="utf-8-sig"))
        old_by_path = {x.get("path"): x for x in old.get("scripts", [])}
        new_by_path = {x.get("path"): x for x in items if "path" in x}
        old_map = {p: x.get("sha256", "") for p, x in old_by_path.items()}
        new_map = {p: x.get("sha256", "") for p, x in new_by_path.items()}
        added = sorted(set(new_map) - set(old_map))
        removed = sorted(set(old_map) - set(new_map))
        changed = sorted(p for p in set(new_map) & set(old_map) if new_map[p] != old_map[p])
        # BG-EV-09: doc(docstring 摘要)漂移单列计数(哈希未变的纯描述改动原先完全不设防)
        doc_drift = sorted(p for p in set(new_map) & set(old_map)
                           if p not in changed
                           and new_by_path[p].get("doc", "") != old_by_path[p].get("doc", ""))
        print("manifest check: 共 %d 现役脚本 | 新增 %d | 删除 %d | 哈希漂移 %d | doc 漂移 %d"
              % (len(new_map), len(added), len(removed), len(changed), len(doc_drift)))
        for tag, lst in (("新增", added), ("删除", removed), ("漂移", changed), ("doc漂移", doc_drift)):
            for pth in lst[:15]:
                print("  [%s] %s" % (tag, pth))
        return 1 if (added or removed or changed or doc_drift) else 0

    if not items and dirs:
        # BG-EV-04: 写模式空扫描拒写, 防 --dirs 手误把 manifest 覆盖成 count=0
        print("拒绝写入: 本次扫描 0 项且 --dirs 非空, 疑似手误(分隔符应为逗号). manifest 未改动.")
        return 2

    payload = {
        "manifest_version": MANIFEST_VER,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "generator": "ckzl/zsk/gczsk/build_manifest.py (P1-7)",
        "scan_dirs": dirs,
        "count": len(items),
        "scripts": items,
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("manifest 已生成: %s (脚本 %d 个)" % (os.path.relpath(OUT, KIT), len(items)))
    for x in items[:5]:
        print("  e.g. %-30s %-8s %s" % (x.get("path", "?"), x.get("sha256", "")[:8], (x.get("doc") or "")[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
