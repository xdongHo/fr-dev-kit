#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kfgj/check_refs.py — fr_dev_kit v2 全库引用完整性检查器（G05 闸门实现件）
======================================================================

扫描全部 .md 指南中引用的库内路径（Markdown 链接 / 反引号路径 / ``根目录 X``），
判定目标是否真实存在。断链 = 指南指令直达死路 = "配置项不被执行"的直接来源。

判定分级:
    FAIL(断链)   库内核心目录(ckzl/lc/ckzl/gzjd/...)下指向不存在的文件,
                 或裸 .md 知识文件全库无此名, 或「根目录 X」不在根目录
    WARN(已声明) 指向 ckzl/bb/外部依赖与归档声明.md 声明的外部工作区(frs 临时归档/
                 reportlets 工程路径/D 盘学习区等) —— 环境相关, 不判失败
    WARN(环境)   绝对路径本机不存在
    SKIP         占位符 / URL / doc-编号 / 代码片段 / 省略号缩写 /
                 evals/fixtures/link_check 断链夹具(故意断链, E-LINKCHK-FIXTURE 依赖)

用法:
    python kfgj/check_refs.py             # 全库检查; 断链时退出码 1
    python kfgj/check_refs.py --warn-only # 只列问题不影响退出码
    python kfgj/check_refs.py --no-baseline           # 忽略基线(治理前原始口径)
    python kfgj/check_refs.py --baseline <其他.json>   # 指定基线文件(缺省=G05_BASELINE_PATH)
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
import os
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 脚本位于 kfgj/，根目录上移一层

# --- G05 断链基线(A15 泳道增量 2026-09-15; 仅豁免登记过的已知噪声, 不改判定逻辑) ---
# 基线文件为 JSON: {"entries": [{"src": 相对路径, "tok": 断链目标, "line": 行号(可省=任意行), "type"/"note": 定性}]}
# 匹配到的 FAIL 降级为「基线豁免」单列展示, 不计入退出码; 删除基线条目或 --no-baseline 即完全回滚。
G05_BASELINE_PATH = os.path.join(
    KIT_ROOT, "kfgj", "evals", "fixtures", "link_check", "g05_baseline.json")


def load_baseline(path=None):
    """装载断链基线。返回 {(norm_src, norm_tok, line或None): note}；文件缺失/损坏返回空(不阻塞闸门)。"""
    p = path or G05_BASELINE_PATH
    try:
        import json
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = {}
        for e in data.get("entries", []):
            key = (norm(str(e.get("src", ""))), norm(str(e.get("tok", ""))),
                   e.get("line") if isinstance(e.get("line"), int) else None)
            out[key] = "%s: %s" % (e.get("type", "known-noise"), e.get("note", ""))
        return out
    except Exception:
        return {}

EXCLUDE_DIRS = {
    "FR_HEADLESS_GUIDE_Ver历史备份", "_archive", "__pycache__", ".git",
    ".claude", "文档语料", "_runs",
    "作战工作区",  # 2026-09-11: 运行态工作目录(gitignore,不入库),子agent提案/报告为过程文本非知识语料,与 _runs 同口径
}

# evals 断链测试夹具目录(相对库根): 内部断链是故意的, 供kfgj/fzpy/link_check.py
# 与评估用例 E-LINKCHK-FIXTURE 验证检出能力 → 夹具内 .md 不作为被扫描指南, 指向夹具的引用判 SKIP
LINKCHECK_FIXTURE_PREFIX = "evals\\fixtures\\link_check"

# 库内核心目录：这些前缀下的文件引用必须真实存在（FAIL 级）
KIT_CORE_DIRS = {
    "ckzl/lc", "ckzl/gzjd", "ckzl/hbfa", "ckzl/zsk/tbcw", "ckzl/zsk/csff",
    "ckzl/zsk/xqfx", "ckzl/zsk/sjfx", "ckzl/zsk/qdjk", "ckzl/zsk/frwd",
    "ckzl/zsk/gczsk", "ckzl/zsk/xtgt", "ckzl/frapi/ex", "ckzl/frapi/doc",
    "ckzl/gf", "kfgj/fzpy", "kfgj/tygs", "kfgj/fr-agent", "kfgj/dsl",
    "kfgj/web_kit", "kfgj/xlyl", "kfgj/evals", "kfgj/patches",
    "jcxt/js", "jcxt/data", "scwj/mb",
}

