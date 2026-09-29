<!--
KB_INDEX: {
  "title": "辅助 Python 脚本",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["SQL", "cpt", "kfgj", "db_schema", "ckzl", "python"],
  "summary": "--- keywords: [sql 验证, SQL 执行验证, verify_sql, 参数宏替换, 验证闭环, 0 行不通过, fr_check, fr_preview, convert_excel_formula, submit_co"
}
-->

---
keywords: [sql 验证, SQL 执行验证, verify_sql, 参数宏替换, 验证闭环, 0 行不通过, fr_check, fr_preview, convert_excel_formula, submit_config_check, export_gate, 提交配置, 内容校验, 导出文件校验, 导出产物校验, 魔数校验, cpt xml 校验, xml 校验工具, 模板自检, XML 合法性校验, db_schema, 数据库表结构, 表结构探查, 字段类型, 搜表, 样例数据, layout_grid, 栅格布局, 坐标计算, 布局栅格, span 合并, BoundsWidget, template_snapshot, 模板结构快照, 模板快照, 结构快照, 数据集字段, 改前快照, node_gate, 节点门禁, 出口门禁, file_lock, 文件锁, 防写冲突, backup_template, 模板备份, userdir, 用户私有目录]
---

<!--
KB_INDEX: {
    "title": "辅助 Python 脚本",
    "stage": "utility-scripts",
    "tags": [
      "脚本",
      "工具"
    ],
    "keywords": [
      "fr_check",
      "fr_preview",
      "verify_sql",
      "template_snapshot",
      "backup_template"
    ],
    "summary": "辅助 Python 脚本索引：校验/预览/快照/备份/SQL 与布局工具的用法与归属（历史一次性项目脚本已迁出，见 ckzl/bb/外部依赖与归档声明.md）"
  }
-->

# 辅助 Python 脚本

> 通用工具脚本集合。这些不是 kfgj/tygs——使用前请确认场景匹配。
> 写死业务路径的一次性项目脚本已随开源裁剪迁出（见 [ckzl/bb/外部依赖与归档声明.md](../../ckzl/bb/外部依赖与归档声明.md)）。

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 按场景查找

| 你遇到的问题 | 用哪个脚本 | 关键细节 |
|-------------|-----------|---------|
| 除法公式除零报错 | `fix_div_zero_all.py` | 添加 `if(len(x)=0\|\|x=0,'',num/x)`（全目录批处理） |
| Excel 公式 → FR 公式 | `convert_excel_formula.py` | 导入前批量转换: ISBLANK→LEN, TEXT→FORMAT, OFFSET→层次坐标, $ 移除, &→+, AND/OR→&&/\|\| |
| 级联参数 SQL 格式错误 | `fix_cascade_sql.py` | `${para}` → FR 公式标准写法 |
| CDATA 引号转义错误 | `fix_cdata_quotes.py` | 修复 CDATA 内部引号 |
| CSS 内容需要更新 | `update_css.py` | 更新注入的 CSS 规则 |
| SQL 需要美化 | `format_sql.py` | 旧版 SQL 格式化（新版用 `kfgj/tygs/`） |
| afterinit 事件注入 | `add_para_init_event.py` | 参数面板初始化事件 |
| 导出产物验收（xlsx/pdf） | `export_gate.py --file <产物> [--kind auto\|xlsx\|pdf]` | G1 存在/G2 魔数/G3 行数/G4 水印/G5 页数；退出码 0/1/2 对齐 fr_check；自检 `export_gate_selftest.py` |
| 填报提交配置内容校验 | `submit_config_check.py <cpt> [--db]` | S1-S7 内容级断言；退出码对齐 fr_check |
| 数据集 SQL 写完先验证 | `verify_sql.py` -s "<SQL含${if(...)}宏>" -p para=值 | 执行闭环：参数宏替换为静态值→真实执行；0 行=不通过，调整重试 ≤3 |
| 多组件布局坐标计算 | `layout_grid.py` -W <宽> -H <高> -n <组件数> [--span] [--row] [--rect] | 布局栅格计算器；--rect 直接输出 BoundsWidget Rect 代码 |
| 改模板前先取结构快照 | `template_snapshot.py` [模板文件] [--save] | 数据集/参数/图表绑定现状；--fields 带数据集字段；--save 存档到用户目录 |
| 改模板前先备份 | `backup_template.py <模板> [-m 备注]` | 备份到 `~/.fr_dev_kit/backup/<模板名>/<时间戳>/`；--list 查看、--prune 清理 |
| 用户私有数据目录定位 | `userdir.py` | `~/.fr_dev_kit/`（backup/snapshot/experience/memory）；初始化向导见 `kfgj/init_user_env.py` |
| 多会话同时改 cpt 防写冲突 | `file_lock.py` acquire/release/check/list | 劝告式文件锁；锁落 _runs/locks/（TTL 30 分钟默认）；领锁失败退出码 1，禁止强写 |

