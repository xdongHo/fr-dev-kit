<!--
KB_INDEX: {
  "title": "fmt_panel_safe.py — 参数面板坐标级安全格式化",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["Label", "fmt_panel_safe", "参数面板控件", "label", "mode", "布局"],
  "summary": "--- name: fmt-panel-safe description: 参数面板控件布局格式化时使用：控件尺寸标准化、对齐排布、水印式无 Label 面板或 Label+控件配对面板、怕正则脚本损坏模板要坐标级安全修改时触发。关键词：参"
}
-->

---
name: fmt-panel-safe
description: 参数面板控件布局格式化时使用：控件尺寸标准化、对齐排布、水印式无 Label 面板或 Label+控件配对面板、怕正则脚本损坏模板要坐标级安全修改时触发。关键词：参数面板布局、fmt_panel_safe、watermark、label 模式、BoundsAttr、控件对齐、dry-run。
---

# fmt_panel_safe.py — 参数面板坐标级安全格式化

一句话：只改控件 `<BoundsAttr x/y/width/height>` 数值与面板 `<DesignAttr>/<Design_Width>`，不增删节点、不碰 CDATA/Listener/JS；改前后 XML 校验+自动备份+幂等自检。**索引目录标注「坐标级安全,推荐」**。

## 两种方案（LAYOUT_SPEC Ver0.5，逐字用法）

```
python fmt_panel_safe.py <cpt路径> [--mode watermark|label] [--dry-run]
```

- `--mode watermark`（默认）无 Label 水印式：输入控件均布 180px 网格，按钮右对齐 40px 间距
- `--mode label` Label+控件配对：Label 左对齐 + Label→5px + 跨行 Label 列对齐（Label 宽度按文本估算）

⚠ 已知坑：全量脚本（run_all/batch_optimize_cpt）1200px 阈值会拆散多列网格（示例实际表踩坑）、无 Label 纯 ComboCheckBox 面板不适用——编排器已禁用全量版，单模板精排优先本脚本。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/fmt_panel_safe.py <cpt>                # 水印式
python .../2.参数面板控件布局/fmt_panel_safe.py <cpt> --mode label --dry-run                    # 先演练
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/fmt_panel_safe.py`（LAYOUT_SPEC 常量/识别控件类清单见源码）
- 知识背景: `ckzl/lc/04_参数面板.md` §17 布局
- 一键编排入口: `kfgj/tygs/skills/run_defaults/SKILL.md`
