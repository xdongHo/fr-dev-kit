# -*- coding: utf-8 -*-
"""Generate 5 supplementary notes (all facts grounded in parsed FR11 docs)."""
import json, os, re
from collections import Counter
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, '_parsed')
NOTE_DIR = BASE

with open(os.path.join(OUT_DIR, 'all_docs.json'), encoding='utf-8') as f:
    docs = json.load(f)
by_id = {int(d['did']): d for d in docs}

today = date.today().isoformat()


def first_sentences(text, n=3, maxlen=240, title=''):
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
        lines.append(ls)
        if len(lines) >= n * 3:
            break
    out = ' '.join(lines[:n])
    if not out:
        out = title
    if len(out) > maxlen:
        out = out[:maxlen]
    return out.strip()


def version_points(text):
    pts = []
    for m in re.finditer(r'11\.0\.\d+', text):
        line_start = text.rfind('\n', 0, m.start()) + 1
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


def doc_entries(dids, maxlen=240):
    out = []
    for did in sorted(dids, key=int):
        d = by_id[did]
        t = d['text']
        concept = first_sentences(t, title=d['title'], maxlen=maxlen) if len(t) > 80 else (t[:150] if t else '无法解析')
        vp = version_points(t)
        out.append(f"### doc-view-{did}｜{d['title']}")
        out.append(f"- **doc-view ID**：{did}")
        out.append(f"- **核心概念**：{concept}")
        if vp:
            out.append(f"- **FR11版本要点**：{vp}")
        out.append('')
    return out


def write(fname, lines):
    path = os.path.join(NOTE_DIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'{fname}: {len(lines)} lines, {sum(len(l) for l in lines)} chars')


