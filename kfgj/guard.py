#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kfgj/guard.py — fr_dev_kit v2 执行契约闸门执行器
================================================

背景（为什么需要它）:
    v1 指南的强制项全部以自然语言散落在 128 个 md 的 1000+ 处"必须/禁止"里，
    依赖大模型自觉执行 → 实际频繁被跳过（"配置项不被执行"）。
    v2 把"必须做的动作"收敛为 12 条硬闸门（见 kfgj/EXEC_CONTRACT.md），
    本脚本是闸门的唯一执行器：跑不过 = 任务未完成。

用法（在仓库根目录执行）:
    python kfgj/guard.py --list                          # 列出全部闸门
    python kfgj/guard.py --selftest                      # 自检(环境/断链/契约同源,不需模板)
    python kfgj/guard.py --task modify --cpt <路径.cpt>  # 修改/格式化模板后收尾
    python kfgj/guard.py --task create  --cpt <路径.cpt> # 新建模板后收尾
    python kfgj/guard.py --task format  --cpt <路径.cpt> # 纯格式化后收尾
    python kfgj/guard.py --task error                    # 排错任务收尾(不产出模板)
    python kfgj/guard.py --task kb --doc <文件.md>       # 新增/修改知识文件后收尾

泳道围栏检查（v2.3 2026-09-06 CAR-009, 出处 R65/T16 deny先行+读写分离）:
    python kfgj/guard.py --check-enclosure <泳道目录> --since <iso时间>
    扫仓库工作区(排除 .git/ _runs/ __pycache__/ node_modules/), 列出 mtime>=since
    且位于泳道目录之外的变更文件; 有违规=退出码1, 无=0。收口前机器验证"只写了泳道"。
    --since 缺省=泳道目录创建时间(取不到则 24h 前)。

FAIL 自动重试（v2.3 2026-09-06 CAR-010, 出处 R65/T06 旁证）:
    python kfgj/guard.py --task ... --auto-retry 1 --redo "<修复命令>"
    闸门 FAIL 时自动执行一次 redo 命令然后复检(仅复检 FAIL 的自动闸门);
    仍 FAIL → 按原 FAIL 出口并标注"已自动重试 1 次未果,转待裁决"。
    不带 --redo 则 --auto-retry 无效并提示; attest/manual 闸门 redo 无法修复, 维持 FAIL。

可选参数:
    --attest G08,G09    声明"过程闸门已在流程中实际执行"(用逗号分隔闸门号)
    --no-backup         本次豁免 G04 备份闸门(会在报告中留痕,禁止连续使用)
    --draft             草稿模式: 未声明的过态闸门降级为 WARN(正式交付禁止使用)

退出码: 0=通过  1=存在 FAIL  2=通过但有 WARN (check-enclosure 模式: 0=合规 1=有违规 2=参数错误)
报告落盘: ~/.fr_dev_kit/runs/gate/gate_report_YYYYMMDD_HHMMSS.md（用户目录，2026-09-29 起）
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
import datetime
import os
import re
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 脚本位于 kfgj/，根目录上移一层


def _runs_dir(*sub):
    """运行痕迹归用户目录（随人走不随套件走，2026-09-29 约定）；不可写时回退套件内 _runs"""
    base = os.path.join(os.path.expanduser("~"), ".fr_dev_kit", "runs")
    try:
        os.makedirs(os.path.join(base, *sub), exist_ok=True)
        return os.path.join(base, *sub)
    except Exception:
        return os.path.join(KIT_ROOT, "_runs", *sub)


RUNS_DIR = _runs_dir("gate")
CONTRACT_MD = os.path.join(KIT_ROOT, "kfgj/EXEC_CONTRACT.md")

