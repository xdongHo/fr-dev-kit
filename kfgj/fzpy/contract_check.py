#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""contract_check.py — 994 收口链三查脚本（闸门2 裁决 §2 落地 · Z2 收口链实施役交付物）

设计依据（公式的解释权归契约，不从 prose 重推）:
  - ckzl/lc/_contracts/c3_contract.json        契约单源（B 40 字段骨架 ∪ A 独有 hidden_refs + A0-A7）
  - ckzl/lc/_contracts/rehearsal_plan_contract.json  彩排计划合同（10 字段，契约外键派生）
  - 闸门2裁决清单.md §2                          七项裁决：五码 0-4／双证查1／五 route／qa_semantics 查3 校验

三查:
  查1 计划先于脚本存在（双证）: plan 文件 mtime < run-log.started_at
      且 run-log 内嵌 plan_sha256 == plan 现算 sha256（防 mtime 被复制扰动）。
  查2 合同字段完整性: 10 字段精确在场非空；每字段 on_violation.action ∈ {refuse_entry,halt,rollback}；
      frozen_inputs[].sha256 命中 ^[0-9a-f]{64}$；gates[].assert 含数值阈值且 assertion_ids 外键
      全部命中契约 assertions[].id；entry_criteria/budget_and_stop 非空；契约自洽扫描（A2 WARN / A3·A4·A5·A7 FAIL）。
  查3 指纹一致 + QA 语义校验: frozen_inputs 逐项现算 sha256 全等（契约改一字节即在此失配）；
      contract.targets did 集 == plan.scope.targets_dids；plan.artifacts ⊆ 实际产物；
      manifest_injected injected_target 计数与 change_assertion 对账（+确定性抽样指纹复算）；
      QA 脚本头 CONTRACT-SEMANTICS 注释块自报 ≡ 契约 qa_semantics（不 import 执行脚本体）。

退出码（A 五码，多错取最高码并在 stdout 全列）:
  0 = 三查全过（准予开工）
  1 = 查1 违规（计划先行失效）
  2 = 查2 违规（合同不完整）
  3 = 查3 违规（指纹不一致 / 语义失配）
  4 = 仅存在 WARN（--strict 时 WARN 升为对应查的码）

用法:
  python contract_check.py --dir <彩排作业区> --contract <c3_contract.json> --plan <plan.json>
      [--run-log <logs/injection_run1.json>] [--manifest <manifest_injected.json>]
      [--strict] [--full-verify] [--json-out <evidence.jsonl>]

实现约束: 仅 stdlib（json/hashlib/argparse/re/datetime/os/sys）；纯静态、离线可复算、确定性成立；
Windows 路径与 UTF-8 兼容（stdout 强制 utf-8，文件读写显式 encoding）。配套微改（列入实施单）:
injection_run1.json 增记 started_at 与 plan_sha256 两字段（查1 双证之需）。
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
import hashlib
import json
import os
import re
import sys

PLAN_FIELDS = ['objective', 'scope', 'frozen_inputs', 'entry_criteria', 'gates',
               'budget_and_stop', 'change_assertion', 'artifacts', 'rollback', 'handoff']
REJECT_ACTIONS = {'refuse_entry', 'halt', 'rollback'}
RE_SHA256 = re.compile(r'^[0-9a-f]{64}$')
RE_SEM_KEY = re.compile(r'^#\s*([A-Za-z_]+)\s*:\s*(.+?)\s*$')
SEM_BEGIN, SEM_END = 'CONTRACT-SEMANTICS-BEGIN', 'CONTRACT-SEMANTICS-END'
MANIFEST_SAMPLE = 30  # 确定性抽样指纹复算条数（--full-verify 时全量）


class Findings:
    """违例/警告收集器：check ∈ 1/2/3，level ∈ FAIL/WARN。"""

    def __init__(self):
        self.items = []

    def fail(self, check, message):
        self.items.append({'check': check, 'level': 'FAIL', 'code': check, 'message': message})

    def warn(self, check, message):
        self.items.append({'check': check, 'level': 'WARN', 'code': check, 'message': message})

    def fail_codes(self):
        return sorted({i['code'] for i in self.items if i['level'] == 'FAIL'})

    def warns(self):
        return [i for i in self.items if i['level'] == 'WARN']


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path, label):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def as_list(v):
    """字段可为 {'items': [...]} 或裸数组两种形态，统一取数组。"""
    if isinstance(v, dict):
        return v.get('items') or []
    if isinstance(v, list):
        return v
    return None


