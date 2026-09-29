# -*- coding: utf-8 -*-
"""统计 i18n 词典 → API 映射覆盖率"""
import json, sqlite3, re
import os
BASE = os.path.dirname(os.path.abspath(__file__))

I18N = json.load(open(os.path.join(BASE, "i18n_zh.json"), encoding="utf-8"))
DB = os.path.join(BASE, "api_kb.sqlite")
conn = sqlite3.connect(DB)
cur = conn.cursor()

total = len(I18N)
print(f"=== i18n 词典总词汇: {total} 条 ===")

# 1. 有 cn_name 的零件
cn_parts = cur.execute("SELECT part_no, name, cn_name FROM parts WHERE cn_name IS NOT NULL AND cn_name != ''").fetchall()
print(f"\n=== 已映射 cn_name 的零件: {len(cn_parts)} 个 ===")

# 2. 词典中哪些词在零件 cn_name 里出现过（精确命中）
cn_values = set()
for p in cn_parts:
    for v in p[2].split(";"):
        v = v.strip()
        if v: cn_values.add(v)

matched_exact = [v for v in I18N.values() if v.strip() in cn_values]
print(f"词典词 精确命中零件 cn_name: {len(matched_exact)} / {total} ({len(matched_exact)/total*100:.1f}%)")

# 3. 词典词在零件 name/class_name/description 里能模糊匹配到的（近似覆盖）
def fuzzy_in_parts(word):
    if len(word) < 2: return False
    # 在零件 name / class_name 短名 / cn_name 中搜索
    r = cur.execute("SELECT 1 FROM parts WHERE name LIKE ? OR cn_name LIKE ? OR class_name LIKE ? LIMIT 1",
                    (f"%{word}%", f"%{word}%", f"%{word}%")).fetchone()
    return bool(r)

matched_fuzzy = 0
samples = []
for v in I18N.values():
    v = v.strip()
    if len(v) < 2 or v in cn_values: 
        continue
    if fuzzy_in_parts(v):
        matched_fuzzy += 1
        if len(samples) < 10: samples.append(v)

print(f"词典词 模糊命中零件(部分): {matched_fuzzy}")
print(f"合计可映射: {len(matched_exact) + matched_fuzzy} / {total} ({(len(matched_exact)+matched_fuzzy)/total*100:.1f}%)")
print(f"\n模糊命中示例: {samples}")

# 4. 分类统计：控件类 vs 属性类 vs 菜单类
widget_words = [v for k, v in I18N.items() if "Widget" in k or "Button" in k]
prop_words = [v for k, v in I18N.items() if re.search(r"Watermark|Visible|Enabled|Allow|Editable|Selection|Leaf", k)]
print(f"\n控件类词: {len(widget_words)}, 属性类词: {len(prop_words)}")

conn.close()
