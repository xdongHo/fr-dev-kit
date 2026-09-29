<!--
KB_INDEX: {
    "title": "一键格式化脚本",
    "stage": "formatting",
    "tags": [
      "格式化",
      "一键",
      "批处理"
    ],
    "keywords": [
      "run_all",
      "batch_optimize",
      "widen_all",
      "fmt_panel_safe"
    ],
    "summary": "一键格式化脚本入口：run_all 全套 / batch_optimize 全目录 / widen_all 精排 / fmt_panel_safe 坐标级安全格式化"
  }
-->

# 一键格式化脚本

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 坐标级安全格式化（推荐）

```powershell
python "CPT模板/默认格式/2.参数面板控件布局/fmt_panel_safe.py" <cpt路径> [--mode watermark|label]
```

只改控件 BoundsAttr 与面板尺寸数值，不增删节点、不碰 CDATA/JS/结构；改前改后 XML 校验 + 自动备份 + 幂等自检。`watermark`（默认，无 Label 水印式）与 `label`（Label 配对分支）两种方案见 LAYOUT_SPEC.md。

## 指定文件全套

```powershell
python "CPT模板/默认格式/2.参数面板控件布局/run_all.py" <cpt路径> [cpt路径...]
```

9 步全套：取消参数模板 → 补 Query/Export 按钮 → CSSImport/CSS 注入 → 填报页设置 → 字体样式 → 行高分类 → 布局精排。自动备份 `_backup_YYYYMMDD_HHMMSS/`。

## 全目录批量

```powershell
python "CPT模板/默认格式/2.参数面板控件布局/batch_optimize_cpt.py"
```

批量优化项目报表目录目录下所有 .cpt 的参数面板：控件尺寸/间距/列对齐/按钮排序/字体/行高。

⚠️ 注意：`fix_parameter_controls` 单行宽度阈值 1200px 会把多列网格拆散（示例实际表.cpt 实测），对已精排报表慎用。

## FR Java API 版

`ckzl/frapi/doc/参数面板格式化器/ParamPanelFormatter.java` — 通过 FR Java API 操作模板对象（引擎语义：字体测宽/插件降级）。⚠ 磁盘读取模板需 FR web 会话环境（`TemplateWorkBookIO.readTemplateWorkBook` 仍受限）；**模板创建+写入已跑通**（fr-agent /exec，2026-08-07 实测）。详见该目录 README。

## 详细清单

见 [CPT模板/默认格式/2.参数面板控件布局/README.md](CPT模板/默认格式/2.参数面板控件布局/README.md)。