# 已声明外部工作区前缀（见 ckzl/bb/外部依赖与归档声明.md）→ WARN 级
DECLARED_EXTERNAL_PREFIXES = {
    "临时", "practice", "notes", "reportlets", "webapps", "web-inf", "webroot",
    "doc", "assets", "fr_plugin_learn", "assist", "embedding", "replica",
    "helper", "work", "src", "scripts", "templates", "references",
    "activator_src", "queue", "fr_dev_kit", "fr_dev_kit_v1", "fr_dev_kit_v2",
    "webroot", "resources", "runouts", "docs",
    # 2026-09-14 G05 收口新增(登记于 ckzl/bb/外部依赖与归档声明.md §六):
    "_runs",            # 运行时证据 _runs/<AgentID或役名>/evidence.md, 不入库
    "desktop",          # 本机桌面路径(如 Desktop\示例需求目录\...)
    "fr_dev_kit_v2.1",  # 旧版本库(已被 v3.0 取代, 本机独立目录)
    "fr10_deep_learn",  # Z3 役历史计划路径(未入库, ckzl/bb/外部依赖与归档声明.md §六)
}

# 已声明外部工作区裸文件名（工具脚本，本体在 fr_overnight/practice 等处）
DECLARED_EXTERNAL_BASENAMES = {
    "jar_class_probe.py", "method_bytecode_probe.py", "field_const_probe.py",
    "branch_bytecode_probe.py", "invoke_owner_probe.py", "jar_ref_scan.py",
    "ldc_seq_probe.py", "hot_reload.py", "force_start2.py", "probe_orig.py",
    "probe_rebuild.py", "probe_s_source.py", "install4.py", "enable_plugin.py",
    "probe_states.py", "diag_plugin.py", "dump_errcodes.py", "decompile.py",
    "morning_check.py", "parse_driver.py", "learn_driver.py", "kb_stress_test.py",
    "verify_widget_plugin.py", "check_plugin_pkg.py", "plugin_catalog.py",
    "analyze_bigzip.py", "overnight_driver.py", "build_queue.py",
    "template_diff.py", "batch_snapshot.py", "snapshot_to_kb.py",
    "widen_cols.py", "widen_ci.py", "merge_bak2.py", "gen_bigdata_export.py",
    # fr_overnight 学习产出（内容已并入知识库, 原件在临时归档, 见 临时/README.md）
    "learnings.md", "agents_updates.md", "learnings_java_api.md",
    # demo 期产物（fr_overnight 工作区, 未随库分发）
    "copa_demo图表配置映射.md", "copa_demo_chart_config.md",
    "frm驾驶舱蓝图设计agent.md", "workflow_authority.md",
    # 本地凭据文件（含密码, 永不入库, 见 kfgj/env.md §5/§6 凭据纪律）
    "本机外置凭据文件", "pg_credentials.env", "env_recovery.credentials.md",
    "api热度报告.md", "图表前端配方对比.md",
    # 2026-09-14 G05 收口新增(登记于 ckzl/bb/外部依赖与归档声明.md §六):
    # miaoda 役历史会话工作文件(未入库)
    "_z2_acceptance.md", "_process_log.md", "_验收与巡检台账.md",
    "_lane_report_b2.md", "_lane_report_b4.md",
    # 历史知识卡与会话产物(未入库, ckzl/bb/外部依赖与归档声明.md §六)
    "gaussdb方言差异知识卡_20260905.md",
    "audit_report.md", "change_list.md",
    # 历史计划提案文件(patches/Z3-R*, 未按原名创建)
    "z3-r0-a.md", "z3-r0-b.md", "z3-r0-c.md",
    "z3-r1-a.md", "z3-r1-b.md",
    "z3-r2-a.md", "z3-r2-b.md", "z3-r2-c.md", "z3-r2-d.md",
    "z3-r3-a.md", "z3-r3-b.md",
}

KNOWN_EXT = {".md", ".py", ".js", ".java", ".xml", ".cpt", ".frm", ".sql",
             ".json", ".yaml", ".yml", ".txt", ".cmd", ".sh", ".sqlite"}

PLACEHOLDER_STEMS = {
    "路径", "文件", "模板", "报表", "xxx", "file", "your_path", "path",
    "某文件", "目标文件", "output", "example", "demo", "config",
}

ALLOWLIST = {"local_env.local.md", "config.toml", "agents.yaml",
             "env_recovery.credentials.md"}

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
CMD_PREFIX_RE = re.compile(r"^(python3?|py|pwsh|powershell|node|java|git|curl)\s+", re.I)
FR_KIT_PREFIX_RE = re.compile(r"^fr_dev_kit(_v\d+)?[\\/]", re.I)


def norm(p):
    return p.replace("/", "\\").strip().strip(".").lower()


def has_known_ext(tok):
    root, ext = os.path.splitext(tok)
    return ext.lower() in KNOWN_EXT and root != ""


