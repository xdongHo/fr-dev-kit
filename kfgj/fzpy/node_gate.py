#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
node_gate.py — 节点出口门禁执行器 v0.1（fr_dev_kit SOP 提速方案 · 方案一原型）

单一事实源: ckzl/gzjd/node_gates.yaml（防 10 处复制漂移）。
职责:
  1. 输入契约校验: 上游产物存在且必填字段齐 → 不过禁入（"增强下一节点输入质量"的第一断言）
  2. 出口门禁: 按矩阵逐条跑命令, deps 不满足按 offline 策略 SKIP/WARN 留痕
  3. 报告: _runs/tasks/<task>/gates/<NN>.json + 自动埋点 llm_call_logger（方案四闭环）
  4. check-artifact 子命令: 独立的产物 schema 校验（01 节点自检也用它）
  5. 熔断(P2-2): 同任务同节点连续 N 次 FAIL（默认 5, --circuit-breaker 可配, 0=关闭）
     → 判定追加 CB<熔断> FAIL（退出码 1, 对齐既有 0/1/2 语义）, 阻断无效自动重试;
     连续失败但未达阈值 → CB<观察> WARN（退出码 2, 仅提醒不阻断）; 熔断解除 = 人工修复后显式带 0 重跑

用法:
  python node_gate.py --node 02 --task-dir _runs/tasks/T-XXX [--cpt 模板.cpt] [--offline]
  python node_gate.py check-artifact <yaml产物> --fields f1,f2[,a.b]
退出码: 0=全过 1=有 FAIL 2=过但有 WARN/SKIP（对齐 fr_check/guard 约定）
依赖: PyYAML（kit 环境已有, guardrails/semantic_layer 同款）
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
import argparse, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
for _ in (HERE, os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE))):
    if os.path.isfile(os.path.join(_, "kfgj/guard.py")):
        ROOT = _
        break
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)  # 便于 import llm_call_logger（放入 kfgj/fzpy/ 后同目录即可）

try:
    import yaml  # noqa: F401  懒加载校验点在 load_matrix(); check-artifact 无需 PyYAML
except ImportError:
    yaml = None

def load_matrix():
    if yaml is None:
        print("需要 PyYAML: pip install pyyaml"); sys.exit(1)
    for cand in (os.path.join(ROOT, "ckzl/gzjd", "node_gates.yaml"),
                 os.path.join(HERE, "node_gates.yaml")):
        if os.path.isfile(cand):
            with open(cand, encoding="utf-8") as f:
                return yaml.safe_load(f)
    print("找不到 node_gates.yaml（应放 ckzl/gzjd/ 下）"); sys.exit(1)

def artifact_ok(path, fields, assert_expr=None):
    """产物存在 + 字段齐(支持 a.b 点路径) + 简单断言(field == 'value')。返回 (ok, 缺失清单)。"""
    if not os.path.isfile(path):
        return False, [f"<文件不存在> {path}"]
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {} if yaml else {}
    except Exception as e:
        return False, [f"<解析失败> {e}"]
    if yaml is None:
        return False, ["<PyYAML 缺失>"]
    missing = []
    for fld in fields or []:
        cur = data
        for part in str(fld).split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                missing.append(fld); break
    if assert_expr and not missing:
        m = re.match(r"^\s*(\w+(?:\.\w+)*)\s*==\s*['\"]([^'\"]*)['\"]\s*$", assert_expr)
        if m:
            cur = data
            for part in m.group(1).split("."):
                cur = cur.get(part) if isinstance(cur, dict) else None
            if str(cur) != m.group(2):
                missing.append(f"断言不满足: {assert_expr}（实际 {cur}）")
        else:
            missing.append(f"断言语法不支持: {assert_expr}")
    return (not missing), missing

