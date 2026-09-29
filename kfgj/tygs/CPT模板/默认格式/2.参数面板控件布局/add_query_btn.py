"""
缺 Query 查询按钮自动补充。
检测 search 控件，不存在则插入 FormSubmitButton（Query + enter 快捷键）。
"""
import sys, os, shutil, re
from datetime import datetime


def add_query_btn(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 文件不存在: {cpt_path}")
        return False

    # 备份
    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'rb') as f:
        raw = f.read()

    if b'WidgetName name="search"' in raw:
        print(f"⚠️  已有 search 按钮，跳过: {os.path.basename(cpt_path)}")
        return False

    query_btn = (
        '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\r\n'
        '<InnerWidget class="com.fr.form.parameter.FormSubmitButton">\r\n'
        '<WidgetName name="search"/>\r\n'
        '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\r\n'
        '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\r\n'
        '<PrivilegeControl/>\r\n'
        '</WidgetAttr>\r\n'
        '<Text><![CDATA[Query]]></Text>\r\n'
        '<Hotkeys><![CDATA[enter]]></Hotkeys>\r\n'
        '</InnerWidget>\r\n'
        '<BoundsAttr x="1000" y="80" width="80" height="26"/>\r\n'
        '</Widget>'
    ).encode('utf-8')

    # 插入到 </Layout> 之前
    idx = raw.rfind(b'</Layout>')
    if idx < 0:
        print(f"❌ 未找到 </Layout>: {os.path.basename(cpt_path)}")
        return False
    raw = raw[:idx] + query_btn + b'\r\n' + raw[idx:]

    # 补充 MobileWidgetList
    mwl_marker = b'<MobileWidgetList>'
    mwl_idx = raw.find(mwl_marker)
    if mwl_idx > 0:
        entry = b'<Widget widgetName="search"/>\r\n'
        raw = raw[:mwl_idx + len(mwl_marker)] + entry + raw[mwl_idx + len(mwl_marker):]

    with open(cpt_path, 'wb') as f:
        f.write(raw)

    print(f"✅ 已添加 Query 按钮: {os.path.basename(cpt_path)}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python add_query_btn.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        add_query_btn(p)