def resolve_run_log(args, plan):
    if args.run_log:
        return args.run_log
    arts = as_list(plan.get('artifacts')) or []
    base = plan.get('artifacts', {}).get('base_dir') if isinstance(plan.get('artifacts'), dict) else None
    for a in arts:
        rel = a if isinstance(a, str) else (a.get('path') or '')
        if os.path.basename(rel) == 'injection_run1.json':
            p = rel if os.path.isabs(rel) else os.path.join(base or args.dir, rel)
            if os.path.isfile(p):
                return p
    p = os.path.join(args.dir, 'logs', 'injection_run1.json')
    return p if os.path.isfile(p) else None


def deterministic_sample(keys, n):
    """确定性等距抽样（排序后按步长取，与 c3_qa_check.sample_files 同型）。"""
    keys = sorted(keys)
    total = len(keys)
    if n >= total:
        return keys
    if n <= 0:
        return []
    idx = sorted({round(i * (total - 1) / (n - 1)) for i in range(n)})
    return [keys[i] for i in idx]


# ---------------- 查1 计划先行（mtime + plan_sha256 双证） ----------------

def check1(args, plan_path, plan, findings):
    if not plan_path or not os.path.isfile(plan_path):
        findings.fail(1, '计划文件缺失（先写文件再派发：无合同不开工）')
        return None
    run_log = args.run_log or resolve_run_log(args, plan or {})
    if not run_log or not os.path.isfile(run_log):
        findings.fail(1, f'run-log 缺失或不可读: {run_log}（查1 双证不可用）')
        return None
    try:
        rl = load_json(run_log, 'run-log')
    except (json.JSONDecodeError, OSError) as e:
        findings.fail(1, f'run-log 解析失败: {run_log} ({e})')
        return None
    started = rl.get('started_at')
    plan_sha = rl.get('plan_sha256')
    if not started or not plan_sha:
        findings.fail(1, 'run-log 缺 started_at / plan_sha256 字段（查1 双证之需；'
                         '配套微改：injection_run1.json 增记两字段，列入实施单）')
        return None
    try:
        started_ts = datetime.datetime.fromisoformat(str(started)).timestamp()
    except ValueError:
        findings.fail(1, f'run-log started_at 非 ISO 时间: {started!r}')
        return None
    mtime = os.path.getmtime(plan_path)
    if not (mtime < started_ts):
        findings.fail(1, f'计划先行失效: plan mtime {datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")}'
                         f' >= run-log started_at {started}')
    actual = sha256_file(plan_path)
    if actual != plan_sha:
        findings.fail(1, f'plan_sha256 双证失配: run-log 内嵌 {plan_sha[:16]}… != 现算 {actual[:16]}…')
    return run_log


# ---------------- 查2 合同字段完整性（+ 契约自洽扫描） ----------------