# ============ 1. fr11_java_api_i18n.md ============
i18n_dids = sorted(int(d['did']) for d in docs if 'i18n' in d['flags'])
L = []
L += [
    '# FR11 Java API 国际化（i18n）接口整理',
    '',
    f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档，gb2312）',
    f'> 生成时间：{today}',
    f'> 文档范围：全量 2289 篇中命中 i18n 关键词（i18n/国际化/多语言/语言包/locale）的 {len(i18n_dids)} 篇',
    '> ⚠️ 纪律声明：本文所有接口/函数/配置均直接转录自上述离线文档原文，并标注来源 doc-view ID；',
    '> ⚠️ FR11 离线 HTML 文档未出现的 Java 类级 API 一律不做断言（见 §6）。',
    '',
    '---',
    '',
    '## 1. i18n 体系总览（FR11 离线文档实际覆盖的层次）',
    '',
    '| 层次 | 机制 | 来源文档 |',
    '|------|------|----------|',
    '| 模板层 | `i18n("键")` 单元格公式 | doc-view-4591（多语言方案） |',
    '| 模板层 | 多语言方案插件「键-值」映射（模板级/服务器级） | doc-view-4591 |',
    '| 前端层 | `FR.i18nText("键")` JS 函数 | doc-view-4591 §2.2.10 |',
    '| 工具栏层 | 「模板语言」控件（模板Web属性>分页预览/填报/数据分析设置） | doc-view-4591 §2.2.7 |',
    '| URL 层 | `&fr_locale=zh_CN` 等 URL 参数 | doc-view-4591 §2.2.8 |',
    '| 参数层 | `fr_locale` 模板/全局参数 + 下拉框数据字典 | doc-view-4591 §2.2.9 |',
    '| 平台层 | 管理系统>语言配置（服务器级键-值，批量导入导出） | doc-view-4591 §2.3.1 |',
    '| 平台层 | 管理系统>语言配置>更多配置（系统语言偏好，管理员） | doc-view-4591 §2.3.2 |',
    '| 用户层 | 「国际化切换接口」插件（决策系统首页简中按钮，逐用户切换） | doc-view-3209 |',
    '| 公式层 | 本地化公式集合插件：ZHMONEY / ZHLUNAR / DATEFORMAT（带 locale 参数） | doc-view-4710 |',
    '| 校验层 | 文本控件校验国际化插件（海外手机/邮编/身份证/社会安全码校验） | doc-view-4778 |',
    '| 移动端 | App 设置>通用>语言（手动切换 / 跟随系统语言） | doc-view-1362 |',
    '| 设计器层 | 设计器切换语言（繁体中文/英文/日文/韩文版产品） | doc-view-4748 §2.2 |',
    '| 报表层 | 单张报表内中英文切换（公式判断 + 条件判断数据源） | doc-view-3164 |',
    '',
    '## 2. 支持的语言与 Locale 代码（doc-view-4591 §2.2.8 原文）',
    '',
    '| 语言 | Locale 值 |',
    '|------|-----------|',
    '| 简体中文 | zh_CN |',
    '| 繁体中文 | zh_TW |',
    '| 英文 | en_US |',
    '| 日文 | ja_JP |',
    '| 韩文 | ko_KR |',
    '',
    '注：多语言方案插件支持上述 5 种语言（doc-view-4591 §1.3）；模板语言设置中「默认语言」可选跟随平台/浏览器语言或指定语言，浏览器语言不在支持范围内时回退备用语言（§2.2.3）。',
    '',
    '## 3. 已核实的接口 / 函数 / 配置（含调用示例，全部来自文档原文）',
    '',
    '### 3.1 单元格公式 `i18n("键")`（doc-view-4591 §3.4）',
    '- 用法：标题单元格插入公式 `i18n("键")`，键在【模板>模板国际化】中预先设置键-值映射',
    '- 局限（§2.2.10）：对前端展现文本（提示、弹窗等）不生效',
    '',
    '### 3.2 前端函数 `FR.i18nText("键")`（doc-view-4591 §2.2.10）',
    '- 用于前端工具栏、事件中的文字国际化 key 调用',
    '- 原文示例（JS 事件）：`var a = FR.i18nText(\'排名第一\'); FR.showDialog("Details",600,400,a);`',
    '',
    '### 3.3 URL 参数 `fr_locale`（doc-view-4591 §2.2.8）',
    '- 预览模板后 URL 加 `&fr_locale=` + 语言值（zh_CN/zh_TW/en_US/ja_JP/ko_KR）即可切换语言',
    '',
    '### 3.4 参数控件方式（doc-view-4591 §2.2.9）',
    '- 新增名为 fr_locale 的模板参数/全局参数，参数面板生成 fr_locale，控件设为下拉框',
    '- 数据字典类型「自定义」，实际值对应 zh_CN、zh_TW、en_US、ja_JP、ko_KR',
    '- 局限：仅对查询后的内容生效（工具栏、其他控件文字等查询前载入内容不生效）；参数控件显示值固定，无法多语言切换',
    '',
    '### 3.5 模板语言控件（doc-view-4591 §2.2.7 / §3.5）',
    '- 模板Web属性>分页预览设置（或填报页面/数据分析设置）>为该模板单独设置>工具栏控件中双击「模板语言」控件',
    '- 支持自定义控件图标、控件名、是否显示图标和名字',
    '',
    '### 3.6 服务器级键-值配置（doc-view-4591 §2.3.1）',
    '- 管理员：管理系统>语言配置，键-值支持新增/删除/修改/查看/批量导入/批量导出（导入 Excel 字段名须满足格式）',
    '- 管理系统自定义显示部分（报表目录、登入标题、平台标题）均可通过呼叫「键」实现国际化切换（§2.3.3）',
    '- 登录页语言切换：平台语言偏好需设置为【简体中文】（§2.3.2）',
    '',
    '### 3.7 国际化切换接口插件（doc-view-3209，插件版本 V1.9.3，服务器 11.0）',
    '- 安装后决策系统首页点击「简中」按钮选择语言（如 English），逐用户切换语言环境',
    '- 注1：FineBI 工程安装后需重启 BI 工程生效；注2：切换语言只改变管理系统字体，目录和模板字体不变',
    '- 切换失败排障：① 清理浏览器缓存（仅关闭重启浏览器无效）；② 管理系统>安全管理>安全防护>Security Headers>开启「浏览器缓存禁用」',
    '',
    '### 3.8 本地化公式集合插件（doc-view-4710，V1.0；10.0 2019-07-31 / 11.0 2022-03-28）',
    '- 针对海外场景扩展 CNMONEY / LUNAR / FORMAT，新增 3 个带 locale 参数的函数：',
    '  - `ZHMONEY(number, unit, locale)`：金额大写，locale 为 zh_TW 时返回繁体。例：`ZHMONEY(3.4567,"wy","zh_TW")` → 叁兆肆仟伍佰陸拾柒億圓整',
    '  - `ZHLUNAR(year, month, day, locale)`：阴历日期。例：`ZHLUNAR(2020, 6, 4)` → 庚子年閏四月十三',
    '  - `DATEFORMAT(date, pattern, locale, chronology)`：按模式/区域/历法格式化日期；chronology "j"=日本年号、"m"=台湾民国历、"t"=泰国佛历。例：`DATEFORMAT(TODAY(),"GGGGyy-MM-dd, EEEE","ja_JP","j")` → 令和03-11-08, 月曜日',
    '- 注意（doc 原文）：令和年号正常显示需 JDK 为 Oracle JDK 7u221 / 8u211 / 11.0.3 或 OpenJDK 7u221 / 8u212-b03 / 11.0.3+7 之后版本',
    '',
    '### 3.9 文本控件校验国际化插件（doc-view-4778，V1.0，10.0 & 11.0）',
    '- 文本控件内置校验规则支持海外区域：中国大陆、中国台湾（手机/身份证/邮编）、美国（手机/邮编/社会安全码）、日本（手机/邮编）、韩国（手机/身份证/邮编）',
    '- 控件设置>填写规则选「特殊」，区域+数据类型组合，免写正则表达式',
    '',
    '### 3.10 App 系统语言（doc-view-1362，App V11.0）',
    '- 设置>通用>语言：手动切换或「跟随系统语言」，保存后提示重启；重启后界面语言切换',
    '- 局限：目录名称、模板名称、模板内容不能自动国际化，需设计对应语言模板',
    '',
    '### 3.11 单张报表内中英文切换（doc-view-3164）',
    '- 公式判断改变标签/文本字符串 + 条件判断字段内容数据源，适用于单模板；多模板场景建议用多语言方案插件（doc-view-4748 §2.4 原话：操作成本过高）',
    '',
    '## 4. i18n 相关文档清单（命中关键词的 41 篇）',
    '',
]
for did in sorted(i18n_dids, key=int):
    d = by_id[did]
    L.append(f'- doc-view-{did}｜{d["title"]}')
