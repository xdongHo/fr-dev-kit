#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
llm_trace_report.py — LLM 调用日志周期复盘分析器（fr_dev_kit SOP 提速方案 · 方案四原型）

六个分析维度（对应方案 §5.3 判读表; 6) 为 P2-1/P2-2 增补）:
  1) 节点健康表   —— 每节点调用数/失败率/重试率/均耗时 → 短板节点
  2) 动作 n-gram  —— 高频连续动作链 → 可合并的脚本工具候选（"机"补位）
  3) 转移边偏差   —— 实际 node 转移 vs 设计 DAG → 未声明回退/跳过 = 工艺错乱信号
  4) 知识命中     —— kb_reads 高频文件 → 与 kb_platform 沉睡表人工对照
  5) 耗时热点     —— 单节点均耗时 Top → 瘦身候选
  6) 预算与失败分类 —— span 分布/步数·token·耗时预算占位/瞬时类 vs 语义类失败/熔断与重复意图信号

用法:
  python llm_trace_report.py [--since 2026-09-01] [--ngram 2,3] [--min-count 3] [--out <path>] [--root <kit根目录>]
默认输出: _runs/llm_trace/report/<date>_llm_report.md + stdout 摘要
节奏: 挂周五体检（复用登记表防重）; 季度并轨 Meta-Optimize 三率。退出码: 0 正常 / 1 无数据
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
import argparse, glob, json, os, sys, time
from collections import defaultdict, Counter

DESIGN_DAG = {  # 方案 §4.1: 设计依赖图（含显式回退边）; 不在此表的高频转移边 = 待裁决信号
    "01": ["02"], "02": ["03"], "03": ["04"],
    "04": ["05", "06", "07", "08", "10"],
    "05": ["08", "07", "10"], "06": ["08", "10"], "07": ["10"], "08": ["10"],
    "09": ["06", "08", "10"], "10": ["02", "03", "04", "05", "06", "07", "08", "09"],  # 10→x 为回退边
    "cross": [n for n in ["01","02","03","04","05","06","07","08","09","10"]],
}
LEGIT_BACK = {("03", "02"), ("04", "02"), ("05", "02"), ("05", "01"),
              ("08", "06"), ("09", "04"), ("09", "06")}  # 方案 §2.3 显式回退矩阵

def load_events(root, since=None):
    events = []
    for path in sorted(glob.glob(os.path.join(root, "_runs", "llm_trace", "*", "*.jsonl"))):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # 交错行容忍
                    if since and ev.get("ts", 0) < since:
                        continue
                    events.append(ev)
        except OSError:
            continue
    events.sort(key=lambda e: (e.get("session_id", ""), e.get("ts", 0)))
    return events

def node_health(events):
    agg = defaultdict(lambda: {"n": 0, "fail": 0, "retry": 0, "dur": []})
    for e in events:
        n = e.get("node", "cross"); a = agg[n]; a["n"] += 1
        if e.get("status") in ("fail", "timeout"): a["fail"] += 1
        if e.get("status") == "retry" or e.get("retry_of"): a["retry"] += 1
        if e.get("duration_ms") is not None: a["dur"].append(e["duration_ms"])
    rows = []
    for n, a in sorted(agg.items()):
        dur = sum(a["dur"]) / len(a["dur"]) if a["dur"] else None
        rows.append((n, a["n"], a["fail"] / a["n"], a["retry"] / a["n"], dur, a["retry"]))
    return rows

def action_ngrams(events, sizes, min_count):
    grams = Counter()
    by_sess = defaultdict(list)
    for e in events:
        by_sess[e.get("session_id", "unknown")].append(e.get("tool") or e.get("gate_id") or e.get("phase", "?"))
    for tools in by_sess.values():
        for size in sizes:
            for i in range(len(tools) - size + 1):
                gram = tuple(tools[i:i + size])
                if len(set(gram)) > 1:
                    grams[gram] += 1
    return [(g, c) for g, c in grams.most_common(20) if c >= min_count]

def edge_stats(events):
    edges = Counter(); last = {}
    for e in events:  # 按会话内时序取 node 转移（跨 phase 的转移才算; 同 node 连续不重复计）
        s, n = e.get("session_id", "unknown"), e.get("node", "cross")
        if s in last and last[s] != n:
            edges[(last[s], n)] += 1
        last[s] = n
    unknown, clean = [], []
    for (a, b), c in edges.most_common():
        ok = b in DESIGN_DAG.get(a, []) or (a, b) in LEGIT_BACK or a == "cross" or b == "cross"
        (clean if ok else unknown).append(((a, b), c))
    return clean, unknown