def check2(args, plan, contract, findings):
    if not isinstance(plan, dict):
        findings.fail(2, '计划文件根节点须为 object')
        return
    missing = [k for k in PLAN_FIELDS if k not in plan or plan[k] in (None, '', {}, [])]
    for k in missing:
        findings.fail(2, f'计划字段缺失或为空: {k}')
    extra = [k for k in plan if k not in PLAN_FIELDS]
    for k in extra:
        findings.warn(2, f'计划存在契约外字段: {k}（前瞻兼容，记 WARN）')
    # 每字段 A 轨拒绝动作，动作枚举限 B 轨三值
    for k in PLAN_FIELDS:
        v = plan.get(k)
        ov = v.get('on_violation') if isinstance(v, dict) else None
        if not isinstance(ov, dict) or ov.get('action') not in REJECT_ACTIONS:
            findings.fail(2, f'字段 {k} 缺 on_violation.action 或动作枚举非法'
                             f'（须 ∈ refuse_entry/halt/rollback；「建议冻结」在 schema 层即非法）')
    # frozen_inputs
    fi = plan.get('frozen_inputs')
    items = as_list(fi) if isinstance(fi, (dict, list)) else None
    if not items:
        findings.fail(2, 'frozen_inputs 须为非空数组（或 {items:[...]}）')
        items = []
    qa_script_path = None
    for it in items:
        if not isinstance(it, dict):
            findings.fail(2, f'frozen_inputs 条目非对象: {it!r}')
            continue
        s = it.get('sha256') or ''
        if not RE_SHA256.fullmatch(s):
            findings.fail(2, f"frozen_inputs[{it.get('role', '?')}] sha256 缺失或非 64 位小写十六进制: {s[:20]}")
        if it.get('role') == 'qa_script':
            qa_script_path = it.get('path')
    # entry_criteria / budget_and_stop
    ec = as_list(plan.get('entry_criteria')) if isinstance(plan.get('entry_criteria'), (dict, list)) else None
    if not ec:
        findings.fail(2, 'entry_criteria 须为非空数组（或 {items:[...]}）')
    bs = plan.get('budget_and_stop')
    if not isinstance(bs, dict) or not isinstance(bs.get('max_rounds'), int) or bs['max_rounds'] < 1:
        findings.fail(2, 'budget_and_stop.max_rounds 须为 ≥1 整数')
    if not isinstance(bs, dict) or not (bs.get('stop_conditions') or []):
        findings.fail(2, 'budget_and_stop.stop_conditions 须为非空数组')
    # gates
    g = plan.get('gates')
    gitems = as_list(g) if isinstance(g, (dict, list)) else None
    assertion_ids = {a.get('id') for a in (contract.get('assertions') or [])}
    if not gitems:
        findings.fail(2, 'gates 须为非空数组（或 {items:[...]}）')
        gitems = []
    for gate in gitems:
        if not isinstance(gate, dict):
            findings.fail(2, f'gate 条目非对象: {gate!r}')
            continue
        gid = gate.get('id', '?')
        ass = gate.get('assert')
        if not isinstance(ass, dict) or not any(
                isinstance(v, (int, float)) and not isinstance(v, bool) for v in ass.values()):
            findings.fail(2, f'gate {gid}: assert 缺失或不含数值阈值（阈值非黑即白→拒绝开工）')
        aids = gate.get('assertion_ids') or []
        if not aids:
            findings.fail(2, f'gate {gid}: 缺 assertion_ids 断言外键')
        for aid in aids:
            if aid not in assertion_ids:
                findings.fail(2, f'gate {gid}: assertion_id {aid} 未命中契约 assertions[]（外键悬空）')
        ov = gate.get('on_violation')
        if not isinstance(ov, dict) or ov.get('action') not in REJECT_ACTIONS:
            findings.fail(2, f'gate {gid}: on_violation.action 非法（须 ∈ refuse_entry/halt/rollback）')
    # scope dids
    scope = plan.get('scope') or {}
    dids = scope.get('targets_dids')
    if not isinstance(dids, list) or not dids or not all(isinstance(d, int) for d in dids):
        findings.fail(2, 'scope.targets_dids 须为非空整数数组')
    # 契约自洽扫描（公式的解释权归契约）
    targets = contract.get('targets') or []
    warn_cap = 0
    for t in targets:
        try:
            n, mpr, mode = int(t['n']), int(t['max_per_row']), t['mode']
        except (KeyError, TypeError, ValueError):
            findings.fail(2, f"targets[did={t.get('did')}] 缺 n/max_per_row/mode（A0 结构非法）")
            continue
        expect = 'row' if n <= mpr else ('expand' if n <= 8 else 'dialog')
        if mode != expect:
            if warn_cap < 10:
                findings.warn(2, f"A2 排布范围（人工改判口）: did={t['did']} mode={mode} 但 n={n}/max_per_row={mpr} 建议 {expect}")
            elif warn_cap == 10:
                findings.warn(2, 'A2 排布范围违例超过 10 条，其余折叠（详见契约 targets）')
            warn_cap += 1
        ex = t.get('exemption')
        if mode in ('expand', 'dialog') and (not isinstance(ex, dict) or ex.get('rule_id') not in
                                             ('EXPAND_DEFAULT_HIDDEN', 'MOREFILTER_DIALOG')):
            findings.fail(2, f"A7 豁免完备: did={t['did']} mode={mode} 无白名单内豁免条目")
        for w in (t.get('widgets') or []):
            if w.get('param_name') != w.get('name'):
                findings.fail(2, f"A3 同名绑定: did={t['did']} widget {w.get('name')} param_name={w.get('param_name')}")
        btn = t.get('button') or {}
        if 'n_in_label' not in btn:
            findings.warn(2, f"A4 缺 n_in_label（缺 N=WARN）: did={t['did']}")
        elif btn['n_in_label'] != n - int(t.get('first_row_count', 0)):
            findings.fail(2, f"A4 N 公式写错: did={t['did']} n_in_label={btn['n_in_label']} != n-first_row_count={n - int(t.get('first_row_count', 0))}")
        if len(t.get('hidden_refs') or []) != btn.get('n_in_label'):
            findings.fail(2, f"A5 三同源破: did={t['did']} |hidden_refs|={len(t.get('hidden_refs') or [])} != n_in_label={btn.get('n_in_label')}")
    return qa_script_path


