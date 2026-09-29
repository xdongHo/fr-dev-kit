# -*- coding: utf-8 -*-
"""
参数面板首行控件 y 统一为 10：取 ReportParameterAttr 块内全部 BoundsAttr 的 y 最小值 min_y，
delta = 10 - min_y，块内所有 BoundsAttr 的 y 统一 += delta（label 与控件同步平移）。
- 只动 ReportParameterAttr 块内的 BoundsAttr；块外（WebWrite 浮动按钮等）一律不碰
- DesignAttr 高度不动
- min_y 已 = 10 的文件跳过
- 改动文件备份同目录 *.bak_<STAMP>（同戳）
用法:
  python unify_panel_y10.py            # dry-run，仅打印计划
  python unify_panel_y10.py --apply    # 备份并实际写盘
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import os, re, sys, shutil, datetime

ROOT = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程"
TARGET_Y = 10.0
APPLY = "--apply" in sys.argv
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

block_re = re.compile(r'<ReportParameterAttr\b[^>]*>.*?</ReportParameterAttr>', re.S)
bounds_re = re.compile(r'<BoundsAttr\b[^>]*?/>')
y_re = re.compile(r'\by="(-?\d+(?:\.\d+)?)"')

def num2str(v):
    return str(int(v)) if v == int(v) else repr(v)

def collect_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if any('_backup_' in part for part in rel.split(os.sep)):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if '_backup_' not in d]
        for fn in filenames:
            if fn.endswith('.cpt') and 'bak' not in fn.lower():
                out.append(os.path.join(dirpath, fn))
    return sorted(out)

def shift_block(block, delta):
    """对块内每个 BoundsAttr 标签的 y 值加 delta，返回 (new_block, n_shifted)"""
    def repl(m):
        tag = m.group(0)
        my = y_re.search(tag)
        if not my:
            return tag
        newv = num2str(float(my.group(1)) + delta)
        return tag[:my.start(1)] + newv + tag[my.end(1):]
    return bounds_re.subn(repl, block)

def main():
    files = collect_files(ROOT)
    changed, skipped, errors = [], [], []
    groups = {}
    for p in files:
        rel = os.path.relpath(p, ROOT)
        raw = open(p, 'rb').read()
        try:
            s = raw.decode('utf-8')
        except UnicodeDecodeError as e:
            errors.append((rel, 'decode-fail: %s' % e)); continue
        blocks = list(block_re.finditer(s))
        if len(blocks) != 1:
            skipped.append((rel, 'skip: %d 个 ReportParameterAttr 块' % len(blocks))); continue
        block = blocks[0].group(0)
        outside_n = len(bounds_re.findall(s[:blocks[0].start()]) + bounds_re.findall(s[blocks[0].end():]))
        tags = list(bounds_re.finditer(block))
        ys = []
        for t in tags:
            my = y_re.search(t.group(0))
            if my:
                ys.append(float(my.group(1)))
        if not ys:
            skipped.append((rel, 'skip: 块内无 BoundsAttr (块外 %d 个不动)' % outside_n)); continue
        min_y = min(ys)
        if abs(min_y - TARGET_Y) < 1e-9:
            skipped.append((rel, 'skip: 首行已是 y=10 (n=%d)' % len(ys))); continue
        delta = TARGET_Y - min_y
        new_block, n_shift = shift_block(block, delta)
        # 校验 1: 数量一致
        new_ys = [float(y_re.search(t.group(0)).group(1)) for t in bounds_re.finditer(new_block)
                  if y_re.search(t.group(0))]
        ok_cnt = (len(new_ys) == len(ys))
        # 校验 2: 平移后首行=10 且所有偏移量一致
        ok_shift = ok_cnt and all(abs((b - a) - delta) < 1e-9 for a, b in zip(sorted(ys), sorted(new_ys)))
        ok_min = ok_cnt and abs(min(new_ys) - TARGET_Y) < 1e-9
        if not (ok_cnt and ok_shift and ok_min):
            errors.append((rel, 'sanity-fail: cnt=%s shift=%s min=%s' % (ok_cnt, ok_shift, ok_min))); continue
        if APPLY:
            bak = p + '.bak_' + STAMP
            shutil.copy2(p, bak)
            open(p, 'wb').write(new_block.join([s[:blocks[0].start()], s[blocks[0].end():]]).encode('utf-8'))
        changed.append((rel, min_y, delta, len(ys), outside_n))
        groups.setdefault((min_y, delta), []).append(rel)

    key = lambda miny: groups[(miny, TARGET_Y - miny)]
    print('== 汇总 (APPLY=%s STAMP=%s) ==' % (APPLY, STAMP))
    print('扫描 %d 个 cpt；改动 %d；跳过 %d；异常 %d' % (len(files), len(changed), len(skipped), len(errors)))
    print('\n-- 按旧首行 y 分组 --')
    for (miny, delta) in sorted(groups):
        print('[旧首行 y=%g -> 10, delta=%+g] %d 个:' % (miny, delta, len(key(miny))))
        for rel in key(miny):
            print('   ', rel)
    print('\n-- 跳过 --')
    for rel, why in skipped:
        print('   ', rel, '|', why)
    if errors:
        print('\n-- 异常(未改动) --')
        for rel, why in errors:
            print('   ', rel, '|', why)

if __name__ == '__main__':
    main()