### 常见问法：查表结构/表字段/建表语句怎么看？这张表有哪些字段、类型、注释？表名记不全怎么找？

| 口语问题 | 用法（db_schema.py argparse 实读核对） |
|---|---|
| 查一下这张表有哪些字段、类型、注释 | `python kfgj/fzpy/db_schema.py <schema.table>`：输出 字段名/类型/注释/NOT NULL（DWS 直连） |
| 顺便看两行真实数据长什么样 | 加 `--sample`：附带前 3 行样例数据 |
| 表名记不全，模糊找一下有哪些表 | `python kfgj/fzpy/db_schema.py --search <关键字>`：按关键字搜表（带表注释）；`--tables` 列全部表 |
| 建表语句/DDL 不在手边，怎么看表结构 | 上述输出即字段级结构等价物；看任意 SQL 会输出哪些字段用 `--sql "<SQL>"`；要机读格式加 `--json` |

### 常见问法：页面 JS 报错/表格空白/控件重叠怎么自动检查？页面打不开怎么排查？

| 口语问题 | 用法（web_kit/probe.py argparse+README 实读核对） |
|---|---|
| 页面跑起来后 JS 报错、数据集静默错误怎么自动抓 | `python web_kit/probe.py <cpt绝对路径或URL>`：真开浏览器抓 pageerror/console/FR 业务错误/加载卡死，出截图+报告 |
| 表格空白/网格不渲染 | runtime.grid 探针主动 POST view_content 复核服务端渲染 |
| 必填没填/校验不过怎么自动点名 | widgets.validation 逐控件 getErrorMsg（warn） |
| 交付前体检怎么跑 | AGENTS.md SOP STEP5：`python web_kit\probe.py <cpt>`，退出码 0 且 error=0 才交付；报告落 `_runs/webprobe/`；误报登记 `web_kit/baseline.yaml` |

## 按类别分类

### 校验/检查类
- `fr_check.py` / `fr_preview.py` — 模板自检 / 预览（另见根目录用法）
- `check_env.py` — 环境检查（读用户目录 fr_env.toml，见 `kfgj/init_user_env.py`）
- `export_gate.py` — 导出文件自动校验（xlsx/pdf 魔数、行数、水印、页数）
- `submit_config_check.py` — 填报提交配置内容校验（S1-S7，--db 库级列校验）
- `verify_sql.py` — SQL 执行验证（生成的新数据集 SQL 必过）
- `template_snapshot.py` — 模板结构快照（--save 存档用户目录）
- `node_gate.py` — 节点出口门禁执行器（--node <NN> 汇总跑 ckzl/gzjd/node_gates.yaml）
- `file_lock.py` — 文件锁：防写冲突
- `receipt_screen.py` — 外部回执/网页正文指令性内容筛查（防注入）

### 修复/转换类
- `convert_excel_formula.py` — Excel→FR 公式转换
- `fix_div_zero_all.py` — 除零保护（全目录）
- `fix_cascade_sql.py` — 级联 SQL 修复
- `fix_cdata_quotes.py` — CDATA 引号修复
- `fix_deep_learn_templates.py` / `unify_panel_y10.py` / `frm_apply_style.py` — 模板批量整理
- `update_css.py` / `add_para_init_event.py` — CSS/事件注入
- `format_sql.py` — SQL 格式化（旧版）

### 数据/布局类
- `db_schema.py` — 表结构探查（--search/--sample/--sql）
- `layout_grid.py` — 布局坐标栅格计算器

### 用户环境类
- `userdir.py` — 用户私有数据目录（`~/.fr_dev_kit/`）路径助手
- `backup_template.py` — 模板修改前统一备份
- `llm_call_logger.py` / `llm_trace_report.py` — LLM 调用埋点与报告
- `jar_class_probe.py` / `kb_keyword_audit.py` / `build_doc_id_registry.py` — 检索/知识配套

## 使用注意

- ⚠️ **每次运行前备份**：会改 CPT 的脚本，先 `backup_template.py <模板>` 领一份备份
- ⚠️ **运行后验证 XML**：`python -c "import xml.etree.ElementTree as ET; ET.parse('file.cpt')"`

## 相关指引

- 批量格式化（字体/布局/行高）→ [../tygs/索引目录.md](../tygs/索引目录.md)
- 填报交互知识 → [../../ckzl/lc/05_填报与交互.md](../../ckzl/lc/05_填报与交互.md)