def is_code_like(t):
    if " " in t:
        return True
    if any(ch in t for ch in "()!=;,:[]"):
        return True
    if t.endswith(".class"):
        return True
    if t.startswith(("com.", "com/", "java.", "java/", "javax.")):
        return True
    return False


def is_skippable(tok_raw):
    t = tok_raw.strip()
    if not t or t.startswith("#"):
        return True
    if "://" in t or t.lower().startswith(("http", "mailto:", "localhost", "\\\\", "//", "/")):
        return True
    if any(ch in t for ch in "<>{}|*?\"'"):
        return True
    if "%" in t:
        return True
    if "..." in t or "…" in t:
        return True
    if re.match(r"^doc-\d+", t, re.I):
        return True
    if re.search(r"[\u4e00-\u9fff]\.(cpt|frm)$", t) and "\\" not in t and "/" not in t:
        pass  # 中文名业务模板占位符仍要走流程, 由 PLACEHOLDER_STEMS/后缀处理
    stem = os.path.splitext(os.path.basename(t.replace("\\", "/")))[0]
    if stem.lower() in PLACEHOLDER_STEMS or "xxx" in stem.lower():
        return True
    if norm(t) in ALLOWLIST:
        return True
    return False


def clean_target(t):
    t = t.split("#", 1)[0]
    try:
        t = urllib.parse.unquote(t)
    except Exception:
        pass
    t = CMD_PREFIX_RE.sub("", t.strip())
    return t.strip().rstrip("。，；、）)」』\"'").strip()


