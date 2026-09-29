# -*- coding: utf-8 -*-
"""
check_cpt_events.py — cpt 事件环静态检测（setValue→afteredit 递归 → Maximum call stack size exceeded）

背景：FR 的 widget.setValue() 会触发目标控件自身的编辑后(afteredit)事件；多个控件互相清值
构成环（如 legal↔bu↔region）时链式点火直至爆栈（RangeError: Maximum call stack size exceeded）。
本工具解析 cpt 全部 <Listener> 事件，提取 getWidgetByName(...).setValue(...) 调用图，
做控件级有向图环检测 + 护栏识别（判值后再清 / clr 函数式包装），分级输出。

用法:
    python check_cpt_events.py <a.cpt> [b.cpt ...] [--json]

退出码: 0=PASS(无环) / 1=ERROR(有环且存在无护栏边,递归风险) / 2=WARN(有环但全护栏,请人工确认护栏模式)

护栏启发式（同一 JS 块内）:
  1) 函数式判值包装: function clr(n){...getWidgetByName(n).getValue()...setValue...}，
     且 getValue 在 setValue 之前 → 调用 clr("X") 产生的边判"有护栏";
  2) 判值比较: 对目标控件(直接或经变量绑定)的 getValue() 出现在 setValue 之前，
     且两者之间存在 if(/三目/&&/||/!=/== 等条件记号 → 该条 setValue 判"有护栏"。
  启发式仅识别"先判值再清"形态，不能证明运行期终止性；全护栏环判 WARN 而非 PASS 即为此留口。
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

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# ---------------------------------------------------------------- JS 分析

RE_CHAIN_CALL = re.compile(
    r'getWidgetByName\s*\(\s*([\'"])([^\'"]+)\1\s*\)\s*(?:\.\s*([A-Za-z_$][\w$]*)\s*\()')
# 变量实参形态: getWidgetByName(n)（包装函数体内, n 为形参）
RE_CHAIN_CALL_VAR = re.compile(
    r'getWidgetByName\s*\(\s*([A-Za-z_$][\w$]*)\s*\)\s*(?:\.\s*([A-Za-z_$][\w$]*)\s*\()')
RE_GETWD_ANY = re.compile(r'getWidgetByName\s*\(\s*([\'"])([^\'"]+)\1\s*\)')
RE_VARBIND = re.compile(
    r'(?:var|let|const)?\s*([A-Za-z_$][\w$]*)\s*=(?![=])\s*[^;\n]*?'
    r'getWidgetByName\s*\(\s*([\'"])([^\'"]+)\2\s*\)')
RE_VARBIND_VAR = re.compile(
    r'(?:var|let|const)?\s*([A-Za-z_$][\w$]*)\s*=(?![=])\s*[^;\n]*?'
    r'getWidgetByName\s*\(\s*([A-Za-z_$][\w$]*)\s*\)')
RE_VARCALL = re.compile(r'([A-Za-z_$][\w$]*)\s*\.\s*(setValue|getValue|reset)\s*\(')
RE_COND_TOKEN = re.compile(r'if\s*\(|\?|&&|\|\||!=|==')
RE_FUNC_HEAD = re.compile(r'function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*\{')

# setValue 会触发目标控件 afteredit 的事件（递归传播事件）
PROPAGATING_EVENTS = {'afteredit', 'editstop', 'valuechange'}


def _match_brace(js, open_pos):
    """从 '{' 起做花括号配对，返回闭 '}' 下标；失败返回 -1。"""
    depth = 0
    for i in range(open_pos, len(js)):
        c = js[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def extract_functions(js):
    """提取顶层 function 定义: [(name, params, body, span)]。"""
    out = []
    for m in RE_FUNC_HEAD.finditer(js):
        end = _match_brace(js, m.end() - 1)
        if end < 0:
            continue
        out.append({'name': m.group(1), 'params': [p.strip() for p in m.group(2).split(',') if p.strip()],
                    'body': js[m.end():end], 'span': (m.start(), end + 1)})
    return out


def _call_records(js, self_name, skip_spans=(), param_names=()):
    """扫描 JS 文本, 产出对具体控件的 getValue/setValue/reset 调用记录。

    返回 [{'pos','target','method'}]，target 为控件名, 或 '__param__'(包装函数形参)/'__unresolved__'。
    """
    # 变量绑定: var w = ...getWidgetByName("name") / getWidgetByName(n)
    bindings = {}
    for m in RE_VARBIND.finditer(js):
        if any(s <= m.start() < e for s, e in skip_spans):
            continue
        bindings[m.group(1)] = m.group(3)
    for m in RE_VARBIND_VAR.finditer(js):
        if any(s <= m.start() < e for s, e in skip_spans):
            continue
        var, arg = m.group(1), m.group(2)
        if var not in bindings:
            bindings[var] = '__param__' if arg in param_names else '__unresolved__'

    records = []
    taken = lambda p: any(s <= p < e for s, e in skip_spans)

    # 1) 链式: getWidgetByName("X").method(...) / getWidgetByName(n).method(...)
    for m in RE_CHAIN_CALL.finditer(js):
        if taken(m.start()):
            continue
        if m.group(3) in ('setValue', 'getValue', 'reset'):
            records.append({'pos': m.start(), 'target': m.group(2), 'method': m.group(3)})
    for m in RE_CHAIN_CALL_VAR.finditer(js):
        if taken(m.start()):
            continue
        if m.group(2) in ('setValue', 'getValue', 'reset'):
            tgt = '__param__' if m.group(1) in param_names else '__unresolved__'
            records.append({'pos': m.start(), 'target': tgt, 'method': m.group(2)})

    # 2) 变量式: w.setValue(...) / this.getValue() / f.getWidgetByName("X") 赋值变量后调用
    for m in RE_VARCALL.finditer(js):
        if taken(m.start()):
            continue
        var, meth = m.group(1), m.group(2)
        if var == 'this' or var == '_this':
            records.append({'pos': m.start(), 'target': self_name or '__self__', 'method': meth})
        elif var in bindings:
            records.append({'pos': m.start(), 'target': bindings[var], 'method': meth})
        # 未绑定变量的 f.getWidgetByName(n)(参数名)由包装函数分析处理, 此处忽略
    records.sort(key=lambda r: r['pos'])
    return records, bindings


def _guarded_direct(js, records, idx):
    """直呼 setValue 的护栏判断: 之前是否存在对同一目标的 getValue 且其后出现条件记号。"""
    tgt, pos = records[idx]['target'], records[idx]['pos']
    for j in range(idx):
        r = records[j]
        if r['method'] == 'getValue' and r['target'] == tgt and r['pos'] < pos:
            seg = js[r['pos']:pos]
            if RE_COND_TOKEN.search(seg):
                return True
    return False


def analyze_block(js, self_name):
    """分析一个事件 JS 块, 返回 (calls, wrappers, bindings)。

    calls: 每条对具体控件 setValue/getValue/reset 的记录, 带 guarded 标志。
    wrappers: 参数化包装函数: {'name','guarded','params'}。
    """
    funcs = extract_functions(js)
    wrappers = []
    func_spans = [f['span'] for f in funcs]

    # --- 包装函数内部独立分析（目标可能是函数参数） ---
    for f in funcs:
        inner_records, _ = _call_records(f['body'], self_name=None,
                                         param_names=set(f['params']))
        has_set = any(r['method'] == 'setValue' for r in inner_records)
        if not has_set:
            continue
        # getValue 是否先于 setValue（判值后清）
        set_pos = min(r['pos'] for r in inner_records if r['method'] == 'setValue')
        get_positions = [r['pos'] for r in inner_records
                         if r['method'] == 'getValue' and r['pos'] < set_pos]
        guarded = bool(get_positions) and bool(RE_COND_TOKEN.search(f['body'][:set_pos]))
        wrappers.append({'name': f['name'], 'guarded': bool(guarded), 'params': f['params'],
                         'body_len': len(f['body'])})

    # --- 顶层调用（排除函数体内部, 避免重复计边） ---
    top_records, bindings = _call_records(js, self_name=self_name, skip_spans=func_spans)
    calls = []
    wrapper_by_name = {w['name']: w for w in wrappers}
    consumed_wrapper_calls = set()

    for i, r in enumerate(top_records):
        calls.append(dict(r, guarded=None, via='direct'))

    # 包装函数调用点: clr("para_bu") → 边(带包装护栏标志)
    for w in wrappers:
        for m in re.finditer(re.escape(w['name']) + r'\s*\(\s*([\'"])([^\'"]+)\1\s*', js):
            if any(s <= m.start() < e for s, e in func_spans):
                continue
            calls.append({'pos': m.start(), 'target': m.group(2), 'method': 'setValue',
                          'guarded': w['guarded'], 'via': 'wrapper:%s' % w['name']})
        # 无字面量实参的调用无法解析目标, 记未解析
        for m in re.finditer(re.escape(w['name']) + r'\s*\((?!\s*[\'"])', js):
            if any(s <= m.start() < e for s, e in func_spans):
                continue
            key = (w['name'], m.start())
            if key not in consumed_wrapper_calls:
                consumed_wrapper_calls.add(key)
                calls.append({'pos': m.start(), 'target': '__unresolved__', 'method': 'setValue',
                              'guarded': w['guarded'], 'via': 'wrapper:%s' % w['name']})

    # 直呼/变量式 setValue 的护栏
    for c in calls:
        if c['via'] == 'direct' and c['method'] == 'setValue':
            c['guarded'] = _guarded_direct(js, top_records,
                                           next(i for i, r in enumerate(top_records)
                                                if r['pos'] == c['pos'] and r['method'] == 'setValue'))
    calls.sort(key=lambda c: c['pos'])
    return calls, wrappers, bindings


# ---------------------------------------------------------------- cpt 解析

def parse_cpt(path):
    """解析 cpt, 返回 {'widgets':[...], 'events':[...], 'mode':'et'|'regex', 'errors':[...]}。

    event: {'widget','event','name','js'}; widget 为归属控件名(取不到记 '__unknown__')。
    """
    raw = io.open(path, encoding='utf-8', errors='replace', newline='').read()
    errors = []
    # 首选 ElementTree（可靠祖先归属）
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
        parent = {c: p for p in root.iter() for c in p}
        widgets = []
        seen = set()
        for el in root.iter():
            if el.tag == 'WidgetName' and el.get('name'):
                if el.get('name') not in seen:
                    seen.add(el.get('name'))
                    widgets.append(el.get('name'))
        events = []
        for el in root.iter():
            if el.tag != 'Listener':
                continue
            # 归属: 向上找最近一个带 WidgetName 子元素的祖先
            owner, p = '__unknown__', parent.get(el)
            while p is not None:
                wn = next((c for c in p if c.tag == 'WidgetName' and c.get('name')), None)
                if wn is not None:
                    owner = wn.get('name')
                    break
                p = parent.get(p)
            js_parts = [c.text or '' for c in el.iter('Content')]
            js = '\n'.join(js_parts)
            events.append({'widget': owner, 'event': el.get('event') or '',
                           'name': el.get('name') or '', 'js': js})
        return {'widgets': widgets, 'events': events, 'mode': 'et', 'errors': errors}
    except Exception as e:
        errors.append('XML 解析失败(%s), 退化为正则扫描: %s' % (type(e).__name__, e))

    # 正则退化: Listener 归属最近前置 WidgetName
    events = []
    wn_iter = list(RE_GETWD_ANY.finditer(raw))  # 占位, 真实归属用 WidgetName 标签
    widget_positions = []
    for m in re.finditer(r'<WidgetName\s+name="([^"]+)"', raw):
        widget_positions.append((m.start(), m.group(1)))
    widgets, seen = [], set()
    for _, n in widget_positions:
        if n not in seen:
            seen.add(n)
            widgets.append(n)
    for m in re.finditer(r'<Listener\s+event="([^"]*)"(?:\s+name="([^"]*)")?\s*>(.*?)</Listener>',
                         raw, re.S):
        cds = re.findall(r'<!\[CDATA\[(.*?)\]\]>', m.group(3), re.S)
        owner = '__unknown__'
        for pos, n in widget_positions:
            if pos < m.start():
                owner = n
            else:
                break
        events.append({'widget': owner, 'event': m.group(1), 'name': m.group(2) or '',
                       'js': '\n'.join(cds)})
    return {'widgets': widgets, 'events': events, 'mode': 'regex-fallback', 'errors': errors}


# ---------------------------------------------------------------- 调用图与环

def build_graph(parsed):
    """从事件清单构建调用图。返回 edges, cycles, events_analyzed。"""
    has_afteredit = {e['widget'] for e in parsed['events'] if e['event'] in PROPAGATING_EVENTS}
    edges = {}   # (src,dst,event) -> {'guarded': all?, 'calls': n, 'unguarded_pos': [...]}
    events_analyzed = []
    for ev in parsed['events']:
        if not ev['js'].strip():
            continue
        calls, wrappers, bindings = analyze_block(ev['js'], self_name=ev['widget'])
        if calls or wrappers:
            events_analyzed.append({'widget': ev['widget'], 'event': ev['event'],
                                    'name': ev['name'], 'calls': len(calls), 'wrappers': wrappers})
        for c in calls:
            if c['method'] != 'setValue':
                continue
            key = (ev['widget'], c['target'], ev['event'])
            e = edges.setdefault(key, {'guarded': True, 'calls': 0})
            e['calls'] += 1
            if c['guarded'] is not True:
                e['guarded'] = False
    # 控件级传播图: afteredit 源 → 有 afteredit 的目标
    prop_edges = []
    for (src, dst, event), info in edges.items():
        if event in PROPAGATING_EVENTS and src in has_afteredit and dst in has_afteredit:
            prop_edges.append({'src': src, 'dst': dst, 'guarded': info['guarded']})
    cycles = find_cycles(prop_edges, has_afteredit)
    return edges, cycles, events_analyzed


def find_cycles(prop_edges, nodes):
    """迭代式 Tarjan SCC; SCC>1 或自环视为环。返回 [{'nodes':[...], 'edges':[...], 'guarded_all':bool}]。"""
    adj = {}
    for e in prop_edges:
        adj.setdefault(e['src'], []).append(e)
    index_counter = [0]
    index, lowlink, on_stack = {}, {}, set()
    stack, sccs = [], []

    for root in list(nodes):
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            v, pi = work.pop()
            if pi == 0:
                index[v] = lowlink[v] = index_counter[0]
                index_counter[0] += 1
                stack.append(v)
                on_stack.add(v)
            recurse = False
            neighbors = adj.get(v, [])
            for i in range(pi, len(neighbors)):
                w = neighbors[i]['dst']
                if w not in index:
                    work.append((v, i + 1))
                    work.append((w, 0))
                    recurse = True
                    break
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])
            if recurse:
                continue
            if lowlink[v] == index[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[v])

    cycles = []
    for scc in sccs:
        scc_set = set(scc)
        in_edges = [e for e in prop_edges if e['src'] in scc_set and e['dst'] in scc_set]
        is_cycle = len(scc) > 1 or any(e['src'] == e['dst'] for e in in_edges)
        if is_cycle:
            cycles.append({'nodes': sorted(scc), 'edges': in_edges,
                           'guarded_all': all(e['guarded'] for e in in_edges)})
    cycles.sort(key=lambda c: (not c['guarded_all'], len(c['nodes'])))
    return cycles


# ---------------------------------------------------------------- 判定与输出

def check_cpt(path):
    parsed = parse_cpt(path)
    if parsed['errors'] and parsed['mode'] == 'regex-fallback' and not parsed['events']:
        return {'file': path, 'verdict': 'ERROR', 'exit': 1, 'parsed': parsed,
                'edges': {}, 'cycles': [], 'events_analyzed': [],
                'fatal': parsed['errors']}
    edges, cycles, events_analyzed = build_graph(parsed)
    verdict, exit_code = 'PASS', 0
    if any(not c['guarded_all'] for c in cycles):
        verdict, exit_code = 'ERROR', 1
    elif cycles:
        verdict, exit_code = 'WARN', 2
    return {'file': path, 'verdict': verdict, 'exit': exit_code, 'parsed': parsed,
            'edges': edges, 'cycles': cycles, 'events_analyzed': events_analyzed, 'fatal': None}


def fmt_report(r):
    out = []
    out.append('=' * 72)
    out.append('文件: %s' % r['file'])
    out.append('判定: %s   (解析模式: %s)' % (r['verdict'], r['parsed']['mode']))
    for msg in (r['fatal'] or []) + r['parsed']['errors']:
        out.append('  [!] %s' % msg)
    out.append('-' * 72)
    out.append('事件清单 (%d 个 Listener, 控件 %d 个):' % (len(r['parsed']['events']), len(r['parsed']['widgets'])))
    for ev in r['parsed']['events']:
        head = ev['js'].strip().splitlines()[0][:46] if ev['js'].strip() else '(空)'
        out.append('  %-14s %-9s %-10s | %s' % (ev['widget'], ev['event'], ev['name'], head))
    out.append('-' * 72)
    out.append('setValue 调用图 (当前控件 → 目标控件):')
    if not r['edges']:
        out.append('  (无跨控件 setValue)')
    for (src, dst, event), info in sorted(r['edges'].items()):
        guard = '护栏' if info['guarded'] else '无护栏'
        prop = '' if event in PROPAGATING_EVENTS else '  [非传播事件:%s]' % event
        out.append('  %s → %s   [%s, %d 次调用]%s' % (src, dst, guard, info['calls'], prop))
    out.append('-' * 72)
    if not r['cycles']:
        out.append('环检测: 无环 → 无 setValue→afteredit 递归风险')
    for c in r['cycles']:
        tag = 'ERROR 递归风险' if not c['guarded_all'] else 'WARN 全护栏环'
        out.append('环: {%s}  → %s' % (', '.join(c['nodes']), tag))
        for e in c['edges']:
            out.append('    %s → %s  %s' % (e['src'], e['dst'], '有护栏' if e['guarded'] else '★无护栏★'))
        if not c['guarded_all']:
            out.append('    链式点火路径: setValue→目标控件 afteredit→再 setValue→…→Maximum call stack size exceeded')
        else:
            out.append('    护栏模式(先判值再清)已识别; 静态分析不能证明终止性, 请人工确认环上不写入非空值。')
    out.append('=' * 72)
    return '\n'.join(out)


def to_json(r):
    return {
        'file': r['file'], 'verdict': r['verdict'], 'exit_code': r['exit'],
        'parse_mode': r['parsed']['mode'], 'errors': (r['fatal'] or []) + r['parsed']['errors'],
        'widgets': r['parsed']['widgets'],
        'events': [{'widget': e['widget'], 'event': e['event'], 'name': e['name'],
                    'js_head': e['js'].strip()[:120]} for e in r['parsed']['events']],
        'edges': [{'src': k[0], 'dst': k[1], 'event': k[2],
                   'guarded': v['guarded'], 'calls': v['calls']}
                  for k, v in sorted(r['edges'].items())],
        'cycles': [{'nodes': c['nodes'],
                    'edges': [{'src': e['src'], 'dst': e['dst'], 'guarded': e['guarded']}
                              for e in c['edges']],
                    'guarded_all': c['guarded_all']} for c in r['cycles']],
        'events_analyzed': r['events_analyzed'],
    }


def main(argv):
    args = [a for a in argv if a != '--json']
    use_json = '--json' in argv
    if not args:
        print(__doc__)
        return 0
    worst = 0
    results = []
    for p in args:
        if not os.path.isfile(p):
            print('[!] 文件不存在: %s' % p)
            worst = max(worst, 1)
            continue
        r = check_cpt(p)
        results.append(r)
        worst = max(worst, r['exit'])
    if use_json:
        payload = [to_json(r) for r in results]
        print(json.dumps(payload[0] if len(payload) == 1 else payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(fmt_report(r))
        print('汇总: %s' % ' | '.join('%s=%s' % (os.path.basename(r['file']), r['verdict']) for r in results))
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
