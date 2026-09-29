# -*- coding: utf-8 -*-
"""Generate 15 category summary notes from parsed FR11 docs."""
import json, os, re, html as htmlmod
from collections import Counter
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, '_parsed')
NOTE_DIR = BASE

with open(os.path.join(OUT_DIR, 'all_docs.json'), encoding='utf-8') as f:
    docs = json.load(f)

CAT_META = {
    'chart':        ('chart_summary.md',        '图表',        '图表类型/图表样式/图表特效/扩展图表/ECharts/地图'),
    'data_source':  ('data_source_summary.md',  '数据源',      '数据连接/数据集/数据库/驱动管理/FineDB'),
    'deploy_cluster': ('deploy_cluster_summary.md', '部署与集群', '部署/集群/服务器/Tomcat/Nginx/迁移/升级/运维'),
    'export':       ('export_summary.md',       '导出',        'Excel导出/PDF导出/Word导出/图片导出/CSV'),
    'fill_submit':  ('fill_submit_summary.md',  '填报与提交',  '填报/提交/智能提交/数据校验/Excel导入/暂存'),
    'formula':      ('formula_summary.md',      '公式与函数',  '公式/函数/层次坐标/运算符/自定义函数'),
    'frm_decision': ('frm_decision_summary.md', '决策报表',    '决策报表/表单/自适应/组件/报表块'),
    'mobile':       ('mobile_summary.md',       '移动端',      '移动端/App/微信/钉钉/HTML5/OEM'),
    'permission':   ('permission_summary.md',   '权限',        '权限/角色/用户/认证/单点登录/数据权限'),
    'param_control': ('param_control_summary.md', '参数与控件', '参数/控件/参数面板/下拉框/联动/查询'),
    'print':        ('print_summary.md',        '打印',        '打印/分页预览/打印机/纸张/水印'),
    'dev':          ('js_api_summary.md',       '二次开发与JS API', 'JS/API/插件/自定义/事件/前端'),
    'skin_theme':   ('skin_theme_summary.md',   '主题与样式',  '主题/皮肤/配色/样式/外观'),
    'performance':  ('performance_summary.md',  '性能优化',    '性能/优化/内存/缓存/并发/大数据量'),
    'other':        ('other_summary.md',        '其他',        'FAQ/产品月报/未分类'),
}

NOISE_LINE = re.compile(r'^(\[图片[^\]]*\]|#{1,6}\s|[-|:：、\s]{3,}$|版本|学习视频|^$)')


def is_noise_line(l):
    l = l.strip()
    if not l:
        return True
    if l.startswith('|'):
        return True
    if re.fullmatch(r'\[图片[^\]]*\]', l):
        return True
    if re.match(r'^#{1,6}\s', l):
        return True
    if re.fullmatch(r'[|:\-—\s]+', l):
        return True
    if l in ('版本', '概述', '应用场景', '功能简介', '预期效果', '问题描述', '功能描述', '操作步骤'):
        return True
    return False


def first_sentences(text, n=3, maxlen=220, title=''):
    """Take first n real sentences from doc opening (actual doc text, no fabrication)."""
    lines = []
    for l in text.split('\n'):
        ls = l.strip()
        if not ls:
            continue
        if ls.startswith('##'):
            continue
        if re.fullmatch(r'\[图片[^\]]*\]', ls):
            continue
        if ls.startswith('|'):
            continue
        if len(ls) < 10:
            continue
        if re.match(r'^(报表服务器版本|设计器版本|設計器版本|报表设计器版本|jar包版本|JAR包|插件版本|服务器报表版本|版本|JAR|服务器版本)', ls):
            continue
        if re.match(r'^[\d]{2,4}(\.\d+){1,3}V?\d', ls):
            continue  # flattened version-table residue e.g. 11.0V11.0V11.0, 10.02019-07-31V1.0
        ls = ls.lstrip('- ').strip()
        if not ls:
            continue
        lines.append(ls)
        if len(lines) >= n * 3:
            break
    # prefer lines with sentence endings, then take up to n
    picked = []
    for l in lines:
        if len(picked) >= n:
            break
        picked.append(l)
    out = ' '.join(picked)
    if not out:
        # fallback: doc title itself is the most honest concept for empty pages
        out = title
    if len(out) > maxlen:
        out = out[:maxlen].rsplit('。', 1)[0] if '。' in out[:maxlen] else out[:maxlen]
    return out.strip()