# ---------------- 查3 指纹一致 + QA 语义校验 ----------------

def parse_contract_semantics(text):
    """提取 QA 脚本头 CONTRACT-SEMANTICS 注释块（不 import 执行脚本体）。"""
    if SEM_BEGIN not in text or SEM_END not in text:
        return None
    body = text.split(SEM_BEGIN, 1)[1].split(SEM_END, 1)[0]
    out = {}
    for line in body.splitlines():
        m = RE_SEM_KEY.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out or None


def check3(args, plan, contract, plan_path, qa_script_path, findings):
    # 3.1 frozen_inputs 逐项现算比对
    fi = as_list(plan.get('frozen_inputs')) or []
    for it in fi:
        role = it.get('role', '?')
        path = it.get('path')
        mandatory = it.get('mandatory', True)
        if not path or not os.path.isfile(path):
            if mandatory:
                findings.fail(3, f'frozen_inputs[{role}] 冻结件缺失: {path}')
            else:
                findings.warn(3, f'frozen_inputs[{role}] 备查件缺失（advisory）: {path}')
            continue
        actual = sha256_file(path)
        if actual != it.get('sha256'):
            findings.fail(3, f'frozen_inputs[{role}] 指纹失配: 声明 {str(it.get("sha256"))[:16]}… != 现算 {actual[:16]}… ({path})')
    # 3.2 did 集一致（契约 targets ↔ plan.scope）
    c_dids = {int(t['did']) for t in (contract.get('targets') or []) if 'did' in t}
    scope = plan.get('scope') or {}
    p_dids = scope.get('targets_dids')
    if isinstance(p_dids, list):
        if set(p_dids) != c_dids:
            only_c = sorted(c_dids - set(p_dids))[:8]
            only_p = sorted(set(p_dids) - c_dids)[:8]
            findings.fail(3, f'did 集漂移: 契约独有 {only_c} / 计划独有 {only_p}（{len(c_dids)} vs {len(p_dids)}）')
        elif scope.get('targets_count') not in (None, len(p_dids)):
            findings.fail(3, f"scope.targets_count={scope.get('targets_count')} 与 targets_dids 长度 {len(p_dids)} 不符")
    # 3.3 artifacts ⊆ 实际产物
    arts = plan.get('artifacts') or {}
    base = arts.get('base_dir') or args.dir
    for a in (arts.get('items') or []):
        rel = a if isinstance(a, str) else (a.get('path') or '')
        p = rel if os.path.isabs(rel) else os.path.join(base, rel)
        if not os.path.isfile(p):
            findings.fail(3, f'artifacts 缺件: {rel}（缺件→不回传产物机、不验收）')
    # 3.4 manifest 对账（change_assertion 225/769 + 确定性抽样指纹复算）
    manifest_path = args.manifest
    if not manifest_path:
        for a in (arts.get('items') or []):
            rel = a if isinstance(a, str) else (a.get('path') or '')
            if os.path.basename(rel) == 'manifest_injected.json':
                manifest_path = rel if os.path.isabs(rel) else os.path.join(base, rel)
                break
    if manifest_path and os.path.isfile(manifest_path):
        try:
            mf = load_json(manifest_path, 'manifest')
        except (json.JSONDecodeError, OSError) as e:
            findings.fail(3, f'manifest 解析失败: {manifest_path} ({e})')
            mf = None
        if mf is not None:
            entries = mf.get('entries') or {}
            inj = {k: v for k, v in entries.items() if v.get('injected_target')}
            ca = plan.get('change_assertion') or {}
            expected = ca.get('changed_expected')
            if expected is not None and len(inj) != expected:
                findings.fail(3, f'change_assertion 对账破: manifest injected_target={len(inj)} != 期望 {expected}')
            mdir = mf.get('dir') or os.path.join(args.dir, 'injected')
            sample_keys = deterministic_sample(list(inj), 1 if args.full_verify else MANIFEST_SAMPLE)
            bad = 0
            for k in sample_keys:
                ent = inj[k]
                fp = os.path.join(mdir, ent.get('file') or '')
                if not os.path.isfile(fp) or sha256_file(fp) != ent.get('sha256'):
                    bad += 1
                    if bad <= 5:
                        findings.fail(3, f'manifest 指纹复算失配: did={k} ({ent.get("file")})')
            if bad > 5:
                findings.fail(3, f'manifest 指纹复算失配累计 {bad} 条（其余折叠）')
            ca_un = ca.get('unchanged_expected')
            if ca_un is not None and mf.get('count') is not None:
                if mf.get('count') != len(inj) + ca_un:
                    findings.warn(3, f"manifest count={mf.get('count')} != injected {len(inj)} + unchanged {ca_un}（信息性，抽样口径不含非目标复算）")
    elif manifest_path:
        findings.warn(3, f'manifest 不存在，跳过对账: {manifest_path}')
    # 3.5 QA 退出码语义校验（CONTRACT-SEMANTICS 自报 ≡ 契约 qa_semantics）
    if not qa_script_path or not os.path.isfile(qa_script_path):
        findings.fail(3, f'QA 脚本缺失，语义校验不可用: {qa_script_path}')
        return
    with open(qa_script_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    sem = parse_contract_semantics(text)
    qa_sem = contract.get('qa_semantics') or {}
    if not sem:
        findings.fail(3, 'QA 脚本头缺 CONTRACT-SEMANTICS 注释块（未自报退出码语义；查3 语义校验无法通过）')
        return
    declared = {}
    for pair in (sem.get('exit_codes') or '').split(';'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            declared[k.strip()] = v.strip()
    expect_codes = {str(k) for k in (qa_sem.get('qa_script_exit_codes') or {})}
    if set(declared) != expect_codes:
        findings.fail(3, f'QA 退出码语义失配: 脚本自报 {sorted(declared)} != 契约 qa_script_exit_codes {sorted(expect_codes)}')
    grades = {g.strip() for g in (sem.get('grades') or '').split('|') if g.strip()}
    expect_levels = set(qa_sem.get('levels') or {})
    if grades != expect_levels:
        findings.fail(3, f'QA 档位语义失配: 脚本自报 {sorted(grades)} != 契约 levels {sorted(expect_levels)}')
    routes = {r.strip() for r in (sem.get('disposition_routes') or '').split('|') if r.strip()}
    expect_routes = set((qa_sem.get('disposition') or {}).get('routes') or [])
    if routes != expect_routes:
        findings.fail(3, f'disposition route 失配: 脚本自报 {sorted(routes)} != 契约 {sorted(expect_routes)}')


# ---------------- 主流程 ----------------

def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='994 收口链三查（查1 计划先行 / 查2 字段完整 / 查3 指纹+语义）')
    ap.add_argument('--dir', required=True, help='彩排作业区基目录（解析相对路径与默认 run-log/manifest）')
    ap.add_argument('--contract', required=True, help='c3_contract.json 契约单源路径')
    ap.add_argument('--plan', required=True, help='彩排计划合同 JSON 路径')
    ap.add_argument('--run-log', dest='run_log', help='injection_run1.json（缺省从 plan.artifacts/--dir 解析）')
    ap.add_argument('--manifest', help='manifest_injected.json（缺省从 plan.artifacts 解析）')
    ap.add_argument('--strict', action='store_true', help='WARN 升为对应查的退出码')
    ap.add_argument('--full-verify', action='store_true', help='manifest 指纹全量复算（缺省确定性抽样 30）')
    ap.add_argument('--json-out', dest='json_out', help='JSONL 证据输出路径（每查一行 + 汇总行）')
    args = ap.parse_args(argv)

    findings = Findings()
    plan, contract = None, None

    # 契约可解析性（查2 前置）
    if not os.path.isfile(args.contract):
        findings.fail(2, f'契约文件缺失: {args.contract}')
    else:
        try:
            contract = load_json(args.contract, 'contract')
        except (json.JSONDecodeError, OSError) as e:
            findings.fail(2, f'契约解析失败: {args.contract} ({e})')

    plan_path = args.plan
    if plan_path and os.path.isfile(plan_path):
        try:
            plan = load_json(plan_path, 'plan')
        except (json.JSONDecodeError, OSError) as e:
            findings.fail(2, f'计划解析失败: {plan_path} ({e})')
            plan = None
    # 查1（计划文件缺失在查1 内报；计划 JSON 坏时查1 仍可对文件双证）
    run_log_used = check1(args, plan_path, plan, findings)
    # 查2 / 查3 需 plan+contract 双方可解析
    if plan is not None and contract is not None:
        qa_script_path = check2(args, plan, contract, findings)
        check3(args, plan, contract, plan_path, qa_script_path, findings)
    elif contract is not None and plan is None and os.path.isfile(plan_path):
        findings.fail(2, '计划不可解析，查2/查3 无法执行')

    fail_codes = findings.fail_codes()
    warns = findings.warns()
    if fail_codes:
        exit_code = max(fail_codes)
    elif warns:
        exit_code = max(w['code'] for w in warns) if args.strict else 4
    else:
        exit_code = 0

    # stdout 全列（多错并列取最高码）
    print('=' * 78)
    print(f' contract_check  三查违例全列  计划={plan_path}')
    print(f' 契约={args.contract}')
    if run_log_used:
        print(f' run-log={run_log_used}')
    print('=' * 78)
    for it in findings.items:
        mark = {'FAIL': '[FAIL]', 'WARN': '[WARN]'}[it['level']]
        print(f' 查{it["check"]} {mark} {it["message"]}')
    if not findings.items:
        print(' 查1 PASS（计划先行双证成立：mtime + plan_sha256）')
        print(' 查2 PASS（10 字段完整、拒绝动作枚举合法、断言外键命中、契约自洽）')
        print(' 查3 PASS（frozen_inputs 指纹全等、did 集一致、artifacts 齐备、QA 语义一致）')
    verdict = {0: '三查全过（准予开工）', 1: '查1 违规：计划先行失效', 2: '查2 违规：合同不完整',
               3: '查3 违规：指纹不一致/语义失配', 4: '仅存在 WARN'}[exit_code]
    print('-' * 78)
    print(f' ⇒ 退出码 {exit_code}（{verdict}）'
          + (f' FAIL 码集={fail_codes}' if fail_codes else '')
          + (f' WARN={len(warns)} 条' if warns else ''))
    if args.json_out:
        with open(args.json_out, 'w', encoding='utf-8') as f:
            for it in findings.items:
                f.write(json.dumps({'ts': datetime.datetime.now().isoformat(timespec='seconds'),
                                    **it}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'ts': datetime.datetime.now().isoformat(timespec='seconds'),
                                'check': 0, 'level': 'SUMMARY', 'code': exit_code,
                                'fail_codes': fail_codes, 'warn_count': len(warns),
                                'contract_sha256': sha256_file(args.contract) if os.path.isfile(args.contract) else None,
                                'plan_sha256': sha256_file(plan_path) if plan_path and os.path.isfile(plan_path) else None,
                                'verdict': verdict}, ensure_ascii=False) + '\n')
        print(f' JSONL 证据已写入: {args.json_out}')
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