L += [
    '',
    '## 5. 相关但非核心的命中说明',
    '',
    '- doc-view-1062（错误代码汇总及解决方案）、doc-view-2471（fine_conf_entity可视化配置）、doc-view-3151（FineDB 表结构）等正文提到 locale/语言相关字段，属数据存储层引用，非 i18n 功能接口',
    '- doc-view-2028（Linux系统安装中文语言包）：部署层面解决 Linux 中文乱码，属环境准备（详见 fr11_install_survey_report.md）',
    '- doc-view-3720（日期转化为英文格式）：单元格格式层实现英文日期展示',
    '- doc-view-5031（itext7导出及国际化换行插件）：PDF 导出国际化换行策略',
    '',
    '## 6. 未在 FR11 离线文档中出现的 API（诚实标注）',
    '',
    '- 离线 HTML 文档**未出现** Java 类级 i18n API（如 LocaleFinder / AbstractLocaleFinder / InterProviderFactory / LanguageConfig 等类名与方法签名）。',
    '- 因此本文**不**对任何 Java 类级 i18n API 做断言；如需验证，须以 FR11 实际 JAR 包 javap / 反编译结果为准。',
    '- 离线文档覆盖的 i18n 面：公式层（i18n()）、前端层（FR.i18nText()）、URL/参数层（fr_locale）、平台配置层（语言配置）、插件层（多语言方案/国际化切换接口/本地化公式/文本控件校验国际化）、移动端（App 语言）。',
]
write('fr11_java_api_i18n.md', L)

