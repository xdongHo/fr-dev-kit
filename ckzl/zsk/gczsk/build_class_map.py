# -*- coding: utf-8 -*-
"""完整闭环: 7033 业务类零件 + i18n key→类 全量匹配
1. 收集所有业务类（designer+核心jar）
2. 生成 api_classes_parts.py（类级零件）
3. i18n key 末段匹配类短名 → 建立映射词典
4. 输出: parts 类覆盖 + 词汇映射率
"""
import zipfile, os, sqlite3, json, re, collections, sys
import os
BASE = os.path.dirname(os.path.abspath(__file__))

LIB = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\lib"
DESIGNER = r"C:\Program Files\FineReport_10.0\lib\fine-report-designer-10.0"
CORE_JARS = ["fine-core-10.0.jar", "fine-report-engine-10.0.jar", "fine-webui-10.0.jar", "fine-datasource-10.0.jar"]
OUT_CLASSES = os.path.join(BASE, "api_classes_parts.py")
OUT_MAP = os.path.join(BASE, "i18n_class_map.json")
DB = os.path.join(BASE, "api_kb.sqlite")

INCLUDE = ["com.fr.design","com.fr.form","com.fr.report","com.fr.data","com.fr.chart","com.fr.base",
           "com.fr.io","com.fr.plugin.chart","com.fr.stable.unit","com.fr.stable.fun","com.fr.script",
           "com.fr.write","com.fr.web.core","com.fr.general","com.fr.json"]
EXCLUDE = ["com.fr.third","com.fr.decision.webservice","com.fr.cluster","com.fr.ssh","com.fr.cert",
           "com.fr.security","com.fr.collections.cluster","com.fr.general.jsqlparser","com.fr.data.core.db",
           "com.fr.design.restful","com.fr.design.mainframe.actions"]

def collect_jar(jar, out):
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if name.endswith(".class") and "$" not in name and name.startswith("com/fr/"):
                cls = name[:-6].replace("/", ".")
                if any(cls.startswith(p) for p in INCLUDE) and not any(cls.startswith(e) for e in EXCLUDE):
                    out.add(cls)

def collect_dir(root, out):
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".class") and "$" not in fn:
                rel = os.path.relpath(os.path.join(dp, fn), root)
                cls = rel[:-6].replace(os.sep, ".")
                if any(cls.startswith(p) for p in INCLUDE) and not any(cls.startswith(e) for e in EXCLUDE):
                    out.add(cls)

classes = set()
for fn in CORE_JARS:
    collect_jar(os.path.join(LIB, fn), classes)
collect_dir(DESIGNER, classes)
classes = sorted(classes)
print(f"业务类总数: {len(classes)}")

conn = sqlite3.connect(DB)
cur = conn.cursor()
existing_cls = set(r[0] for r in cur.execute("SELECT DISTINCT class_name FROM parts").fetchall())
new_classes = [c for c in classes if c not in existing_cls]
print(f"新增类(不在零件表): {len(new_classes)}")

# 1. 生成类级零件
lines = ['# -*- coding: utf-8 -*-',
         '"""全量 FR 业务类零件（自动生成自 collect_classes，勿手改）"""',
         '', 'EXTRA_PARTS = [']
next_no = 4646
for cls in new_classes:
    short = cls.split(".")[-1]
    cat = "DESIGNER" if cls.startswith("com.fr.design") else "OTHER"
    lines.append('    ("P-{:04d}", "{}", "{}", "new {}()", "{}", "{} 类（全量枚举）", "-", "-", "类级登记", "类枚举", 0),'.format(
        next_no, short, cls, short, cat, short))
    next_no += 1
lines.append(']')
lines.append('')
open(OUT_CLASSES, "w", encoding="utf-8").write("\n".join(lines))
print(f"已生成 {OUT_CLASSES}: P-4646..P-{next_no-1:04d} ({len(new_classes)} 类)")

# 2. i18n key → 类匹配
I18N = json.load(open(os.path.join(BASE, "i18n_zh.json"), encoding="utf-8"))
# 全部类短名（含新类）
all_shorts = {}
for cls in classes:
    all_shorts.setdefault(cls.split(".")[-1].lower(), cls)

def key_tokens(key):
    parts = key.split("_")
    while parts and parts[0].lower() in ("fine","design","core","designer","basic","report","chart","form"):
        parts.pop(0)
    return parts

matched = 0
match_map = {}
for k, v in I18N.items():
    toks = key_tokens(k)
    if not toks: continue
    found = None
    if toks[-1].lower() in all_shorts:
        found = all_shorts[toks[-1].lower()]
    elif len(toks) >= 2:
        combo = "".join(toks[-2:]).lower()
        if combo in all_shorts:
            found = all_shorts[combo]
    if found:
        matched += 1
        match_map.setdefault(found, []).append({"key": k, "zh": v})

print(f"\ni18n key→类 匹配: {matched} / {len(I18N)} ({matched/len(I18N)*100:.1f}%)")
print(f"命中类数: {len(match_map)}")
json.dump(match_map, open(OUT_MAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"映射已存 {OUT_MAP}")

# 3. 输出命中类示例
print("\n=== 命中类 top 20 ===")
for cls in sorted(match_map, key=lambda c: -len(match_map[c]))[:20]:
    ex = match_map[cls][:3]
    print(f"  {cls} ({len(match_map[cls])}词): {[e['zh'] for e in ex]}")
conn.close()