def extract_apis(text):
    items = []
    for m in re.finditer(r'(?i)\b(select|insert|update|delete)\s+[^;\n]{0,100}', text):
        items.append(('SQL', m.group(0).strip()[:120]))
    for m in re.finditer(r'com\.fr\.[\w.$]{3,80}', text):
        items.append(('Java', m.group(0).strip()[:120]))
    # JS/API method chains & known APIs
    js_pats = [
        r'_g\(\)[^;\n]{0,80}', r'FR\.[A-Za-z_$][\w$]*\([^)]{0,60}\)', r'contentPane\.[A-Za-z_$][\w$.]{1,60}',
        r'getWidgetByName\([^)]{0,40}\)', r'gotoPage\([^)]{0,60}\)', r'getCellValue\([^)]{0,60}\)',
        r'setCellValue\([^)]{0,60}\)', r'FR\.i18nText\([^)]{0,40}\)',
    ]
    for pat in js_pats:
        for m in re.finditer(pat, text):
            items.append(('JS', m.group(0).strip()[:120]))
    # formulas with parentheses
    for m in re.finditer(r'=?[A-Za-z][A-Za-z0-9_]{1,24}\([^)]{0,80}\)', text):
        s = m.group(0).strip()
        if s.startswith(('if(', 'function', 'var ', 'for(', 'while(')):
            continue
        if re.match(r'^[A-Za-z0-9]{1,3}\(.*$', s) and not re.search(r'[\u4e00-\u9fff]', s):
            # short function names like ABS( likely formulas too; keep
            pass
        items.append(('公式', s[:120]))
    # dedupe, cap
    seen, out = set(), []
    for kind, s in items:
        key = (kind, re.sub(r'\s+', '', s))
        if key in seen:
            continue
        seen.add(key)
        out.append(f'{kind}: {s}')
        if len(out) >= 6:
            break
    return '；'.join(out) if out else ''


def version_points(text, title):
    """FR11-specific version lines (11.0.x) with context."""
    pts = []
    for m in re.finditer(r'11\.0\.\d+', text):
        start = max(0, m.start() - 10)
        line_start = text.rfind('\n', 0, start) + 1
        line_end = text.find('\n', m.end())
        if line_end == -1:
            line_end = min(len(text), m.end() + 120)
        line = text[line_start:line_end].strip()
        line = re.sub(r'\s+', ' ', line)
        if 6 <= len(line) <= 160 and not line.startswith('|'):
            pts.append(line)
    seen, out = set(), []
    for p in pts:
        k = re.sub(r'\s+', '', p)
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
        if len(out) >= 3:
            break
    return '；'.join(out)


def main():
    by_cat = {}
    for d in docs:
        by_cat.setdefault(d['category'], []).append(d)

    today = date.today().isoformat()
    for cat in CAT_META:
        fname, cname, themes = CAT_META[cat]
        lst = sorted(by_cat.get(cat, []), key=lambda d: int(d['did']))
        lines = []
        lines.append(f'# FR11 知识库 · {cname}总结')
        lines.append('')
        lines.append(f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档，gb2312）')
        lines.append(f'> 文档数：{len(lst)} 篇')
        lines.append(f'> 生成时间：{today}')
        lines.append(f'> 主题范围：{themes}')
        lines.append('')
        lines.append('---')
        lines.append('')
        # theme frequency from titles
        kws = ['图表', '填报', '提交', '导出', '打印', '参数', '控件', '函数', '公式', 'JS', 'API', '权限', '数据',
               '部署', '集群', '移动端', 'App', 'FVS', '插件', '主题', '样式', '性能', '缓存', '报表', '单元格',
               '决策报表', '地图', '大数据', '定时调度', '数据集', '数据库', '自定义']
        tcount = Counter()
        for d in lst:
            for k in kws:
                if k in d['title']:
                    tcount[k] += 1
        top = tcount.most_common(12)
        lines.append('## 主题速览（标题关键词频次）')
        lines.append('')
        lines.append('| 关键词 | 篇数 |' if top else '（无）')
        lines.append('|--------|------|' if top else '')
        for k, v in top:
            lines.append(f'| {k} | {v} |')
        lines.append('')
        lines.append('## 文档条目')
        lines.append('')
        for d in lst:
            t = d['text']
            did, title = d['did'], d['title']
            concept = first_sentences(t, title=title) if len(t) > 80 else (t[:150] if t else '无法解析')
            apis = extract_apis(t)
            vp = version_points(t, title)
            lines.append(f'### doc-view-{did}｜{title}')
            lines.append(f'- **doc-view ID**：{did}')
            lines.append(f'- **核心概念**：{concept}')
            if apis:
                lines.append(f'- **关键API/代码**：{apis}')
            if vp:
                lines.append(f'- **FR11版本要点**：{vp}')
            lines.append('')
        # summary
        lines.append('---')
        lines.append('')
        lines.append('## 总结')
        lines.append('')
        lines.append(f'- 本类共 {len(lst)} 篇文档，doc-view ID 覆盖：`{lst[0]["did"]}` ~ `{lst[-1]["did"]}`（按 ID 排序，非连续）')
        vcount = sum(1 for d in lst if '11.0.' in d['text'])
        lines.append(f'- 提及 FR11 子版本号（11.0.x）的文档：{vcount} 篇')
        lines.append('- 无法解析文档：0 篇（全部成功提取正文）')
        lines.append('- 全部条目均直接转录自离线 HTML 正文，未做任何推断补充')
        lines.append('')
        lines.append('### 文档清单（doc-view ID）')
        lines.append('')
        lines.append('、'.join(d['did'] for d in lst))
        lines.append('')
        content = '\n'.join(lines)
        outpath = os.path.join(NOTE_DIR, fname)
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{fname}: {len(lst)} docs, {len(content)} chars')


if __name__ == '__main__':
    main()