# ============ 2. fr11_i18n_api_optimization.md ============
L = [
    '# FR11 i18n 优化建议（基于离线文档实际约束）',
    '',
    f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档）',
    f'> 生成时间：{today}',
    '> 纪律：每条建议均标注依据的文档 ID 与原文约束，不做文档之外的推测。',
    '',
    '---',
    '',
    '## 1. 方案选型优化（多张报表 vs 单张报表）',
    '',
    '| 场景 | 推荐方案 | 依据 |',
    '|------|----------|------|',
    '| 单张报表中英文切换 | 公式判断标签/文本 + 条件判断数据源字段 | doc-view-3164 / 4748 §2.3 |',
    '| 多张报表语言切换 | 多语言方案插件（键-值映射，模板级/服务器级） | doc-view-4748 §2.4（单报表公式法多报表场景"操作成本过高"） |',
    '| 逐用户语言偏好 | 国际化切换接口插件（决策系统首页语言按钮） | doc-view-3209 |',
    '| 平台整体默认语言 | 管理系统>语言配置>更多配置>系统语言偏好 | doc-view-4591 §2.3.2 |',
    '',
    '## 2. 已知局限 → 规避策略',
    '',
    '1. **单元格公式 I18N() 对前端展现文本不生效**（doc-view-4591 §2.2.10）：提示、弹窗等前端文本必须走 `FR.i18nText("键")` 事件方案，不能只依赖单元格公式。',
    '2. **fr_locale 参数控件方式只对查询后内容生效**（doc-view-4591 §2.2.9）：工具栏、其他控件文字等查询前载入内容不会切换；需同时配合模板语言控件或 URL 参数。',
    '3. **参数控件显示值固定，无法多语言切换**（doc-view-4591 §2.2.9）：语言下拉框的显示名只可设一种语言。',
    '4. **切换语言只改变管理系统字体**（doc-view-3209 注2）：目录和模板字体不变——目录/模板名称的国际化需在模板层自行实现（键-值 + 模板设计）。',
    '5. **App 切换语言后目录名称/模板名称/模板内容不自动国际化**（doc-view-1362）：需要用户设计对应语言的模板，并修改目录和模板名称。',
    '6. **登录页语言切换需平台语言偏好为简体中文**（doc-view-4591 §2.3.2）。',
    '7. **语言字段至少填写一个语言的显示内容才可提交**（doc-view-4591 §2.2.2/§2.2.5）——键-值维护时的表单约束。',
    '',
    '## 3. 排障优化（切换语言失败）',
    '',
    '- 清理浏览器缓存（仅关闭重启浏览器无效）——doc-view-3209 方案一',
    '- 管理系统>安全管理>安全防护>Security Headers>开启「浏览器缓存禁用」——doc-view-3209 方案二',
    '- FineBI 工程安装国际化切换接口插件后需重启 BI 工程——doc-view-3209 注1',
    '- 多语言方案插件要求 jar 包 10.0.17 及以上——doc-view-4591 §1.3 注（跨版本兼容提示，非 FR11 特有）',
    '',
    '## 4. 本地化公式使用优化',
    '',
    '- `DATEFORMAT` 的日本年号（令和）显示依赖 JDK 版本：Oracle JDK 7u221 / 8u211 / 11.0.3 或 OpenJDK 7u221 / 8u212-b03 / 11.0.3+7 之后——doc-view-4710',
    '- locale 参数写法："zh"、"zh_TW"、"en_US"、"ja_JP"；chronology 参数 "j"/"m"/"t" 对应日本年号/民国历/佛历——doc-view-4710',
    '- 报表示例直接可用的公式组合：`=ZHMONEY(3.45,"w","zh_TW")`、`=ZHLUNAR(2020,6,4,"zh_TW")`、`=DATEFORMAT(TODAY(),"YYYY-MM-dd, EEEE","en_US")`——doc-view-4710 §4.1',
    '',
    '## 5. 海外校验规则优化（免正则）',
    '',
    '- 文本控件校验国际化插件按「区域+数据类型」组合覆盖海外校验（中国大陆/台湾/美国/日本/韩国），无需手写正则——doc-view-4778',
    '- 各区域支持的数据类型不同：中国大陆、台湾、韩国=手机/身份证/邮编；美国=手机/邮编/社会安全码；日本=手机/邮编——doc-view-4778 注2',
    '',
    '## 6. 部署层国际化',
    '',
    '- Linux 部署中文乱码：安装中文语言包——doc-view-2028；工程部署环境准备文档亦提示：中文用户部署 Linux 需确认系统有中文语言包——doc-view-4409 注',
]
write('fr11_i18n_api_optimization.md', L)

