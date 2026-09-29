#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sql.py — SQL 生成验证闭环工具（借鉴 FR AI 助手 copilot_plan 的强制验证原则）

AI 助手规则原文："SQL 必须验证确保执行没问题才能进行下一步，验证SQL时将参数替换为静态值
进行验证，否则就尝试重新进行上面的步骤最多三次，如果最终没有数据就返回尝试生成失败。"

用法：
    python verify_sql.py <sql_file> [-p para=value ...] [--conn NAME] [--limit N] [--dry]
    python verify_sql.py -s "SELECT * FROM demo_ads.t WHERE year=${year}" -p year=2026

参数宏替换（FR 风格）：
    ${para}                  → 直接替换为 -p 提供的静态值
    ${if(len(para)==0,A,B)}  → 简化解析：len(para)==0 为真取 A，否则取 B；B 中 para 引用替换为值
    未提供值的参数 → 替换为空串并提示（SQL 可能执行失败，正好暴露问题）

连接（默认直连 DWS/GaussDB，FR 连接名 demo_connection=此库）：
    --conn 未指定时用 DWS 直连（psycopg2）
    未来可扩展 FR SQLRunner 通道
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
import re
import sys
import time

DWS_DSN = dict(
    host="YOUR_DWS_HOST", port=8000, dbname="demo_db",
    user="demo_db_user", password="YOUR_DB_PASSWORD",
    options="-c search_path=demo_ads",
)

# ── 2026-09-11 DSN 收敛: 优先读 KIT 根 LOCAL_ENV.local.md「## DB 连接」节, 缺文件/缺字段回落上方硬编码常量 ──
def _load_local_env_dsn():
    """简单键值查找(与 guard.py 读 LOCAL_ENV 同为纯文本惯例): 只解析「## DB 连接」节内的 DSN 字段。"""
    import os, re
    env_md = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "LOCAL_ENV.local.md")
    try:
        with open(env_md, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except Exception:
        return {}
    m = re.search(r"^## DB 连接.*$", txt, re.M)
    if not m:
        return {}
    seg = txt[m.end():]
    nxt = re.search(r"^## ", seg, re.M)
    if nxt:
        seg = seg[:nxt.start()]
    dsn = {}
    for k, v in re.findall(r"(host|port|dbname|user|password|pwd)\s*=\s*([^\s]+)", seg):
        dsn["password" if k == "pwd" else k] = v
    if isinstance(dsn.get("port"), str) and dsn["port"].isdigit():
        dsn["port"] = int(dsn["port"])
    return dsn

DWS_DSN.update({k: v for k, v in _load_local_env_dsn().items() if v})

PARAM_RE = re.compile(r"\$\{([^}]+)\}")


def replace_fr_macro(sql, params):
    """替换 FR 参数宏为静态值。返回 (替换后SQL, 警告列表)。"""
    warnings = []

    def repl(m):
        inner = m.group(1).strip()

        # ${if(len(para)==0,A,B)} 形式
        ifm = re.match(r'^if\(\s*len\((\w+)\)\s*==\s*0\s*,(.*)\)$', inner, re.S)
        if ifm:
            pname = ifm.group(1)
            branches = ifm.group(2)
            # 分支可能含逗号，粗分：取最后一个逗号前的为 A，其后为 B
            parts = split_top_level_commas(branches)
            if len(parts) >= 2:
                a_branch = ",".join(parts[:-1])
                b_branch = parts[-1]
            else:
                warnings.append(f"无法解析 if 分支: {inner}")
                return ""
            a_branch = a_branch.strip()
            b_branch = b_branch.strip()
            # 去掉外层引号（FR 宏分支常带双引号）
            a_branch = unquote(a_branch)
            b_branch = unquote(b_branch)
            if pname in params:
                val = params[pname]
                if val == "":
                    return a_branch  # 空值 → 空条件分支
                # 值分支里的参数引用替换（处理 FR 拼接语法 "..."+"para"+"..."）
                b_branch = re.sub(r'"\s*\+\s*(\w+)\s*\+\s*"', r"\g<1>", b_branch)  # "+para+" → para
                b_branch = b_branch.replace('"', "")
                b_branch = re.sub(r"\b" + pname + r"\b", val, b_branch)
                return b_branch
            else:
                warnings.append(f"参数 {pname} 未提供值，if 分支取空条件分支")
                return a_branch

        # ${para} 形式
        if inner in params:
            return params[inner]
        # 带引号形式 "${para}" 已由外层处理
        warnings.append(f"参数 {inner} 未提供值 → 替换为空串")
        return ""

    out = PARAM_RE.sub(repl, sql)
    return out, warnings


def split_top_level_commas(s):
    """按顶层逗号分割（忽略引号内逗号）。"""
    parts, depth, cur = [], 0, ""
    in_str = None
    for ch in s:
        if in_str:
            cur += ch
            if ch == in_str:
                in_str = None
            continue
        if ch in "\"'":
            in_str = ch
            cur += ch
        elif ch == "(":
            depth += 1
            cur += ch
        elif ch == ")":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def run_psycopg2(sql, limit):
    import psycopg2
    conn = psycopg2.connect(**DWS_DSN)
    cur = conn.cursor()
    t0 = time.time()
    cur.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchmany(limit)
    dur = time.time() - t0
    cur.close()
    conn.close()
    return cols, rows, dur


def main():
    ap = argparse.ArgumentParser(description="SQL 生成验证（FR 参数宏替换 + 真实执行）")
    ap.add_argument("sql_file", nargs="?", help="SQL 文件路径")
    ap.add_argument("-s", "--sql", help="SQL 字符串")
    ap.add_argument("-p", dest="params", action="append", default=[], metavar="para=value", help="参数静态值")
    ap.add_argument("--conn", default="DWS", help="连接名（默认 DWS 直连）")
    ap.add_argument("--limit", type=int, default=5, help="显示行数（默认5）")
    ap.add_argument("--dry", action="store_true", help="只替换宏不执行")
    args = ap.parse_args()

    if args.sql_file:
        with open(args.sql_file, encoding="utf-8") as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        ap.error("需要 sql_file 或 -s")

    params = {}
    for p in args.params:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k.strip()] = v.strip()

    final_sql, warnings = replace_fr_macro(sql, params)
    print("=" * 60)
    print("[参数宏替换]")
    for w in warnings:
        print(f"  ⚠ {w}")
    print(f"  params: {params if params else '(无)'}")

    if args.dry:
        print("=" * 60)
        print("[DRY] 替换后 SQL:")
        print(final_sql)
        return 0

    print("=" * 60)
    print(f"[执行验证] conn={args.conn}")
    try:
        cols, rows, dur = run_psycopg2(final_sql, args.limit)
    except Exception as e:
        print(f"  ❌ 执行失败: {e}")
        print("=" * 60)
        print("[DRY] 替换后 SQL（供检查）:")
        print(final_sql)
        return 1

    print(f"  ✅ 执行成功  列数={len(cols)}  耗时={dur:.2f}s")
    print(f"  列: {', '.join(cols)}")
    if not rows:
        print("  ⚠ 0 行数据 —— 按 AI 助手规则应视为验证不通过，需调整 SQL")
        return 2
    print(f"  前 {len(rows)} 行:")
    for r in rows:
        print("    " + " | ".join(str(x)[:30] if x is not None else "NULL" for x in r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
