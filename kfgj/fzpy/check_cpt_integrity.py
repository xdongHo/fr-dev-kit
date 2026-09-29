# -*- coding: utf-8 -*-
"""
check_cpt_integrity.py — cpt 三合一完整性体检（数据集引用 / 公式函数白名单 / 超链目标存在性）

背景（2026-09-06/07 三次实战事故的工具化，见 ckzl/zsk/tbcw/ 两篇条目）：
  检查1 DSColumn 悬空数据集引用：格子 <O t="DSColumn"> 绑定的 dsName 必须出现在
        TableDataMap 定义集内；悬空数据集在列显隐遮蔽下不暴露，版本参数一选中即整列空白
        （实战：示例预算表 副本版 403 处悬空，页面无任何报错）。
  检查2 公式函数白名单：fr_check 只查公式语法不查函数名是否在引擎注册表内——
        "语法合法但函数不存在"是盲区（实战：ISNUMBER 204 处，服务端日志每日 6120 条
        no function found；FR10 引擎 165+ 注册函数中无 ISNUMBER，替代写法 NVL(x,0)）。
  检查3 超链目标存在性：<ReportletName> CDATA 路径相对 reportlets 根必须指向存在的文件；
        目标页删除而主表超链漏摘即成死链（实战：FS 钻取明细/钻取明细预算 删除时 172+41
        处超链同步摘除；另发现 FS ADJ填报.cpt 21 处死链——目标文件从未存在）。

用法:
    python check_cpt_integrity.py <a.cpt> [b.cpt ...] [--fr-home <FR根/WEB-INF/lib>] [--reportlets-root <路径>] [--json]

退出码: 0=PASS / 1=ERROR(任一检查发现硬伤) / 2=WARN(仅软性警示, 如无法定位 reportlets 根)

白名单来源优先级: --fr-home 扫 jar(实时, 结果写缓存) > 脚本同目录缓存 > 内嵌名单。
内嵌名单生成方法: 扫描 WEB-INF\\lib 各 jar 中 com/fr/function/ 顶层类名(剔除内部类与
Abstract*/辅助基类)，生成日期 2026-09-07，本机 FR 10.0(fine-core/fine-report-engine)。
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
import io
import json
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# ---------------------------------------------------------------- 内嵌函数白名单（降级用）
# 生成日期 2026-09-07；方法: zipfile 扫 WEB-INF\lib\*.jar 的 com/fr/function/ 顶层 .class
# (193 个含内部类 → 187 顶层 → 剔除 Abstract*/LambdaFunction/RangeCondition* 6 个基类辅助 → 181)
EMBEDDED_DATE = '2026-09-07'
EMBEDDED_FUNCTIONS = set(
    "ABS ACOS ACOSH ADD2ARRAY AND ARRAY ASIN ASINH ATAN ATAN2 ATANH AVERAGE BITNOT "
    "BITOPERATION CEILING CHAR CIRCULAR CLASS CNMONEY CODE COL COLCOUNT COLNAME COMBIN "
    "CONCATENATE CORREL COS COSH COUNT CROSSLAYERTOTAL DATE DATEDELTA DATEDIF DATEINMONTH "
    "DATEINQUARTER DATEINWEEK DATEINYEAR DATESUBDATE DATETIME DATETONUMBER DAY DAYS360 "
    "DAYSOFMONTH DAYSOFQUARTER DAYSOFYEAR DAYVALUE DECIMAL DECODE DEGREES ENCODE ENDWITH "
    "ENMONEY ENNUMBER EVAL EVEN EXACT EXP FACT FIELDS FILENAME FILESIZE FILETYPE FIND FLOOR "
    "FORMAT GETUSERDEPARTMENTS GETUSERJOBTITLES GREPARRAY HIERARCHY HOUR I18N IF INARRAY "
    "INDEX INDEXOF INDEXOFARRAY INT ISNULL JOINARRAY JVM LAYERTOTAL LEFT LEN LET LN LOG LOG10 "
    "LOWER LUNAR MAP MAPARRAY MAX MEDIAN MID MIN MINUTE MOD MOM MONTH MONTHDELTA NOW NUMTO "
    "NVL ODD OR PI POWER PRODUCT PROMOTION PROPER PROPORTION QUERY QUERYForJ2V8 RADIANS RAND "
    "RANDBETWEEN RANGE RANK RECORDS REGEXP REMOVEARRAY REPEAT REPLACE REVERSE REVERSEARRAY "
    "RIGHT ROUND ROUND5 ROUNDDOWN ROUNDUP ROW ROWCOUNT SECOND SEQ SIGN SIN SINH SLICEARRAY "
    "SORT SORTARRAY SPLIT SQL SQRT STARTWITH STDEV SUBSTITUTE SUM SUMPRECISE SUMSQ SWITCH "
    "TABLEDATAFIELDS TABLEDATAS TABLES TAN TANH TIME TOBIGDECIMAL TOBINARY TODATE TODAY "
    "TODOUBLE TOHEX TOIMAGE TOINTEGER TOOCTAL TOTEXT TREELAYER TRIM TRUNC UNIQUEARRAY UPPER "
    "UUID VALUE WEBIMAGE WEEK WEEKDATE WEEKDAY WEIGHTEDAVERAGE WRITEARRAY YEAR YEARDELTA"
    .split())

CACHE_NAME = 'check_cpt_integrity.functions.cache.json'
# 非可调用基类/辅助类（jar 里有类名但不是注册函数，进白名单会造成假阴性）
FUNC_CLASS_EXCLUDE_PREFIX = ('Abstract',)
FUNC_CLASS_EXCLUDE = {'LambdaFunction', 'RangeCondition', 'RangeConditionBuilder',
                      'RangeConditionScene'}
DEFAULT_REPORTLETS_ROOT = r'C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets'

RE_FUNC_CALL = re.compile(r'([A-Za-z_$][A-Za-z0-9_$]*)\s*\(')
RE_STRING_LIT = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
RE_DS_REGEX = re.compile(r'<O t="DSColumn">\s*<Attributes\s+dsName="([^"]+)"(?:\s+columnName="([^"]*)")?')
RE_TDM_REGEX = re.compile(r'<TableData\s+name="([^"]+)"')
RE_FORMULA1_REGEX = re.compile(r'<Formula[^>]*>\s*<!\[CDATA\[(.*?)\]\]>', re.S)
RE_FORMULA2_REGEX = re.compile(
    r'class="com\.fr\.base\.Formula"[^>]*>\s*<Attributes>\s*<!\[CDATA\[(.*?)\]\]>', re.S)
RE_REPORTLET_REGEX = re.compile(r'<ReportletName[^>]*>\s*<!\[CDATA\[(.*?)\]\]>', re.S)


# ---------------------------------------------------------------- 函数白名单

def candidate_lib_dirs(fr_home):
    """--fr-home 归一为 lib 目录候选列表(优先 WEB-INF/lib 引擎库)。

    FR 安装根下常有设计器用 <根>/lib(无 com/fr/function 注册类), 不能因它提前返回——
    引擎函数注册类在 webapps/webroot/WEB-INF/lib。返回按优先级排列的候选, 逐个扫描。
    """
    if not fr_home or not os.path.isdir(fr_home):
        return []
    cands = []
    direct = os.path.join(fr_home, 'WEB-INF', 'lib')
    if os.path.isdir(direct):
        cands.append(direct)
    # 限深 4 层 walk 找全部 WEB-INF/lib(Tomcat webapps 部署)
    base_depth = os.path.normpath(fr_home).count(os.sep)
    for dirpath, dirnames, _ in os.walk(fr_home):
        if os.path.basename(dirpath).lower() == 'lib' and \
                os.path.basename(os.path.dirname(dirpath)).upper() == 'WEB-INF' and \
                os.path.isdir(dirpath):
            if dirpath not in cands:
                cands.append(dirpath)
        if os.path.normpath(dirpath).count(os.sep) - base_depth >= 4:
            dirnames[:] = []
    # 兜底: 设计器 <根>/lib 或根目录散装 jar(排最后, 里面的包结构未必是服务器引擎)
    fallback = os.path.join(fr_home, 'lib')
    if os.path.isdir(fallback) and fallback not in cands:
        cands.append(fallback)
    if glob_jars(fr_home) and fr_home not in cands:
        cands.append(fr_home)
    return cands


def glob_jars(d):
    try:
        return [f for f in os.listdir(d) if f.lower().endswith('.jar')]
    except Exception:
        return []


def scan_function_classes(lib_dir):
    """扫 lib(+plugins) jar 的 com/fr/function/ 顶层类名 → (名单, 来源描述, 错误)。"""
    import zipfile
    jars = [os.path.join(lib_dir, j) for j in glob_jars(lib_dir)]
    plugins = os.path.join(os.path.dirname(lib_dir), 'plugins')
    if os.path.isdir(plugins):
        for dirpath, _, files in os.walk(plugins):
            jars += [os.path.join(dirpath, f) for f in files if f.lower().endswith('.jar')]
    names, errors = set(), []
    scanned = 0
    for jp in jars:
        try:
            z = zipfile.ZipFile(jp)
        except Exception as e:
            errors.append('%s: %s' % (os.path.basename(jp), e))
            continue
        scanned += 1
        try:
            for n in z.namelist():
                if n.startswith('com/fr/function/') and n.endswith('.class'):
                    short = n[:-len('.class')].rsplit('/', 1)[-1]
                    if '$' in short:
                        continue  # 内部类非独立注册函数
                    names.add(short)
        except Exception as e:
            errors.append('%s: %s' % (os.path.basename(jp), e))
    wl = {n for n in names
          if not n.startswith(FUNC_CLASS_EXCLUDE_PREFIX) and n not in FUNC_CLASS_EXCLUDE}
    if not wl:
        return None, None, errors or ['未从 jar 提取到 com/fr/function/ 类(混淆/布局变化?)']
    src = '%d 个 jar 扫描(com/fr/function/ 顶层类 %d, 剔基类后 %d)' % (scanned, len(names), len(wl))
    return wl, src, errors


def load_whitelist(fr_home):
    """优先级: 实时扫描(写缓存) > 缓存 > 内嵌。返回 (names, meta, warnings)。"""
    warns = []
    wl = src = None
    errors = []
    for lib_dir in candidate_lib_dirs(fr_home):
        wl, src, errors = scan_function_classes(lib_dir)
        if wl:
            break
        errors = errors or ['%s: 未提取到 com/fr/function/ 类' % lib_dir]
    if fr_home and not wl:
        warns.append('函数清单提取失败(%s), 降级: %s'
                     % (fr_home, '; '.join(errors[-2:])))
    if wl:
        meta = {'source': 'scan', 'detail': src, 'date': time.strftime('%Y-%m-%d'),
                'path': lib_dir, 'count': len(wl)}
        _write_cache(wl, meta)
        return wl, meta, warns
    elif fr_home and not candidate_lib_dirs(fr_home):
        warns.append('--fr-home 无效: %s' % fr_home)

    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_NAME)
    if os.path.isfile(cache):
        try:
            data = json.load(io.open(cache, encoding='utf-8'))
            wl = set(data['functions'])
            meta = {'source': 'cache', 'detail': data.get('meta', {}).get('detail', ''),
                    'date': data.get('meta', {}).get('date', '?'), 'path': cache,
                    'count': len(wl)}
            return wl, meta, warns
        except Exception as e:
            warns.append('缓存损坏(%s), 用内嵌名单' % e)

    meta = {'source': 'embedded',
            'detail': '内嵌 %d 名(生成方法见脚本头注)' % len(EMBEDDED_FUNCTIONS),
            'date': EMBEDDED_DATE, 'path': os.path.abspath(__file__),
            'count': len(EMBEDDED_FUNCTIONS)}
    return set(EMBEDDED_FUNCTIONS), meta, warns


def _write_cache(wl, meta):
    try:
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_NAME)
        io.open(fp, 'w', encoding='utf-8').write(json.dumps(
            {'functions': sorted(wl), 'meta': meta}, ensure_ascii=False, indent=1))
    except Exception:
        pass


# ---------------------------------------------------------------- cpt 解析

def _cell_pos(parent_map, el):
    """沿祖先找最近 <C c= r=>, 返回 0-based (c, r) 或 None。"""
    p = parent_map.get(el)
    while p is not None:
        if p.tag == 'C' and p.get('c') is not None:
            try:
                return (int(p.get('c')), int(p.get('r')))
            except (TypeError, ValueError):
                return None
        p = parent_map.get(p)
    return None


def parse_cpt(path):
    """解析 cpt → {'tabledata':set, 'ds_refs':[(ds,colname,pos)], 'formulas':[(text,pos)],
                    'reportlets':[(path,pos)], 'mode':..., 'errors':[...]}"""
    raw = io.open(path, encoding='utf-8', errors='replace', newline='').read()
    errors = []
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
        parent_map = {c: p for p in root.iter() for c in p}
        tabledata = {el.get('name') for el in root.iter('TableData') if el.get('name')}
        ds_refs, formulas, reportlets = [], [], []
        for el in root.iter():
            if el.tag == 'O' and el.get('t') == 'DSColumn':
                attrs = el.find('Attributes')
                ds = attrs.get('dsName') if attrs is not None else None
                if ds:
                    ds_refs.append((ds, (attrs.get('columnName') or '') if attrs is not None else '',
                                    _cell_pos(parent_map, el)))
            elif el.tag == 'Formula' and el.text and el.text.strip():
                formulas.append((el.text.strip(), _cell_pos(parent_map, el)))
            elif el.tag == 'O' and 'Formula' in (el.get('class') or ''):
                a = el.find('Attributes')
                if a is not None and (a.text or '').strip():
                    formulas.append((a.text.strip().lstrip('='), _cell_pos(parent_map, el)))
            elif el.tag == 'ReportletName' and (el.text or '').strip():
                reportlets.append((el.text.strip(), _cell_pos(parent_map, el)))
        return {'tabledata': tabledata, 'ds_refs': ds_refs, 'formulas': formulas,
                'reportlets': reportlets, 'mode': 'et', 'errors': errors}
    except Exception as e:
        errors.append('XML 解析失败(%s), 退化为正则扫描(无格位): %s' % (type(e).__name__, e))

    tabledata = set(RE_TDM_REGEX.findall(raw))
    ds_refs = [(ds, cn, None) for ds, cn in RE_DS_REGEX.findall(raw)]
    formulas = [(t.strip(), None) for t in RE_FORMULA1_REGEX.findall(raw)]
    formulas += [(t.strip().lstrip('='), None) for t in RE_FORMULA2_REGEX.findall(raw)]
    reportlets = [(t.strip(), None) for t in RE_REPORTLET_REGEX.findall(raw)]
    return {'tabledata': tabledata, 'ds_refs': ds_refs, 'formulas': formulas,
            'reportlets': reportlets, 'mode': 'regex-fallback', 'errors': errors}


# ---------------------------------------------------------------- 三项检查

def colname(c0):
    """0-based 列号 → A1 列名。"""
    s = ''
    c = c0
    while True:
        s = chr(ord('A') + c % 26) + s
        c = c // 26 - 1
        if c < 0:
            return s


def pos_str(pos):
    return '(%s%d)' % (colname(pos[0]), pos[1] + 1) if pos else '(?)'


def check_dangling_ds(parsed):
    """检查1: DSColumn dsName ⊄ TableDataMap → {(ds): {'count','cols','samples'}}"""
    tdm = parsed['tabledata']
    groups = {}
    for ds, colname_attr, pos in parsed['ds_refs']:
        g = groups.setdefault(ds, {'count': 0, 'cols': set(), 'samples': []})
        g['count'] += 1
        if colname_attr:
            g['cols'].add(colname_attr)
        if len(g['samples']) < 5:
            g['samples'].append(pos_str(pos))
    return {ds: {'count': g['count'], 'cols': sorted(g['cols']), 'samples': g['samples']}
            for ds, g in sorted(groups.items()) if ds not in tdm}


def formula_functions(text):
    """词法提取标识符+`(` 的函数名; 跳过字符串字面量与前导 `.`(对象方法)。"""
    t = RE_STRING_LIT.sub('""', text)
    out = set()
    for m in RE_FUNC_CALL.finditer(t):
        i = m.start(1) - 1
        while i >= 0 and t[i] in ' \t\r\n':
            i -= 1
        if i >= 0 and t[i] == '.':
            continue
        out.add(m.group(1))
    return out


def check_formula_functions(parsed, whitelist):
    """检查2: 公式函数 ∉ 引擎注册表 → {fn: {'count','samples','positions'}}

    FR 公式函数名大小写不敏感(year(now()) 即 YEAR/NOW), 白名单按大写比对。
    """
    wl_up = {w.upper() for w in whitelist}
    groups = {}
    n_formula = 0
    for text, pos in parsed['formulas']:
        n_formula += 1
        for fn in formula_functions(text):
            if fn.upper() in wl_up:
                continue
            g = groups.setdefault(fn, {'count': 0, 'samples': [], 'positions': []})
            g['count'] += 1
            if len(g['samples']) < 3:
                g['samples'].append(text[:80])
            if len(g['positions']) < 5 and pos:
                g['positions'].append(pos_str(pos))
    return n_formula, {fn: {'count': g['count'], 'samples': g['samples'],
                            'positions': g['positions']}
                       for fn, g in sorted(groups.items())}


def resolve_reportlets_root(cpt_path, targets, explicit_root):
    """定位 reportlets 根: 显式参数 > 用已存在目标反推祖先 > 本机默认路径。"""
    if explicit_root and os.path.isdir(explicit_root):
        return explicit_root, '参数指定'
    uniq = sorted({t for t in targets if t.startswith('/')})
    anc = os.path.dirname(os.path.abspath(cpt_path))
    while anc:
        hit = sum(1 for t in uniq if os.path.isfile(os.path.join(anc, t.lstrip('/').replace('/', os.sep))))
        if uniq and hit == len(uniq):
            return anc, '由存在目标反推'
        nxt = os.path.dirname(anc)
        if nxt == anc:
            break
        anc = nxt
    if os.path.isdir(DEFAULT_REPORTLETS_ROOT):
        return DEFAULT_REPORTLETS_ROOT, '本机默认路径'
    return None, None


def check_reportlet_targets(path, parsed, explicit_root):
    """检查3: ReportletName 相对 reportlets 根存在性 → {'root','root_src','total','missing'}"""
    targets = [t for t, _ in parsed['reportlets']]
    total = len(targets)
    if not total:
        return {'root': None, 'root_src': '-', 'total': 0, 'skipped': None, 'missing': {}}
    root, src = resolve_reportlets_root(path, targets, explicit_root)
    if not root:
        return {'root': None, 'root_src': None, 'total': total,
                'skipped': '无法定位 reportlets 根(可传 --reportlets-root), 检查跳过',
                'missing': {}}
    groups = {}
    for t, pos in parsed['reportlets']:
        ok = os.path.isfile(os.path.join(root, t.lstrip('/').replace('/', os.sep)))
        if not ok:
            g = groups.setdefault(t, {'count': 0, 'samples': []})
            g['count'] += 1
            if len(g['samples']) < 5:
                g['samples'].append(pos_str(pos))
    return {'root': root, 'root_src': src, 'total': total, 'skipped': None,
            'missing': {t: {'count': g['count'], 'samples': g['samples']}
                        for t, g in sorted(groups.items())}}


# ---------------------------------------------------------------- 汇总/输出

def check_cpt(path, whitelist, wl_meta, reportlets_root=None):
    parsed = parse_cpt(path)
    c1 = check_dangling_ds(parsed)
    n_formula, c2 = check_formula_functions(parsed, whitelist)
    c3 = check_reportlet_targets(path, parsed, reportlets_root)

    checks = {'c1_dangling_ds': c1, 'c2_unknown_fn': c2, 'c3_dead_links': c3}
    errors, warns = list(parsed['errors']), []
    if c1:
        errors.append('检查1: %d 个悬空数据集 / %d 处引用' % (
            len(c1), sum(v['count'] for v in c1.values())))
    if c2:
        errors.append('检查2: %d 个公式函数不在引擎注册表 / %d 处' % (
            len(c2), sum(v['count'] for v in c2.values())))
    if c3.get('skipped'):
        warns.append('检查3: %s' % c3['skipped'])
    elif c3['missing']:
        errors.append('检查3: %d 个目标文件不存在 / %d 处死链' % (
            len(c3['missing']), sum(v['count'] for v in c3['missing'].values())))
    if wl_meta['source'] == 'embedded':
        warns.append('函数白名单为内嵌降级名单(生成日期 %s), 建议传 --fr-home 重扫' % wl_meta['date'])

    if errors:
        verdict, exit_code = 'ERROR', 1
    elif warns:
        verdict, exit_code = 'WARN', 2
    else:
        verdict, exit_code = 'PASS', 0
    return {'file': path, 'verdict': verdict, 'exit': exit_code, 'parsed': parsed,
            'whitelist_meta': wl_meta, 'n_formula': n_formula,
            'checks': checks, 'errors': errors, 'warns': warns}


def fmt_report(r):
    out = []
    out.append('=' * 72)
    out.append('文件: %s' % r['file'])
    out.append('判定: %s   (解析模式: %s)' % (r['verdict'], r['parsed']['mode']))
    wm = r['whitelist_meta']
    out.append('函数白名单: %d 名 [%s, %s, %s]' % (
        wm['count'], wm['source'], wm.get('detail', ''), wm['date']))
    for msg in r['parsed']['errors']:
        out.append('  [!] %s' % msg)
    out.append('-' * 72)
    c1 = r['checks']['c1_dangling_ds']
    n_ds = len(r['parsed']['ds_refs'])
    if not c1:
        out.append('检查1 数据集引用: PASS — %d 处 DSColumn 引用全部在 TableDataMap 内(%d 个数据集)'
                   % (n_ds, len(r['parsed']['tabledata'])))
    else:
        out.append('检查1 数据集引用: FAIL — %d 个悬空数据集 / %d 处引用(定义集 %d 个)'
                   % (len(c1), sum(v['count'] for v in c1.values()), len(r['parsed']['tabledata'])))
        for ds, v in c1.items():
            out.append('  %-16s %4d 处  绑定列[%s]  首现 %s'
                       % (ds, v['count'], ','.join(v['cols'][:4]), ' '.join(v['samples'][:3])))
        out.append('  ★ 悬空数据集被列显隐遮蔽时不暴露, 版本参数选中即空列')
    out.append('-' * 72)
    c2 = r['checks']['c2_unknown_fn']
    if not c2:
        out.append('检查2 公式函数白名单: PASS — %d 个公式, 函数全部在引擎注册表内' % r['n_formula'])
    else:
        out.append('检查2 公式函数白名单: FAIL — %d 个函数未注册 / %d 处调用(公式 %d 个)'
                   % (len(c2), sum(v['count'] for v in c2.values()), r['n_formula']))
        for fn, v in c2.items():
            out.append('  %-16s %4d 处  位置 %s' % (fn, v['count'], ' '.join(v['positions']) or '(?)'))
            out.append('    例: %s' % v['samples'][0])
        out.append('  ★ 服务端日志表象: no function found ... 每次计算刷屏')
    out.append('-' * 72)
    c3 = r['checks']['c3_dead_links']
    if c3.get('skipped') or c3['root'] is None:
        out.append('检查3 超链目标存在性: WARN — %s' % (c3.get('skipped') or '无法定位根'))
    elif not c3['missing']:
        out.append('检查3 超链目标存在性: PASS — %d 处 ReportletName 引用, 目标全部存在(根: %s)'
                   % (c3['total'], c3['root']))
    else:
        out.append('检查3 超链目标存在性: FAIL — %d 个目标缺失 / %d 处死链(共 %d 处引用, 根: %s)'
                   % (len(c3['missing']), sum(v['count'] for v in c3['missing'].values()),
                      c3['total'], c3['root']))
        for t, v in c3['missing'].items():
            out.append('  %4d 处 → %s  首现 %s' % (v['count'], t, ' '.join(v['samples'][:3])))
    for w in r['warns']:
        out.append('  [W] %s' % w)
    out.append('=' * 72)
    return '\n'.join(out)


def to_json(r):
    return {
        'file': r['file'], 'verdict': r['verdict'], 'exit_code': r['exit'],
        'parse_mode': r['parsed']['mode'], 'errors': r['errors'], 'warnings': r['warns'],
        'whitelist': r['whitelist_meta'], 'n_formula': r['n_formula'],
        'tabledata_count': len(r['parsed']['tabledata']),
        'ds_ref_count': len(r['parsed']['ds_refs']),
        'c1_dangling_ds': r['checks']['c1_dangling_ds'],
        'c2_unknown_fn': r['checks']['c2_unknown_fn'],
        'c3_dead_links': r['checks']['c3_dead_links'],
    }


def main(argv):
    use_json = '--json' in argv
    reportlets_root = None
    fr_home = None
    files = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--fr-home':
            i += 1
            fr_home = argv[i] if i < len(argv) else None
        elif a == '--reportlets-root':
            i += 1
            reportlets_root = argv[i] if i < len(argv) else None
        elif a == '--json':
            pass
        else:
            files.append(a)
        i += 1
    if not files:
        print(__doc__)
        return 0
    whitelist, wl_meta, wl_warns = load_whitelist(fr_home)
    worst = 0
    results = []
    for p in files:
        if not os.path.isfile(p):
            print('[!] 文件不存在: %s' % p)
            worst = max(worst, 1)
            continue
        r = check_cpt(p, whitelist, wl_meta, reportlets_root)
        r['warns'] = wl_warns + r['warns']
        results.append(r)
        worst = max(worst, r['exit'])
    if use_json:
        payload = [to_json(r) for r in results]
        print(json.dumps(payload[0] if len(payload) == 1 else payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(fmt_report(r))
        print('汇总: %s  (白名单 %d 名 @%s)' % (
            ' | '.join('%s=%s' % (os.path.basename(r['file']), r['verdict']) for r in results),
            wl_meta['count'], wl_meta['date']))
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
