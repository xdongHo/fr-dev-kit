"""
缺 Export 导出按钮自动补充。
检测 formSubmit3 控件，不存在则插入 FreeButton（点击事件: _g().exportReportToExcel('simple')）。
"""
import sys, os, shutil, re
from datetime import datetime


def add_export_btn(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 文件不存在: {cpt_path}")
        return False

    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'rb') as f:
        raw = f.read()

    if b'WidgetName name="formSubmit3"' in raw:
        print(f"⚠️  已有 Export 按钮，跳过: {os.path.basename(cpt_path)}")
        return False

    export_btn = (
        '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\r\n'
        '<InnerWidget class="com.fr.form.ui.FreeButton">\r\n'
        '<Listener event="click" name="Export_Click">\r\n'
        '<JavaScript class="com.fr.js.JavaScriptImpl">\r\n'
        '<Parameters/>\r\n'
        '<Content>\r\n'
        '<![CDATA[_g().exportReportToExcel(\'simple\')]]></Content>\r\n'
        '</JavaScript>\r\n'
        '</Listener>\r\n'
        '<WidgetName name="formSubmit3"/>\r\n'
        '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\r\n'
        '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\r\n'
        '<PrivilegeControl/>\r\n'
        '</WidgetAttr>\r\n'
        '<Text><![CDATA[Export]]></Text>\r\n'
        '<Hotkeys><![CDATA[]]></Hotkeys>\r\n'
        '</InnerWidget>\r\n'
        '<BoundsAttr x="1100" y="80" width="80" height="26"/>\r\n'
        '</Widget>'
    ).encode('utf-8')

    idx = raw.rfind(b'</Layout>')
    if idx < 0:
        print(f"❌ 未找到 </Layout>: {os.path.basename(cpt_path)}")
        return False
    raw = raw[:idx] + export_btn + b'\r\n' + raw[idx:]

    # 补充 MobileWidgetList
    mwl_marker = b'<MobileWidgetList>'
    mwl_idx = raw.find(mwl_marker)
    if mwl_idx > 0:
        entry = b'<Widget widgetName="formSubmit3"/>\r\n'
        raw = raw[:mwl_idx + len(mwl_marker)] + entry + raw[mwl_idx + len(mwl_marker):]

    with open(cpt_path, 'wb') as f:
        f.write(raw)

    print(f"✅ 已添加 Export 按钮: {os.path.basename(cpt_path)}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python add_export_btn.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        add_export_btn(p)