# ----------------------------------------------------------------------------
# 闸门注册表（与 kfgj/EXEC_CONTRACT.md 表格一一对应；G07 会校验两边同源）
# kind:   auto=guard 直接执行 / attest=过程闸门,需 --attest 声明 / manual=人工执行
# severity: hard=FAIL 阻断 / warn=仅 WARN
# tasks:  适用任务类型；"any"=全部
# ----------------------------------------------------------------------------
GATES = {
    "G01": {"title": "本机环境已加载(kfgj/env.md 可解析)", "kind": "auto",
            "severity": "warn", "tasks": ["any"], "fn": "gate_env"},
    "G02": {"title": "XML 合法性(ET.parse 通过)", "kind": "auto",
            "severity": "hard", "tasks": ["create", "modify", "format"],
            "fn": "gate_xml", "needs": "cpt"},
    "G03": {"title": "fr_check 静态+98条官方规则校验", "kind": "auto",
            "severity": "hard", "tasks": ["create", "modify", "format"],
            "fn": "gate_fr_check", "needs": "cpt"},
    "G04": {"title": "修改前备份目录存在(_backup_*)", "kind": "auto",
            "severity": "hard", "tasks": ["modify", "format"],
            "fn": "gate_backup", "needs": "cpt"},
    "G05": {"title": "全库引用完整(断链=0)", "kind": "auto",
            "severity": "hard", "tasks": ["any"], "fn": "gate_refs"},
    "G06": {"title": "知识文件含 KB_INDEX 元数据头", "kind": "auto",
            "severity": "hard", "tasks": ["kb"], "fn": "gate_kb_index", "needs": "doc"},
    "G07": {"title": "契约文档(kfgj/EXEC_CONTRACT.md)与本执行器同源", "kind": "auto",
            "severity": "hard", "tasks": ["any"], "fn": "gate_contract_sync"},
    "G08": {"title": "新数据集 SQL 过 verify_sql 闭环(0行=不通过,重试<=3)", "kind": "attest",
            "severity": "hard", "tasks": ["create"]},
    "G09": {"title": "新公式过 eval_formula.js 三态判定", "kind": "attest",
            "severity": "hard", "tasks": ["create", "modify"]},
    "G10": {"title": "改模板前已取 template_snapshot 结构快照", "kind": "attest",
            "severity": "hard", "tasks": ["modify", "format"]},
    "G11": {"title": "写 SQL 前已用 db_schema 探查表结构", "kind": "attest",
            "severity": "hard", "tasks": ["create"]},
    "G12": {"title": "浏览器预览 HTTP 200 且无报错文本(需 FR 运行)", "kind": "manual",
            "severity": "hard", "tasks": ["create", "modify", "format"]},
}

TASK_LABELS = {
    "create": "创建新报表", "modify": "修改已有模板", "format": "纯格式化",
    "error": "排查报错", "kb": "知识库维护",
}


# ----------------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------------
def run_cmd(args, timeout=120):
    """执行子进程，返回 (rc, output_tail)。"""
    try:
        p = subprocess.run(
            args, capture_output=True, cwd=KIT_ROOT, timeout=timeout,
            **({"text": True, "encoding": "utf-8", "errors": "replace"}))
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()
    except Exception as e:  # noqa: BLE001
        return 99, "执行异常: %r" % e


def find_local_env():
    return os.path.join(KIT_ROOT, "kfgj/env.md")


# v2.3 CAR-009: 泳道围栏检查排除目录(仓库工作区扫描时跳过)
ENCLOSURE_EXCLUDE_DIRS = {".git", "_runs", "__pycache__", "node_modules"}


