# -*- coding: utf-8 -*-
"""Python zipfile 全量扫描 FR jar 的 com.fr 类 → 类级零件
（不依赖 fr-agent，直接读文件系统）
"""
import zipfile, os, sqlite3, sys
import os
BASE = os.path.dirname(os.path.abspath(__file__))

LIB = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\lib"
OUT = os.path.join(BASE, "api_classes_parts.py")
DRY = "--dry-run" in sys.argv

classes = []
for fn in sorted(os.listdir(LIB)):
    if not fn.endswith(".jar"): continue
    jar = os.path.join(LIB, fn)
    try:
        with zipfile.ZipFile(jar) as z:
            n = 0
            for name in z.namelist():
                if name.endswith(".class") and "$" not in name and name.startswith("com/fr/"):
                    cls = name[:-6].replace("/", ".")
                    classes.append(cls)
                    n += 1
            print(f"  {fn}: +{n}")
    except Exception as e:
        print(f"  {fn}: 跳过 ({e})")

classes = sorted(set(classes))
print(f"\ncom.fr 类总数: {len(classes)}")

# 与现有零件对比
conn = sqlite3.connect(os.path.join(BASE, "api_kb.sqlite"))
existing_cls = set(r[0] for r in conn.execute("SELECT DISTINCT class_name FROM parts").fetchall())
conn.close()
new_classes = [c for c in classes if c not in existing_cls]
print(f"新增类(不在零件表): {len(new_classes)}")
if DRY:
    print("[dry-run] 未生成"); sys.exit(0)

lines = ['# -*- coding: utf-8 -*-',
         '"""全量 com.fr 类零件（自动生成自 reflect_all_classes.py，勿手改）"""',
         '', 'EXTRA_PARTS = [']
next_no = 4646
for cls in new_classes:
    short = cls.split(".")[-1]
    lines.append('    ("P-{:04d}", "{}", "{}", "new {}()", "{}", "{} 类（jar 全量枚举）", "-", "-", "类级登记，方法未枚举", "jar全量", 0),'.format(
        next_no, short, cls, short, "OTHER", short))
    next_no += 1
lines.append(']')
lines.append('')
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"已生成 {OUT}: P-4646..P-{next_no-1:04d} ({len(new_classes)} 类)")
