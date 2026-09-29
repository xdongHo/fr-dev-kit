#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_check.py — 无服务器kfgj/xlyl验证 · 编排层（backend 可插拔）

链路: 模板(cpt/frm) → [renderer backend] → HTML → 对照 expect_manifest 断言 → JSON 报告

Backends:
  skeleton   纯Python结构预览(默认; 布局骨架HTML, 非引擎渲染, 断言仅供校准)
  manifest   仅生成期望清单(零依赖 dry-run, 不渲染) —— 回归基线/冒烟
  java       独立 headless JVM 渲染 —— ❌ 已判死(探针A: FR初始化链原子耦合,
             FineAssist需Attach API/FinePluginBridge加密/EntityDao需模块链, 见
             probeA_独立JVM渲染_否定结论.md; 槽位保留仅为接口兼容)
  injected   设计器 JVM fr-agent /exec 渲染(主押路线, 探针B验证中)

用法:
  python render_check.py <cpt|frm|目录> [--backend manifest|java|injected]
                         [--out 报告.json] [--html-dir 输出目录] [--timeout 60]
退出码: 0=全过 1=有FAIL 2=环境不可用(backend缺失/超时)
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from expect_manifest import extract_manifest, check_rendered  # noqa: E402


# ── backends ───────────────────────────────────────────────────────────

def backend_manifest(tpl, html_dir, timeout):
    """dry-run: 不渲染, 返回空 HTML → 断言必然 WARN/FAIL。
    用途: manifest 生成 + 断言规则自测 + 批量回归的基线。"""
    return {"ok": False, "reason": "dry-run backend 无渲染产物", "html": None}


def backend_skeleton(tpl, html_dir, timeout):
    """结构预览: preview_skeleton.generate → HTML。
    ⚠ 非引擎渲染(不做数据/公式计算), 断言结果是管线校准而非真实验证。"""
    try:
        import preview_skeleton
        out_html = os.path.join(html_dir, os.path.splitext(os.path.basename(tpl))[0] + ".skeleton.html")
        html = preview_skeleton.generate(tpl)
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        return {"ok": True, "html": out_html, "log": "skeleton 结构预览"}
    except Exception as e:
        return {"ok": False, "reason": f"skeleton 生成失败: {e}", "html": None}


