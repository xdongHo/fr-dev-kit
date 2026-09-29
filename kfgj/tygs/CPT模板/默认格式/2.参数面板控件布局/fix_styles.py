"""
字体统一为微软雅黑 + 左右 padding 6。
"""
import sys, os, shutil, re
from datetime import datetime


def fix_styles(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 不存在: {cpt_path}")
        return False

    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    content = content.replace('name="SimSun"', 'name="微软雅黑"')

    def add_padding(m):
        tag = m.group(0)
        inner = m.group(1)
        if 'paddingLeft=' not in inner:
            tag = tag.replace('<Style ', '<Style paddingLeft="6" ')
        if 'paddingRight=' not in inner:
            tag = tag.replace('<Style ', '<Style paddingRight="6" ')
        return tag

    content = re.sub(r'<Style\s([^>]*)>', add_padding, content)

    if content != original:
        with open(cpt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 样式已修复: {os.path.basename(cpt_path)}")
        return True
    else:
        print(f"⚠️  无变化: {os.path.basename(cpt_path)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python fix_styles.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        fix_styles(p)