def kb_reads(events):
    c = Counter()
    for e in events:
        for f in e.get("kb_reads", []):
            c[f] += 1
    return c.most_common(15)

def hotspots(events, top=5):
    agg = defaultdict(list)
    for e in events:
        if e.get("duration_ms") is not None:
            agg[e.get("node", "cross")].append(e["duration_ms"])
    return sorted(((n, sum(v)/len(v), max(v), len(v)) for n, v in agg.items()),
                  key=lambda x: -x[1])[:top]

def budget_and_failures(events):
    """P2-1/P2-2 增补(2026-09-14): span 分布/三重预算/失败分类/熔断信号。"""
    def kind(e):
        sk = e.get("span_kind")
        if sk in ("agent", "tool", "llm"):
            return sk
        if e.get("model") or e.get("provider"):
            return "llm"
        if e.get("tool") and e.get("phase") in ("execute", "gate"):
            return "tool"
        return "agent"

    by_kind = Counter(kind(e) for e in events)
    toks = sum(e.get("tokens_est") or 0 for e in events)
    costs = [e.get("cost_est") for e in events if e.get("cost_est") is not None]
    cost = sum(costs)
    dur_total = sum(e.get("duration_ms") or 0 for e in events if e.get("duration_ms") is not None)
    fails = [e for e in events if e.get("status") in ("fail", "timeout")]
    steps_total = len(events)  # 三重预算之"步数"占位: 一条事件≈一步
    sess_n = len({e.get("session_id", "unknown") for e in events})
    rep_intent = 0  # P2-2 级联失败信号: 同会话相邻两条同 tool+args_digest 的失败
    prev = None
    for e in events:
        cur = (e.get("session_id", "?"), e.get("tool") or "", e.get("args_digest") or "")
        if e.get("status") in ("fail", "timeout") and cur == prev:
            rep_intent += 1
        prev = cur

    def fcls(e):
        ec = (e.get("error_class") or "").lower()
        if e.get("status") == "timeout" or any(k in ec for k in ("timeout", "超时", "限流", "rate", "connection", "network", "网络")):
            return "瞬时类(可自动重试)"
        if ec:
            return "语义类(升级人工)"
        return "未分类(建议补 error_class)"

    fc = Counter(fcls(e) for e in fails)
    streaks, worst = defaultdict(int), defaultdict(int)
    for e in events:  # load_events 已按 (session, ts) 排序
        key = (e.get("session_id", "?"), e.get("node", "cross"))
        if e.get("status") in ("fail", "timeout"):
            streaks[key] = streaks.get(key, 0) + 1
            worst[key] = max(worst.get(key, 0), streaks[key])
        else:
            streaks[key] = 0
    hot = sorted(((n, s, v) for (s, n), v in worst.items() if v >= 3), key=lambda x: -x[2])[:5]

    L = ["", "## 6) 预算与失败分类（P2-1/P2-2 增补 2026-09-14）", ""]
    L.append("- span 分布: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(by_kind.items()))
             + "（旧日志无 span_kind 时按 model/phase 推断）")
    L.append("- 步数: 事件合计 %d, 会话 %d, 均 %.1f 步/会话"
             % (steps_total, sess_n, steps_total / sess_n if sess_n else 0.0))
    L.append("- 预算: token 估计合计 %s | 费用估计合计 %s | 耗时合计 %.0fms"
             % (toks if toks else "—", ("%.4f" % cost) if cost else "—", dur_total))
    if fails:
        L.append("- 失败事件 %d 条: " % len(fails) + "；".join("%s=%d" % (k, v) for k, v in fc.most_common()))
    else:
        L.append("- 失败事件: 0 条")
    L.append("- 熔断信号(同会话同节点连续≥3 次 FAIL): "
             + (", ".join("节点%s×%d(会话%s)" % (n, v, s[:8]) for n, s, v in hot) if hot else "无"))
    if rep_intent:
        L.append("- 级联失败信号: 相邻重复同意图失败 %d 组（同 tool+args 连续重复 → 优先熔断升级人工）"
                 % rep_intent)
    L.append("- 待补字段: 精确 token 拆分(prompt/completion)、模型单价表(费用核算依据)、"
             "会话级三重预算上限(步数/token/时间) —— 当前日志仅有估计值, 上限未接入")
    return L


