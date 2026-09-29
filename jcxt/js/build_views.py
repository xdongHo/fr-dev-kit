#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_views.py — 知识库多维目录视图构建器（PageIndex 视图层，2026-09-29）

用途:
    读 jcxt/js/views.yaml（维度规则，外置可改）+ jcxt/data/_tree_index.json（页表），
    生成 jcxt/data/_views.json：三个维度（scenario 场景 / temperature 冷热 / practice 实战）
    共 13 个视图，每视图含 name/desc/rules_summary/pages/count；hot 页附 hot_score（全库
    被引用次数）。物理文件零移动——视图只是页表之上的选择规则投影。

    被引用次数口径: 扫描 ckzl 全部 md + AGENTS.md 内指向 ckzl/*.md 的相对链接（markdown
    链接与 `ckzl/...md` 路径 token 两种形态，去重计数），解析到实际存在的文件才计数。

用法:
    python jcxt/js/build_views.py            # 生成 _views.json
    python jcxt/js/build_views.py --verify   # 自检: 视图页 id 均存在于 tree_index 等
依赖:
    python jcxt/js/build_tree_index.py       # 先有树索引
    查询入口: python jcxt/js/query_kb.py --views / --view 运维维护 / --hot / --cold
"""

# --- console-safe guard (win GBK 控制台) ---
from kb_common import setup_console
setup_console()
# --- end guard ---
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import (DATA_DIR, KB_ROOT, TREE_INDEX, iter_md_files,
                       page_id_of, rel_posix)

VIEWS_YAML = Path(__file__).resolve().parent / "views.yaml"   # 维度规则（外置可改）
VIEWS_INDEX = DATA_DIR / "_views.json"                        # 视图产物


# ================================================================ 极简配置解析
# 只支持 views.yaml 自己的格式：顶层 `key:` + 下一层 `field: value` /
# `field:` + `- item` 块列表；行内列表 [a, b]；# 整行注释。两层缩进，无嵌套映射。
def parse_mini_yaml(text):
    root, cur, curlist = {}, None, None
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            if not s.endswith(":") or ":" != s[-1]:
                raise ValueError(f"第{ln}行: 顶层视图键应以冒号结尾 → {s}")
            cur = s[:-1].strip()
            curlist = None
            if cur in root:
                raise ValueError(f"第{ln}行: 视图 key 重复定义 → {cur}")
            root[cur] = {}
            continue
        if curlist is not None:
            if not s.startswith("- "):
                raise ValueError(f"第{ln}行: 块列表条目应以 '- ' 开头 → {s}")
            curlist.append(s[2:].strip())
            continue
        if ":" not in s:
            raise ValueError(f"第{ln}行: 规则字段应为 `字段: 值` 形态 → {s}")
        k, v = s.split(":", 1)
        k, v = k.strip(), v.strip()
        if not k:
            raise ValueError(f"第{ln}行: 空字段名 → {s}")
        if v == "":                       # 块列表开头
            curlist = []
            root[cur][k] = curlist
        elif v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            root[cur][k] = ([x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                            if inner else [])
        else:
            root[cur][k] = v.strip("'\"")
    return root


# ================================================================ 引用计数
_LINK_RE = re.compile(r"\]\(([^)\s]+?\.md)[^)]*\)")
_TOKEN_RE = re.compile(r"ckzl/[^\s`\)\]\[#,,;；]+\.md")


def _resolve_ref(base_dir, target):
    """链接目标 → ckzl 内实际存在的 posix 路径；候选: 相对源文件目录 → 相对套件根。"""
    t = target.replace("%20", " ").replace("\\", "/")
    while t.startswith("./"):
        t = t[2:]
    for c in (base_dir / t, KB_ROOT / t):
        try:
            rp = c.resolve().relative_to(KB_ROOT.resolve()).as_posix()
        except ValueError:
            continue
        if rp.startswith("ckzl/") and rp.endswith(".md") and (KB_ROOT / rp).is_file():
            return rp
    return None


def _path_to_id(rp):
    return rp[len("ckzl/"):-3] if rp.startswith("ckzl/") else rp[:-3]


def count_refs():
    """ckzl 全部 md + AGENTS.md → Counter{页id: 被引用次数}（自引用不计）。"""
    cnt, n_links = Counter(), 0
    sources = list(iter_md_files()) + [KB_ROOT / "AGENTS.md"]
    for f in sources:
        if not f.exists():
            continue
        try:
            src_pid = page_id_of(f)
        except ValueError:
            src_pid = None  # AGENTS.md 等套件根文件
        text = f.read_text(encoding="utf-8-sig", errors="replace")

        def _link_repl(m):
            nonlocal n_links
            n_links += 1
            rp = _resolve_ref(f.parent, m.group(1))
            if rp:
                pid = _path_to_id(rp)
                if pid != src_pid:
                    cnt[pid] += 1
            return " "  # 剔除已计数的链接目标，避免路径 token 重复计数

        text = _LINK_RE.sub(_link_repl, text)
        for m in _TOKEN_RE.finditer(text):
            rp = _resolve_ref(KB_ROOT, m.group(0))
            if rp:
                pid = _path_to_id(rp)
                if pid != src_pid:
                    cnt[pid] += 1
    return cnt, len(sources), n_links


# ================================================================ 规则求值
def _norm_dir(d):
    d = d.strip().replace("\\", "/").strip("/")
    return d if d.startswith("ckzl/") else "ckzl/" + d


def _match_key(pages_by_key, key):
    """paths/exclude_paths 条目 → 页 id（精确 id / 精确路径 / 路径后缀，全部容忍 .md）。"""
    k = key.strip().replace("\\", "/")
    for suf in (".md", ""):
        kk = (k[:-3] if k.lower().endswith(".md") else k) + suf
        for cand in (kk, "ckzl/" + kk):
            if cand in pages_by_key:
                return pages_by_key[cand]["id"]
    for pid, pg in pages_by_key.items():
        if pg["path"].endswith("/" + k) or pg["path"].endswith(k) or pid.endswith(k):
            return pid
    return None


def _referenced_by(ref_srcs):
    """源文件（AGENTS.md / FR_HEADLESS_GUIDE 等）直链/路径引用的页 id 集合。"""
    ids = set()
    for src in ref_srcs:
        f = KB_ROOT / src.strip().replace("\\", "/")
        if not f.is_file():
            print(f"⚠ referenced_by 源不存在，跳过: {src}")
            continue
        text = f.read_text(encoding="utf-8-sig", errors="replace")

        def _repl(m):
            rp = _resolve_ref(f.parent, m.group(1))
            if rp:
                ids.add(_path_to_id(rp))
            return " "

        text = _LINK_RE.sub(_repl, text)
        for m in _TOKEN_RE.finditer(text):
            rp = _resolve_ref(KB_ROOT, m.group(0))
            if rp:
                ids.add(_path_to_id(rp))
    return ids


def _meta_text(p):
    """keywords_regex 的匹配文本: title + summary + keywords + tags。"""
    return " ".join([p["title"], p.get("summary") or "",
                     " ".join(p.get("keywords") or []),
                     " ".join(p.get("tags") or [])])


def eval_view(spec, pages, pages_by_key, refs):
    """按规则字段求值 → (页id集合, rules_summary)。各规则字段取并集。"""
    sel, rs = set(), []
    dirs = spec.get("dirs") or []
    if dirs:
        for d in dirs:
            dk = _norm_dir(d)
            sel |= {p["id"] for p in pages if p["path"].startswith(dk + "/")}
        rs.append(f"目录前缀×{len(dirs)}")
    paths = spec.get("paths") or []
    if paths:
        hit = [_match_key(pages_by_key, k) for k in paths]
        miss = [k for k, h in zip(paths, hit) if not h]
        sel |= {h for h in hit if h}
        rs.append(f"显式路径×{len(paths)}" + (f"(未命中{len(miss)})" if miss else ""))
    rex = spec.get("path_regex")
    if rex:
        cr = re.compile(rex)
        sel |= {p["id"] for p in pages if cr.search(p["path"]) or cr.search(p["id"])}
        rs.append(f"路径正则/{rex}")
    kex = spec.get("keywords_regex")
    if kex:
        ck = re.compile(kex, re.I)
        sel |= {p["id"] for p in pages if ck.search(_meta_text(p))}
        rs.append(f"元数据正则/{kex}")
    tags = spec.get("tags") or []
    if tags:
        sel |= {p["id"] for p in pages if set(tags) & set(p.get("tags") or [])}
        rs.append(f"标签∈{tags}")
    rbs = spec.get("referenced_by") or []
    if rbs:
        sel |= _referenced_by(rbs)
        rs.append("直链引用源:" + "+".join(rbs))
    tr = spec.get("top_refs")
    if tr:
        n = int(tr)
        top = [pid for pid, _ in sorted(refs.items(), key=lambda x: (-x[1], x[0]))[:n]
               if pid in pages_by_key]
        sel |= set(top)
        rs.append(f"引用top{n}")
    mr = spec.get("min_refs")
    if mr is not None and str(mr) != "" and int(mr) > 0:
        n = int(mr)
        sel |= {pid for pid, c in refs.items() if c >= n and pid in pages_by_key}
        rs.append(f"引用≥{n}")
    ex = spec.get("exclude_paths") or []
    if ex:
        for k in ex:
            pid = _match_key(pages_by_key, k)
            sel.discard(pid)
        rs.append(f"剔除×{len(ex)}")
    comp = spec.get("complement_of") or []
    if comp:
        rs.append("补集(全库−" + ",".join(comp) + ")")
    return sel, "；".join(rs) if rs else "（无规则）"


# ================================================================ 构建
def do_build():
    if not TREE_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {TREE_INDEX}，请先运行: python jcxt/js/build_tree_index.py")
    tree = json.loads(TREE_INDEX.read_text(encoding="utf-8"))
    pages = tree.get("pages", [])
    pages_by_key = {}
    for p in pages:
        pages_by_key[p["id"]] = p
        pages_by_key.setdefault(p["path"], p)
    try:
        cfg = parse_mini_yaml(VIEWS_YAML.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"[错误] 解析 {VIEWS_YAML} 失败: {e}")
    if not cfg:
        raise SystemExit(f"[错误] {VIEWS_YAML} 未定义任何视图")
    refs, n_src, n_link = count_refs()

    views, sets = {}, {}
    # 第一遍: 非补集视图
    for key, spec in cfg.items():
        sel, rs = eval_view(spec, pages, pages_by_key, refs)
        sets[key] = sel
        views[key] = (spec, sel, rs)
    # 温度维度分区铁律: hot 优先级最高，规则型冷/温视图先剔除 hot 成员，
    # 补集视图（warm）再基于剔除后的集合求差，保证 hot/warm/cold 两两不交。
    hotset = sets.get("temperature_hot")
    if hotset:
        for key in sets:
            if (key.startswith("temperature_") and key != "temperature_hot"
                    and not (cfg[key].get("complement_of") or [])):
                sets[key] -= hotset
    # 第二遍: 补集视图（temperature_warm 等，依赖第一遍结果）
    for key, spec in cfg.items():
        if not (spec.get("complement_of") or []):
            continue
        excl = set()
        for other in spec["complement_of"]:
            excl |= sets.get(other, set())
        sel = {p["id"] for p in pages} - excl
        sel, rs2 = _apply_exclude(spec, sel, pages_by_key)
        rs = "；".join(x for x in (eval_view(spec, pages, pages_by_key, refs)[1], rs2) if x)
        sets[key] = sel
        views[key] = (spec, sel, rs)

    out_views = {}
    for key, (spec, sel, rs) in views.items():
        chosen = sorted((pages_by_key[pid] for pid in sel), key=lambda p: p["path"])
        if spec.get("dim") == "temperature" and key.endswith("hot"):
            chosen.sort(key=lambda p: (-refs.get(p["id"], 0), p["path"]))
        out_pages = []
        for p in chosen:
            item = {k: p[k] for k in ("id", "path", "title", "summary", "lines")}
            if spec.get("dim") == "temperature" and key.endswith("hot"):
                item["hot_score"] = refs.get(p["id"], 0)
            out_pages.append(item)
        out_views[key] = {
            "key": key,
            "dim": spec.get("dim", "?"),
            "name": spec.get("name", key),
            "desc": spec.get("desc", ""),
            "rules_summary": rs,
            "external": spec.get("external") or [],
            "count": len(out_pages),
            "pages": out_pages,
        }

    doc = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tree_generated_at": tree.get("generated_at", "?"),
        "page_count": len(pages),
        "ref_scan": {"sources": n_src, "links_resolved": n_link,
                     "pages_referenced": len(refs)},
        "views": out_views,
    }
    VIEWS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    VIEWS_INDEX.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✅ 多维视图完成  {VIEWS_INDEX}")
    print(f"   树索引: {len(pages)} 页（生成于 {doc['tree_generated_at']}）| "
          f"引用扫描: {n_src} 文件 / {n_link} 链接 / {len(refs)} 页被引用")
    print(f"   视图: {len(out_views)} 个")
    cur_dim = None
    for v in out_views.values():
        if v["dim"] != cur_dim:
            cur_dim = v["dim"]
            print(f"   [{cur_dim}]")
        hot = f" (hot_score top: {v['pages'][0]['hot_score']})" if v["pages"] and "hot_score" in v["pages"][0] else ""
        print(f"     {v['key']:<18} {v['name']:<10} {v['count']:>3} 页{hot}")
    print("   下一步: python jcxt/js/query_kb.py --views  或  --view 运维维护")
    return 0


def _apply_exclude(spec, sel, pages_by_key):
    ex = spec.get("exclude_paths") or []
    rs = ""
    if ex:
        for k in ex:
            pid = _match_key(pages_by_key, k)
            sel = sel - {pid} if pid else sel
        rs = f"剔除×{len(ex)}"
    return sel, rs


# ================================================================ 自检
def do_verify():
    if not VIEWS_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {VIEWS_INDEX}，请先运行: python jcxt/js/build_views.py")
    if not TREE_INDEX.exists():
        raise SystemExit(f"[错误] 找不到 {TREE_INDEX}，请先运行: python jcxt/js/build_tree_index.py")
    doc = json.loads(VIEWS_INDEX.read_text(encoding="utf-8"))
    tree = json.loads(TREE_INDEX.read_text(encoding="utf-8"))
    tree_ids = {p["id"] for p in tree.get("pages", [])}
    views = doc.get("views", {})
    ok = True
    print(f"视图: {len(views)} 个 | 全库: {doc.get('page_count')} 页 | "
          f"树索引生成于 {doc.get('tree_generated_at', '?')}")

    # 1) 每个视图页 id 均存在于 tree_index，count 与 pages 一致且非空
    bad_ids, bad_cnt, empty = [], [], []
    for key, v in views.items():
        if v["count"] != len(v["pages"]):
            bad_cnt.append(key)
        if v["count"] == 0:
            empty.append(key)
        for p in v["pages"]:
            if p["id"] not in tree_ids:
                bad_ids.append(f"{key}:{p['id']}")
    ok &= not bad_ids and not bad_cnt and not empty
    print(f"① 页 id 存在性/计数一致性: {'✓' if not (bad_ids or bad_cnt) else '✗'}"
          + (f" 异常id={bad_ids[:5]} 计数={bad_cnt}" if (bad_ids or bad_cnt) else "")
          + (f" ⚠ 空视图={empty}" if empty else ""))

    # 2) hot 页均带 hot_score 且分数非负
    hotv = views.get("temperature_hot", {})
    noscore = [p["id"] for p in hotv.get("pages", []) if "hot_score" not in p or p["hot_score"] < 0]
    ok &= not noscore
    print(f"② hot 页 hot_score: {'✓ 全部携带且≥0' if not noscore else '✗ ' + str(noscore[:5])}")

    # 3) temperature 三视图两两不交且并集=全库
    dims = ["temperature_hot", "temperature_warm", "temperature_cold"]
    if all(d in views for d in dims):
        idsets = {d: {p["id"] for p in views[d]["pages"]} for d in dims}
        pairs = [(a, b) for i, a in enumerate(dims) for b in dims[i + 1:]]
        inter = [(a, b, idsets[a] & idsets[b]) for a, b in pairs if idsets[a] & idsets[b]]
        union = set().union(*idsets.values())
        cover_ok = union == tree_ids
        ok &= not inter and cover_ok
        print(f"③ 冷热分区: {'✓ 两两不交且覆盖全库' if not inter and cover_ok else '✗'}"
              + (f" 重叠={[(a, b, len(s)) for a, b, s in inter]}" if inter else "")
              + ("" if cover_ok else f" 未覆盖 {len(tree_ids - union)} 页"))
    else:
        print("③ 冷热分区: - 跳过（缺 temperature 视图）")

    # 4) 场景/实战视图抽样
    for key in ("scenario_ops", "practice_flow_f"):
        if key in views:
            v = views[key]
            sample = "、".join(p["id"].rsplit("/", 1)[-1] for p in v["pages"][:3])
            print(f"④ 抽样 {key}: {v['count']} 页（{sample} …）")
    print(f"\n{'✅ verify PASS' if ok else '❌ verify FAIL'}")
    raise SystemExit(0 if ok else 1)


def main():
    setup_console()
    ap = argparse.ArgumentParser(
        description="知识库多维视图构建器（views.yaml 规则 → _views.json）")
    ap.add_argument("--verify", action="store_true", help="自检 _views.json")
    args = ap.parse_args()
    if args.verify:
        do_verify()
    else:
        raise SystemExit(do_build())


if __name__ == "__main__":
    main()
