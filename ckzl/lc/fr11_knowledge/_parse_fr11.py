# -*- coding: utf-8 -*-
"""Parse all FR11 offline docs: extract title + content_1 text, clean, classify into 15 categories."""
import re, glob, json, html as htmlmod, os, time

SRC = 'D:/fr11_docs/doc-view-*.html'
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_parsed')
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORIES = {
    'chart':        ['图表', '柱状图', '饼图', '折线图', '条形图', '面积图', '雷达图', '散点图', '仪表盘', '图例', '坐标轴',
                     '图表样式', '图表特效', '钻取', '图表联动', '漏斗图', '瀑布图', '甘特图', '词云', '热力图', '地图',
                     '扩展图表', '图表类型', '图表插件', '图表数据', '图形'],
    'data_source':  ['数据连接', '数据集', '数据源', '数据库', 'JDBC', '服务器数据集', '内置数据集', '文件数据集',
                     '存储过程', '连接池', '数据源连接', '驱动程序', '驱动管理'],
    'deploy_cluster': ['部署', '集群', '服务器', 'Tomcat', 'WebLogic', 'WebSphere', 'JBoss', 'Resin', '安装',
                     '迁移', '升级', '注册', '容器', 'docker', '负载均衡', '多机', '单机', '工程', 'war', '启动', '宕机',
                     '运维', '备份', '环境'],
    'export':       ['导出', '导出的', '导出excel', '导出pdf', '导出word', '图片导出', '导出权限', '批量导出',
                     '导出插件', 'excel导出', 'pdf导出'],
    'fill_submit':  ['填报', '提交', '智能提交', '数据校验', '校验规则', '暂存', '入库', '批量提交', '填报属性',
                     '数据录入', '编辑', '填写', '表单提交', '重复校验'],
    'formula':      ['公式', '函数', '运算符', '层次坐标', '单元格引用', '参数公式', '公式编辑', '自定义函数',
                     '计算', '表达式', '内置函数'],
    'frm_decision': ['决策报表', '表单', '自适应', '组件', '空白块', '报表块', '绝对布局', '自适应布局',
                     '模板块', '决策平台', 'frm'],
    'mobile':       ['移动端', 'App', 'APP', '手机', '平板', '微信', '钉钉', '企业微信', 'HTML5', '触屏', '手势',
                     'ios', 'android', '手机端'],
    'permission':   ['权限', '角色', '认证', '单点登录', 'SSO', '数据权限', '权限管理', '组织机构', '部门',
                     '用户管理', '访问控制', '授权'],
    'param_control': ['参数', '控件', '下拉框', '下拉树', '日期控件', '复选框', '单选', '复选', '参数面板',
                     '查询按钮', '控件事件', '文本控件', '数字控件', '按钮', '默认值'],
    'print':        ['打印', '分页预览', '打印机', '纸张', '打印设置', '打印预览', '打印导出'],
    'dev':          ['JS', 'JavaScript', 'API', '接口', '二次开发', '插件', '自定义', '事件', '前端', '后端',
                     '调用', '集成', '开发', '代码', 'java'],
    'skin_theme':   ['主题', '皮肤', '配色', '外观', '样式', '换肤', '背景', '风格', '标题'],
    'performance':  ['性能', '优化', '内存', '缓存', '并发', '加速', '卡顿', '慢', '大数据量', '性能优化',
                     '服务器性能', 'jvm'],
}

PRIORITY = ['chart', 'formula', 'fill_submit', 'frm_decision', 'param_control', 'mobile',
            'permission', 'data_source', 'export', 'print', 'deploy_cluster', 'skin_theme',
            'performance', 'dev', 'other']

BOILER = [
    (r'划词内容：.*', ''),
    (r'附件列表\s*下载次数.*?主题：.*', ''),
    (r'附件列表.*', ''),
    (r'下载次数：.*', ''),
    (r'文档创建者：.*?文档助手\d?\s*', ''),
    (r'最近更新：.*?\d{4}-\d{2}-\d{2}\s*', ''),
    (r'历史版本：\s*\d+\s*', ''),
    (r'已经是第一篇.*', ''),
    (r'已经是最后一篇.*', ''),
    (r'售前咨询电话.*?400-811-8890.*?转\d', ''),
    (r'在线技术支持.*?在线支持', ''),
    (r'总裁办24H投诉.*?173-1278-1526', ''),
    (r'智能客服.*', ''),
    (r'对此内容反馈.*', ''),
    (r'当前为11\.0版本文档.*?最新版帮助文档\s*', ''),
    (r'使用此篇文档遇到问题.*?基础服务范围》\s*', '', ),
]


