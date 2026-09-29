"""
SQL 格式化 — 使用 sqlglot 格式化所有 CPT 文件数据集中的 SQL 查询。
自动保护 FR 公式 ${...} 不被破坏。

用法:
    python format_dataset_sql.py                    # 格式化明细报表目录下所有 CPT
    python format_dataset_sql.py <cpt路径> [cpt...]  # 格式化指定文件
"""
import sys, os, shutil, re, sqlglot
from datetime import datetime
from pathlib import Path

DEFAULT_DIR = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'


def format_sql(sql):
    """格式化 SQL，保护 FR 公式 ${...}"""
    placeholders = []

    def save_fr(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f'FRPLACEHOLDER{idx}'

    sql_protected = re.sub(r'\$\{[^}]+\}', save_fr, sql)
    try:
        formatted = sqlglot.transpile(sql_protected, read='mysql', pretty=True)[0]
    except Exception:
        return sql

    for i, val in enumerate(placeholders):
        formatted = formatted.replace(f'FRPLACEHOLDER{i}', val)
    return formatted.strip()


def process_file(filepath):
    f = Path(filepath)
    if not f.exists():
        print(f"❌ 不存在: {f}")
        return 0

    with open(f, 'rb') as fh:
        raw = fh.read()

    if b'<Query>' not in raw:
        return 0

    query_re = re.compile(rb'(<Query>\s*<!\[CDATA\[)(.*?)(\]\]></Query>)', re.DOTALL)
    counts = [0]

    def repl(m):
        sql = m.group(2).decode('utf-8').strip()
        if not sql or (sql.upper().startswith('SELECT') and len(sql) < 20):
            return m.group(0)
        formatted = format_sql(sql)
        if formatted == sql:
            return m.group(0)
        counts[0] += 1
        return m.group(1) + formatted.encode('utf-8') + m.group(3)

    new_raw = query_re.sub(repl, raw)
    count = counts[0]

    if count > 0:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = f.parent / f'_backup_{ts}'
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(f), str(bak / f.name))
        with open(f, 'wb') as fh:
            fh.write(new_raw)
        print(f'✅ {f.name}: {count} 条 SQL 已格式化')
    return count


if __name__ == '__main__':
    if len(sys.argv) > 1:
        total = 0
        for p in sys.argv[1:]:
            total += process_file(p)
    else:
        total = 0
        for f in sorted(Path(DEFAULT_DIR).glob('*.cpt')):
            if '_backup' in f.name:
                continue
            total += process_file(str(f))
    print(f'\n共格式化 {total} 条 SQL')
