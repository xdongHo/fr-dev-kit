"""
使用 sqlglot 格式化所有 CPT 文件数据集中的 SQL 查询。
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
import os, shutil, re, sqlglot
from datetime import datetime
from pathlib import Path

BASE = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'

def format_sql(sql):
    """格式化 SQL，保留 FR 公式"""
    # 保护 FR 公式 ${...}
    placeholders = {}
    def save_fr(m):
        key = f'__FR_{len(placeholders)}__'
        placeholders[key] = m.group(0)
        return key
    
    sql_protected = re.sub(r'\$\{[^}]+\}', save_fr, sql)
    
    try:
        formatted = sqlglot.transpile(sql_protected, read='mysql', pretty=True)[0]
    except Exception:
        return sql  # 格式化失败，返回原文
    
    # 恢复 FR 公式
    for key, val in placeholders.items():
        formatted = formatted.replace(key, val)
    
    return formatted.strip()


for f in sorted(Path(BASE).glob('*.cpt')):
    if '_backup' in f.name:
        continue

    with open(f, 'rb') as fh:
        raw = fh.read()

    if b'<Query>' not in raw:
        continue

    # 匹配 Query CDATA
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
    else:
        print(f'⏭️  {f.name}')
