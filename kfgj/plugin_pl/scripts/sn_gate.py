#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
sn_gate.py — 插件开发工艺流水线机器闸门 v1.1（pipeline_v1 / SN-12 总闸）
对插件工程目录跑自动化检查，退出码对齐 kit 口径：0=通过 / 1=有 FAIL / 2=仅 WARN。
用法:
  python sn_gate.py --config <工程>\sn_gate.config.json [--report <报告.md>] [--root <覆盖工程根>]
检查项编号与《03_标准节点包》一一对应（C01-C12），文档见 SN-03/SN-04/SN-06/SN-11。
仅用标准库；只读检查器，不修改工程任何文件。
"""
import argparse, json, os, re, sys, datetime, xml.etree.ElementTree as ET

FAIL, WARN = "FAIL", "WARN"

def scan_files(root, exts, skip_dirs=("build", "dist", "classes", "test-classes", "node_modules", "__pycache__", ".git")):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in skip_dirs]
        for fn in fns:
            if fn.lower().endswith(exts):
                yield os.path.join(dp, fn)

def read_text(p, limit=2_000_000):
    try:
        with open(p, "rb") as f:
            return f.read(limit).decode("utf-8", errors="ignore")
    except OSError:
        return ""

class Gate:
    def __init__(self):
        self.rows = []
    def add(self, cid, name, status, detail):
        self.rows.append((cid, name, status, detail))
    def fail(self, cid, name, detail): self.add(cid, name, FAIL, detail)
    def warn(self, cid, name, detail): self.add(cid, name, WARN, detail)
    def ok(self, cid, name, detail):   self.add(cid, name, "PASS", detail)
    @property
    def code(self):
        return 1 if any(r[2] == FAIL for r in self.rows) else (2 if any(r[2] == WARN for r in self.rows) else 0)

def main():
    ap = argparse.ArgumentParser(description="插件工艺流水线机器闸门 (SN-12)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--root", default=None, help="覆盖配置中的 plugin_root")
    ap.add_argument("--report", default=None, help="Markdown 报告输出路径")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    root = args.root or cfg.get("plugin_root") or os.path.dirname(os.path.abspath(args.config))
    root = os.path.abspath(root)
    src = os.path.join(root, cfg.get("src", "src"))
    g = Gate()
    now = datetime.date.today().isoformat()

    px = os.path.join(root, cfg.get("plugin_xml", "plugin.xml"))

    # C01 plugin.xml 存在 (SN-03)
    if not os.path.isfile(px):
        g.fail("C01", "plugin.xml 存在", f"未找到 {px}")
        px_tree = px_data = None
    else:
        g.ok("C01", "plugin.xml 存在", px)
        raw = open(px, "rb").read()
        # C02 无 BOM (SN-03 四道门)
        if raw[:3] == b"\xef\xbb\xbf":
            g.fail("C02", "plugin.xml 无 BOM", "检测到 UTF-8 BOM——FR 装载解析会失败")
        else:
            g.ok("C02", "plugin.xml 无 BOM", "utf-8 无 BOM")
        px_data = raw.decode("utf-8", errors="ignore")
        try:
            px_tree = ET.fromstring(px_data)
        except ET.ParseError as e:
            g.fail("C02", "plugin.xml 良构", f"XML 解析失败: {e}")
            px_tree = None

    ver = None
    if px_tree is not None:
        vid = (px_tree.findtext("id") or "").strip()
        ver = (px_tree.findtext("version") or "").strip()
        active = (px_tree.findtext("active") or "").strip().lower()
        jartime = (px_tree.findtext("jartime") or "").strip()
        # C03 关键字段 + jartime 下限 (SN-03 四道门)
        probs = []
        if not vid: probs.append("缺 <id>")
        if not ver: probs.append("缺 <version>")
        if active != "yes": probs.append(f"<active>={active or '缺'} (应 yes)")
        if not re.match(r"\d{4}-\d{2}-\d{2}", jartime):
            probs.append("<jartime> 缺失或格式错")
        elif jartime < "2024-01-01":
            probs.append(f"<jartime>={jartime} 早于 2024-01-01 (FR10 装载门)")
        if probs:
            g.fail("C03", "plugin.xml 关键字段/四道门", "；".join(probs))
        else:
            g.ok("C03", "plugin.xml 关键字段/四道门", f"id={vid} ver={ver} jartime={jartime}")
        # C04 扩展点 class 源文件存在 (SN-03)
        missing = []
        if os.path.isdir(src):
            for el in px_tree.iter():
                cls = el.get("class")
                if cls and el.tag in ("SystemOptionProvider", "ControllerRegisterProvider", "HttpHandlerProvider",
                                       "MenuHandler", "JavaScriptFileHandler", "lifecycle-monitor",
                                       "function-recorder", "AbstractProvider", "Provider"):
                    rel = cls.replace(".", "/") + ".java"
                    if not os.path.isfile(os.path.join(src, rel)):
                        missing.append(f"{el.tag}:{cls}")
        if missing:
            g.fail("C04", "扩展点 class 源文件存在", "未找到: " + ", ".join(missing))
        else:
            g.ok("C04", "扩展点 class 源文件存在", "全部命中 src")

    # C05 前导斜杠 getResourceAsStream (SN-03 资源路径总表 / 台账 P04)
    bad5 = []
    for p in scan_files(src, (".java",)) if os.path.isdir(src) else []:
        for m in re.finditer(r'getResourceAsStream\s*\(\s*"(/[^"]*)"', read_text(p)):
            bad5.append(f"{os.path.relpath(p, root)}: {m.group(1)[:60]}")
    if bad5:
        g.fail("C05", "禁前导斜杠 getResourceAsStream", f"{len(bad5)} 处 (FR10 插件类加载器不支持绝对资源路径→资源全 null)；" + " | ".join(bad5[:5]))
    else:
        g.ok("C05", "禁前导斜杠 getResourceAsStream", "0 处")

    # C06 ScriptPath/StylePath 斜杠形式 (SN-03 / 台账 P04)
    bad6 = []
    for p in scan_files(src, (".java",)) if os.path.isdir(src) else []:
        t = read_text(p)
        for m in re.finditer(r'(?:ScriptPath|StylePath)\.build\s*\(\s*"([^"]*)"', t):
            v = m.group(1)
            head = v.rsplit("/", 1)[0] if "/" in v else ""
            # v1.1 修复（复刻实践断点-3）：文件名扩展名点号合法（frdoc.js）；只有目录段含点（点形式包名）或前导斜杠才违规
            if v.startswith("/") or "." in head:
                bad6.append(f"{os.path.relpath(p, root)}: {v[:60]} (目录段含点=点形式包名,或前导斜杠)")
    if bad6:
        g.fail("C06", "ScriptPath/StylePath 斜杠形式", f"{len(bad6)} 处；" + " | ".join(bad6[:5]))
    else:
        g.ok("C06", "ScriptPath/StylePath 斜杠形式", "0 处违规")

    # C07 版本一致性 (SN-11 / 台账 P05)
    pairs = cfg.get("version_pairs", [])
    mism, checked = [], 0
    for fname, pat in pairs:
        fp = os.path.join(root, fname)
        t = read_text(fp)
        m = re.search(pat, t)
        checked += 1
        if not m:
            mism.append(f"{fname}: 正则未命中")
        elif ver and m.group(1) != ver:
            mism.append(f"{fname}: {m.group(1)} != plugin.xml {ver}")
    if mism:
        g.fail("C07", "版本多处一致", "；".join(mism))
    else:
        g.ok("C07", "版本多处一致", f"{checked} 对全等" + (f" (={ver})" if ver else ""))

    # C08 改名/残留 grep (SN-03 / 台账 P10)
    for rule in cfg.get("residual_greps", []):
        pat = rule["pattern"]; scope = rule.get("scope", ["src"])
        hits = []
        for s in scope:
            base = os.path.join(root, s)
            exts = tuple(rule.get("exts", ".java .js .xml .html .css".split()))
            for p in scan_files(base, exts) if os.path.isdir(base) else []:
                if re.search(pat, read_text(p)):
                    hits.append(os.path.relpath(p, root))
        if hits:
            g.fail("C08", f"残留检查 [{pat}]", f"{len(hits)} 文件命中: " + ", ".join(hits[:5]))
        else:
            g.ok("C08", f"残留检查 [{pat}]", "0 命中")

    # C09 HttpHandler getPath 单段 (SN-04 / 台账 P09)
    bad9 = []
    for p in scan_files(src, (".java",)) if os.path.isdir(src) else []:
        for m in re.finditer(r'getPath\s*\(\s*\)\s*\{[^}]*?return\s*"([^"]+)"', read_text(p)):
            seg = m.group(1).lstrip("/")  # 容许单个前导斜杠（FR 实测兼容），内部出现 / 即多段=违规
            if "/" in seg or not seg:
                bad9.append(f"{os.path.relpath(p, root)}: \"{m.group(1)}\" 非单段 (多路由走 query)")
    if bad9:
        g.fail("C09", "HttpHandler getPath 单段", "；".join(bad9[:6]))
    else:
        g.ok("C09", "HttpHandler getPath 单段", "0 处违规")

    # C10 POST body 依赖启发 (SN-04 / 台账 P01, WARN 级)
    for p in scan_files(os.path.join(root, cfg.get("web", "web")), (".js",)) if os.path.isdir(os.path.join(root, cfg.get("web", "web"))) else []:
        t = read_text(p)
        if re.search(r'\.(send|fetch)\s*[(]', t) and re.search(r'POST', t) and "Content-Type" not in t:
            g.warn("C10", "POST 显式 Content-Type", f"{os.path.relpath(p, root)}: 疑似 POST 未设 Content-Type (XHR 默认 text/plain→Servlet 不解析 body, 参数放 URL 查询串)")
    if not any(r[0] == "C10" for r in g.rows):
        g.ok("C10", "POST 显式 Content-Type", "未发现风险模式")

    # C11 构建脚本清理策略 (SN-06 / 台账 P06, WARN 级)
    for bs in cfg.get("build_scripts", []):
        bp = os.path.join(root, bs)
        if not os.path.isfile(bp):
            continue
        t = read_text(bp)
        notes = []
        if re.search(r'rm\s+-rf', t): notes.append("rm -rf (改 mv .trash)")
        if re.search(r'Remove-Item[^\n]*-Recurse[^\n]*-Force', t): notes.append("Remove-Item -Recurse -Force (改 mv .trash)")
        if re.search(r'\brd\s+/s\s+/q', t): notes.append("rd /s /q (改 mv .trash)")
        if re.search(r'(del|Remove-Item|rm)[^\n]*\.jar', t): notes.append("删除 *.jar (清理白名单: jar 只保留)")
        if notes:
            g.warn("C11", f"构建清理白名单 [{bs}]", "；".join(notes))
        else:
            g.ok("C11", f"构建清理白名单 [{bs}]", "未发现高风险删除")

    # C12 环境硬编码路径 (WARN)
    markers = cfg.get("env_path_markers", ["C:\\Program Files\\FineReport", "C:\\frjars"])
    hits12 = []
    for p in scan_files(src, (".java", ".js", ".xml")) if os.path.isdir(src) else []:
        t = read_text(p)
        for mk in markers:
            if mk in t:
                hits12.append(f"{os.path.relpath(p, root)}: {mk}")
    if hits12:
        g.warn("C12", "环境路径硬编码", f"{len(hits12)} 处 (改配置/LOCAL_ENV 注入): " + " | ".join(hits12[:5]))
    else:
        g.ok("C12", "环境路径硬编码", "0 处")

    # C13 包声明与目录一致性（复刻实践 2026-09-15 新增：javac 对目录错位零报错，C2 现场发现）
    bad13 = []
    for p in scan_files(src, (".java",)) if os.path.isdir(src) else []:
        m = re.search(r'^\s*package\s+([\w.]+)\s*;', read_text(p, limit=4000), re.M)
        if not m:
            bad13.append(f"{os.path.relpath(p, root)}: 缺 package 声明")
            continue
        rel = os.path.relpath(p, src).replace("\\", "/")
        expect = m.group(1).replace(".", "/") + "/" + os.path.basename(p)
        if rel != expect:
            bad13.append(f"{os.path.relpath(p, root)}: package={m.group(1)} 但实际路径 {rel}")
    if bad13:
        g.fail("C13", "包声明与目录一致", "；".join(bad13[:6]))
    else:
        g.ok("C13", "包声明与目录一致", f"{sum(1 for _ in scan_files(src, ('.java',))) if os.path.isdir(src) else 0} 个文件全部一致")

    # 汇总
    code = g.code
    lines = [f"# sn_gate 报告 — {now}", "",
             f"- 工程根: `{root}`",
             f"- 结果: **{'PASS' if code == 0 else ('FAIL' if code == 1 else 'WARN-ONLY')}** (退出码 {code})",
             f"- PASS {sum(1 for r in g.rows if r[2]=='PASS')} / WARN {sum(1 for r in g.rows if r[2]==WARN)} / FAIL {sum(1 for r in g.rows if r[2]==FAIL)}", "",
             "| 检查项 | 名称 | 结果 | 说明 |", "|---|---|---|---|"]
    for cid, name, st, detail in g.rows:
        esc_detail = detail.replace("|", "\\|")[:300]
        lines.append(f"| {cid} | {name} | {st} | {esc_detail} |")
    lines += ["", "> 退出码口径：0=通过 / 1=有 FAIL / 2=仅 WARN（与 fr_check/kfgj/guard.py 一致）。检查项文档见 kfgj/plugin_pl/03_标准节点包/。"]
    out = "\n".join(lines)
    print(out)
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    sys.exit(code)

if __name__ == "__main__":
    main()
