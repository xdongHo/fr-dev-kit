#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_standardize_frontmatter.py — fr11_knowledge 各主题 SKILL.md frontmatter 标准化工具

用法:
    python _standardize_frontmatter.py --check
        全量检查全部主题 SKILL.md 的 frontmatter 与 KB_INDEX(README) 状况并输出清单;
        全部主题齐备标准字段(name/description/compatibility) → 退出码 0, 否则 1。只读不改。
    python _standardize_frontmatter.py --apply --topics chart图表,i18n国际化
        对指定主题补齐标准 frontmatter。修改前先备份为 SKILL.md.bak_20260914
        (备份已存在则保留首次原始备份, 不覆盖); 幂等, 字段已齐则 NOCHANGE 不写盘。

    name          = 主题目录名(必填)
    description   = 触发场景祈使句 + 关键词 + 何时不用边界(必填; 文案内嵌 DESCRIPTIONS
                    字典, 人工撰写, 不自动生成)
    compatibility = FR11
增强规则: 已有 frontmatter 的就地增强——仅追加缺失的标准字段, 原有字段与取值一律保留;
    name 与目录名不一致时不改写, 仅在 --check 中给出 WARN(避免破坏既有引用)。
混合换行透明度: 同文件 CRLF/LF 并存时 detect_eol 打印 WARN(仅提示, 不改变行为)。
其他: 行尾保持原文件风格; 输出统一 UTF-8 无 BOM; 只改主题目录下 SKILL.md;
    不删文件; 不碰 git; 不进入 _parsed\\。
