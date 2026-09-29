"""
更新所有 CPT 文件的 afterinit CSS 注入内容。
如果已有 afterinit 则替换 CDATA 内容，否则调用 add_para_init_event.py 逻辑注入。
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
import os, re, shutil
from datetime import datetime
from pathlib import Path

BASE = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表'
CSS_FILE = r'C:\Users\<你的用户名>\Desktop\fr_dev_kit\kfgj/tygs\CPT模板\默认格式\2.参数面板控件布局\css样式.txt'

with open(CSS_FILE, 'r', encoding='utf-8') as f:
    js_content = f.read().strip()

# 找所有非 backup 的 .cpt
targets = []
for f in Path(BASE).iterdir():
    if f.suffix == '.cpt' and '_backup' not in f.name and '_backup' not in str(f.parent):
        targets.append(str(f))

print(f"目标: {len(targets)} 个文件")

for cpt_path in targets:
    name = Path(cpt_path).name

    # 备份
    bak_dir = Path(BASE) / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    bak_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cpt_path, bak_dir / name)

    with open(cpt_path, 'rb') as f:
        raw = f.read()

    if b'<Listener event="afterinit"' not in raw:
        # 没有 afterinit：需要在 </Layout> 后、<DesignAttr 前插入
        print(f"⚠️  {name}: 无 afterinit，跳过（需手动运行 add_para_init_event.py）")
        continue

    # 已有 afterinit：替换 <![CDATA[...]]> 内容
    # 查找 afterinit listener 中的 CDATA
    listener_start = raw.find(b'<Listener event="afterinit"')
    listener_end = raw.find(b'</Listener>', listener_start)
    if listener_start < 0 or listener_end < 0:
        print(f"❌ {name}: 找不到 Listener 边界")
        continue

    cdata_start = raw.find(b'<![CDATA[', listener_start)
    cdata_end = raw.find(b']]>', cdata_start)
    if cdata_start < 0 or cdata_end < 0:
        print(f"❌ {name}: 找不到 CDATA")
        continue

    # 替换 CDATA 内容
    new_cdata = b'<![CDATA[\r\n' + js_content.encode('utf-8') + b'\r\n    ]]>'
    raw = raw[:cdata_start] + new_cdata + raw[cdata_end+3:]

    with open(cpt_path, 'wb') as f:
        f.write(raw)

    print(f"✅ {name}: CSS 已更新")

print("完成")
