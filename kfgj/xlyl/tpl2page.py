#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tpl2page.py — 模板→页面一键工具(设计迭代加速器)

给模板快速产出高保真页面: 真引擎渲染(agent 服务端, 免登录免浏览器)
  → 结构化 JSON(单元格级/组件树级)
  → 高保真 HTML 页面(json_page.py: 表格网格/绝对布局画布/降级警示)
  → 真引擎 PDF(export_pdf.py: 图表/样式完整绘制, 人工审阅用)

用法:
  python kfgj/xlyl\tpl2page.py <模板.cpt/.frm>              # HTML+PDF+JSON 全套
  python kfgj/xlyl\tpl2page.py <模板> --open                # 完成后自动打开 HTML
  python kfgj/xlyl\tpl2page.py <页面URL或viewlet路径>        # 与 page2tpl 同源输入解析
输出(kfgj/xlyl/out/): <名>.json + <名>_page.html + <名>.pdf
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_check import backend_injected  # noqa: E402
from page2tpl import resolve_input, DEFAULT_REPORTLETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="模板→页面一键工具(HTML+PDF+JSON)")
    ap.add_argument("src", help="模板路径 / 页面URL / viewlet相对路径")
    ap.add_argument("--out", default=os.path.join(HERE, "out"), help="输出目录")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--open", action="store_true", help="完成后打开 HTML")
    ap.add_argument("--no-pdf", action="store_true", help="跳过 PDF(更快)")
    args = ap.parse_args()

    tpl, how = resolve_input(args.src, DEFAULT_REPORTLETS)
    print(f"[输入] {how}\n  → {tpl}")
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(tpl))[0]

    # 1) 真引擎渲染 → JSON
    r = backend_injected(tpl, args.out, args.timeout)
    if not r.get("ok"):
        print(f"[1] ❌ 渲染失败: {r.get('reason')}")
        print("    (模板不可用/损坏,或 agent/设计器未运行)")
        sys.exit(2)
    json_path = os.path.join(args.out, f"{stem}.json")
    os.replace(r["html"], json_path)
    print(f"[1] 渲染产物 → {json_path}")

    # 2) JSON → 高保真 HTML
    import json_page
    html_path = os.path.join(args.out, f"{stem}_page.html")
    json_page.generate(json_path, html_path)
    print(f"[2] HTML 页面 → {html_path}")

    # 3) 真引擎 PDF(cpt; frm 无 PDF 导出链, 跳过)
    pdf_path = None
    if not args.no_pdf and tpl.lower().endswith(".cpt"):
        pdf_path = os.path.join(args.out, f"{stem}.pdf")
        ep = os.path.join(HERE, "export_pdf.py")
        rp = subprocess.run([sys.executable, ep, tpl, pdf_path],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=args.timeout, cwd=HERE)
        if rp.returncode == 0:
            print(f"[3] PDF → {pdf_path}")
        else:
            print(f"[3] PDF 失败(不影响 HTML): {(rp.stdout or rp.stderr or '')[-160:]}")
            pdf_path = None

    print("DONE")
    if args.open:
        os.startfile(html_path)  # noqa


if __name__ == "__main__":
    main()
