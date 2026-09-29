#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
layout_grid.py — 栅格布局计算器（借鉴 FR AI 助手 dashboard_analyze_plan 的栅格化布局法）

AI 助手提示词原文（dashboard_analyze_plan.txt §6 布局规则）：
    - 无缝填充整张画布，不留任何空白；任意组件之间不得重叠
    - 根据组件数量N，选取行列数(rows, cols)，使 rows × cols ≥ N 且画布浪费最小
    - 每格尺寸 cellW = width / cols, cellH = height / rows
    - 组件i坐标 x = (i%cols)*cellW, y = floor(i/cols)*cellH；宽高 cellW、cellH
    - 重点组件可合并相邻格

用法：
    python layout_grid.py --width 1920 --height 1080 --n 4            # 4 组件等分
    python layout_grid.py -W 1920 -H 1080 -n 6 --span 2,1,1,1,1,2    # 第1/6个组件占2格(横跨)
    python layout_grid.py -W 1280 -H 720 -n 5 --gap 5 --margin 10     # 带间距/边距
    python layout_grid.py -W 1920 -H 1080 -n 4 --rect                 # 输出 FR BoundsWidget Rect 构造代码

输出：每个组件 (x, y, width, height) 的 JSON，可直接喂给 Java API 脚本 / LLM 参考。
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
import math


def pick_grid(n, width=0, height=0, force_row=False):
    """选 (rows, cols)：rows*cols >= n 且浪费最小，越接近正方形越好；横向画布平局偏好多列。"""
    if force_row:
        return 1, n
    best = None
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        waste = rows * cols - n
        # 方向仅平局决胜：1x5 vs 5x1 同分时按画布形状选（横向偏多列，纵向偏多行）
        orient = -cols if width >= height else -rows
        # 先浪费，再方正，最后方向
        score = (waste, abs(cols - rows), orient)
        if best is None or score < best[0]:
            best = (score, rows, cols)
    return best[1], best[2]


def grid_layout(width, height, n, spans=None, gap=0, margin=0, force_row=False):
    """
    栅格布局。spans[i] = 组件 i 占的格数（默认 1；>1 横跨多格）。
    返回 [(x, y, w, h), ...]。
    """
    spans = spans or [1] * n
    if len(spans) < n:
        spans = spans + [1] * (n - len(spans))
    total_cells = sum(spans)
    rows, cols = pick_grid(total_cells, width, height, force_row)
    cell_w = (width - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (height - 2 * margin - (rows - 1) * gap) / rows

    rects = []
    r = c = 0
    for i in range(n):
        s = max(1, spans[i])
        # 如果当前行放不下，换行
        if c + s > cols:
            r += 1
            c = 0
        x = margin + c * (cell_w + gap)
        y = margin + r * (cell_h + gap)
        w = s * cell_w + (s - 1) * gap
        h = cell_h
        rects.append((round(x, 1), round(y, 1), round(w, 1), round(h, 1)))
        c += s
    return rects


def validate(rects, width, height, n, eps=1.0):
    """校验：数量、不越界、不重叠。eps=允许误差(像素，默认1px 容忍浮点舍入)。返回 (ok, 问题列表)。"""
    problems = []
    if len(rects) != n:
        problems.append(f"组件数 {len(rects)} != {n}")
    for i, (x, y, w, h) in enumerate(rects):
        if x < -eps or y < -eps or x + w > width + eps or y + h > height + eps:
            problems.append(f"组件{i} 越界: ({x},{y},{w},{h}) 画布 {width}x{height}")
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            if not (a[0] + a[2] <= b[0] + eps or b[0] + b[2] <= a[0] + eps
                    or a[1] + a[3] <= b[1] + eps or b[1] + b[3] <= a[1] + eps):
                problems.append(f"组件{i} 与 {j} 重叠")
    return (len(problems) == 0, problems)


def to_rect_code(rects, names=None):
    """输出 FR Java API 的 BoundsWidget Rect 构造代码（Nashorn 可直接用）。"""
    lines = []
    for i, (x, y, w, h) in enumerate(rects):
        name = names[i] if names and i < len(names) else f"widget{i}"
        lines.append(f'new BoundsWidget({name}, new Rect({x:.0f}, {y:.0f}, {w:.0f}, {h:.0f}))')
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="栅格布局计算器")
    ap.add_argument("-W", "--width", type=int, required=True, help="画布宽")
    ap.add_argument("-H", "--height", type=int, required=True, help="画布高")
    ap.add_argument("-n", "--count", type=int, required=True, help="组件数量")
    ap.add_argument("--span", default=None, help="重点组件占格，逗号分隔（如 2,1,1,1,1,2）")
    ap.add_argument("--row", action="store_true", help="单行模式（参数面板按钮/横排控件）")
    ap.add_argument("--gap", type=float, default=0, help="格间距（默认0=无缝）")
    ap.add_argument("--margin", type=float, default=0, help="画布边距（默认0）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--rect", action="store_true", help="输出 FR BoundsWidget Rect 构造代码")
    ap.add_argument("--names", default=None, help="组件名，逗号分隔（配合 --rect）")
    args = ap.parse_args()

    spans = [int(x) for x in args.span.split(",")] if args.span else None
    rects = grid_layout(args.width, args.height, args.count, spans, args.gap, args.margin, force_row=args.row)
    ok, problems = validate(rects, args.width, args.height, args.count)

    if args.rect:
        names = args.names.split(",") if args.names else None
        print(to_rect_code(rects, names))
    else:
        out = {"width": args.width, "height": args.height, "count": args.count,
               "rects": [{"x": x, "y": y, "w": w, "h": h} for x, y, w, h in rects]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    if not ok:
        print(f"# ⚠ 校验问题: {problems}", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