def render(rows, grams, clean, unknown, kbs, hots, since, n_events, sessions, budget_lines=None):
    L = [f"# LLM 调用日志复盘报告", "",
         f"- 生成: {time.strftime('%Y-%m-%d %H:%M')}  范围: since={since or '全部'}  "
         f"事件: {n_events}  会话: {sessions}", ""]
    L += ["## 1) 节点健康（失败率>30% 且重试≥2 → 节点短缺信号, 样本≥5 才提案）", "",
          "| 节点 | 调用 | 失败率 | 重试率 | 均耗时ms |", "|---|---|---|---|---|"]
    for n, cnt, fr, rr, dur, rc in rows:
        flag = " ⚠️" if (cnt >= 5 and fr > 0.3 and rc >= 2) else ""
        L.append(f"| {n} | {cnt} | {fr:.0%} | {rr:.0%} | {dur:.0f} |{flag}" if dur is not None
                 else f"| {n} | {cnt} | {fr:.0%} | {rr:.0%} | — |{flag}")
    L += ["", "## 2) 高频动作链（≥min-count → 脚本工具候选, 登记 ckzl/zsk/gczsk'机'）", ""]
    L += [f"- `{' → '.join(g)}` ×{c}" for g, c in grams] or ["- （无）"]
    edge_clean = [f"- {a}→{b} ×{c}" for (a, b), c in clean[:12]] or ["- （无）"]
    edge_unknown = [f"- {a}→{b} ×{c}" for (a, b), c in unknown] or ["- （无）"]
    L += ["", "## 3) 节点转移边（未知边高频 = 工艺错乱信号 → 方案三裁决项）", "",
          "**合规边**:", *edge_clean,
          "**未声明边（待裁决）**:", *edge_unknown]
    L += ["", "## 4) 知识命中 Top（零命中文档 → 对照 kb_platform 沉睡表）", ""]
    L += [f"- {f} ×{c}" for f, c in kbs] or ["- （无 kb_reads 记录）"]
    L += ["", "## 5) 耗时热点（均耗时 Top5 → 上下文瘦身候选）", "",
          "| 节点 | 均耗时ms | 最大ms | 样本 |", "|---|---|---|---|"]
    L += [f"| {n} | {d:.0f} | {m:.0f} | {c} |" for n, d, m, c in hots]
    if budget_lines:
        L += budget_lines
    L += ["", "> 处置纪律: 每周报告结论 ≥5 样本才形成提案; 提案并入周五体检/Meta-Optimize; "
             "重要结论写回知识库（_runs 不入 git）。"]
    return "\n".join(L)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--since", help="YYYY-MM-DD, 只统计此后事件")
    p.add_argument("--ngram", default="2,3")
    p.add_argument("--min-count", type=int, default=3)
    p.add_argument("--out", default="")
    p.add_argument("--root", default="",
                   help="指定 kit 根目录（默认按脚本位置向上找 kfgj/guard.py; 便于对副本/临时目录做只读复盘）")
    a = p.parse_args()
    if a.root:
        root = os.path.abspath(a.root)
    else:
        root = os.path.dirname(os.path.abspath(__file__))
        for _ in range(4):
            if os.path.isfile(os.path.join(root, "kfgj/guard.py")):
                break
            parent = os.path.dirname(root)
            if parent == root:
                break
            root = parent
    since = time.mktime(time.strptime(a.since, "%Y-%m-%d")) if a.since else None
    events = load_events(root, since)
    if not events:
        print("无日志数据（先跑 llm_call_logger.py 或 node_gate.py 产生事件）"); sys.exit(1)
    rows = node_health(events)
    grams = action_ngrams(events, [int(x) for x in a.ngram.split(",")], a.min_count)
    clean, unknown = edge_stats(events)
    kbs = kb_reads(events); hots = hotspots(events)
    sessions = len({e.get("session_id", "unknown") for e in events})
    budget_lines = budget_and_failures(events)
    md = render(rows, grams, clean, unknown, kbs, hots, a.since, len(events), sessions,
                budget_lines=budget_lines)
    out = a.out or os.path.join(root, "_runs", "llm_trace", "report",
                                f"{time.strftime('%Y%m%d')}_llm_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"报告: {out}\n事件 {len(events)} / 会话 {sessions} / "
          f"未声明转移边 {len(unknown)} / 短板节点 "
          f"{[n for n, c, fr, rr, d, rc in rows if c >= 5 and fr > 0.3 and rc >= 2]}")
    sys.exit(0)

if __name__ == "__main__":
    main()