def parse_since(text):
    """解析 --since ISO 时间为本地 naive datetime; 解析失败返回 None。"""
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y%m%d_%H%M%S"):
            try:
                dt = datetime.datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
        else:
            return None
    if dt.tzinfo is not None:  # 带时区输入折算成本地 naive 再比对 mtime
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def run_check_enclosure(lane, since_text):
    """CAR-009: 扫仓库工作区, 列出 mtime>=since 且在泳道目录之外的变更文件。
    返回退出码: 0=合规 1=有违规 2=参数错误。"""
    lane_abs = os.path.abspath(lane)
    if not os.path.isdir(lane_abs):
        print("[FAIL] 泳道目录不存在: %s" % lane_abs)
        return 2
    # --since 缺省: 泳道目录创建时间(Windows getctime); 取不到/异常 → 24h 前
    default_src = "目录创建时间"
    if since_text:
        dt = parse_since(since_text)
        if dt is None:
            print("[FAIL] --since 无法解析为 ISO 时间: %r (示例 2026-09-06T10:00:00)" % since_text)
            return 2
    else:
        try:
            ct = os.path.getctime(lane_abs)
            dt = datetime.datetime.fromtimestamp(ct) if 0 < ct <= time.time() else None
        except (OSError, ValueError, OverflowError):
            dt = None
        if dt is None:
            dt = datetime.datetime.now() - datetime.timedelta(hours=24)
            default_src = "24h 前(创建时间不可得)"
    since_ts = dt.timestamp()

    lane_prefix = lane_abs.rstrip(os.sep) + os.sep
    violations, scanned = [], 0
    for root, dirs, files in os.walk(KIT_ROOT):
        keep = []
        for d in dirs:
            ap = os.path.abspath(os.path.join(root, d))
            if d in ENCLOSURE_EXCLUDE_DIRS:
                continue
            if ap == lane_abs or ap.startswith(lane_prefix):  # 泳道目录整棵放行
                continue
            keep.append(d)
        dirs[:] = keep
        for fn in files:
            ap = os.path.abspath(os.path.join(root, fn))
            if ap.startswith(lane_prefix):  # 泳道内文件不判违规
                continue
            scanned += 1
            try:
                mt = os.path.getmtime(ap)
            except OSError:
                continue
            if mt >= since_ts:
                violations.append((os.path.relpath(ap, KIT_ROOT), mt))

    print("=" * 62)
    print("  泳道围栏检查 --check-enclosure")
    print("  泳道: %s" % lane_abs)
    print("  since: %s (%s)%s" % (dt.isoformat(sep=" "), default_src,
                                  "" if not since_text else "  [用户指定]"))
    print("  扫描文件: %d (排除 %s)" % (scanned, "/".join(sorted(ENCLOSURE_EXCLUDE_DIRS))))
    if violations:
        print("  [FAIL] 违规 %d 处: 泳道目录之外存在 mtime>=since 的变更文件" % len(violations))
        for rel, mt in sorted(violations):
            print("    - %s  (mtime %s)" % (rel, datetime.datetime.fromtimestamp(mt)
                                            .isoformat(sep=" ", timespec="seconds")))
        print("  收口要求: 违规文件回滚或经主控确认后重跑; 泳道只写自己名下文件域")
        print("=" * 62)
        return 1
    print("  [PASS] 合规: 泳道目录之外无 since 后变更")
    print("=" * 62)
    return 0


def run_redo(cmd, timeout=300):
    """CAR-010: 执行 --redo 修复命令(shell), 返回 (rc, 输出)。"""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, cwd=KIT_ROOT,
                           timeout=timeout, **({"text": True, "encoding": "utf-8",
                                                "errors": "replace"}))
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:  # noqa: BLE001
        return 99, "redo 执行异常: %r" % e


# ----------------------------------------------------------------------------
# 自动闸门实现（返回 (status, detail)；status ∈ PASS/FAIL/WARN/SKIP）
# ----------------------------------------------------------------------------
def gate_env(ctx):
    path = find_local_env()
    if not os.path.isfile(path):
        return "WARN", "kfgj/env.md 不存在(换机/首次使用请按 ckzl/bb/外部依赖与归档声明.md知识管理规范-维护流程.md §0.15 模板创建)"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except Exception as e:  # noqa: BLE001
        return "WARN", "读取失败: %r" % e
    has_path = re.search(r"[A-Za-z]:\\\\", txt) or re.search(r"[A-Za-z]:\\", txt)
    has_fr = ("reportlets" in txt) or ("FineReport" in txt) or ("FR10" in txt) or ("FR11" in txt)
    if has_path and has_fr:
        return "PASS", "kfgj/env.md 存在且含 FR 路径信息"
    return "WARN", "kfgj/env.md 存在但未解析出 FR/路径信息，涉路径操作前先补全"


