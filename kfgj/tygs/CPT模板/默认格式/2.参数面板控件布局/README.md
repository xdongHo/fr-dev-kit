<!--
KB_INDEX: {
    "title": "参数面板控件布局 — 脚本目录",
    "stage": "formatting",
    "tags": [
      "脚本目录",
      "一键格式化",
      "fmt_panel_safe"
    ],
    "keywords": [
      "run_all",
      "batch_optimize",
      "widen_all",
      "fmt_panel_safe",
      "适用边界"
    ],
    "summary": "参数面板一键格式化脚本目录：fmt_panel_safe(推荐)/run_all/batch_optimize/widen_all 用法、踩坑与适用边界"
  }
-->

# 参数面板控件布局 — 脚本目录

> 所有脚本均可独立运行，自动创建 `_backup_YYYYMMDD_HHMMSS/` 备份。
> 修改后必须验 XML：`python -c "import xml.etree.ElementTree as ET; ET.parse('file.cpt')"`

## 推荐入口

| 场景 | 脚本 | 用法 |
|------|------|------|
| **容器网格排布缺省方案（Ver1.0 2026-08-20 首选）** | `layout_panel.py` — 容器=Label+控件配对成单元格：控件统一180×26、Label同列最大宽自适应、组间15/行距41/边距12、>1200折行、按钮末行右对齐(>1500独立行)、超宽控件独立末行、面板宽精确重算；**查询/导出默认按钮缺失自动补，自定义按钮按需保留**；容差行聚类+label就近配对(不分左右)，修复老batch的全部已知坑 | `python layout_panel.py --cpt <cpt> [--cpt b.cpt] [--dry-run]` |
| **区块模型自动布局（Ver0.7）** | `auto_layout_watermark.py` — 区块=兼容 Label 的布局单元，三形态：watermark(无Label)/label-h(Label左 100+控件+20)/label-v(Label上 14+26)；控件宽按类(YearControl=100)；Y 按钮 max(80,中文×15+字母×8)；每行<1500、总高<300 双约束；坐标级安全修改 | `python auto_layout_watermark.py <cpt> [--mode watermark\|label-h\|label-v] [--dry-run]` |
| **坐标级安全格式化（通用）** | `fmt_panel_safe.py` — 只改 BoundsAttr/DesignAttr 数值，不增删节点、不碰 CDATA/JS，改前改后 XML 校验 + 备份 + 幂等自检（watermark 默认 / label 分支） | `python fmt_panel_safe.py <cpt> [--mode watermark\|label] [--dry-run]` |
| **指定文件全套** | `run_all.py`（主方法，9 步：取消参数模板→补Query/Export→CSS注入→填报表→样式→行高→布局精排） | `python run_all.py <cpt> [cpt...]` |
| **全目录批量** | `batch_optimize_cpt.py`（项目报表目录下全部 .cpt） | `python batch_optimize_cpt.py` |
| **FR Java API 版** | `ParamPanelFormatter.java`（ckzl/frapi/doc/参数面板格式化器/）— 引擎语义格式化，⚠ 需 web 会话环境 | 见该目录 README |

⚠️ **踩坑（示例实际表.cpt 实测 2026-08-05）**：`batch_optimize_cpt.py` 内 `fix_parameter_controls` 的单行宽度阈值 1200px，会把原本整齐的多列网格拆成 4/4/4/4/2 犬牙交错，且部分 Label 宽度不按文字重算。**对已手工精排/多列网格布局的报表慎用全量脚本**，优先 `layout_panel.py`（已修复上述全部坑：列宽按同列最大重算、面板宽精确重算、容差行聚类、label就近配对）或 `auto_layout_watermark.py`/`fmt_panel_safe.py`/`run_all.py` 定向处理。

⚠️ **适用边界**：`widen_all.py`/`run_all.py` 等脚本围绕「Label + 输入控件」配对布局；`auto_layout_watermark.py` 已统一覆盖三种形态（watermark 无 Label 级联面板 / label-h 水平 / label-v 上下），无 Label 可配对时自动退化 watermark。

## 组件脚本（被 run_all 调用，也可单独跑）

### 🔘 按钮
| 脚本 | 说明 | 用法 |
|------|------|------|
| `add_query_btn.py` | 缺 Query 自动补 | `python add_query_btn.py <cpt>` |
| `add_export_btn.py` | 缺 Export 自动补 (`_g().exportReportToExcel('simple')`) | `python add_export_btn.py <cpt>` |

### 🎨 样式
| 脚本 | 说明 | 用法 |
|------|------|------|
| `fix_styles.py` | 字体统一微软雅黑 + 左右 padding 6 | `python fix_styles.py <cpt>` |
| `add_para_init_event.py` | 参数面板 afterinit CSS 注入 | `python add_para_init_event.py <cpt>` |
| `add_css_import.py` | CSSImport 外部样式引用 | `python add_css_import.py <cpt>` |
| `css样式.txt` | CSS 注入源文件 | 被 `add_para_init_event.py` 引用 |

### ⚙️ 设置
| 脚本 | 说明 | 用法 |
|------|------|------|
| `cancel_params_template.py` | 取消常用参数组合 | `python cancel_params_template.py <cpt>` |
| `set_write_no_toolbar.py` | 填报页面单独设置 + 禁用工具栏 | `python set_write_no_toolbar.py <cpt>` |
| `fix_row_heights.py` | 行高自动分类（表头10mm/明细8mm） | `python fix_row_heights.py <cpt>` |

### 📐 布局
| 脚本 | 说明 | 用法 |
|------|------|------|
| `widen_all.py` | 单模板精排 — 自动识别控件，按宽度约束分行 + 跨行列对齐 | `python widen_all.py <cpt> [cpt...]` |
| `LAYOUT_SPEC.md` | 布局规范文档（180×26、Label→5px、组间20px、内边距12px） | 参考文档 |

## 已归档（移入 `_archive/参数面板控件布局/`，2026-08-05）

| 脚本 | 原因 |
|------|------|
| `widen_cols.py` | 硬编码 示例实际表.cpt 路径，功能被 `widen_all.py` 取代 |
| `widen_ci.py` | CI 报表专用（Label 在控件上方）；当前 CI 报表面板为纯 ComboCheckBox 布局，不再适用 |