# ============ 3. fr10_i18n_verification_report.md ============
L = [
    '# FR11 离线文档 i18n 验证报告',
    '',
    f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档，共 2289 篇）',
    f'> 生成时间：{today}',
    '> 验证方法：全量 2289 篇正文扫描关键词 i18n / 国际化 / 多语言 / 语言包 / locale，命中 41 篇；对命中文档逐篇精读，提取接口与约束。',
    '',
    '---',
    '',
    '## 1. 验证结论摘要',
    '',
    '| 验证项 | 结果 |',
    '|--------|------|',
    '| 扫描文档数 | 2289 篇（全部成功解析，0 无法解析） |',
    '| 命中 i18n 关键词文档 | 41 篇 |',
    '| 文档级 i18n 接口（公式/JS/URL/配置/插件） | ✅ 已逐条核实（见下） |',
    '| Java 类级 i18n API（LocaleFinder 等） | ❌ 未出现在离线 HTML 文档中，无法由此源验证 |',
    '| FR10 专有 i18n 接口对比 | 本文仅报告 FR11 离线文档实际出现内容，FR10 推断不混入 |',
    '',
    '## 2. 已核实（出现在离线文档原文，附 doc-view ID）',
    '',
    '| 接口/机制 | 出处 | 核实状态 |',
    '|--------|------|----------|',
    '| `i18n("键")` 单元格公式 | doc-view-4591 | ✅ 含用法与局限 |',
    '| `FR.i18nText("键")` 前端函数 | doc-view-4591 | ✅ 含 JS 示例 |',
    '| `fr_locale` URL 参数（zh_CN/zh_TW/en_US/ja_JP/ko_KR） | doc-view-4591 | ✅ |',
    '| `fr_locale` 模板参数+下拉框数据字典 | doc-view-4591 | ✅ 含局限说明 |',
    '| 模板语言工具栏控件 | doc-view-4591 | ✅ |',
    '| 管理系统>语言配置（键-值+批量导入导出） | doc-view-4591 | ✅ |',
    '| 系统语言偏好设置（管理员） | doc-view-4591 | ✅ |',
    '| 国际化切换接口插件（用户级） | doc-view-3209 | ✅ 含版本 V1.9.3 与排障方案 |',
    '| ZHMONEY / ZHLUNAR / DATEFORMAT（locale 参数） | doc-view-4710 | ✅ 含签名与示例 |',
    '| 文本控件校验国际化插件 | doc-view-4778 | ✅ 含区域/数据类型矩阵 |',
    '| App 系统语言（手动/跟随系统） | doc-view-1362 | ✅ |',
    '| 语言切换方法汇总 | doc-view-4748 | ✅ 概述页 |',
    '| 单张报表内中英文切换 | doc-view-3164 | ✅ |',
    '| 日期转化为英文格式 | doc-view-3720 | ✅ |',
    '| itext7 导出及国际化换行插件 | doc-view-5031 | ✅ |',
    '| Linux 中文语言包 | doc-view-2028 | ✅ 部署层 |',
    '',
    '## 3. 未在离线文档中出现的 i18n 内容（不作为已确认结论）',
    '',
    '1. Java 类级接口（LocaleFinder / AbstractLocaleFinder / InterProvider / InterProviderFactory / LanguageConfig 等）在 2289 篇离线 HTML 中**无任何命中**——离线文档不覆盖平台 Java API 层。',
    '2. 前端 JS 全局对象（如 FR.i18n 相关全局对象）除 `FR.i18nText()` 外无其他出现。',
    '3. FineDB 中 i18n 相关表（FINE_INTERNATIONAL 等）未在离线文档表结构文档中确认（doc-view-3151 FineDB 表结构正文未见该表名断言，需以实际数据库为准）。',
    '',
    '## 4. 验证局限',
    '',
    '- 离线 HTML 为产品帮助文档，非 API 参考手册；"未出现"不等于"不存在"，仅代表该来源无法佐证。',
    '- 涉及真实 JAR 包的类名/方法签名验证，须用 javap / 反编译手段另行完成。',
]
write('fr10_i18n_verification_report.md', L)