def backend_java(tpl, html_dir, timeout):
    """独立 headless JVM: 调 kfgj/xlyl/java/RenderCLI.jar(Phase 1 交付物)"""
    jar = os.path.join(HERE, "java", "RenderCLI.jar")
    if not os.path.exists(jar):
        return {"ok": False, "reason": f"java backend 未就绪(缺 {jar})", "html": None, "missing": True}
    out_html = os.path.join(html_dir, os.path.splitext(os.path.basename(tpl))[0] + ".html")
    try:
        r = subprocess.run(
            ["java", "-jar", jar, tpl, out_html],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace")
        if r.returncode == 0 and os.path.exists(out_html):
            return {"ok": True, "html": out_html, "log": r.stdout[-2000:]}
        return {"ok": False, "reason": f"exit={r.returncode}: {(r.stderr or r.stdout)[-500:]}",
                "html": out_html if os.path.exists(out_html) else None}
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": f"渲染超时(>{timeout}s)", "html": None, "timeout": True}
    except FileNotFoundError as e:
        return {"ok": False, "reason": f"环境缺 java: {e}", "html": None, "missing": True}


def backend_injected(tpl, html_dir, timeout):
    """设计器 JVM 注入渲染: 经 19000 /exec 跑渲染脚本。
    产物主选 Excel(FR 导出的 .xls 实为 OOXML, 单元格级断言最强);
    模板脚本 injected_render.js (探针B产物演化, __TEMPLATE__/__OUT__ 占位)。"""
    js_tpl = os.path.join(HERE, "injected_render.js")
    if not os.path.exists(js_tpl):
        return {"ok": False, "reason": "injected backend 未就绪(缺 injected_render.js)", "html": None, "missing": True}
    out_xls = os.path.join(html_dir, os.path.splitext(os.path.basename(tpl))[0] + ".json")
    script = open(js_tpl, encoding="utf-8").read()
    # 设计器 JVM 的 CWD ≠ 本进程 CWD → 模板与产物路径必须绝对化
    script = (script
              .replace("__TEMPLATE__", os.path.abspath(tpl).replace("\\", "/"))
              .replace("__OUT__", os.path.abspath(out_xls).replace("\\", "/")))
    try:
        req = json.dumps({"script": script}).encode("utf-8")
        import urllib.request
        r = urllib.request.Request("http://localhost:19000/exec", data=req,
                                   headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("status") == "ok" and os.path.exists(out_xls):
            return {"ok": True, "html": out_xls, "log": str(result.get("result"))[:500]}
        return {"ok": False, "reason": f"exec 失败: {str(result.get('error'))[:400]}", "html": None}
    except Exception as e:
        return {"ok": False, "reason": f"19000 不可达或执行异常: {e}", "html": None, "unreachable": True}


BACKENDS = {"manifest": backend_manifest, "skeleton": backend_skeleton,
            "java": backend_java, "injected": backend_injected}


# ── 主流程 ─────────────────────────────────────────────────────────────

def run_one(tpl, backend, html_dir, timeout):
    entry = {"file": os.path.relpath(tpl), "backend": backend}
    try:
        m = extract_manifest(tpl)
        entry["manifest"] = m
    except Exception as e:
        entry.update(status="FAIL", reason=f"manifest 提取失败: {e}")
        return entry

    t0 = time.time()
    rend = BACKENDS[backend](tpl, html_dir, timeout)
    entry["render_ms"] = int((time.time() - t0) * 1000)

    if not rend["ok"]:
        entry["render"] = rend
        # missing/unreachable/timeout → 环境级退出码 2 的信号
        entry["status"] = "ENV" if (rend.get("missing") or rend.get("unreachable") or rend.get("timeout")) else "FAIL"
        return entry

    # 产物类型 → 断言器路由：JSON(单元格级) > Excel(openpyxl) > HTML(正则)
    product = rend["html"]
    try:
        if product.lower().endswith(".json"):
            from json_assert import assert_json
            p, f_, w = assert_json(m, product)
            entry["assert_mode"] = "json"
        elif product.lower().endswith((".xls", ".xlsx")):
            from excel_assert import assert_excel
            p, f_, w = assert_excel(m, product)
            entry["assert_mode"] = "excel"
        else:
            p, f_, w = check_rendered(m, product)
            entry["assert_mode"] = "html"
    except Exception as e:
        entry.update(status="FAIL", reason=f"断言器异常: {e}")
        return entry
    entry.update({
        "render": {"ok": True, "product": os.path.relpath(product)},
        "asserts": {"pass": p, "warn": w, "fail": f_},
        "status": "FAIL" if f_ else ("WARN" if w else "PASS"),
    })
    # 性能感知: 注入渲染器产物自带的阶段耗时 → 阈值 WARN(慢模板嗅探)
    if product.lower().endswith(".json"):
        try:
            tj = json.load(open(product, encoding="utf-8")).get("timing") or {}
            if tj:
                entry["timing"] = tj
                SLOW = {"loadMs": 3000, "execMs": 5000, "totalMs": 10000}
                for k, v in tj.items():
                    if isinstance(v, (int, float)) and v > SLOW.get(k, 1e9):
                        w.append("PERF %s=%dms 超阈值 %dms(慢模板候选)" % (k, v, SLOW[k]))
                        entry["status"] = "FAIL" if f_ else "WARN"
        except Exception:
            pass
    return entry


def main():
    ap = argparse.ArgumentParser(description="无服务器kfgj/xlyl验证")
    ap.add_argument("target", help="cpt/frm 文件或目录")
    ap.add_argument("--backend", default="skeleton", choices=list(BACKENDS))
    ap.add_argument("--out", help="JSON 报告输出路径")
    ap.add_argument("--html-dir", default=os.path.join(HERE, "out"))
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    if os.path.isdir(args.target):
        files = sorted(glob.glob(os.path.join(args.target, "**", "*.cpt"), recursive=True)
                       + glob.glob(os.path.join(args.target, "**", "*.frm"), recursive=True))
    else:
        files = [args.target]
    if not files:
        print("未找到模板文件", file=sys.stderr); sys.exit(2)

    os.makedirs(args.html_dir, exist_ok=True)
    entries = [run_one(f, args.backend, args.html_dir, args.timeout) for f in files]

    n_pass = sum(1 for e in entries if e["status"] == "PASS")
    n_warn = sum(1 for e in entries if e["status"] == "WARN")
    n_fail = sum(1 for e in entries if e["status"] == "FAIL")
    n_env = sum(1 for e in entries if e["status"] == "ENV")
    summary = {"target": args.target, "backend": args.backend,
               "ts": datetime.datetime.now().isoformat(timespec="seconds"),
               "total": len(entries), "pass": n_pass, "warn": n_warn,
               "fail": n_fail, "env": n_env, "entries": entries}

    out_path = args.out or os.path.join(HERE, "render_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"backend={args.backend}  total={len(entries)}  "
          f"PASS={n_pass} WARN={n_warn} FAIL={n_fail} ENV={n_env}")
    for e in entries:
        mark = {"PASS": "✅", "WARN": "⚠", "FAIL": "❌", "ENV": "⛓"}[e["status"]]
        extra = ""
        if e["status"] in ("FAIL", "ENV"):
            extra = " — " + (e.get("reason") or e.get("render", {}).get("reason", ""))[:80]
        print(f"  {mark} {e['file']}{extra}")
    print(f"报告: {out_path}")
    sys.exit(2 if (n_env and not n_fail and n_pass == 0) else (1 if n_fail else 0))


if __name__ == "__main__":
    main()