"""

import argparse
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BACKUP_SUFFIX = ".bak_20260914"
STANDARD_KEYS = ("name", "description", "compatibility")
KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:")
NAME_VALUE_RE = re.compile(r"^name:\s*(.+?)\s*$")

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# 人工撰写的标准 description 文案(触发场景祈使句 + 关键词 + 何时不用边界)。
# 仅在主题 SKILL.md 缺失 description 字段时作为补齐来源; 已有 description 的主题
# 一律保留原文案。试点两主题(chart图表/i18n国际化)已按正文核对(现文件已含 description,
# 本字典仅作兜底); 其余主题文案基于 README「主题范围」列编写, 推广前建议逐主题过目微调。
DESCRIPTIONS = {
    "chart图表": "用于 FR11 图表开发与排障：图表类型选型（内置图表/扩展图表）、单元格元素与悬浮元素插入、数据集/单元格数据源选择、样式属性（标题/图例/标签/坐标轴）、ECharts 与扩展图表取数及定时刷新、区域/钻取/缩放地图与 GIS 图层、图表联动/轮播/切换、超级链接传参。关键词：图表、chart、ECharts、扩展图表、地图钻取、图表联动、大数据模式。表格样式、参数控件、FVS 大屏页面布局不用本主题。",
    "data-source数据源": "用于 FR11 数据连接与取数：JDBC/JSON/内置等数据连接配置、SQL 数据集、数据库驱动管理、FineDB、连接池与取数报错排查。关键词：数据源、数据连接、数据集、SQL、驱动、FineDB。数据库自身运维与 ETL 清洗不用本主题。",
    "deploy-cluster部署集群": "用于 FR11 部署与集群：独立/容器化部署、Tomcat/Nginx 等服务器配置、集群搭建与节点管理、状态服务器与负载均衡、工程迁移升级与运维排障。关键词：部署、集群、Tomcat、Nginx、负载均衡、迁移、升级。单机环境的功能配置不用本主题。",
    "export导出": "用于 FR11 导出：Excel/PDF/Word/图片/CSV 等格式导出、导出样式与分页、大数据量导出、导出内容缺失或报错排查。关键词：导出、Excel、PDF、Word、图片、CSV、分页。填报入库与打印出纸场景不用本主题。",
    "fill-submit填报提交": "用于 FR11 填报与提交：填报模板设计、录入控件与数据校验、智能提交与多表增删改、Excel 导入、暂存与审核流程。关键词：填报、提交、智能提交、数据校验、Excel 导入、暂存。仅查询展示类报表不用本主题。",
    "formula公式函数": "用于 FR11 公式与函数：内置函数用法、层次坐标、运算符、单元格/条件属性公式、公式报错排查、自定义函数扩展。关键词：公式、函数、层次坐标、运算符、自定义函数。JS 事件脚本逻辑不用本主题。",
    "frm-decision决策报表": "用于 FR11 决策报表（FRM）：frm 模板设计、组件与报表块布局、自适应、决策报表参数与联动、控件适配。关键词：决策报表、frm、表单、自适应、组件、报表块。普通 cpt 分页报表设计不用本主题。",
    "fvs-dashboard大屏": "用于 FR11 FVS 可视化大屏：FVS 模板搭建、组件与数据绑定、大屏动效与轮播、发布与自适应。关键词：FVS、大屏、可视化、组件、轮播。frm 决策报表与 cpt 普通报表不用本主题。",
    "i18n国际化": "用于 FR11 国际化与多语言：报表中英文等多语言切换、i18n() 公式与 FR.i18nText() 前端国际化、fr_locale 参数、管理系统语言配置键值维护、多语言方案/国际化切换接口/本地化公式等插件选型、语言切换失败排障。关键词：i18n、国际化、多语言、语言切换、语言包、fr_locale、本地化。单一中文场景、字体乱码或编码转换不用本主题。",
    "js-api二次开发": "用于 FR11 JS 与二次开发：前端 JS API（报表/控件/弹窗/提交）、事件脚本、插件开发、自定义扩展与接口调用。关键词：JS、API、插件、自定义、事件、前端。纯公式计算不用本主题。",
    "mobile移动端": "用于 FR11 移动端：App/HTML5 适配、移动端控件与交互、微信/钉钉集成、消息推送、OEM 与移动端专属配置排障。关键词：移动端、App、微信、钉钉、HTML5、推送、OEM。PC 端专属功能不用本主题。",
    "param-control参数控件": "用于 FR11 参数与控件：参数面板设计、下拉框/日期/复选等控件用法、参数联动与默认值、查询场景与控件事件显隐。关键词：参数、控件、参数面板、下拉框、联动、查询。填报录入控件不用本主题。",
    "performance性能优化": "用于 FR11 性能优化：报表打开/导出慢排查、内存/缓存/并发问题、大数据量方案、JVM 调优与模板设计优化。关键词：性能、优化、内存、缓存、并发、大数据量。功能配置类问题不用本主题。",
    "permission权限": "用于 FR11 权限：用户/角色管理、模板与数据权限、目录权限、认证与单点登录（SSO）、权限不生效排查。关键词：权限、角色、用户、认证、单点登录、数据权限。报表内控件显隐控制不用本主题。",
    "print打印": "用于 FR11 打印：普通/套打/零客户端打印、打印机与纸张设置、分页预览、水印、打印样式问题排查。关键词：打印、套打、零客户端、分页预览、纸张、水印。导出文件场景不用本主题。",
    "skin-theme主题样式": "用于 FR11 主题与样式：平台主题/皮肤/配色、登录页与导航样式自定义、报表外观与 CSS 样式调整。关键词：主题、皮肤、配色、样式、外观。图表内部样式配置不用本主题。",
}


def discover_topics():
    topics = []
    for d in sorted(os.listdir(BASE)):
        p = os.path.join(BASE, d)
        if os.path.isdir(p) and not d.startswith("_") and os.path.isfile(os.path.join(p, "SKILL.md")):
            topics.append(d)
    return topics


def read_file(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return f.read()


def detect_eol(text, name=""):
    # BG-EV-11 透明度: 同文件 CRLF/LF 并存(混合换行)时打印 WARN, 不改变返回值与后续行为
    if "\r\n" in text and "\n" in text.replace("\r\n", ""):
        where = ("[%s] " % name) if name else ""
        print("WARN: %s混合换行，按主导 EOL 规范化" % where)
    return "\r\n" if "\r\n" in text[:4096] else "\n"


def parse_frontmatter(text, name=""):
    """返回 (status, fm_lines, rest_lines, eol)，status ∈ {'ok','none','unclosed'}。"""
    eol = detect_eol(text, name)
    lines = text.split(eol)
    if not lines or lines[0].strip() != "---":
        return "none", None, lines, eol
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "ok", lines[1:i], lines[i + 1:], eol
    return "unclosed", None, lines, eol


def fm_key_set(fm_lines):
    keys = set()
    for ln in fm_lines:
        m = KEY_RE.match(ln)
        if m:
            keys.add(m.group(1).lower())
    return keys


def fm_name_value(fm_lines):
    for ln in fm_lines:
        m = NAME_VALUE_RE.match(ln)
        if m:
            return m.group(1)
    return None


def missing_standard_fields(topic, keys):
    """返回需追加的标准字段行; 文案字典未收录时返回 None(不自动生成)。"""
    add = []
    if "name" not in keys:
        add.append("name: %s" % topic)
    if "description" not in keys:
        desc = DESCRIPTIONS.get(topic)
        if not desc:
            return None
        add.append("description: %s" % desc)
    if "compatibility" not in keys:
        add.append("compatibility: FR11")
    return add


def kb_reference_texts():
    """KB_INDEX 状况数据源: kit 约定写在 README.md 头部 KB_INDEX 注释, 兼容 KB_INDEX* 文件。"""
    texts = []
    for f in sorted(os.listdir(BASE)):
        fp = os.path.join(BASE, f)
        if os.path.isfile(fp) and (f == "README.md" or f.lower().startswith("kb_index")):
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    texts.append((f, fh.read()))
            except OSError:
                pass
    return texts


def check_all():
    topics = discover_topics()
    kb_texts = kb_reference_texts()
    print("BASE: %s" % BASE)
    print("topics: %d | KB_INDEX sources: %s" % (
        len(topics), ", ".join(f for f, _ in kb_texts) or "(none)"))
    print("-" * 110)
    print("%-26s %-4s %-16s %-12s %-4s %s" % (
        "topic", "fm", "missing", "name==dir", "kb", "status"))
    print("-" * 110)
    all_ok = True
    warn = 0
    for t in topics:
        path = os.path.join(BASE, t, "SKILL.md")
        try:
            text = read_file(path)
        except OSError as e:
            print("%-26s %-4s %-16s %-12s %-4s READ_ERROR(%s)" % (t, "?", "-", "-", "?", e))
            all_ok = False
            continue
        status, fm_lines, _rest, _eol = parse_frontmatter(text, os.path.relpath(path, BASE))
        keys = fm_key_set(fm_lines) if status == "ok" else set()
        missing = [k for k in STANDARD_KEYS if k not in keys]
        kb_hit = any(t in txt for _f, txt in kb_texts)
        if status != "ok":
            st = "NO_FM" if status == "none" else "UNCLOSED"
            fm_col = "N" if status == "none" else "BAD"
            name_eq = "-"
        else:
            fm_col = "Y"
            if missing:
                st = "ADD[%s]" % ",".join(missing)
            else:
                st = "OK"
            nm = fm_name_value(fm_lines)
            name_eq = "Y" if nm == t else "N(%s)" % nm
            if nm != t:
                warn += 1
        if missing or status != "ok":
            all_ok = False
        print("%-26s %-4s %-16s %-12s %-4s %s" % (
            t, fm_col, ",".join(missing) or "-", name_eq,
            "Y" if kb_hit else "N", st))
    print("-" * 110)
    print("summary: %d topics | all-standard=%s | name!=dir WARN: %d (仅告警不改写)" % (
        len(topics), "Y" if all_ok else "N", warn))
    code = 0 if all_ok else 1
    print("EXIT_CODE=%d" % code)
    return code


def apply_topics(topics):
    results = []
    for t in topics:
        path = os.path.join(BASE, t, "SKILL.md")
        if not os.path.isfile(path):
            results.append((t, "ERROR", "SKILL.md 不存在"))
            continue
        try:
            text = read_file(path)
        except OSError as e:
            results.append((t, "ERROR", "读取失败 %s" % e))
            continue
        status, fm_lines, rest, eol = parse_frontmatter(text, os.path.relpath(path, BASE))
        if status == "unclosed":
            results.append((t, "SKIP", "frontmatter 未闭合, 需人工处理"))
            continue
        if status == "ok":
            add = missing_standard_fields(t, fm_key_set(fm_lines))
            if add is None:
                results.append((t, "SKIP", "缺 description 且文案字典未收录, 不自动生成"))
                continue
            if not add:
                results.append((t, "NOCHANGE", "标准字段已齐备, 无需修改"))
                continue
            new_lines = ["---"] + fm_lines + add + ["---"] + rest
            change = "追加字段: %s" % ", ".join(a.split(":", 1)[0] for a in add)
        else:
            desc = DESCRIPTIONS.get(t)
            if not desc:
                results.append((t, "SKIP", "无 frontmatter 且文案字典未收录, 不自动生成"))
                continue
            block = ["---", "name: %s" % t, "description: %s" % desc,
                     "compatibility: FR11", "---"]
            new_lines = block + rest if (rest and rest[0].strip() == "") else block + [""] + rest
            change = "顶部插入 frontmatter 块(%d 行): name/description/compatibility" % len(block)
        new_text = eol.join(new_lines)
        backup = path + BACKUP_SUFFIX
        if os.path.exists(backup):
            bmsg = "备份保留首次原始版(已存在): SKILL.md%s" % BACKUP_SUFFIX
        else:
            with open(path, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
            bmsg = "已备份原始版: SKILL.md%s" % BACKUP_SUFFIX
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_text)
        results.append((t, "UPDATED", "%s | %s" % (change, bmsg)))

    print("=" * 110)
    for t, st, msg in results:
        print("[%s] %s | %s" % (st, t, msg))
    print("=" * 110)
    bad = [r for r in results if r[1] in ("ERROR", "SKIP")]
    print("applied: %d updated, %d nochange, %d skip/error" % (
        sum(1 for r in results if r[1] == "UPDATED"),
        sum(1 for r in results if r[1] == "NOCHANGE"),
        len(bad)))
    code = 1 if bad else 0
    print("EXIT_CODE=%d" % code)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description="fr11_knowledge SKILL.md frontmatter 标准化工具")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="全量检查(只读), 退出码 0=全部达标/1=有缺失")
    g.add_argument("--apply", action="store_true", help="对 --topics 指定主题补齐标准 frontmatter")
    ap.add_argument("--topics", default="", help="逗号分隔的主题目录名, 仅 --apply 时使用")
    args = ap.parse_args(argv)

    if args.check:
        return check_all()

    topics = [x.strip() for x in args.topics.split(",") if x.strip()]
    if not topics:
        print("ERROR: --apply 需要非空 --topics, 例: --topics chart图表,i18n国际化")
        return 2
    known = set(discover_topics())
    unknown = [t for t in topics if t not in known]
    if unknown:
        print("ERROR: 未识别的主题目录: %s (可用: %s)" % (
            ", ".join(unknown), ", ".join(sorted(known))))
        return 2
    return apply_topics(topics)


if __name__ == "__main__":
    sys.exit(main())