# ============ 4. fvs_dashboard_summary.md ============
fvs_dids = [int(d['did']) for d in docs if 'fvs' in d['flags']]
L = [
    '# FR11 知识库 · FVS 可视化看板（大屏）总结',
    '',
    f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档，gb2312）',
    f'> 文档数：{len(fvs_dids)} 篇（标题含 FVS，独立于 15 分类的专题篇）',
    f'> 生成时间：{today}',
    '',
    '---',
    '',
    '## 1. FVS 产品定位（doc-view-4222 原文要点）',
    '',
    '- FVS 是专为大屏可视化场景打造的产品，基于 FineReport 设计器开发，以插件形式交付（JAR 2021-11-15 / 插件 V1.0.0 起）',
    '- 应用 B/S 端技术，兼具 B/S 便捷高效与 C/S 安全稳定',
    '- 不支持移动端；需在 License 注册中购买对应功能',
    '- 核心亮点：三维城市一键生成、自定义模型导入、多分页故事大屏、分页平滑过渡、所见即所得编辑、4 种自适应模式（自动/宽度铺满/高度铺满/无）、内置图标背景装饰素材、点九图填充',
    '',
    '## 2. 组件体系（doc-view-4210 原文）',
    '',
    '| 大类 | 组件 |',
    '|------|------|',
    '| 三维组件 | 三维城市组件、自定义模型组件 |',
    '| 图表 | 普通模板各类分析图表（柱形图等）+ 扩展图表全部图表（水球图等） |',
    '| 文字 | 富文本组件、标题组件、表格组件（类似决策报表报表块） |',
    '| 媒体 | 本地视频、监控视频、图片组件 |',
    '| 容器 | 网页框组件（引入网络页面/工程下普通报表、决策报表、FVS 模板）、轮播器组件 |',
    '| 控件 | 文本框、日期时间、下拉框、下拉复选框、单选按钮组、复选按钮组（11.0.6 / V1.5.0 新增六种控件组件，参数联动其他组件） |',
    '',
    '## 3. 版本特性（来自各文档版本表）',
    '',
    '- 11.0.2 / V1.2.0：除表格组件外，其他组件字体单位统一使用 px；新增 jxbrowser 缺失检测（doc-view-4210 / 4188）',
    '- 11.0.4 / V1.3.0：jxbrowser 版本为 6.23 和 7.22（doc-view-4188）',
    '- 11.0.6 / V1.5.0：新增六种控件组件（doc-view-4210）',
    '',
    '## 4. 文档条目（65 篇）',
    '',
] + doc_entries(fvs_dids) + [
    '## 5. 总结',
    '',
    f'- 本专题共 {len(fvs_dids)} 篇 FVS 文档（在 15 分类中分别归属图表/决策报表/皮肤主题/二次开发等，此处按专题聚合）',
    '- 全部条目转录自离线 HTML 正文，未做推断补充',
]
write('fvs_dashboard_summary.md', L)

