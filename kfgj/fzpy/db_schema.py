#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_schema.py — 数据库/数据集结构探查（借鉴 FR AI 助手 DatasetTools/DataSetFetcherTools）

AI 助手工具能力（逆向）：
    getTables(conn)            → 数据连接中所有表
    getColNames(conn, table)   → 指定表所有字段名+类型
    getColumnsFromDataset(ds)  → 数据集字段清单
    getDataSetData(ds)         → 数据集前几条数据
    getSqlFromDataset(ds)      → 数据集原始SQL
我们落地：DWS/GaussDB 直连探查（不依赖 FR 运行时），开发数据集 SQL 前的标准动作。

用法：
    python db_schema.py --tables                          # 连接所有表
    python db_schema.py demo_ads.fin_copa_input_detail_basedata          # 表字段(名/类型/注释)
    python db_schema.py demo_ads.fin_copa_input_detail_basedata --sample # + 前3行样例
    python db_schema.py --sql "SELECT oem, sales FROM ..." --sample     # 任意SQL字段+样例
    python db_schema.py --search 表名关键字                             # 模糊搜表

输出 JSON（或表格），可直接作为开发/LLM 上下文。
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
import sys

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


def connect():
    import psycopg2
    return psycopg2.connect(**DWS_DSN)


def split_table(t):
    """'schema.table' → (schema, table)；纯表名用默认 schema。"""
    if "." in t:
        s, tb = t.split(".", 1)
        return s, tb
    return "demo_ads", t


def list_tables(keyword=None, all_schema=False):
    conn = connect()
    cur = conn.cursor()
    sql = ("SELECT table_schema, table_name, obj_description((quote_ident(table_schema)||'.'||quote_ident(table_name))::regclass) "
           "FROM information_schema.tables WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema')")
    conds, params = [], []
    if not all_schema:
        conds.append("table_schema = %s")
        params.append("demo_ads")
    if keyword:
        conds.append("(table_name ILIKE %s OR table_schema ILIKE %s)")
        params += [f"%{keyword}%", f"%{keyword}%"]
    if conds:
        sql += " AND " + " AND ".join(conds)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"schema": r[0], "table": r[1], "comment": r[2]} for r in rows]


def table_columns(table, sample=False, limit=3):
    schema, tb = split_table(table)
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT column_name, data_type, COALESCE(character_maximum_length::text,''), "
        "COALESCE(column_default,''), is_nullable, col_description(cl.oid, a.attnum) "
        "FROM information_schema.columns c "
        "JOIN pg_attribute a ON a.attrelid = (quote_ident(%s)||'.'||quote_ident(%s))::regclass AND a.attname = c.column_name "
        "JOIN pg_class cl ON cl.oid = a.attrelid "
        "WHERE c.table_schema=%s AND c.table_name=%s ORDER BY c.ordinal_position",
        (schema, tb, schema, tb))
    cols = [{"name": r[0], "type": r[1] + (f"({r[2]})" if r[2] else ""),
             "default": r[3], "nullable": r[4] == "YES", "comment": r[5]} for r in cur.fetchall()]
    out = {"schema": schema, "table": tb, "columns": cols}
    if sample:
        try:
            cur.execute(f'SELECT * FROM "{schema}"."{tb}" LIMIT {limit}')
            rows = cur.fetchall()
            names = [d[0] for d in cur.description]
            out["sample"] = [dict(zip(names, [str(v)[:40] if v is not None else None for v in r])) for r in rows]
            out["sample_row_count"] = len(rows)
        except Exception as e:
            out["sample_error"] = str(e)
    cur.close()
    conn.close()
    return out


def sql_schema(sql, sample=False, limit=3):
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    names = [d[0] for d in cur.description]
    out = {"columns": [{"name": n, "type": str(d.type_code)} for n, d in zip(names, cur.description)],
           "sql": sql}
    if sample:
        rows = cur.fetchmany(limit)
        out["sample"] = [dict(zip(names, [str(v)[:40] if v is not None else None for v in r])) for r in rows]
        out["sample_row_count"] = len(rows)
    cur.close()
    conn.close()
    return out


def main():
    ap = argparse.ArgumentParser(description="数据库/数据集结构探查（DWS 直连）")
    ap.add_argument("table", nargs="?", help="表名（schema.table 或 demo_ads 默认）")
    ap.add_argument("--tables", action="store_true", help="列出连接所有表(默认仅 demo_ads schema)")
    ap.add_argument("--all-schema", action="store_true", help="--tables 时列出所有 schema(可能权限受限)")
    ap.add_argument("--search", default=None, help="按关键字模糊搜表")
    ap.add_argument("--sql", default=None, help="任意 SQL 探查字段")
    ap.add_argument("--sample", action="store_true", help="附带前3行样例数据")
    ap.add_argument("--json", action="store_true", help="JSON 输出（默认表格）")
    args = ap.parse_args()

    try:
        if args.tables or args.search:
            data = list_tables(args.search, args.all_schema)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(f"共 {len(data)} 张表")
                for r in data:
                    print(f"  {r['schema']}.{r['table']}" + (f"  -- {r['comment']}" if r["comment"] else ""))
            return 0
        if args.sql:
            data = sql_schema(args.sql, args.sample)
        elif args.table:
            data = table_columns(args.table, args.sample)
        else:
            ap.error("需要 table 或 --tables 或 --sql")
            return 1

        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"== {data.get('schema','')}.{data.get('table', data.get('sql','')[:40])} ==")
            for c in data["columns"]:
                extra = ""
                if "comment" in c and c["comment"]:
                    extra = f"  -- {c['comment']}"
                if "nullable" in c:
                    extra += "" if c["nullable"] else "  NOT NULL"
                print(f"  {c['name']:<40} {c['type']}{extra}")
            if "sample" in data and data["sample"]:
                print(f"-- 样例 {len(data['sample'])} 行:")
                for r in data["sample"]:
                    print("  " + " | ".join(str(v)[:30] if v is not None else "NULL" for v in r.values()))
        return 0
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
