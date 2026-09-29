"""修复 CDATA 内多余的 \" 转义符 → " """

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
import os, shutil, re
from datetime import datetime
from pathlib import Path

BASE = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'

for f in sorted(Path(BASE).glob('*.cpt')):
    if '_backup' in f.name:
        continue

    with open(f, 'rb') as fh:
        raw = fh.read()

    # 只在 CDATA 内替换 \" → "
    cdata_re = re.compile(rb'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)

    def fix_quotes(m):
        inner = m.group(1)
        fixed = inner.replace(b'\\"', b'"')
        if fixed == inner:
            return m.group(0)
        return b'<![CDATA[' + fixed + b']]>'

    new_raw = cdata_re.sub(fix_quotes, raw)

    if new_raw != raw:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = f.parent / f'_backup_{ts}'
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(f), str(bak / f.name))
        with open(f, 'wb') as fh:
            fh.write(new_raw)
        print(f'✅ {f.name}')
    else:
        print(f'⏭️  {f.name}')