# ============ 5. fr11_install_survey_report.md ============
inst_dids = [int(d['did']) for d in docs if 'install' in d['flags']]
L = [
    '# FR11 安装调研报告（基于离线文档）',
    '',
    f'> 数据源：`D:\\fr11_docs\\doc-view-{{did}}.html`（FR11 离线文档，gb2312）',
    f'> 文档数：{len(inst_dids)} 篇（标题含 安装/部署环境/环境准备/系统要求/配置要求）',
    f'> 生成时间：{today}',
    '',
    '---',
    '',
    '## 1. 工程部署环境要求（doc-view-4409 原文）',
    '',
    '| 类别 | 要求 |',
    '|------|------|',
    '| 操作系统 | Linux：Centos 6.5-6.9 / 7.0-7.4、RedHat 6.5-6.9 / 7.0-7.4、Ubuntu 10.04.4、Amazon Linux 2018.03；Windows Server 2008 / 2012 |',
    '| 网络 | 公网 10M+ 同网段；内网无带宽要求 |',
    '| 内存 | 服务器 16G+；JVM 建议 8G+（不超过 32G，过大会导致 FullGC 时间过长） |',
    '| 磁盘 | 根目录空余 40G+；/usr 15G+（日志默认路径） |',
    '| 数据目录 | .FineReport110 文件夹所在盘需留空余（Windows 在 C:\\Users\\<用户名>，Linux root 在 /root 下） |',
    '| 容器 | 建议用服务器部署包（内置 Oracle OpenJDK，无需装 Tomcat/JDK）；不支持 OpenLogic OpenJDK |',
    '| 中文 | Linux 部署需确认系统有中文语言包（doc-view-2028） |',
    '',
    '## 2. 集群环境要求（doc-view-2642 原文）',
    '',
    '- JDK 1.8 且小版本 JDK8u102+；一套集群不支持一台服务器部署多个集群节点工程',
    '- Nginx 作负载均衡：并发需求 <300 可部署在 Windows Server，>300 不建议（Windows Server 上 Nginx 不能支撑较高并发）',
    '- 两节点集群基础方案：Nginx + Tomcat + Redis + FTP；有条件建议三者分服务器部署',
    '- Redis/Nginx 依赖 GCC 编译环境（gcc -v 检查，yum install gcc gcc-c++）；Linux 安装 FTP 需 root',
    '- 通信检测：Linux 用集群环境检测工具或 ping；Windows 用 ping / telnet',
    '',
    '## 3. FVS 插件安装要求（doc-view-4188 原文）',
    '',
    '- FVS 大屏编辑模式插件：JAR 2021-11-15 起、插件 V1.0.0；11.0.4/V1.3.0 起 jxbrowser 6.23 / 7.22',
    '- 需 FineReport License 注册购买对应功能（doc-view-4222 注2）',
    '',
    '## 4. 文档条目（21 篇）',
    '',
] + doc_entries(inst_dids) + [
    '## 5. 常见安装问题入口',
    '',
    '- doc-view-4532 部署环境异常、doc-view-4914 设计器安装常见问题、doc-view-4812 第三方插件安装失败说明、doc-view-4840 数据门户插件安装说明',
]
write('fr11_install_survey_report.md', L)

print('done')
