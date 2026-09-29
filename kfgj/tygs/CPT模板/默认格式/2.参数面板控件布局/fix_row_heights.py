"""
行高自动分类：表头 10mm (1442289 FU) / 明细 8mm (1153643 FU)。
检测是否有 DSColumn → 有则按数据集列区分，无则按公式区分。
Row 0 强制保护 + 原高度 ≥1.8M FU 保护。
"""
import sys, os, shutil, re
from datetime import datetime

H_HEADER = "1442289"   # 10mm
H_DETAIL = "1153643"   # 8mm


def fix_row_heights(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 不存在: {cpt_path}")
        return False

    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分类行类型
    row_info = {}
    has_any_ds = False
    for m in re.finditer(r'<C c="\d+" r="(\d+)".*?>(.*?)</C>', content, re.DOTALL):
        row = int(m.group(1))
        body = m.group(2)
        is_ds = 't="DSColumn"' in body or 'ds1.G(' in body or 'ds1.S(' in body or '>.G(' in body
        is_fm = 'class="com.fr.base.Formula"' in body
        if row not in row_info:
            row_info[row] = {'ds': False, 'formula': False}
        if is_ds:
            row_info[row]['ds'] = True
            has_any_ds = True
        if is_fm:
            row_info[row]['formula'] = True

    row_types = {}
    for row, info in row_info.items():
        if has_any_ds:
            row_types[row] = 'data' if info['ds'] else 'header'
        else:
            row_types[row] = 'data' if info['formula'] else 'header'

    if 0 in row_types:
        row_types[0] = 'header'

    # 原高度 ≥1.8M FU 保护
    rh = re.search(r'<RowHeight\s+defaultValue="\d+"\s*>\s*<!\[CDATA\[([^\]]*?)\]\]>', content, re.DOTALL)
    if rh:
        for i, h in enumerate(rh.group(1).split(',')):
            try:
                if int(h.strip()) >= 1800000 and i in row_types:
                    row_types[i] = 'header'
            except:
                pass

    if not row_types:
        print(f"⚠️  无行数据: {os.path.basename(cpt_path)}")
        return False

    def repl(m):
        p1, d, p3, hs, p5 = m.groups()
        heights = [h.strip() for h in hs.split(',') if h.strip()]
        if not heights:
            return m.group(0)
        nh = [H_HEADER if row_types.get(i, 'header') == 'header' else H_DETAIL for i in range(len(heights))]
        return f"{p1}{H_DETAIL}{p3}{','.join(nh)}{p5}"

    rh_re = re.compile(
        r'(<RowHeight\s+defaultValue=")(\d+)("\s*>\s*<!\[CDATA\[)([^\]]*?)(\]\]>\s*</RowHeight>)',
        re.DOTALL)
    new_content = rh_re.sub(repl, content)

    if new_content != content:
        with open(cpt_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 行高已修复: {os.path.basename(cpt_path)}")
        return True
    else:
        print(f"⚠️  无变化: {os.path.basename(cpt_path)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python fix_row_heights.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        fix_row_heights(p)
