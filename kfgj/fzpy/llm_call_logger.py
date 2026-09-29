#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
llm_call_logger.py — LLM 开发会话的动作级日志写入器（fr_dev_kit SOP 提速方案 · 方案四原型）

定位: 调用方侧记录（兼容 kb_platform"绝不侵入 agent 会话"铁律），一行一 JSON 事件追加写。
落盘: ~/.fr_dev_kit/runs/llm_trace/<YYYY-MM>/<session_id>.jsonl（用户目录，随人走；不可写回退套件 _runs）

用法:
  1) CLI（agent 每步工具执行后一行; AGENTS.md STEP4 增补纪律）:
     python llm_call_logger.py log --node 02 --tool verify_sql --status fail \
         --dur-ms 12300 --detail "0 rows: ds_sales" --task T-FS-0417 --gate G08 \
         --artifacts "_runs/tasks/T-FS-0417/02_datasets.yaml" --kb-reads "ckzl/lc/02_数据建模.md"
  2) import（node_gate.py / 脚本内嵌自动埋点）:
     from llm_call_logger import log_call
     log_call(node="02", tool="node_gate", phase="gate", status="ok", gate_id="G08", duration_ms=8.2)
  3) python llm_call_logger.py id        # 打印一个事件 id（供 retry_of 关联）
  4) P2-1 span 字段（全可选, 不传行为与原来一致）: --span-kind agent|tool|llm  --tokens N  --cost F

退出码: 恒 0（日志器自身故障绝不影响主任务——静默失败纪律）
安全: args/detail 自动脱敏（password/pwd/conn 等赋值片段打码）; 脱敏是底线不是保证, 凭据请勿入参
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
import argparse, json, os, re, sys, time, uuid, hashlib

# ---- 仓库定位: 与 kit 惯例一致, 由 __file__ 推导（放入 kfgj/fzpy/ 后自动指向仓库根）----
def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    # 若在 kfgj/fzpy/ 下则上一级是仓库根; 若在 DELIVERY 等其他目录, 向上找 kfgj/guard.py
    for cand in (here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))):
        if os.path.isfile(os.path.join(cand, "kfgj/guard.py")):
            return cand
    return os.path.dirname(here)  # 兜底: 上一级

SECRET_RE = re.compile(
    r"(?i)(password|passwd|pwd|secret|token|dsn|conn(?:ection)?_?string)\s*[=:]\s*\S+")
def mask(text, cap=300):
    if not text:
        return ""
    text = SECRET_RE.sub(r"\1=***", str(text))
    return text[:cap] + ("…" if len(text) > cap else "")

def session_id():
    return (os.environ.get("KB_AUDIT_TAG") or os.environ.get("FR_SESSION_ID")
            or os.environ.get("FR_TASK_CARD") or "unknown")

def new_event_id():
    return hashlib.sha1(f"{time.time_ns()}-{uuid.uuid4().hex}".encode()).hexdigest()[:12]

