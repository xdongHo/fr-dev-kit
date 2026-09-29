"""
为 CPT 模板添加 CSSImport 引用（purchase_v1.css + py20px.css + window_mask.css）。
"""
import sys, os, shutil
from datetime import datetime

CSS_IMPORT = (
    '<CSSImport><![CDATA[help/purchase/css/purchase_v1.css]]></CSSImport>\r\n'
    '<CSSImport><![CDATA[help/purchase/css/py20px.css]]></CSSImport>\r\n'
    '<CSSImport><![CDATA[help/purchase/css/window_mask.css]]></CSSImport>\r\n'
).encode('utf-8')


def add_css_import(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 不存在: {cpt_path}")
        return False

    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'rb') as f:
        raw = f.read()

    if b'purchase_v1.css' in raw:
        print(f"⚠️  已有 CSSImport: {os.path.basename(cpt_path)}")
        return True  # 幂等: 目标状态已达成

    # 正确位置实证(duplicate_invoice_processing_fill*.cpt): CSSImport 是 <ReportWebAttr> 的子元素
    marker = b'</ReportWebAttr>'
    if marker in raw:
        idx = raw.find(marker)
        raw = raw[:idx] + CSS_IMPORT + raw[idx:]
    else:
        # 无 ReportWebAttr: 创建块, 插在 <WorkBook ...> 开标签之后(内部) — 修复: 原版插根元素外导致 XML 不良构
        import re as _re
        m = _re.search(rb'<WorkBook[^>]*>', raw)
        if not m:
            print(f"❌ 未找到插入点: {os.path.basename(cpt_path)}")
            return False
        block = b'<ReportWebAttr>\r\n' + CSS_IMPORT + b'</ReportWebAttr>\r\n'
        raw = raw[:m.end()] + b'\r\n' + block + raw[m.end():]

    # 写回前良构自检(坏了不落盘, 编排器约定: 报警必须可靠)
    import xml.etree.ElementTree as _ET
    try:
        _ET.fromstring(raw)
    except _ET.ParseError as e:
        print(f"❌ 注入后 XML 不良构, 已放弃写入(保持原文件): {e}")
        return False

    with open(cpt_path, 'wb') as f:
        f.write(raw)

    print(f"✅ 已添加 CSSImport: {os.path.basename(cpt_path)}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python add_css_import.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        add_css_import(p)