def gate_xml(ctx):
    cpt = ctx.get("cpt")
    if not cpt:
        return "SKIP", "未提供 --cpt"
    import xml.etree.ElementTree as ET
    try:
        ET.parse(cpt)
        return "PASS", "XML 解析通过: %s" % cpt
    except FileNotFoundError:
        return "FAIL", "目标文件不存在: %s" % cpt
    except ET.ParseError as e:
        return "FAIL", "XML 非法(%s；铁律A: >2次修复失败必须还原备份)" % e
    except Exception as e:  # noqa: BLE001
        return "FAIL", "解析异常: %r" % e


def gate_fr_check(ctx):
    cpt = ctx.get("cpt")
    if not cpt:
        return "SKIP", "未提供 --cpt"
    script = os.path.join(KIT_ROOT, "kfgj/fzpy", "fr_check.py")
    if not os.path.isfile(script):
        return "FAIL", "找不到 %s" % script
    if not os.path.isfile(cpt):
        return "FAIL", "目标文件不存在: %s" % cpt
    rc, out = run_cmd([sys.executable, script, cpt], timeout=180)
    tail = "\n".join(out.splitlines()[-6:])
    if "PermissionError" in out or rc == 99:
        return "FAIL", ("fr_check 无法启动(子进程管道被拒或解释器异常)。\n%s\n"
                        "本机自证: python kfgj/fzpy/fr_check.py <cpt>" % tail)
    if rc in (0, 2):
        return "PASS", "fr_check 退出码=%d(0=通过 2=仅警告)\n%s" % (rc, tail)
    return "FAIL", "fr_check 退出码=%d(存在错误)\n%s" % (rc, tail)


def gate_backup(ctx):
    cpt = ctx.get("cpt")
    if not cpt:
        return "SKIP", "未提供 --cpt"
    if ctx.get("no_backup"):
        return "SKIP", "已用 --no-backup 豁免(本次已在报告留痕；连续豁免=流程违规)"
    d = os.path.dirname(os.path.abspath(cpt))
    for depth in range(3):  # 当前目录 + 上两级
        if not os.path.isdir(d):
            break
        hits = [x for x in os.listdir(d) if x.startswith("_backup_")]
        if hits:
            return "PASS", "发现备份目录: %s" % os.path.join(d, sorted(hits)[-1])
        d = os.path.dirname(d)
    return "FAIL", ("未找到 _backup_* 备份目录(铁律A: 修改前必备份)。"
                    "确属只读校验/新建文件用 --no-backup 豁免并留痕")


def gate_refs(ctx):
    script = os.path.join(KIT_ROOT, "kfgj/check_refs.py")
    if not os.path.isfile(script):
        return "FAIL", "找不到 %s" % script
    # 同进程 import 执行（避免子进程管道在受限环境下被拒）
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_refs_mod", script)
    mod = importlib.util.module_from_spec(spec)
    saved_argv = sys.argv
    saved_stdout = sys.stdout
    try:
        import io
        buf = io.StringIO()
        sys.stdout = buf
        sys.argv = ["kfgj/check_refs.py"]
        spec.loader.exec_module(mod)
        rc = mod.main()
    except SystemExit as e:
        rc = e.code or 0
    except Exception as e:  # noqa: BLE001
        return "FAIL", "执行异常: %r" % e
    finally:
        sys.stdout = saved_stdout
        sys.argv = saved_argv
    tail = "\n".join(buf.getvalue().splitlines()[-10:])
    if rc == 0:
        return "PASS", "全库引用完整\n%s" % tail
    return "FAIL", "存在断链(修复后再交付)\n%s" % tail


