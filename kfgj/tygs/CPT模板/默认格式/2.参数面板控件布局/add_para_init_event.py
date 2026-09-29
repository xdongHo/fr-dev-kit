"""
向 CPT 模板的参数面板 para 注入 afterinit CSS 初始化事件。

用法:
    python add_para_init_event.py <cpt路径> [css文件路径]

默认 CSS 文件: 同目录下的 css样式.txt
"""
import os, sys, shutil
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("用法: python add_para_init_event.py <cpt路径> [css文件路径]")
        sys.exit(1)

    cpt_path = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    css_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(script_dir, "css样式.txt")

    if not os.path.exists(cpt_path):
        print(f"❌ CPT 文件不存在: {cpt_path}")
        sys.exit(1)
    if not os.path.exists(css_file):
        print(f"❌ CSS 文件不存在: {css_file}")
        sys.exit(1)

    # 1. 备份
    base_dir = os.path.dirname(os.path.abspath(cpt_path))
    backup_dir = os.path.join(base_dir, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(backup_dir, os.path.basename(cpt_path)))
    print(f"✅ 备份到: {backup_dir}")

    # 2. 读取 CSS 内容
    with open(css_file, "r", encoding="utf-8") as f:
        js_content = f.read().strip()

    # 3. 读取 CPT (binary — CPT 文件用 \r\n)
    with open(cpt_path, "rb") as f:
        raw = f.read()

    # 4. 检查是否已有 afterinit
    if b'<Listener event="afterinit"' in raw:
        print("⚠️ 已存在 afterinit 事件！跳过。")
        sys.exit(0)

    # 5. 构造 Listener XML
    listener = (
        '<Listener event="afterinit">\r\n'
        '  <JavaScript class="com.fr.js.JavaScriptImpl">\r\n'
        '    <Content><![CDATA[\r\n'
        + js_content + '\r\n'
        '    ]]></Content>\r\n'
        '  </JavaScript>\r\n'
        '</Listener>\r\n'
    ).encode('utf-8')

    # 6. 插入位置: </Layout> 之后、<DesignAttr 之前（支持换行和紧凑两种格式）
    marker = b'</Layout><DesignAttr'
    if marker not in raw:
        marker = b'</Layout>\r\n<DesignAttr'
    if marker not in raw:
        print("❌ 未找到插入点 '</Layout>...<DesignAttr'，文件结构可能不同。")
        sys.exit(1)

    replacement = b'</Layout>\r\n' + listener + b'\r\n<DesignAttr'
    raw = raw.replace(marker, replacement, 1)

    # 7. 写回
    with open(cpt_path, "wb") as f:
        f.write(raw)

    print(f"✅ 已注入 afterinit CSS 事件")
    print(f"   目标: {cpt_path}")
    print(f"   CSS : {css_file}")


if __name__ == "__main__":
    main()
