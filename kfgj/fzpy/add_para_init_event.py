"""
替换 示例实际表.cpt 中 afterinit 事件的占位符为实际 CSS 注入代码。
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
import os, shutil
from datetime import datetime

CPT_PATH = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表\示例实际表.cpt"
CSS_FILE = r"C:\Users\<你的用户名>\Desktop\fr_dev_kit\kfgj/tygs\CPT模板\默认格式\2.参数面板控件布局\css样式.txt"

# 1. 备份
BASE_DIR = os.path.dirname(CPT_PATH)
backup_dir = os.path.join(BASE_DIR, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
os.makedirs(backup_dir, exist_ok=True)
shutil.copy2(CPT_PATH, os.path.join(backup_dir, "示例实际表.cpt"))
print(f"✅ 备份到: {backup_dir}")

# 2. 读取 CSS 内容
with open(CSS_FILE, "r", encoding="utf-8") as f:
    js_content = f.read().strip()

# 3. 读取 CPT (binary)
with open(CPT_PATH, "rb") as f:
    raw = f.read()

# 4. 替换占位符
placeholder = b"var flag='\xe8\xbf\x99\xe9\x87\x8c\xe6\x98\xaf\xe5\x8f\x82\xe6\x95\xb0\xe9\x9d\xa2\xe6\x9d\xbf\xe5\x88\x9d\xe5\xa7\x8b\xe5\x8c\x96\xe4\xba\x8b\xe4\xbb\xb6\xe5\xa1\xab\xe5\x86\x99\xe4\xbd\x8d\xe7\xbd\xae'"

if placeholder not in raw:
    print("❌ 未找到占位符!")
    # Try with the text search
    idx = raw.find(b"flag='")
    if idx >= 0:
        print(f"找到 'flag=' 在 offset {idx}: {repr(raw[idx:idx+80])}")
    exit(1)

raw = raw.replace(placeholder, js_content.encode('utf-8'), 1)

# 5. 写回
with open(CPT_PATH, "wb") as f:
    f.write(raw)

print("✅ 占位符已替换为 CSS 初始化代码")
print(f"   目标: {CPT_PATH}")