def gate_kb_index(ctx):
    doc = ctx.get("doc")
    if not doc:
        return "SKIP", "未提供 --doc"
    try:
        with open(doc, "r", encoding="utf-8", errors="replace") as f:
            head = f.read(2000)
    except Exception as e:  # noqa: BLE001
        return "FAIL", "读取失败: %r" % e
    if "KB_INDEX" in head:
        return "PASS", "KB_INDEX 元数据头存在"
    return "FAIL", "缺少 KB_INDEX 头(ckzl/bb/外部依赖与归档声明.md知识管理规范-维护流程.md §0.2 要求所有知识文件带元数据)"


def gate_contract_sync(ctx):
    if not os.path.isfile(CONTRACT_MD):
        return "FAIL", "kfgj/EXEC_CONTRACT.md 不存在"
    with open(CONTRACT_MD, "r", encoding="utf-8", errors="replace") as f:
        txt = f.read()
    md_ids = set(re.findall(r"\bG\d{2}\b", txt))
    code_ids = set(GATES.keys())
    only_md = sorted(md_ids - code_ids)
    only_code = sorted(code_ids - md_ids)
    if only_md or only_code:
        return "FAIL", ("契约文档与执行器不同源: 仅文档有 %s, 仅执行器有 %s"
                        % (only_md or "无", only_code or "无"))
    return "PASS", "kfgj/EXEC_CONTRACT.md 与 kfgj/guard.py 闸门集合一致(%d 条)" % len(code_ids)


# ----------------------------------------------------------------------------
# 动作日志埋点（A124 2026-09-15, 根因 A118: guard 全文 0 处接线致动作日志覆盖率 0%）
# 复用 node_gate 同款形态: from llm_call_logger import log_call + try/except 全兜底,
# 日志失败绝不影响 guard 主流程; KB_AUDIT_TAG 环境变量可选归因(写入 task_id)。
# ----------------------------------------------------------------------------
def _log_trace(phase, status, notes="", artifacts=None, target_file=""):
    """写一条动作日志事件; 任何异常静默吞掉(与 node_gate L227-246 同纪律)。"""
    try:
        aux = os.path.join(KIT_ROOT, "kfgj/fzpy")
        if aux not in sys.path:
            sys.path.insert(0, aux)
        from llm_call_logger import log_call
        log_call(node="guard", phase=phase, tool="guard", status=status,
                 task_id=os.environ.get("KB_AUDIT_TAG") or "",
                 notes=(notes or "")[:300], artifacts=artifacts or [],
                 target_file=target_file or "")
    except Exception:  # noqa: BLE001
        pass


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def select_gates(task):
    return {gid: g for gid, g in GATES.items()
            if "any" in g["tasks"] or task in g["tasks"]}


def gate_headless_render(ctx):
    """G12 headless 通道(v2.1 2026-08-22): 调 kfgj/xlyl/render_check.py。
    退出码映射: 0=PASS 1=FAIL 2=环境不可用(降级 WARN 回退人工)。"""
    cpt = ctx.get("cpt")
    if not cpt:
        return "WARN", "--render 需要 --cpt; 回退人工通道"
    script = os.path.join(KIT_ROOT, "kfgj/xlyl", "render_check.py")
    if not os.path.isfile(script):
        return "WARN", "渲染验证器未安装(kfgj/xlyl/render_check.py), 回退人工通道"
    backend = ctx.get("render_backend", "java")
    try:
        r = subprocess.run(
            [sys.executable, script, cpt, "--backend", backend],
            capture_output=True, text=True, timeout=180,
            encoding="utf-8", errors="replace", cwd=KIT_ROOT)
        tail = "\n       " + "\n       ".join((r.stdout or "").strip().splitlines()[-4:])
        if r.returncode == 0:
            return "PASS", "headless 渲染验证通过(%s)%s" % (backend, tail)
        if r.returncode == 2:
            return "WARN", "渲染后端环境不可用(%s), 回退人工通道%s" % (backend, tail)
        return "FAIL", "headless 渲染验证未通过(%s)%s" % (backend, tail)
    except Exception as e:
        return "WARN", "渲染验证器执行异常(%r), 回退人工通道" % e


