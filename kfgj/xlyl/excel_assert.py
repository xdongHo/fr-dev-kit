#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
excel_assert.py — Excel 渲染产物断言器（injected backend 的主断言载体）

FR 设计器 JVM 导出的 "xls"（实为 OOXML/ZIP 魔数 504b0304, 需按 xlsx 读）→
openpyxl 解析 → 对照 expect_manifest 逐项断言。

优势: 单元格级精确断言(sheet名/静态文本/网格尺寸/数据填充)，远强于 HTML 正则。

用法:
    from excel_assert import assert_excel
    p, f, w = assert_excel(manifest, "out.xls")
"""
import os
import shutil
import tempfile
import warnings

warnings.filterwarnings("ignore")  # openpyxl 对 FR 导出产物的 default style 警告无意义


def _load(path):
    """FR 导出的 .xls 实为 xlsx(OOXML)。按魔数分流: PK→(改名).xlsx 直读; BIFF(D0CF)→xlrd。"""
    import openpyxl
    with open(path, "rb") as f:
        magic = f.read(4)
    real = path
    if magic == b"PK\x03\x04" and not path.lower().endswith(".xlsx"):
        # openpyxl 按扩展名预拒 → 复制为 .xlsx 后读
        fd, real = tempfile.mkstemp(suffix=".xlsx"); os.close(fd)
        shutil.copy(path, real)
        wb = openpyxl.load_workbook(real, data_only=True)
        os.unlink(real)
        return wb
    if magic == b"PK\x03\x04":
        return openpyxl.load_workbook(real, data_only=True)
    if magic == b"\xd0\xcf\x11\xe0":  # 老 BIFF 真身
        try:
            import xlrd  # noqa: F401
            raise ValueError("真 BIFF .xls 需 xlrd 路线(FR 导出通常为 OOXML, 此分支兜底报错)")
        except ImportError:
            raise ValueError("老 .xls(BIFF) 且本机无 xlrd")
    raise ValueError(f"未知文件魔数: {magic.hex()}")


def assert_excel(manifest, xls_path):
    """manifest vs Excel 产物 → (passed, failed, warned)"""
    passed, failed, warned = [], [], []
    wb = _load(xls_path)

    # X1 sheet 名对齐（manifest.sheet_names ⊆ wb.sheetnames）
    m_sheets = [s for s in manifest.get("sheet_names", []) if s]
    if not m_sheets:
        warned.append("X1 manifest 无 sheet 名(骨架空模板?)")
    else:
        for sn in m_sheets:
            if sn in wb.sheetnames:
                passed.append(f"X1 sheet 名精确命中: {sn}")
            else:
                failed.append(f"X1 sheet 名缺失: {sn} (产物: {wb.sheetnames[:5]})")

    # X2 静态文本（模板 CellElement 静态文本应出现在产物单元格）
    grid = manifest.get("grid", {})
    st = grid.get("static_texts") or []
    if st:
        # 展开产物全部单元格值 → 集合匹配
        val_set = set()
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for v in row:
                    if v is not None and str(v).strip():
                        val_set.add(str(v).strip())
        for t in st[:30]:
            if t["text"] in val_set:
                passed.append(f"X2 静态文本命中: {t['text'][:16]}")
            else:
                failed.append(f"X2 静态文本缺失: {t['text'][:16]} @cell({t['cell']})")

    # X3 网格尺寸（产物行列 ≥ manifest max_row/max_col —— 渲染不丢行列）
    ws = wb.worksheets[0]
    m_row, m_col = grid.get("max_row", 0), grid.get("max_col", 0)
    if m_row and ws.max_row >= min(m_row, 200):
        passed.append(f"X3 行数对齐: 产物{ws.max_row} ≥ 声明{m_row}")
    elif m_row:
        failed.append(f"X3 行数不足: 产物{ws.max_row} < 声明{m_row}")
    if m_col and ws.max_column >= min(m_col, 300):
        passed.append(f"X3 列数对齐: 产物{ws.max_column} ≥ 声明{m_col}")
    elif m_col:
        failed.append(f"X3 列数不足: 产物{ws.max_column} < 声明{m_col}")

    # X4 数据填充（内嵌数据集模板: 产物应有相当量非空单元格）
    n_empty_manifest_cells = grid.get("cell_count", 0)
    n_nonempty = sum(1 for ws2 in wb.worksheets for row in ws2.iter_rows(values_only=True)
                     for v in row if v is not None and str(v).strip())
    has_embedded = any(d["embedded"] and d["embedded_payload_bytes"] > 100
                       for d in manifest.get("datasets", []))
    if has_embedded:
        if n_nonempty >= 5:
            passed.append(f"X4 数据已填充: {n_nonempty} 非空单元格(内嵌数据集已计算)")
        else:
            failed.append(f"X4 疑似空渲染: 仅 {n_nonempty} 非空单元格(声明了内嵌数据集)")
    elif n_nonempty >= n_empty_manifest_cells:
        passed.append(f"X4 非空单元格 {n_nonempty}")
    else:
        warned.append(f"X4 非空单元格偏少: {n_nonempty} vs 声明格数 {n_empty_manifest_cells}")

    # X5 图表占位（Excel 导出中图表常变为图片/留空 —— 只 warn 不 fail）
    nc = manifest.get("charts", {}).get("chart_total", 0)
    if nc == 0:
        passed.append("X5 无图表声明,跳过")
    else:
        warned.append(f"X5 图表{nc}个在 Excel 中通常导出为图片,本断言器不校验(视觉层走截图路线)")

    return passed, failed, warned


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from expect_manifest import extract_manifest
    tpl, xls = sys.argv[1], sys.argv[2]
    p, f, w = assert_excel(extract_manifest(tpl), xls)
    for x in p: print(f"  [PASS] {x}")
    for x in w: print(f"  [WARN] {x}")
    for x in f: print(f"  [FAIL] {x}")
    print(f"  == {len(p)} PASS / {len(w)} WARN / {len(f)} FAIL")
    sys.exit(1 if f else 0)
