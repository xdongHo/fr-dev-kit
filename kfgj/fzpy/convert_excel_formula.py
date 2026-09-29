"""
Excel 公式 → FineReport 公式转换器
===================================
用于 Excel 导入 CPT 前批量转换公式，尽可能自动完成兼容层转换，
对无法自动转换的复杂场景生成警告报告供人工处理。

用法:
  # 转换单个公式字符串
  python convert_excel_formula.py --formula "=IF(ISBLANK(A1),0,A1/B1)"

  # 批量处理 CPT 文件中的公式
  python convert_excel_formula.py --cpt path/to/report.cpt

  # 批量处理目录下所有 CPT
  python convert_excel_formula.py --dir path/to/reportlets/

  # 仅检查不修改（dry-run）
  python convert_excel_formula.py --cpt path/to/report.cpt --dry-run

转换规则:
  ┌──────────────────────────────┬─────────────────────────────────────┐
  │ Excel 公式                    │ FR 公式                             │
  ├──────────────────────────────┼─────────────────────────────────────┤
  │ TEXT(val, fmt)              │ FORMAT(val, fmt)                    │
  │ ISBLANK(x)                  │ LEN(x)=0                            │
  │ A1 & B1                     │ A1 + B1                             │
  │ $A$1 (绝对引用)              │ A1 (移除 $ 符号)                    │
  │ OFFSET(A1, -1, 0)          │ A1[-1]                              │
  │ OFFSET(A1, 0, 1)           │ A1[;+1]                             │
  │ OFFSET(A1, -1, 1)          │ A1[-1;+1]                           │
  │ AND(a,b,c)                  │ a && b && c                         │
  │ OR(a,b,c)                   │ a || b || c                         │
  │ Sheet1!A1 (跨sheet引用)      │ ✅ 兼容，FR 支持相同语法              │
  │                              │ 特殊字符需加引号: ='sheet-1'!A1      │
  │                              │ ⚡ 注意避免循环引用(见注意事项)       │
  │ VLOOKUP(...)                │ ⚠️ 警告: 建议用 MAP() 或 VALUE()      │
  └──────────────────────────────┴─────────────────────────────────────┘

注意事项:
  - FR 同模板内跨 sheet 引用与 Excel 语法一致: =sheetname!cellname
  - Sheet 名称含特殊字符(短线/下划线等)需加单引号: ='sheet-name'!A1
  - ⚡ 避免循环跨 sheet 引用: 一个 sheet 只能触发一个其引用的 sheet，
    多级依赖会导致计算中断返回空值。建议将公共依赖提取到独立 sheet。
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

import re
import os
import sys
import shutil
import argparse
from datetime import datetime
from typing import List, Tuple, Optional


# ─── 转换规则定义 ───────────────────────────────────────────────

def _split_args(arg_str: str) -> List[str]:
    """按逗号分割函数参数，尊重嵌套括号和引号"""
    args = []
    depth = 0
    in_string = False
    string_char = None
    current = []

    i = 0
    while i < len(arg_str):
        ch = arg_str[i]

        if in_string:
            current.append(ch)
            if ch == string_char and (i == 0 or arg_str[i-1] != '\\'):
                in_string = False
        elif ch in ('"', "'"):
            in_string = True
            string_char = ch
            current.append(ch)
        elif ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1

    if current:
        args.append(''.join(current).strip())
    return args


def convert_remove_dollar(formula: str) -> Tuple[str, int]:
    """移除 Excel 绝对引用符号 $"""
    new_f = re.sub(r'\$', '', formula)
    return new_f, len(formula) - len(new_f)


def convert_text_to_format(formula: str) -> Tuple[str, int]:
    """TEXT(value, format) → FORMAT(value, format)"""
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        return 'FORMAT('

    new_f = re.sub(r'\bTEXT\(', repl, formula)
    return new_f, count


def convert_isblank(formula: str) -> Tuple[str, int]:
    """ISBLANK(x) → LEN(x)=0"""
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        return f'LEN({m.group(1)})=0'

    # 匹配 ISBLANK(...)，尊重嵌套括号
    pattern = r'ISBLANK\('
    result = []
    i = 0
    while i < len(formula):
        # 防止误匹配（如 DISBLANK 中的 ISBLANK）
        if i > 0 and (formula[i-1].isalnum() or formula[i-1] == '_'):
            result.append(formula[i])
            i += 1
            continue
        match = re.match(pattern, formula[i:])
        if not match:
            result.append(formula[i])
            i += 1
            continue

        # 找到 ISBLANK( 的位置，解析括号内的内容
        start = i + match.end()
        depth = 1
        j = start
        in_str = False
        str_ch = None
        while j < len(formula) and depth > 0:
            ch = formula[j]
            if in_str:
                if ch == str_ch and formula[j-1] != '\\':
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            j += 1

        if depth == 0:
            inner = formula[start:j-1]
            result.append(f'LEN({inner})=0')
            count += 1
            i = j
        else:
            result.append(formula[i])
            i += 1

    return ''.join(result), count


def convert_string_concat(formula: str) -> Tuple[str, int]:
    """
    A1&B1 → A1+B1 (FR 用 + 做字符串拼接)
    注意: 不转换引号字符串内的 &，如 "Profit & Loss"
    """
    count = 0
    result = []
    in_string = False
    string_char = None
    i = 0

    while i < len(formula):
        ch = formula[i]
        if in_string:
            result.append(ch)
            if ch == string_char and (i == 0 or formula[i-1] != '\\'):
                in_string = False
        elif ch in ('"', "'"):
            in_string = True
            string_char = ch
            result.append(ch)
        elif ch == '&':
            # 检查前后是否是公式元素（非运算符上下文）
            result.append('+')
            count += 1
        else:
            result.append(ch)
        i += 1

    return ''.join(result), count


def convert_offset(formula: str) -> Tuple[str, int]:
    """OFFSET(ref, rows, cols, [height], [width]) → 层次坐标"""
    count = 0

    pattern = r'OFFSET\('
    result = []
    i = 0

    while i < len(formula):
        # 防止误匹配（如 SUBOFFSET 中的 OFFSET）
        if i > 0 and (formula[i-1].isalnum() or formula[i-1] == '_'):
            result.append(formula[i])
            i += 1
            continue
        match = re.match(pattern, formula[i:])
        if not match:
            result.append(formula[i])
            i += 1
            continue

        # 解析 OFFSET 参数
        start = i + match.end()
        depth = 1
        j = start
        in_str = False
        str_ch = None
        while j < len(formula) and depth > 0:
            ch = formula[j]
            if in_str:
                if ch == str_ch and formula[j-1] != '\\':
                    in_str = False
            elif ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            j += 1

        if depth != 0:
            result.append(formula[i])
            i += 1
            continue

        inner = formula[start:j-1]
        args = _split_args(inner)

        if len(args) < 3:
            # OFFSET 至少需要 3 个参数
            result.append(f'OFFSET({inner})')
            i = j
            continue

        ref = args[0]
        rows = args[1].strip()
        cols = args[2].strip()

        # 如果有 height/width → 无法转换，保留原样并标记
        if len(args) >= 4 and args[3].strip() not in ('', '0', '1'):
            result.append(f'OFFSET({inner})')
            i = j
            continue
        if len(args) >= 5 and args[4].strip() not in ('', '0', '1'):
            result.append(f'OFFSET({inner})')
            i = j
            continue

        # 构造层次坐标
        parts = []
        if rows != '0':
            if rows.startswith('-'):
                parts.append(rows)
            else:
                parts.append(f'+{rows}' if rows != '0' else '')
        if cols != '0':
            if cols.startswith('-'):
                parts.append(f';{cols}')
            else:
                parts.append(f';+{cols}')

        if not parts:
            # rows=0, cols=0 → 就是 ref 本身
            coord = ref
        elif len(parts) == 1 and not parts[0].startswith(';'):
            coord = f'{ref}[{parts[0]}]'
        elif len(parts) == 1 and parts[0].startswith(';'):
            coord = f'{ref}[{parts[0]}]'
        else:
            coord = f'{ref}[{"".join(parts)}]'

        result.append(coord)
        count += 1
        i = j

    return ''.join(result), count


def convert_and_or(formula: str) -> Tuple[str, int]:
    """AND(a,b,c) → a&&b&&c, OR(a,b,c) → a||b||c"""
    count = 0

    def convert_func(func_name, operator):
        nonlocal count
        pattern = rf'{func_name}\('
        res = []
        i = 0
        while i < len(formula):
            # 使用 re.match 逐字符扫描，但需额外校验：位置 i 之前不能是单词字符
            # 否则 IFERROR 中的 OR 会被误匹配（\b 在子串开头会失效）
            if i > 0 and (formula[i-1].isalnum() or formula[i-1] == '_'):
                res.append(formula[i])
                i += 1
                continue
            match = re.match(pattern, formula[i:])
            if not match:
                res.append(formula[i])
                i += 1
                continue

            start = i + match.end()
            depth = 1
            j = start
            in_str = False
            str_ch = None
            while j < len(formula) and depth > 0:
                ch = formula[j]
                if in_str:
                    if ch == str_ch and formula[j-1] != '\\':
                        in_str = False
                elif ch in ('"', "'"):
                    in_str = True
                    str_ch = ch
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                j += 1

            if depth != 0:
                res.append(formula[i])
                i += 1
                continue

            inner = formula[start:j-1]
            args = _split_args(inner)
            if len(args) >= 2:
                res.append(f' {operator} '.join(args))
                count += 1
            else:
                res.append(f'{func_name}({inner})')
            i = j
        return ''.join(res)

    formula = convert_func('AND', '&&')
    formula = convert_func('OR', '||')
    return formula, count


# ─── 警告检测 ──────────────────────────────────────────────────

WARNING_PATTERNS = [
    (r'\bVLOOKUP\(', 'VLOOKUP 建议改为 MAP("ds", key, "col") 或 VALUE("ds", row, col)'),
    (r'\bHLOOKUP\(', 'HLOOKUP 建议改为 MAP() 或 VALUE()'),
    (r'\bINDIRECT\(', 'INDIRECT 在 FR 中无等价公式，需重新设计逻辑'),
    (r'\bINDEX\(', 'INDEX 在 FR 中用法不同，建议用层次坐标或 VALUE() 替代'),
    (r'\bMATCH\(', 'MATCH 在 FR 中无直接等价函数，建议用 MAP() 或数据集过滤'),
    (r'\bROW\(\s*\)', 'ROW() 在 FR 中返回扩展行号，语义不同，注意验证'),
    (r'\bCOLUMN\(\s*\)', 'COLUMN() 在 FR 中返回扩展列号，语义不同，注意验证'),
    (r'\bTRANSPOSE\(', 'TRANSPOSE 在 FR 中不支持，需重新设计布局'),
]


def detect_warnings(formula: str) -> List[str]:
    """检测需要人工处理的公式模式"""
    warnings = []
    for pattern, message in WARNING_PATTERNS:
        matches = re.findall(pattern, formula)
        if matches:
            for m in matches[:3]:  # 最多报告 3 次
                if isinstance(m, tuple):
                    m = m[0] if m else ''
                warnings.append(f"  ⚠ {message}  → 发现: {m}")
            if len(matches) > 3:
                warnings.append(f"  ⚠ (还有 {len(matches)-3} 处相同模式)")
    return warnings


# ─── 核心转换引擎 ──────────────────────────────────────────────

def convert_formula(excel_formula: str) -> Tuple[str, List[str], bool]:
    """
    转换单条 Excel 公式为 FR 公式。

    参数:
        excel_formula: Excel 公式字符串（可带或不带前导 =）

    返回:
        (fr_formula, warnings, changed): 转换后公式、警告列表、是否修改
    """
    original = excel_formula.strip()

    # 去掉前导 =
    if original.startswith('='):
        formula = original[1:]
    else:
        formula = original

    total_changes = 0
    all_warnings = []

    # ── 检测警告（转换前） ──
    pre_warnings = detect_warnings(formula)
    all_warnings.extend(pre_warnings)

    # ── 按顺序执行转换 ──
    # 顺序很重要: &→+ 必须在 AND/OR→&&/|| 之前执行，
    # 否则 && 中的 & 会被错误转换为 +。
    conversions = [
        ('移除 $ 绝对引用', convert_remove_dollar),
        ('TEXT → FORMAT', convert_text_to_format),
        ('ISBLANK → LEN()=0', convert_isblank),
        ('OFFSET → 层次坐标', convert_offset),
        ('& → + (字符串拼接)', convert_string_concat),   # ← 先处理 & 拼接
        ('AND/OR → && / ||', convert_and_or),            # ← 再处理 AND/OR
    ]

    for name, converter in conversions:
        new_formula, changes = converter(formula)
        if changes > 0:
            total_changes += changes
        formula = new_formula

    # ── 检测警告（转换后） ──
    post_warnings = detect_warnings(formula)
    # 去重
    existing = set(all_warnings)
    for w in post_warnings:
        if w not in existing:
            all_warnings.append(w)

    changed = total_changes > 0 or len(all_warnings) > 0
    return '=' + formula, all_warnings, changed


# ─── CPT 文件处理 ──────────────────────────────────────────────

def _extract_formula_cdata(content: str) -> List[Tuple[int, int, str]]:
    """从 CPT XML 中提取所有公式 CDATA 的位置和内容"""
    # 匹配 CellElementList 中的公式 = 开头的 CDATA
    pattern = re.compile(r'(<Attributes>\s*<!\[CDATA\[)(=.*?)(\]\]></Attributes>)', re.DOTALL)
    matches = []
    for m in pattern.finditer(content):
        matches.append((m.start(2), m.end(2), m.group(2)))
    return matches


def process_cpt_file(cpt_path: str, dry_run: bool = False) -> dict:
    """
    处理单个 CPT 文件中的所有公式。

    返回:
        {
            'file': path,
            'formulas_processed': int,
            'formulas_changed': int,
            'warnings': [(cell_context, warning_msg), ...],
            'errors': [str, ...]
        }
    """
    result = {
        'file': cpt_path,
        'formulas_processed': 0,
        'formulas_changed': 0,
        'warnings': [],
        'errors': [],
    }

    # 读取文件
    try:
        with open(cpt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['errors'].append(f'读取失败: {e}')
        return result

    # 提取公式
    formulas = _extract_formula_cdata(content)
    if not formulas:
        return result

    result['formulas_processed'] = len(formulas)

    # 从后往前替换（避免位置偏移）
    new_content = content
    for start, end, formula in reversed(formulas):
        fr_formula, warnings, changed = convert_formula(formula)

        if changed:
            result['formulas_changed'] += 1

        if warnings:
            # 获取公式上下文（所在行附近）
            line_start = content.rfind('\n', 0, start) + 1
            line_num = content[:start].count('\n') + 1
            context = f'行 {line_num}: {formula[:60]}...'
            for w in warnings:
                result['warnings'].append((context, w))

        # 替换
        new_content = new_content[:start] + fr_formula + new_content[end:]

    # 写入
    if not dry_run and result['formulas_changed'] > 0:
        try:
            # 备份
            base = os.path.dirname(cpt_path)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            bak_dir = os.path.join(base, f'_formula_backup_{ts}')
            os.makedirs(bak_dir, exist_ok=True)
            fname = os.path.basename(cpt_path)
            shutil.copy2(cpt_path, os.path.join(bak_dir, fname))

            with open(cpt_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # XML 校验
            import xml.etree.ElementTree as ET
            try:
                ET.fromstring(new_content)
            except ET.ParseError as e:
                result['errors'].append(f'XML 损坏: {e} — 已从备份恢复')
                shutil.copy2(os.path.join(bak_dir, fname), cpt_path)
                result['formulas_changed'] = 0

        except Exception as e:
            result['errors'].append(f'写入失败: {e}')

    return result


def _find_cpt_files(directory: str) -> List[str]:
    """递归查找目录中所有 .cpt 文件"""
    cpt_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过备份目录
        dirs[:] = [d for d in dirs if not d.startswith('_')]
        for f in files:
            if f.endswith('.cpt'):
                cpt_files.append(os.path.join(root, f))
    return cpt_files


# ─── 输出格式化 ────────────────────────────────────────────────

def format_report(results: List[dict], verbose: bool = False) -> str:
    """格式化转换报告"""
    lines = []
    total_processed = sum(r['formulas_processed'] for r in results)
    total_changed = sum(r['formulas_changed'] for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)
    total_errors = sum(len(r['errors']) for r in results)
    files_with_changes = sum(1 for r in results if r['formulas_changed'] > 0)
    files_with_warnings = sum(1 for r in results if r['warnings'])

    lines.append('=' * 60)
    lines.append('  Excel → FR 公式转换报告')
    lines.append('=' * 60)
    lines.append(f'  处理文件: {len(results)} 个')
    lines.append(f'  公式总数: {total_processed}')
    lines.append(f'  已转换:   {total_changed}')
    lines.append(f'  警告:     {total_warnings}')
    lines.append(f'  错误:     {total_errors}')
    lines.append('')

    if verbose or total_warnings > 0:
        for r in results:
            if r['warnings'] or r['errors']:
                lines.append(f'── {r["file"]} ──')
                for ctx, warn in r['warnings']:
                    lines.append(f'  {ctx}')
                    lines.append(f'    {warn}')
                for err in r['errors']:
                    lines.append(f'  ❌ {err}')
                lines.append('')

    # 转换明细
    if verbose:
        lines.append('── 转换明细 ──')
        for r in results:
            if r['formulas_processed'] > 0:
                status = '✓' if r['errors'] == [] else '✗'
                lines.append(
                    f'  {status} {os.path.basename(r["file"])}: '
                    f'{r["formulas_changed"]}/{r["formulas_processed"]} 已转换'
                )

    return '\n'.join(lines)


# ─── CLI ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Excel 公式 → FineReport 公式转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --formula "=IF(ISBLANK(A1),0,A1/B1)"
  %(prog)s --cpt report.cpt
  %(prog)s --dir reportlets/test/ --verbose
  %(prog)s --cpt report.cpt --dry-run
        """
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--formula', '-f', type=str,
                       help='转换单条 Excel 公式')
    group.add_argument('--cpt', '-c', type=str,
                       help='处理单个 CPT 文件中的公式')
    group.add_argument('--dir', '-d', type=str,
                       help='批量处理目录下所有 CPT 文件')

    parser.add_argument('--dry-run', action='store_true',
                        help='仅检查不修改文件')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出')
    args = parser.parse_args()

    if args.formula:
        # 单公式模式
        fr_formula, warnings, changed = convert_formula(args.formula)
        print(f'Excel:  {args.formula}')
        print(f'FR:     {fr_formula}')
        if warnings:
            print('\n⚠ 警告:')
            for w in warnings:
                print(f'  {w}')
        if not changed and not warnings:
            print('\n✓ 公式兼容，无需转换')

    elif args.cpt:
        # 单文件模式
        cpt_path = os.path.abspath(args.cpt)
        if not os.path.isfile(cpt_path):
            print(f'✗ 文件不存在: {cpt_path}')
            sys.exit(1)

        result = process_cpt_file(cpt_path, dry_run=args.dry_run)
        print(format_report([result], verbose=args.verbose))

        if args.dry_run and result['formulas_changed'] > 0:
            print(f'[DRY RUN] 将修改 {result["formulas_changed"]} 条公式，使用 --cpt 正式执行')

    elif args.dir:
        # 批量模式
        dir_path = os.path.abspath(args.dir)
        if not os.path.isdir(dir_path):
            print(f'✗ 目录不存在: {dir_path}')
            sys.exit(1)

        cpt_files = _find_cpt_files(dir_path)
        if not cpt_files:
            print(f'✗ 目录中未找到 .cpt 文件: {dir_path}')
            sys.exit(1)

        results = []
        for i, cpt_f in enumerate(cpt_files, 1):
            rel = os.path.relpath(cpt_f, dir_path)
            if args.verbose:
                print(f'[{i}/{len(cpt_files)}] {rel} ...')
            result = process_cpt_file(cpt_f, dry_run=args.dry_run)
            results.append(result)

        print(format_report(results, verbose=args.verbose))

        if args.dry_run:
            changed = sum(1 for r in results if r['formulas_changed'] > 0)
            if changed > 0:
                print(f'[DRY RUN] {changed} 个文件有待转换，使用 --dir 正式执行')


if __name__ == '__main__':
    main()