def collect_files():
    mds, all_files = [], set()
    for dirpath, dirnames, filenames in os.walk(KIT_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = norm(os.path.relpath(full, KIT_ROOT))
            all_files.add(rel)
            if fn.lower().endswith(".md"):
                if rel.startswith(LINKCHECK_FIXTURE_PREFIX):
                    continue  # 断链测试夹具: 故意断链, 不作为被扫描指南
                mds.append(full)
    return sorted(mds), all_files


def suffix_hit(tok, real_paths):
    t = norm(tok)
    return any(rp == t or rp.endswith("\\" + t) for rp in real_paths)


def glob_pipeline_shorthand(t):
    """ckzl/lc/NN → ckzl/lc\\NN_*.md 缩写解析。"""
    m = re.match(r"^(pipeline)[\\/](\d{2})(?:-\d{2})?$", t, re.I)
    if not m:
        return False
    base = os.path.join(KIT_ROOT, "pipeline")
    if not os.path.isdir(base):
        return False
    for fn in os.listdir(base):
        if fn.lower().startswith(m.group(2) + "_") and fn.lower().endswith(".md"):
            return True
    return False


def resolve(tok, base_dir, real_paths, root_ctx):
    """返回 (status, msg)。"""
    if os.path.isabs(tok) or re.match(r"^[A-Za-z]:[\\/]", tok) or tok.startswith("~"):
        if os.path.exists(tok):
            return "OK", ""
        return "WARN-ENV", "绝对路径本机不存在(以 kfgj/env.md 为准)"

    t = tok.replace("/", "\\")
    t = FR_KIT_PREFIX_RE.sub("", t)
    if t.startswith(".\\"):
        t = t[2:]
    if not t:
        return "SKIP", ""

    first = norm(t).split("\\", 1)[0]

    def exists_rel(root):
        return os.path.isfile(os.path.join(root, t))

    # 相对 md 所在目录 / 仓库根
    if exists_rel(base_dir) or exists_rel(KIT_ROOT):
        return "OK", ""
    if root_ctx and has_known_ext(t):
        return "FAIL", "标注为根目录文件但不在仓库根目录"

    # ../ 前缀：剥掉后按剩余路径做后缀命中（../X.md 常指库内其它目录同名文件）
    stripped = t
    while stripped.startswith("..\\"):
        stripped = stripped[3:]
    base = os.path.basename(t)

    # 外部工作区前缀 → 已声明 WARN
    if first in DECLARED_EXTERNAL_PREFIXES:
        return "WARN-EXT", "指向已声明外部工作区(ckzl/bb/外部依赖与归档声明.md)"
    if base.lower() in DECLARED_EXTERNAL_BASENAMES:
        return "WARN-EXT", "外部工作区文件(ckzl/bb/外部依赖与归档声明.md)"
    if t.lower().endswith(".agent.md"):
        return "WARN-EXT", "reportlets 侧车文档(*.agent.md, ckzl/bb/外部依赖与归档声明.md §六)"
    if LINKCHECK_FIXTURE_PREFIX in norm(t):
        return "SKIP", "evals 断链测试夹具(E-LINKCHK-FIXTURE 依赖, 不判断链)"

    if glob_pipeline_shorthand(t):
        return "OK", ""

    # 无扩展名：目录/缩写引用不判死(信息量不足), 归 SKIP
    if not has_known_ext(t):
        return "SKIP", ""

    # 有扩展名
    if stripped != t and suffix_hit(stripped, real_paths):
        return "OK", ""
    if first in KIT_CORE_DIRS:
        if suffix_hit(t, real_paths):
            return "OK", ""
        return "FAIL", "库内核心目录下无此文件"
    if base.lower().endswith(".md"):
        # 裸 .md 或非核心目录 .md：知识文件必须全库可寻
        if suffix_hit(t, real_paths):
            return "OK", ""
        return "FAIL", "全库无此知识文件"
    # 其余(裸脚本/产物名/工程内路径)
    if suffix_hit(t, real_paths):
        return "OK", ""
    return "WARN-EXT", "库内无此文件(外部工程/工作区产物)"


def extract_tokens(line):
    seen = set()
    for m in MD_LINK_RE.finditer(line):
        t = clean_target(m.group(2))
        if not t or t in seen:
            continue
        if not (has_known_ext(t) or "/" in t or "\\" in t):
            continue
        seen.add(t)
        yield t, False
    for m in BACKTICK_RE.finditer(line):
        t = clean_target(m.group(1))
        if not t or t in seen:
            continue
        if not (has_known_ext(t) or "/" in t or "\\" in t):
            continue
        pre = line[max(0, m.start() - 12):m.start()]
        root_ctx = "根目录" in pre
        seen.add(t)
        yield t, root_ctx


def main():
    warn_only = "--warn-only" in sys.argv
    no_baseline = "--no-baseline" in sys.argv
    baseline_path = None
    if "--baseline" in sys.argv:
        i = sys.argv.index("--baseline")
        if i + 1 < len(sys.argv):
            baseline_path = sys.argv[i + 1]
    baseline = {} if no_baseline else load_baseline(baseline_path)
    md_files, real_paths = collect_files()

    fails, ext_warns, env_warns, base_hits = [], [], [], []
    for md in md_files:
        rel_md = os.path.relpath(md, KIT_ROOT)
        try:
            with open(md, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:  # noqa: BLE001
            fails.append((rel_md, 0, "(读取失败 %r)" % e, ""))
            continue
        for i, line in enumerate(lines, 1):
            for tok, root_ctx in extract_tokens(line):
                if is_skippable(tok) or is_code_like(tok):
                    continue
                status, msg = resolve(tok, os.path.dirname(md), real_paths, root_ctx)
                if status == "FAIL":
                    note = None
                    if baseline:
                        for (bs, bt, bl), nt in baseline.items():
                            if bs == norm(rel_md) and bt == norm(tok) and bl in (None, i):
                                note = nt
                                break
                    if note is not None:
                        base_hits.append((rel_md, i, tok, note))
                    else:
                        fails.append((rel_md, i, tok, msg))
                elif status == "WARN-EXT":
                    ext_warns.append((rel_md, i, tok))
                elif status == "WARN-ENV":
                    env_warns.append((rel_md, i, tok))

    print("=" * 62)
    print("  fr_dev_kit v2 引用完整性检查")
    print("  扫描 md 文件: %d 个" % len(md_files))
    print("=" * 62)
    if fails:
        print("\n❌ 断链 %d 处(FAIL — 修复后才能过 G05 闸门):" % len(fails))
        cur = None
        for f, ln, tok, msg in fails:
            if f != cur:
                print("  ▸ %s" % f)
                cur = f
            print("     L%-5d %s   %s" % (ln, tok, msg))
    else:
        print("\n✅ 断链 0 处")
    if base_hits:
        print("\n⚖️ 基线豁免 %d 处(已知噪声, 不计退出码; 登记表 %s)"
              % (len(base_hits), os.path.relpath(G05_BASELINE_PATH, KIT_ROOT) if not baseline_path else baseline_path))
        cur = None
        for f, ln, tok, note in base_hits:
            if f != cur:
                print("  ▸ %s" % f)
                cur = f
            print("     L%-5d %s   [%s]" % (ln, tok, note))
    if ext_warns:
        print("\n⚠️ 外部工作区引用 %d 处(已声明, 不判失败; 清单见 ckzl/bb/外部依赖与归档声明.md)" % len(ext_warns))
    if env_warns:
        print("⚠️ 本机绝对路径缺失 %d 处(环境相关)" % len(env_warns))
    print("=" * 62)
    print("  结果: %s   (断链=%d%s)" % ("✅ 通过" if not fails else "❌ 未通过", len(fails),
          "" if not base_hits else " + 基线豁免=%d" % len(base_hits)))
    if warn_only:
        return 0
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
