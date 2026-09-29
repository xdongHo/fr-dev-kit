"""
批量：目录下所有非backup CPT文件添加除零保护
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
import re, shutil, os
from datetime import datetime
from pathlib import Path

BASE = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'

def wrap_div(m):
    full = m.group(0)
    inner = m.group(1)
    if inner.startswith('if(len(') or inner.startswith('if('):
        return full
    parts = inner.rsplit(' / ', 1)
    if len(parts) != 2:
        return full
    numerator, divisor = parts
    divisor = divisor.strip()
    numerator = numerator.strip()
    if re.match(r'^-?\d+(\.\d+)?$', divisor):
        return full
    # 检查 divisor 括号平衡
    if divisor.count('(') != divisor.count(')'):
        return full
    new_inner = f"if(len({divisor})=0||{divisor}=0,'',{numerator}/{divisor})"
    return full.replace(inner, new_inner)


for f in sorted(Path(BASE).glob('*.cpt')):
    if '_backup' in f.name or f.name == '示例实际表.cpt':
        continue  # 示例实际表已处理

    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # 先检查是否有除法公式
    if ' / ' not in content:
        print(f'⏭️  {f.name}: 无除法公式')
        continue

    # 备份
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f.parent / f'_backup_{ts}'
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(f), str(bak / f.name))

    counts = [0]
    formula_re = re.compile(r'<!\[CDATA\[=(.*?)\]\]>', re.DOTALL)

    def repl_with_count(m):
        result = wrap_div(m)
        if result != m.group(0):
            counts[0] += 1
        return result

    new_content = formula_re.sub(repl_with_count, content)
    count = counts[0]

    if count > 0:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        print(f'✅ {f.name}: {count} 个除法公式已保护')
    else:
        print(f'⏭️  {f.name}: 无需处理')
