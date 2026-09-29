"""
将级联参数从 ${para_xxx} 直写改为 FR 公式形式：
${if(len(控件名)==0,"","and 字段 in ('"+控件名+"')")}
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
import os, shutil, re
from datetime import datetime
from pathlib import Path

BASE = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'

replacements = [
    # dict_region: bu IN ('${para_bu}')
    (
        r"WHERE bu IN \('\$\{para_bu\}'\)",
        r"WHERE 1=1 ${if(len(para_bu)==0,\"\",\"and bu in ('\"+para_bu+\"')\")}"
    ),
    # dict_plant: region IN ('${para_region}')
    (
        r"WHERE region IN \('\$\{para_region\}'\)",
        r"WHERE 1=1 ${if(len(para_region)==0,\"\",\"and region in ('\"+para_region+\"')\")}"
    ),
]

for f in sorted(Path(BASE).glob('*.cpt')):
    if '_backup' in f.name:
        continue

    with open(f, 'r', encoding='utf-8') as fh:
        raw = fh.read()

    changed = False
    for pattern, replacement in replacements:
        new_raw = re.sub(pattern, replacement, raw)
        if new_raw != raw:
            changed = True
            raw = new_raw

    if changed:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = f.parent / f'_backup_{ts}'
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(f), str(bak / f.name))

        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(raw)
        print(f'✅ {f.name}')
    else:
        print(f'⏭️  {f.name}')
