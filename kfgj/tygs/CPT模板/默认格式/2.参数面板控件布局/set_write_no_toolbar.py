"""
为 CPT 模板添加填报页面单独设置（禁用工具栏）。

用法:
    python set_write_no_toolbar.py <cpt路径>

- 自动创建 _backup_YYYYMMDD_HHMMSS/ 备份
- 已有 WebWriteContent 则跳过
"""
import sys, os, shutil
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("用法: python set_write_no_toolbar.py <cpt路径>")
        sys.exit(1)

    cpt_path = sys.argv[1]
    if not os.path.exists(cpt_path):
        print(f"❌ 文件不存在: {cpt_path}")
        sys.exit(1)

    # 1. 备份
    base_dir = os.path.dirname(os.path.abspath(cpt_path))
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(base_dir, f'_backup_{ts}')
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(backup_dir, os.path.basename(cpt_path)))
    print(f"✅ 备份: {backup_dir}")

    # 2. 读取
    with open(cpt_path, 'rb') as f:
        raw = f.read()

    # 3. 已有则跳过
    if b'<WebWriteContent>' in raw:
        print("⚠️ 已有 WebWriteContent，跳过")
        sys.exit(0)

    # 4. 检测换行符
    nl_pos = raw[:500]
    if b'\r\n' in nl_pos:
        RN = '\r\n'
    elif b'\n' in nl_pos:
        RN = '\n'
    else:
        RN = '\r\n'

    # 5. WebWriteContent（填报单独设置，无工具栏）
    web_write = (
        f'<WebWriteContent>{RN}'
        f'<ToolBars/>{RN}'
        f'<EditRowColor setColor="false"/>{RN}'
        f'<WebWrite SheetPosition="3"/>{RN}'
        f'<RptLocation isShowAtLeft="true"/>{RN}'
        f'<UnloadCheck/>{RN}'
        f'<ShowWidgets/>{RN}'
        f'<OtherAttr autoStash="false"/>{RN}'
        f'</WebWriteContent>{RN}'
    ).encode('utf-8')

    # 6. 两种情况处理
    if b'<ReportWebAttr>' in raw:
        # 已有 ReportWebAttr：在 </ReportWebAttr> 之前插入 WebWriteContent
        marker = f'</ReportWebAttr>{RN}'.encode('utf-8')
        if marker in raw:
            raw = raw.replace(marker, web_write + marker, 1)
        else:
            # 尝试找 </WebPageContent> 之后插入
            marker2 = f'</WebPageContent>{RN}'.encode('utf-8')
            if marker2 in raw:
                raw = raw.replace(marker2, marker2 + web_write, 1)
            else:
                print("❌ 未找到 </ReportWebAttr> 或 </WebPageContent>")
                sys.exit(1)
    else:
        # 没有 ReportWebAttr：完整新建，插入到 <ElementCaseMobileAttr> 之前
        report_web = (
            f'<ReportWebAttr>{RN}'
            f'<ServerPrinter/>{RN}'
            f'<WebPageContent>{RN}'
            f'<ToolBars>{RN}'
            f'<ToolBarManager>{RN}'
            f'<Location>{RN}'
            f'<Embed position="3"/>{RN}'
            f'</Location>{RN}'
            f'<ToolBar/>{RN}'
            f'</ToolBarManager>{RN}'
            f'</ToolBars>{RN}'
            f'<WebPage isPage="false" showAsImage="false" autoScale="false" tdHeavy="false"/>{RN}'
            f'</WebPageContent>{RN}'
        ).encode('utf-8') + web_write + f'</ReportWebAttr>{RN}'.encode('utf-8')

        marker = f'<ElementCaseMobileAttr>{RN}'.encode('utf-8')
        if marker not in raw:
            # fallback: 插入到 <Report 之前
            marker = f'<Report class="com.fr.report.worksheet.WorkSheet"{RN}'.encode('utf-8')
        if marker not in raw:
            print("❌ 未找到插入点")
            sys.exit(1)

        raw = raw.replace(marker, report_web + marker, 1)

    # 7. 写回
    with open(cpt_path, 'wb') as f:
        f.write(raw)

    print(f"✅ 已添加填报页面单独设置（无工具栏）")
    print(f"   目标: {cpt_path}")


if __name__ == "__main__":
    main()
