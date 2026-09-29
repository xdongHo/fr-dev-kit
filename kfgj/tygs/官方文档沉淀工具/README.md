<!--
KB_INDEX: {
  "title": "官方文档沉淀工具(已降级为知识映射表)",
  "stage": "formatting",
  "tags": ["已归档", "官方文档", "知识映射", "doc编号"],
  "keywords": ["级联", "排序", "图表", "导出", "权限", "定时调度", "doc-编号"],
  "summary": "原 27 个官方文档沉淀脚本已删除(知识已双重沉淀进 fr_rules_doc/fr_rules_export 静态校验规则 + ckzl/lc/ckzl/gzjd)。本文件保留 doc-编号→功能 映射表作索引。"
}
-->

# 官方文档沉淀工具(已降级为知识映射表)

> ⚠️ **2026-08-14 归档**:原 27 个 `.py` 生成/注入脚本已删除。
> 原因:核心方针已切换为「构建 .cpt/.frm 一律用 FR Java API,Python 不再用于模板构建(易报错)」,
> 这些 Python + XML 手写节点的脚本已被 Java API 路线取代。
>
> **知识未丢失,已双重沉淀**:
> 1. **静态校验规则** → `kfgj/fzpy/fr_rules_doc.py`(188K)+ `fr_rules_export.py`(156K),由 `fr_check.py` Layer 1.5 自动加载
> 2. **知识点正文** → 各 doc 对应的功能知识已并入 `ckzl/lc/*`、`ckzl/gzjd/*`、`AGENTS.md` §3 路由表
>
> 本文件仅保留 **doc-编号 → 功能** 映射表,作为「按官方文档编号反查知识点」的索引。

## doc-编号 → 功能 映射表

| doc 编号 | 功能主题 | 知识落点 |
|----------|---------|---------|
| doc-157 | 模板参数 | `ckzl/lc/04_参数面板.md` |
| doc-159 | 全局参数(工程级) | `ckzl/lc/04_参数面板.md` |
| doc-175 | 图表单元格数据源 | `ckzl/gzjd/06_图表模块.md` |
| doc-176 | 图表数据集数据源 | `ckzl/gzjd/06_图表模块.md` |
| doc-225 | 预览/打印/导出单元格 | `ckzl/lc/06_Web呈现层.md` |
| doc-608 | 填报控件数据字典联动 | `ckzl/lc/05_填报与交互.md` |
| doc-684 | 定时调度邮件通知 | ckzl/gf/zxzt.md §1(⚠跨模块依赖,平台侧) |
| doc-865 | 权限细粒度参数控制 | ckzl/gf/zxzt.md §1 权限(参数驱动) |
| doc-866 | 权限细粒度模板内容控制 | `ckzl/lc/03_报表构建.md` 权限节点 |
| doc-996 | 单数据集分页 SQL(行式引擎) | `ckzl/lc/02_数据建模.md` |
| doc-1128 | Word 导出自动调整行高 | `ckzl/lc/06_Web呈现层.md` |
| doc-1130 | Word 导出页眉页脚 | `ckzl/lc/06_Web呈现层.md` |
| doc-1284 | SQL 实现下拉框参数联动 | `ckzl/lc/04_参数面板.md` 级联 |
| doc-1457 | JS 决策报表定时刷新 | `ckzl/gzjd/08_交互联动.md` |
| doc-1672 | 图表样式注册 | `ckzl/gzjd/06_图表模块.md` |
| doc-1782 | 横向扩展列多列排序 | `ckzl/lc/03_报表构建.md` 排序 |
| doc-1868 | JS 填报联动自动生成默认值 | `ckzl/gzjd/08_交互联动.md` |
| doc-1894 | JS 决策报表点击标题排序 | `ckzl/lc/03_报表构建.md` 排序 |
| doc-1995 | 下拉框和图表联动 | `ckzl/gzjd/08_交互联动.md` |
| doc-2684 | 按分组汇总结果排序 | `ckzl/lc/03_报表构建.md` 排序 |
| doc-3120 | JS 参数联动层级限制弹提示 | `ckzl/gzjd/08_交互联动.md` |
| doc-3315 | 定时调度支持的公式 | ckzl/gf/zxzt.md §1 定时调度 |
| doc-3707 | 根据参数批量导出多个文件 | `ckzl/lc/06_Web呈现层.md` 导出 |
| doc-3710 | 根据参数选择导出不同报表 | `ckzl/lc/06_Web呈现层.md` 导出 |
| doc-4202 | 单元格动态参数超链 | `ckzl/lc/03_报表构建.md` 超链 |

## 使用约定

- **查知识点** → 直接读「知识落点」列对应的 ckzl/lc/ckzl/gzjd章节,或用jcxt/js `python jcxt/js/query_kb.py "<问题>"`
- **校验规则** → `python kfgj/fzpy/fr_check.py <cpt> --no-rules` 关闭 Layer 1.5,默认开启
- **构建模板** → 一律 FR Java API(fr-agent /exec),不用 Python 手写 XML 节点
