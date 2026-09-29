# -*- coding: utf-8 -*-
"""冻结表头（通配规则，用户定稿 2026-08-06）
在 <ReportSettings> 内加 <FrozenColumnRow columnrow="A{N+1}"/>，冻结前 N 行表头。
用法：python freeze_header.py <cpt路径> [--rows N]   （默认 N=2，即冻结 2 行表头）
坐标级修改，自动备份 + XML 校验；已存在冻结配置则跳过。"""
import re, sys, shutil
from datetime import datetime
from pathlib import Path

def main():
    fp = Path(sys.argv[1])
    rows = 2
    if '--rows' in sys.argv:
        rows = int(sys.argv[sys.argv.index('--rows') + 1])

    c = fp.read_text(encoding='utf-8')
    if 'FrozenColumnRow' in c:
        print('ℹ️  已有冻结配置，跳过'); return 0

    anchor = '<ReportSettings headerHeight="0" footerHeight="0">\n<PaperSetting/>'
    n = c.count(anchor)
    assert n >= 1, '未找到 ReportSettings/PaperSetting 结构'
    new = (f'<ReportSettings headerHeight="0" footerHeight="0">\n'
           f'<FrozenColumnRow columnrow="A{rows + 1}"/>\n'
           '<PaperSetting/>')
    c = c.replace(anchor, new, n)

    bak = fp.parent / ('_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fp, bak / fp.name)
    fp.write_text(c, encoding='utf-8')

    import xml.etree.ElementTree as ET
    ET.parse(fp)
    print(f'✅ 冻结前 {rows} 行表头: <FrozenColumnRow columnrow="A{rows + 1}"/> ({n} 处), 备份 {bak}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