def gate_roundtrip(ctx):
    """G12 round-trip 通道(v2.2 2026-08-22): 调 kfgj/xlyl/page2tpl.py 一一核对。
    退出码语义(与 render_check 相反!): 0=PASS全过 2=原模板不可渲染 3=逆向器缺陷。
    环境不可达(agent掉线/设计器未开)从 stderr/reason 识别 → WARN 回退人工。"""
    cpt = ctx.get("cpt")
    if not cpt:
        return "WARN", "--roundtrip 需要 --cpt; 回退人工通道"
    script = os.path.join(KIT_ROOT, "kfgj/xlyl", "page2tpl.py")
    if not os.path.isfile(script):
        return "WARN", "round-trip 工具未安装(kfgj/xlyl/page2tpl.py), 回退人工通道"
    try:
        r = subprocess.run(
            [sys.executable, script, cpt, "--timeout", "300"],
            capture_output=True, text=True, timeout=600,
            encoding="utf-8", errors="replace", cwd=KIT_ROOT)
        out = (r.stdout or "") + (r.stderr or "")
        tail = "\n       " + "\n       ".join(out.strip().splitlines()[-5:])
        if r.returncode == 0:
            return "PASS", "round-trip 一一核对通过(页面⇄模板 T1-T8)%s" % tail
        if "不可达" in out or "19000" in out:
            return "WARN", "渲染环境不可达(agent/设计器未运行), 回退人工通道%s" % tail
        if r.returncode == 2:
            return "FAIL", "模板不可用/损坏(原模板无法渲染 — 问题清单第一类直接证据)%s" % tail
        return "FAIL", "round-trip 核对未通过(布局/值/组件差异,详见报告)%s" % tail
    except Exception as e:
        return "WARN", "round-trip 工具执行异常(%r), 回退人工通道" % e


