#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""req_workbook 产物自检: 结构规范符合性"""
import sys
from openpyxl import load_workbook

fp = sys.argv[1]
wb = load_workbook(fp)
print("sheets(%d): %s" % (len(wb.sheetnames), ", ".join(wb.sheetnames)))

errs = []

# 1. 物料信息(需求总览七区)
ws = wb["物料信息"]
kv = {ws.cell(r, 1).value: ws.cell(r, 2).value for r in range(1, ws.max_row + 1)}
print("\n[物料信息] 报表=%s 类型=%s 数据集数=%s" % (
    kv.get("报表名称"), kv.get("模板类型"), kv.get("数据集数")))
secs = [str(ws.cell(r, 1).value)[:2] for r in range(1, ws.max_row + 1)
        if ws.cell(r, 1).value and str(ws.cell(r, 1).value)[:2] in
        ("一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、")]
print("  总览九区: %s" % secs)
NINE = ("一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、")
if len(secs) != 9:
    errs.append("总览九区缺: %s" % [x for x in NINE if x not in secs])
# 表资源区必须有实测字段数(有 DB 表时)
for r in range(1, ws.max_row + 1):
    if ws.cell(r, 1).value == "表名":
        has_num = any(isinstance(ws.cell(r2, 4).value, int) for r2 in range(r + 1, ws.max_row + 1))
        print("  表资源区实测字段数: %s" % ("✅" if has_num else "无(DB表为0或探查失败)"))
        break

# 2. 实体表样例页(T_): 表头+字段类型行+数据
n_t = 0
for nm in wb.sheetnames:
    if nm.startswith("T_"):
        wt = wb[nm]
        if wt["A1"].value and wt["A2"].value and str(wt["A2"].value).startswith("字段:"):
            n_t += 1
print("\n[实体页 T_] %d 个含全表名+字段类型清单" % n_t)

# 2b. 字典类数据集不建页(取值并入参数区/五区)
import re as _re
dict_sheets = [nm for nm in wb.sheetnames if _re.search(r"(?:^|_)dict(?:_|$)", nm)
               and not nm.startswith(("表样_", "SQL_"))]
if dict_sheets:
    errs.append("字典类不应建独立页: %s" % dict_sheets)
print("[字典页检查] %s" % ("✅ 无独立字典页" if not dict_sheets else "❌ %s" % dict_sheets))

# 3. 数据集示例 sheet(单模板模式; 项目模式已并入数据集逻辑页)
n_ok = 0
for nm in wb.sheetnames:
    if nm.startswith(("SQL_", "表样_", "T_")) or nm in ("物料信息", "数据集逻辑"):
        continue
    ws2 = wb[nm]
    hdr = [c.value for c in ws2[1] if c.value]
    nrows = sum(1 for r in range(2, ws2.max_row + 1) if ws2.cell(r, 1).value and not str(ws2.cell(r, 1).value).startswith("…"))
    if hdr and nrows > 0:
        n_ok += 1
print("\n[示例数据] %d 个独立 sheet(项目模式=0, 已并入数据集逻辑页)" % n_ok)

# 4. 数据集逻辑页(项目模式) 或 SQL_ 页(单模板模式)
n_sql = sum(1 for nm in wb.sheetnames if nm.startswith("SQL_") and wb[nm].max_row > 2)
if "数据集逻辑" in wb.sheetnames:
    wdl = wb["数据集逻辑"]
    n_sec = sum(1 for r in range(1, wdl.max_row + 1)
                if str(wdl.cell(r, 1).value or "").startswith("◆"))
    print("[数据集逻辑] 1 页, %d 数据集节" % n_sec)
    if n_sec == 0:
        errs.append("数据集逻辑页无数据集节")
elif n_sql:
    print("[SQL] %d 个 sheet 含 SQL 正文(单模板模式)" % n_sql)

# 5. 表样
tp = [nm for nm in wb.sheetnames if nm.startswith("表样_")]
if tp:
    ws3 = wb[tp[0]]
    print("\n[表样 %s] 合并区 %d 个" % (tp[0], len(ws3.merged_cells.ranges)))
    # 顶部5行 = 参数区(cpt 表样; frm 画布页无参数区约定, 跳过断言)
    pcells = [(c.coordinate, c.value) for row in ws3.iter_rows(min_row=1, max_row=5) for c in row if c.value]
    print("  参数区(行1-5) %d 格: %s" % (len(pcells), [v for _, v in pcells[:6]]))
    if not any("[参数]" in str(v) for _, v in pcells) and not str(ws3["A1"].value or "").startswith("↓"):
        errs.append("表样顶部5行无参数面板示例")
    # ds.field 引用
    refs = [c.value for row in ws3.iter_rows(min_row=6) for c in row if c.value and "." in str(c.value)[:14]
            and not str(c.value).startswith(("=", "[图表"))]
    print("  ds.field 引用 %d 格: %s" % (len(refs), refs[:6]))
    charts = [c.value for row in ws3.iter_rows() for c in row if c.value and str(c.value).startswith("[图表")]
    print("  图表占位 %d 格: %s" % (len(charts), charts[:4]))
    # 静态表头样例
    static = [c.value for row in ws3.iter_rows(min_row=6, max_row=8) for c in row
              if c.value and not str(c.value).startswith(("ds", "[图表", "="))]
    print("  静态表头样例: %s" % static[:8])

print("\n%s" % ("❌ 自检失败: %s" % errs if errs else "✅ 自检通过"))
sys.exit(1 if errs else 0)