def decode(raw):
    for enc in ['utf-8', 'gb2312', 'gbk', 'gb18030']:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('gb18030', errors='replace')


def extract_content(text):
    """Depth-track the content_1 div, return cleaned plain text (markdown-ish)."""
    idx = text.find('content_1 wordcut')
    if idx == -1:
        idx = text.find('class="content_1"')
    if idx == -1:
        return None
    start = text.find('>', idx) + 1
    depth = 1
    pos = start
    end = len(text)
    maxpos = min(len(text), start + 400000)
    while pos < maxpos:
        n_open = text.find('<div', pos)
        n_close = text.find('</div>', pos)
        if n_close == -1:
            break
        if n_open != -1 and n_open < n_close:
            depth += 1
            pos = n_open + 4
        else:
            depth -= 1
            if depth <= 0:
                end = n_close
                break
            pos = n_close + 6
    body = text[start:end]
    # cut at boilerplate anchors if inside
    for marker in ['对此内容反馈', '附件列表', 'class="doc-aside"', 'class="foot"', 'id="feedback"',
                   '<!-- main end', 'class="bottom"']:
        i = body.find(marker)
        if i != -1 and i > 100:
            body = body[:i]
    # structure to text
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</p>', '\n', body)
    body = re.sub(r'</(tr|li|h[1-6]|div|table|pre)>', '\n', body)
    body = re.sub(r'<h([1-6])[^>]*>', lambda m: '\n' + '#' * int(m.group(1)) + ' ', body)
    body = re.sub(r'<pre[^>]*>\s*<code[^>]*>', '\n```\n', body)
    body = re.sub(r'</code>\s*</pre>', '\n```\n', body)
    body = re.sub(r'<code>', '`', body)
    body = re.sub(r'</code>', '`', body)
    body = re.sub(r'<li[^>]*>', '\n- ', body)
    body = re.sub(r'<(?:strong|b)>', '**', body)
    body = re.sub(r'</(?:strong|b)>', '**', body)
    body = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'[图片:\1]', body)
    body = re.sub(r'<img[^>]*>', '[图片]', body)
    body = re.sub(r'<[^>]+>', '', body)
    body = htmlmod.unescape(body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r'\n\s*\n\s*\n+', '\n\n', body)
    # boilerplate cleanup
    for pat, rep in BOILER:
        body = re.sub(pat, rep, body, flags=re.S)
    body = re.sub(r'\n\s*\n\s*\n+', '\n\n', body)
    return body.strip()


def classify(title, text):
    scores = {c: 0 for c in CATEGORIES}
    tl = title.lower()
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            kl = kw.lower()
            if kl in tl:
                scores[cat] += 5
            if kw in text:
                scores[cat] += 1
    best = max(scores, key=lambda k: (scores[k], -PRIORITY.index(k)))
    if scores[best] == 0:
        return 'other'
    return best


def main():
    files = sorted(glob.glob(SRC))
    docs = []
    unparseable = []
    t0 = time.time()
    for i, path in enumerate(files):
        did = path.split('doc-view-')[-1].replace('.html', '')
        with open(path, 'rb') as f:
            raw = f.read()
        text = decode(raw)
        tm = re.search(r'<title>(.*?)</title>', text, re.S)
        title = ''
        if tm:
            title = tm.group(1).strip()
            title = re.sub(r'\s*-\s*FineReport帮助文档.*$', '', title).strip()
        body = extract_content(text)
        if body is None or len(body) < 80:
            unparseable.append({'did': did, 'title': title, 'len': len(body) if body else 0})
            body = body or ''
        cat = classify(title, body)
        t = title + body
        flags = []
        if re.search(r'FVS', title):
            flags.append('fvs')
        if re.search(r'i18n|国际化|多语言|语言包|locale', t, re.I):
            flags.append('i18n')
        if re.search(r'安装|部署环境|环境准备|系统要求|配置要求', title):
            flags.append('install')
        docs.append({'did': did, 'title': title, 'category': cat, 'text': body, 'flags': flags})
        if (i + 1) % 400 == 0:
            print(f'  parsed {i+1}/{len(files)}', flush=True)
    # save
    with open(os.path.join(OUT_DIR, 'all_docs.json'), 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, 'unparseable.json'), 'w', encoding='utf-8') as f:
        json.dump(unparseable, f, ensure_ascii=False)
    # stats
    from collections import Counter
    cc = Counter(d['category'] for d in docs)
    print('--- category distribution ---')
    for c, n in cc.most_common():
        print(f'  {c}: {n}')
    print(f'--- unparseable: {len(unparseable)} ---')
    for u in unparseable[:30]:
        print(' ', u)
    print(f'time: {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