def main():
    ap = argparse.ArgumentParser(description="fr_dev_kit v2 执行契约闸门执行器")
    ap.add_argument("--task", choices=sorted(TASK_LABELS.keys()), help="任务类型")
    ap.add_argument("--cpt", help="目标 .cpt/.frm 模板路径")
    ap.add_argument("--doc", help="目标知识文件路径(kb 任务用)")
    ap.add_argument("--attest", default="", help="声明已执行的过程闸门,如 G08,G09")
    ap.add_argument("--no-backup", action="store_true", help="豁免 G04 备份闸门(留痕)")
    ap.add_argument("--draft", action="store_true", help="草稿模式:未声明过程闸门降级 WARN")
    ap.add_argument("--render", action="store_true",
                    help="G12 走 headless 渲染验证(kfgj/xlyl/render_check.py, 不传则人工通道)")
    ap.add_argument("--render-backend", default="injected",
                    help="渲染后端: injected(设计器fr-agent,默认,主押路线) | skeleton(纯Python结构预览) | manifest(dry-run) | java(已判死,探针A否定)")
    ap.add_argument("--roundtrip", action="store_true",
                    help="G12 走 round-trip 一一核对(kfgj/xlyl/page2tpl.py, 比 --render 更强: 布局/值/组件逐项核对)")
    ap.add_argument("--check-enclosure", metavar="泳道目录", default=None,
                    help="CAR-009: 扫工作区找出泳道目录外 mtime>=since 的变更文件(独立模式, 不需 --task)")
    ap.add_argument("--since", default=None,
                    help="check-enclosure 起始 ISO 时间; 缺省=泳道目录创建时间(取不到则 24h 前)")
    ap.add_argument("--auto-retry", type=int, default=0, metavar="1",
                    help="CAR-010: FAIL 时自动执行一次 --redo 命令并复检(仅支持 1)")
    ap.add_argument("--redo", default=None, metavar='"<命令>"',
                    help="auto-retry 用的修复命令(shell 执行); 不带 --auto-retry 1 则被忽略并提示")
    ap.add_argument("--list", action="store_true", help="列出全部闸门")
    ap.add_argument("--selftest", action="store_true", help="自检(等价 --task error + G07)")
    args = ap.parse_args()

    # ---- 独立模式: 泳道围栏检查(CAR-009) ----
    if args.check_enclosure:
        if args.task or args.cpt or args.doc:
            print("[FAIL] --check-enclosure 是独立模式, 请勿与 --task/--cpt/--doc 混用")
            return 2
        return run_check_enclosure(args.check_enclosure, args.since)

    if args.auto_retry not in (0, 1):
        ap.error("--auto-retry 仅支持 1 (当前语义: FAIL 后自动执行一次 redo 并复检)")

    if args.list:
        print("闸门清单(kfgj/guard.py v2):")
        for gid, g in sorted(GATES.items()):
            tasks = "/".join(g["tasks"])
            print("  %s [%s|%s] 适用:%-28s %s"
                  % (gid, g["kind"], g["severity"], tasks, g["title"]))
        return 0

    task = args.task or ("error" if args.selftest else None)
    if not task:
        print(__doc__)
        print("示例: python kfgj/guard.py --task modify --cpt xxx.cpt --attest G10")
        return 1

    ctx = {"cpt": os.path.abspath(args.cpt) if args.cpt else None,
           "doc": os.path.abspath(args.doc) if args.doc else None,
           "no_backup": args.no_backup,
           "render": args.render, "render_backend": args.render_backend,
           "roundtrip": args.roundtrip}
    # A124: 任务开始埋点(task 类型 + 目标文件)
    _log_trace(phase="execute", status="ok",
               notes="task=%s cpt=%s doc=%s" % (task, ctx["cpt"] or "-",
                                                ctx["doc"] or "-"),
               target_file=ctx["cpt"] or ctx["doc"] or "")
    attested = {x.strip().upper() for x in args.attest.split(",") if x.strip()}
    gates = select_gates(task)

    results = []  # (gid, status, detail)
    for gid, g in sorted(gates.items()):
        fn = globals().get(g["fn"]) if g["kind"] == "auto" else None
        if g["kind"] == "auto" and fn:
            status, detail = fn(ctx)
        elif g["kind"] == "attest":
            if gid in attested:
                status, detail = "PASS", "已声明在流程中实际执行(--attest)"
            else:
                status = "WARN" if args.draft else "FAIL"
                detail = ("未声明已执行。若确已执行, 收尾命令加 --attest %s ; "
                          "过程闸门不允许跳过" % gid)
        else:  # manual
            if gid == "G12" and ctx.get("roundtrip"):
                status, detail = gate_roundtrip(ctx)
            elif gid == "G12" and ctx.get("render"):
                status, detail = gate_headless_render(ctx)
            else:
                status, detail = "WARN", "人工闸门: 请浏览器预览确认 HTTP 200 无报错后视为通过"
        results.append((gid, g, status, detail))

    # ---- FAIL 自动重试(CAR-010): --auto-retry 1 + --redo "<命令>" ----
    auto_retry_note = ""
    has_fail = any(s == "FAIL" for _, _, s, _ in results)
    if has_fail and (args.auto_retry or args.redo):
        if not args.redo:
            print("提示: --auto-retry 需搭配 --redo \"<修复命令>\" 才生效; 本次未提供 --redo, 参数无效")
        elif not args.auto_retry:
            print("提示: --redo 需搭配 --auto-retry 1 使用; 本次未提供 --auto-retry, 已忽略 --redo")
        else:
            print("-" * 62)
            print("  [auto-retry] 存在 FAIL → 执行 --redo(第 1/1 次): %s" % args.redo)
            rrc, rout = run_redo(args.redo)
            print("  [auto-retry] redo 退出码=%d" % rrc)
            if rout:
                for line in rout.splitlines()[-6:]:
                    print("         %s" % line)
            for i, (gid, g, status, detail) in enumerate(results):
                if status != "FAIL":
                    continue
                if g["kind"] == "auto" and g.get("fn"):
                    s2, d2 = globals()[g["fn"]](ctx)
                    results[i] = (gid, g, s2,
                                  "%s\n       [auto-retry] 首跑 FAIL → redo 后复检结果如上" % d2)
                else:
                    results[i] = (gid, g, status,
                                  "%s\n       [auto-retry] %s 闸门无法由 redo 修复, 维持 FAIL"
                                  % (detail, g["kind"]))
            still_fail = any(s == "FAIL" for _, _, s, _ in results)
            auto_retry_note = ("已自动重试 1 次未果，转待裁决" if still_fail
                               else "auto-retry: redo 后复检通过")

    # ---- 汇总 ----
    n_fail = sum(1 for _, _, s, _ in results if s == "FAIL")
    n_warn = sum(1 for _, _, s, _ in results if s in ("WARN", "SKIP"))
    n_pass = sum(1 for _, _, s, _ in results if s == "PASS")

    icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}
    print("=" * 62)
    print("  fr_dev_kit v2 闸门报告  任务=%s(%s)  模板=%s"
          % (task, TASK_LABELS[task], ctx["cpt"] or "-"))
    print("=" * 62)
    for gid, g, status, detail in results:
        print("%s %s %s" % (icon[status], gid, g["title"]))
        for line in detail.splitlines():
            print("       %s" % line)
    print("-" * 62)
    verdict = ("✅ 通过" if n_fail == 0 and n_warn == 0 else
               ("⚠️ 通过但有 %d 项 WARN/SKIP" % n_warn if n_fail == 0
                else "❌ 未通过: %d 项 FAIL" % n_fail))
    print("  结果: %s   (PASS=%d WARN/SKIP=%d FAIL=%d)"
          % (verdict, n_pass, n_warn, n_fail))
    if auto_retry_note:
        print("  ⚠ %s" % auto_retry_note)

    # ---- 报告落盘 ----
    os.makedirs(RUNS_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rp = os.path.join(RUNS_DIR, "gate_report_%s.md" % ts)
    with open(rp, "w", encoding="utf-8") as f:
        f.write("# 闸门报告 %s\n\n- 任务: %s(%s)\n- 模板: %s\n- 豁免: no_backup=%s draft=%s\n- 结果: %s\n\n"
                % (ts, task, TASK_LABELS[task], ctx["cpt"] or "-", args.no_backup,
                   args.draft, verdict))
        if auto_retry_note:
            f.write("- auto-retry: %s (redo: `%s`)\n\n" % (auto_retry_note, args.redo))
        f.write("| 闸门 | 状态 | 说明 |\n|---|---|---|\n")
        for gid, g, status, detail in results:
            f.write("| %s %s | %s | %s |\n"
                    % (gid, g["title"], status,
                       detail.splitlines()[0].replace("|", "/")[:120]))
    print("  报告: %s" % rp)
    print("=" * 62)
    # A124: 收尾埋点(总退出码 + FAIL/WARN 数, 与 node_gate gate 阶段同形态)
    _log_trace(phase="gate", status="ok" if n_fail == 0 else "fail",
               notes="exit=%d; fail=%d warn=%d pass=%d; report=%s"
                     % (1 if n_fail else (2 if n_warn else 0),
                        n_fail, n_warn, n_pass, os.path.basename(rp)),
               artifacts=[rp], target_file=ctx["cpt"] or ctx["doc"] or "")
    return 1 if n_fail else (2 if n_warn else 0)


if __name__ == "__main__":
    sys.exit(main())