def log_call(node="cross", phase="execute", tool="", status="ok", duration_ms=None,
             task_id=None, card=None, agent_role=None, args_digest="", target_file="",
             error_class="", retry_of="", artifacts=None, kb_reads=None, gate_id="",
             tokens_est=None, notes="", model=None, provider=None,
             span_kind=None, cost_est=None):
    """写一条事件; 任何异常静默吞掉。返回事件 id（失败返回 ""）。"""
    if span_kind not in ("agent", "tool", "llm"):   # (2026-09-15 BG-DL-04) import 路径与 CLI choices 对齐: 非法值不落盘, 走自动推断
        span_kind = None
    try:
        root = repo_root()
        now = time.time()
        model_eff = model or os.environ.get("LLM_MODEL") or ""           # (2026-09-15 BG-DL-03) 有效值(含 env 回退):
        provider_eff = provider or os.environ.get("LLM_PROVIDER") or ""  # 事件体与 span_kind 推断共用同一对, 消除写/读口径分裂
        ev = {
            "ts": round(now, 3),
            "event_id": new_event_id(),
            "session_id": session_id(),
            "agent_role": agent_role or os.environ.get("FR_AGENT_ROLE") or "main",
            "task_id": task_id or os.environ.get("FR_TASK_ID") or "",
            "card": card or os.environ.get("FR_TASK_CARD") or "",
            "node": node,
            "phase": phase,                      # route|read|execute|verify|gate|handoff
            "tool": tool,
            "args_digest": mask(args_digest),
            "target_file": target_file or "",
            "status": status,                    # ok|fail|retry|timeout|skip
            "duration_ms": round(float(duration_ms), 1) if duration_ms is not None else None,
            "error_class": error_class,
            "retry_of": retry_of,
            "artifacts": artifacts or [],
            "kb_reads": kb_reads or [],
            "gate_id": gate_id,
            "model": model_eff,
            "provider": provider_eff,
            "tokens_est": tokens_est,
            "notes": mask(notes, 500),
            # P2-1 (2026-09-14): OTel GenAI 三级 span 语义 agent|tool|llm; 旧调用方不传时自动推断
            "span_kind": span_kind or ("llm" if (model_eff or provider_eff)
                                       else ("tool" if (tool and phase in ("execute", "gate"))
                                             else "agent")),
            "cost_est": cost_est,
        }
        ev = {k: v for k, v in ev.items() if v not in (None, "", [])}
        month = time.strftime("%Y-%m", time.localtime(now))
        # 运行痕迹归用户目录（随人走不随套件走，2026-09-29 约定）；不可写回退套件 _runs
        try:
            d = os.path.join(os.path.expanduser("~"), ".fr_dev_kit", "runs",
                             "llm_trace", month)
            os.makedirs(d, exist_ok=True)
        except Exception:
            d = os.path.join(root, "_runs", "llm_trace", month)
            os.makedirs(d, exist_ok=True)
        path = os.path.join(d, f"{session_id()}.jsonl")
        with open(path, "a", encoding="utf-8") as f:   # 单行 write, 多进程下最坏交错一行
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev["event_id"]
    except Exception:
        if os.environ.get("LLM_LOG_DEBUG"):        # 排障开关: 不影响静默失败纪律
            import traceback; traceback.print_exc()
        return ""

def main():
    p = argparse.ArgumentParser(description="LLM 动作级日志写入器（原型）")
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--node", default="cross"); lg.add_argument("--phase", default="execute")
    lg.add_argument("--tool", default=""); lg.add_argument("--status", default="ok",
        choices=["ok", "fail", "retry", "timeout", "skip"])
    lg.add_argument("--dur-ms", type=float, dest="dur_ms")
    lg.add_argument("--task", dest="task_id"); lg.add_argument("--card")
    lg.add_argument("--role", dest="agent_role"); lg.add_argument("--args", dest="args_digest")
    lg.add_argument("--target", dest="target_file"); lg.add_argument("--err", dest="error_class")
    lg.add_argument("--retry-of", dest="retry_of"); lg.add_argument("--gate", dest="gate_id")
    lg.add_argument("--artifacts", default="", help="逗号分隔")
    lg.add_argument("--kb-reads", default="", help="逗号分隔")
    lg.add_argument("--model", default="", help="LLM 调用类事件必填（或环境变量 LLM_MODEL）")
    lg.add_argument("--provider", default="", help="或环境变量 LLM_PROVIDER")
    lg.add_argument("--tokens", type=int, dest="tokens_est")
    lg.add_argument("--cost", type=float, dest="cost_est", help="费用估计(可选, P2-1)")
    lg.add_argument("--span-kind", dest="span_kind", choices=["agent", "tool", "llm"],
                    default=None, help="span 层级; 缺省按 model/phase 自动推断(P2-1)")
    lg.add_argument("--detail", dest="notes")
    sub.add_parser("id")
    a = p.parse_args()
    if a.cmd == "id":
        print(new_event_id()); return
    eid = log_call(node=a.node, phase=a.phase, tool=a.tool, status=a.status,
                   duration_ms=a.dur_ms, task_id=a.task_id, card=a.card,
                   agent_role=a.agent_role, args_digest=a.args_digest or "",
                   target_file=a.target_file or "", error_class=a.error_class or "",
                   retry_of=a.retry_of or "", gate_id=a.gate_id or "",
                   artifacts=[x for x in (a.artifacts or "").split(",") if x],
                   kb_reads=[x for x in (a.kb_reads or "").split(",") if x],
                   tokens_est=a.tokens_est, notes=a.notes or "",
                   model=a.model or None, provider=a.provider or None,
                   span_kind=a.span_kind, cost_est=a.cost_est)
    print(eid)  # 恒退出码 0（argparse 错误除外）

if __name__ == "__main__":
    try:
        main()
    except SystemExit as _e:      # argparse 参数错误等, 保留原退出码
        sys.exit(_e.code or 0)
    except Exception:
        pass                      # 静默失败纪律
    sys.exit(0)