def run_gate(g, ctx):
    """跑一条门禁。返回 {id, status, detail, duration_ms}。"""
    if g.get("enabled") is False:
        return {"id": g["id"], "status": "SKIP", "detail": "占位新工具未启用"}
    deps = g.get("deps") or []
    if ctx.get("offline"):
        policy = g.get("offline", "skip")          # --offline: 按各门禁声明的降级策略, 缺省 skip
    elif deps and not ctx.get("deps_ok"):
        policy = g.get("offline", "fail")          # 运行时依赖缺失: 缺省 FAIL(不静默)
    else:
        policy = None
    if policy in ("warn", "dry"):
        return {"id": g["id"], "status": "WARN", "detail": f"依赖缺失({','.join(deps) or 'offline'}), offline 策略={policy}"}
    if policy == "skip":
        return {"id": g["id"], "status": "SKIP", "detail": f"依赖缺失({','.join(deps) or 'offline'})"}
    if policy:
        return {"id": g["id"], "status": "FAIL", "detail": "依赖缺失且无 offline 降级策略"}
    cmd = g["cmd"].format(**ctx)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=g.get("timeout", 300), cwd=ROOT)
        code = p.returncode
        out = (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return {"id": g["id"], "status": "FAIL", "detail": "timeout", "duration_ms": (time.time()-t0)*1000}
    dur = (time.time() - t0) * 1000
    status = "PASS" if code == 0 else ("WARN" if code == 2 else "FAIL")
    return {"id": g["id"], "status": status, "exit": code,
            "detail": out.strip().splitlines()[-1][:200] if out.strip() else "",
            "cmd": cmd, "duration_ms": round(dur, 1)}

# P2-2(2026-09-14): 三重预算占位（步数/token/时间）—— 上限接入任务卡/环境变量后启用, None=不设限
TRIPLE_BUDGET = {"max_steps": None, "max_tokens": None, "max_ms": None}

def circuit_breaker_hits(task_dir, node, threshold):
    """P2-2(2026-09-14): 扫 _runs/llm_trace 近期日志, 统计同 (task,node) 从最新往回的连续 FAIL 数。
    只计 node_gate 的 phase=gate 事件（每跑一次恰落一条; decision 与 gate 成对落盘, 计入会翻倍）。"""
    try:
        import glob
        # (2026-09-15 BG-DL-01) 先过滤后限窗: 遍历当月+上月全部 jsonl, 先按 (task_id,node,phase,tool) 过滤
        # 聚合再统计连败; 不再按 mtime 取"最近 3 个文件"（多会话并发下当前任务文件跌出窗口 → 漏判 fail-open）。
        _lt = time.localtime()
        _months = []
        _y, _mo = _lt.tm_year, _lt.tm_mon
        for _ in range(2):                       # 当月 + 上月
            _months.append("%04d-%02d" % (_y, _mo))
            _mo -= 1
            if _mo < 1:
                _y, _mo = _y - 1, 12
        paths = []
        for _m in _months:
            # 双址扫描: 用户目录(现行) + 套件 _runs(历史遗留), 2026-09-29 迁移约定
            for _base in (os.path.join(os.path.expanduser("~"), ".fr_dev_kit", "runs"), ROOT):
                paths.extend(glob.glob(os.path.join(_base, "llm_trace", _m, "*.jsonl")))
        evs = []
        for p in paths:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    if (e.get("task_id") == task_dir and e.get("node") == node
                            and e.get("phase") == "gate" and e.get("tool") == "node_gate"):
                        evs.append(e)
        evs.sort(key=lambda e: e.get("ts", 0))
        n = 0
        for e in reversed(evs):
            if e.get("status") in ("fail", "timeout"):
                n += 1
            else:
                break
        return n, (n >= max(threshold, 1) if threshold else False)   # (2026-09-15 BG-DL-02) 负阈值钳到 1: 零失败不再误熔断; 0=关闭语义不变
    except Exception:
        return 0, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node"); ap.add_argument("--task-dir", dest="task_dir", default="")
    ap.add_argument("--cpt", default=""); ap.add_argument("--frm", default="")
    ap.add_argument("--sql-file", dest="sql_file", default="")
    ap.add_argument("--table", default=""); ap.add_argument("--params", default="")
    ap.add_argument("--export-file", dest="export_file", default="")
    ap.add_argument("--task-type", dest="task_type", default="create")
    ap.add_argument("--attests", default="")
    ap.add_argument("--circuit-breaker", type=int, default=5, metavar="N",
                    help="P2-2: 同任务同节点连续 N 次 FAIL 触发熔断(默认 5; 0=关闭)")
    ap.add_argument("--offline", action="store_true", help="按 offline 策略处理全部依赖门禁")
    ap.add_argument("--deps-ok", action="store_true", help="声明 dws/fr_server/designer 依赖已满足")
    sub = ap.add_subparsers(dest="cmd")
    ca = sub.add_parser("check-artifact")
    ca.add_argument("path"); ca.add_argument("--fields", required=True)
    a = ap.parse_args()

    if a.cmd == "check-artifact":
        ok, missing = artifact_ok(a.path, [x for x in a.fields.split(",") if x])
        print(json.dumps({"artifact": a.path, "ok": ok, "missing": missing}, ensure_ascii=False))
        sys.exit(0 if ok else 1)

    if not a.node or not a.task_dir:
        ap.error("--node 与 --task-dir 必填")
    m = load_matrix(); spec = m["nodes"].get(a.node)
    if not spec:
        print(f"node_gates.yaml 无节点 {a.node}"); sys.exit(1)

    ctx = {"artifacts_dir": f"_runs/tasks/{a.task_dir}", "tools_dir": m["common"]["tools_dir"],
           "cpt": a.cpt, "frm": a.frm, "sql_file": a.sql_file, "table": a.table,
           "params": a.params, "export_file": a.export_file, "task_type": a.task_type,
           "attests": a.attests, "task_dir": a.task_dir,
           "offline": a.offline, "deps_ok": a.deps_ok}
    results, has_fail, has_warn = [], False, False

    for inp in spec.get("inputs") or []:            # 1) 输入契约: 上游产物质量断言
        path = inp["artifact"].format(**ctx)
        ok, missing = artifact_ok(path, inp.get("required_fields"), inp.get("assert"))
        results.append({"id": f"IN<{os.path.basename(path)}>", "status": "PASS" if ok else "FAIL",
                        "detail": f"缺失: {missing}" if missing else "上游产物契约满足"})
        has_fail |= not ok

    for g in spec.get("gates") or []:               # 2) 出口门禁
        r = run_gate(g, ctx)
        results.append(r)
        has_fail |= r["status"] == "FAIL"
        has_warn |= r["status"] in ("WARN", "SKIP")

    if getattr(a, "circuit_breaker", 0):      # P2-2(2026-09-14): 熔断默认开启(阈值 5), --circuit-breaker 0 关闭
        n_fail, tripped = circuit_breaker_hits(a.task_dir, a.node, a.circuit_breaker)
        if tripped:
            results.append({"id": "CB<熔断>", "status": "FAIL",
                            "detail": ("同任务同节点连续 %d 次 FAIL ≥ 阈值 %d → 熔断: 停止自动重试, "
                                       "失败先分类(瞬时=带幂等重试/语义=升级人工), 写待裁决" % (n_fail, a.circuit_breaker))})
            has_fail = True
        elif n_fail:
            results.append({"id": "CB<观察>", "status": "WARN",
                            "detail": "连续 %d 次 FAIL < 阈值 %d, 未熔断（观察项, 提醒不阻断）"
                                      % (n_fail, a.circuit_breaker)})
            has_warn = True

    report = {"node": a.node, "name": spec.get("name"), "task_dir": a.task_dir,
              "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "verdict": "FAIL" if has_fail else ("WARN" if has_warn else "PASS"),
              "results": results}
    out_dir = os.path.join(ROOT, "_runs", "tasks", a.task_dir, "gates")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{a.node}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    try:                                            # 3) 自动埋点（方案四闭环）
        from llm_call_logger import log_call
        log_call(node=a.node, phase="gate", tool="node_gate", status="ok" if not has_fail else "fail",
                 duration_ms=sum(r.get("duration_ms") or 0 for r in results),
                 gate_id=",".join(r["id"] for r in results),
                 artifacts=[os.path.join(out_dir, f"{a.node}.json")], task_id=a.task_dir)
    except Exception:
        pass
    try:                                            # 4) 决策事件(节点级 LLM 判断流水, kb_platform P1-②)
        from llm_call_logger import log_call as _lc
        det = "; ".join("%s=%s" % (r["id"], r["status"]) for r in results)
        _lc(node=a.node, phase="decision", tool="node_gate",
            status="ok" if not has_fail else "fail",
            notes=("verdict=%s; fail=%d warn=%d; %s" % (
                report["verdict"],
                sum(1 for r in results if r["status"] == "FAIL"),
                sum(1 for r in results if r["status"] == "WARN"), det))[:300],
            task_id=a.task_dir)
    except Exception:
        pass

    for r in results:
        print(f"[{r['status']:^4}] {r['id']}  {r.get('detail','')}")
    print(f"节点 {a.node}({spec.get('name')}) 判定: {report['verdict']} → 报告 {out_dir}\\{a.node}.json")
    sys.exit(1 if has_fail else (2 if has_warn else 0))

if __name__ == "__main__":
    main()
