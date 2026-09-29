# -*- coding: utf-8 -*-
"""人机料法环(5M1E)ckzl/zsk/gczsk扩展建库脚本
用法: python build_5m1e.py          # 在 api_kb.sqlite 基础上建 人/料/机/环 表 + 工艺挂脚本
      python build_5m1e.py --rebuild # 删除 api_kb.sqlite 全量重建(需先 build_kb.py)
依赖: 先运行 build_kb.py 建立 parts/bom/routing 三表
"""
import sqlite3, os, sys

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_kb.sqlite")

SCHEMA_5M1E = """
CREATE TABLE IF NOT EXISTS personnel (          -- 人 Man
  person_id INTEGER PRIMARY KEY,
  code      TEXT UNIQUE NOT NULL,               -- U-001 用户 / A-001 AI
  name      TEXT NOT NULL,
  role      TEXT NOT NULL,                      -- 需求方/设计方 / 开发执行方
  scope     TEXT,
  note      TEXT
);
CREATE TABLE IF NOT EXISTS materials (          -- 料 Material（资料物料主数据）
  material_id INTEGER PRIMARY KEY,
  mat_no      TEXT UNIQUE NOT NULL,             -- M-0001
  name        TEXT NOT NULL,
  type        TEXT NOT NULL,                    -- DOC文档/TEMPLATE模板/EXAMPLE示例/DATA数据/REFERENCE参考
  category    TEXT,                             -- 子类
  path        TEXT,                             -- 相对仓库路径
  description TEXT,
  status      TEXT DEFAULT '在用',               -- 在用/归档/待核验
  updated     TEXT,
  source      TEXT,
  embed_vec   BLOB,
  embed_dim   INTEGER DEFAULT 1024,
  embed_model TEXT,
  usage_count INTEGER DEFAULT 0,                -- WMS: 跨项目累计使用次数(聚合自 material_usage)
  used_projects TEXT,                           -- WMS: 使用过的项目清单(逗号分隔,聚合)
  UNIQUE(name, path)
);
CREATE TABLE IF NOT EXISTS material_usage (     -- 料的使用台账(WMS: 项目×物料×次数×角色)
  usage_id    INTEGER PRIMARY KEY,
  project     TEXT NOT NULL,                    -- 项目名(示例驾驶舱 / 示例报表工程 / 基础工具链 / <新项目>)
  mat_no      TEXT NOT NULL,                    -- M-xxxx
  role        TEXT NOT NULL DEFAULT 'PROJECT',  -- PROJECT=项目直接使用 / WIP=半成品(项目内模板/生成产物)使用
  count       INTEGER DEFAULT 1,                -- 使用次数
  note        TEXT,
  UNIQUE(project, mat_no, role)
);
CREATE TABLE IF NOT EXISTS machines (           -- 机 Machine（脚本/工具）
  machine_id    INTEGER PRIMARY KEY,
  m_no          TEXT UNIQUE NOT NULL,           -- MC-001
  name          TEXT NOT NULL,
  path          TEXT,
  type          TEXT NOT NULL,                  -- PYTHON/JAVA/BATCH/JAR
  function      TEXT,
  usage         TEXT,
  related_routing TEXT,                         -- 法->机: 对应工艺号 R-xxx
  note          TEXT
);

CREATE TABLE IF NOT EXISTS echarts_fr_map (      -- ECharts -> FR 图表映射（还原 demo 输入接口）
  map_id        INTEGER PRIMARY KEY,
  echarts_type  TEXT NOT NULL,                   -- ECharts series.type: bar/line/pie/...
  echarts_variant TEXT,                          -- 变体: 横向/堆积/面积/环形...
  fr_name       TEXT NOT NULL,                   -- FR 设计器图表类型（用户可见）
  fr_part_no    TEXT,                            -- 关联零件号（P-0184...）
  fr_class      TEXT,                            -- FR Java 类
  key_mapping   TEXT,                            -- 关键配置映射: ECharts option -> FR 属性
  status        TEXT DEFAULT '待验证',           -- 已验证/待验证/无对应
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS environments (       -- 环 Environment
  env_id    INTEGER PRIMARY KEY,
  e_no      TEXT UNIQUE NOT NULL,               -- ENV-001
  name      TEXT NOT NULL,
  category  TEXT NOT NULL,                      -- 硬件/软件/连接/配置/仓库
  version   TEXT,
  location  TEXT,
  status    TEXT,
  note      TEXT
);
"""

PERSONNEL = [
 ("U-001","用户","需求方/设计方","提需求/验收/手动调整布局样式/提供业务资料","设计器手动操作者；布局样式基线以用户调整为准；**资料索取对象**:表名/字段清单/提交逻辑/级联关系/样式基线/Excel 样例——缺料时按 ckzl/zsk/xqfx/README.md 清单索要(判断>选择>填空>问答)"),
 ("A-001","Hermes(AI)","开发执行方","Java API 生成模板/Python 属性修改/知识维护/主动索取缺失资料","fr-agent /exec + query_kb 检索;缺资料不问→按ckzl/zsk/xtgt四级框架主动索要"),
]

MATERIALS = [
 # 文档 DOC
 ("M-0001","FR_HEADLESS_GUIDE 主路由","DOC","指南","ckzl/gf/FR_HEADLESS_GUIDE.md","全局铁律 A-K 唯一入口",None,"在用",None,"2026-08-07 定稿"),
 ("M-0002","pipeline 阶段文档 01-10","DOC","指南","ckzl/lc/","10 个阶段细节(环境/建模/构建/参数/填报/Web/FRM/调试/GUI/滚动)",None,"在用",None,"懒加载原则"),
 ("M-0003","Java API 构建速查","DOC","API参考","ckzl/frapi/doc/JavaAPI构建速查.md","doc-xxx 逐篇沉淀 API 要点(原夜间学习速查,2026-09-29 改名)",None,"在用",None,"2026-08-06~09"),
 ("M-0004","API 验证记录","DOC","API参考","ckzl/frapi/doc/API验证记录_2026-07-31.md","API 签名验证记录",None,"在用",None,"-"),
 ("M-0005","参数面板格式化 API 清单","DOC","API参考","ckzl/frapi/doc/参数面板格式化API清单.md","参数面板 API 清单",None,"在用",None,"-"),
 ("M-0016","报表平台 BOM 拆解","DOC","参考","ckzl/zsk/frwd/报表平台BOM拆解.md","设计器/服务器/数据库三定点拆解",None,"在用",None,"2026-08-11"),
 ("M-0017","ckzl/zsk/gczsk README","DOC","参考","ckzl/zsk/gczsk/README.md","5M1E 知识库使用说明",None,"在用",None,"2026-08-11"),
 # 模板 TEMPLATE
 ("M-0023","ckzl/frapi/ex","EXAMPLE","示例","ckzl/frapi/ex/","Java 示例代码(AltRowTest等)",None,"在用",None,"-"),
 # 数据 DATA
 ("M-0025","向量索引库","DATA","索引","jcxt/js/jcxt/data/_kb_vector.db","embedding 向量库(gitignore)",None,"在用",None,"阿里云百炼 text-embedding-v4"),
 ("M-0026","KB 索引 yaml","DATA","索引","jcxt/data/_kb_index.yaml","知识文件索引",None,"在用",None,"kfgj/sync_kb_index.py 生成"),
 ("M-0027","api_kb.sqlite","DATA","知识库","ckzl/zsk/gczsk/api_kb.sqlite","5M1E+零件+BOM+工艺数据库",None,"在用",None,"构建产物可重建"),
 # 2026-08-12 复盘补登:整目录物料
 ("M-0028","ckzl/gzjd导航(NODE-01~10)","DOC","指南","ckzl/gzjd/","节点式工作流入口(判定题定向加载)",None,"在用",None,"开发任务首选入口"),
 ("M-0030","ckzl/zsk/qdjk(FR JS API)","DOC","API参考","ckzl/zsk/qdjk/","dev.fanruan.com/jsdoc JS API",None,"在用",None,"写JS回调时查"),
 ("M-0031","ckzl/zsk/sjfx","DOC","指南","ckzl/zsk/sjfx/","字段映射/SQL设计",None,"在用",None,"-"),
 ("M-0032","ckzl/zsk/tbcw","DOC","错误库","ckzl/zsk/tbcw/","错误案例索引表",None,"在用",None,"排查报错先查"),
 ("M-0033","ckzl/zsk/csff","DOC","指南","ckzl/zsk/csff/","验证流程/ckzl/zsk/csff论",None,"在用",None,"-"),
 ("M-0034","ckzl/zsk/xqfx(含决策清单)","DOC","指南","ckzl/zsk/xqfx/","报表分类决策树/字段清单/提交逻辑设计",None,"在用",None,"2026-08-12 补登"),
 ("M-0035","ckzl/zsk/xtgt框架(四级沟通+问卷)","DOC","指南","ckzl/zsk/xtgt/","怎么问(判断>选择>填空>问答)+问什么(5W1H+KANO)",None,"在用",None,"2026-08-12 补登"),
 ("M-0039","scwj/mb(生成器产物落地)","TEMPLATE","输出","scwj/mb/","生成器产出暂存区",None,"在用",None,"-"),
 ("M-0040","kfgj/tygs索引","DOC","指南","kfgj/tygs/索引目录.md","批量格式化脚本清单(样式/参数面板/SQL美化)",None,"在用",None,"格式化任务先查"),
 ("M-0042","FRM 全局默认格式.ini","DATA","配置","frm 报表全局通用默认格式.ini","设计器 FRM 全局默认格式配置",None,"在用",None,"2026-08-11"),
 ("M-0043","报表平台 BOM 拆解(三定点)","DOC","参考","ckzl/zsk/frwd/报表平台BOM拆解.md","设计器/服务器/数据库三定点拆解",None,"在用",None,"2026-08-11"),
 ("M-0044","ckzl/zsk/gczsk 5M1E 总览","DOC","参考","ckzl/zsk/gczsk/README.md","人机料法环各表结构与查询用法",None,"在用",None,"2026-08-12 复盘更新"),
 ]

MACHINES = [
# fr-agent 工具链
("MC-001","fr-agent.jar","fr-agent/fr-agent.jar","JAR","FR Java Agent(注入设计器 JVM)","/exec Nashorn + /events + /eval + :19000 exec-server","R-001~R-005",None),
("MC-002","inject.py","fr-agent/inject.py","PYTHON","注入 fr-agent 到设计器","python inject.py(选内存最大 java 进程)","R-00x",None),
("MC-003","ping.py / fr_agent_client.py","fr-agent/ping.py","PYTHON","fr-agent 存活探测 + exec 客户端","ping :18999 / client :19000","R-00x",None),
("MC-004","start_fr_with_agent.cmd","fr-agent/start_fr_with_agent.cmd","BATCH","带 agent 启动设计器","双击运行","环",None),
("MC-004b","trace3.py","fr-agent/trace3.py","PYTHON","GUI 操作事件流追踪","python trace3.py 拉 :18999/events","R-00x",None),
# ckzl/zsk/gczsk工具
("MC-005","build_kb.py","ckzl/zsk/gczsk/build_kb.py","PYTHON","建 parts/bom/routing 三表","python build_kb.py [--rebuild]","R-001~R-005",None),
("MC-006","build_5m1e.py","ckzl/zsk/gczsk/build_5m1e.py","PYTHON","建 人/料/机/环 表 + 工艺挂脚本","python build_5m1e.py","R-001~R-005",None),
("MC-007","query_kb.py","ckzl/zsk/gczsk/query_kb.py","PYTHON","知识库查询(part/bom/route/mat/machine/env/5m1e)","python query_kb.py <cmd> <kw>","R-001~R-005",None),
("MC-008","kfgj/sync_kb_index.py","kfgj/sync_kb_index.py","PYTHON","同步 jcxt/data/_kb_index.yaml","改知识文件后必跑","知识维护",None),
("MC-009","build_vector_index.py","jcxt/js/build_vector_index.py","PYTHON","重建向量索引","需 config.toml(百炼 key)","知识维护",None),
("MC-010","query_kb.py(向量)","jcxt/js/query_kb.py","PYTHON","jcxt/js知识块","python jcxt/js\\query_kb.py \"问题\" --top 5","知识检索",None),
# 格式化/生成脚本(kfgj/fzpy)
("MC-012","fmt_wildcard.py","kfgj/tygs/CPT模板/默认格式/fmt_wildcard.py","PYTHON","泛化通配格式化脚本","python fmt_wildcard.py <cpt>","R-00x",None),
("MC-013","param_panel_style.py","kfgj/tygs/CPT模板/默认格式/param_panel_style.py","PYTHON","参数面板完整 CSS 套件注入","5600+ 字符 CSS 源","R-005",None),
("MC-013b","fmt_detail_cells.py","kfgj/tygs/CPT模板/默认格式/fmt_detail_cells.py","PYTHON","明细单元格样式格式化","按默认格式目录套用","R-004",None),
("MC-013c","freeze_header.py","kfgj/tygs/CPT模板/默认格式/freeze_header.py","PYTHON","冻结表头脚本","模板构建后自动跑","R-004",None),
("MC-014","fr_check.py","kfgj/fzpy/fr_check.py","PYTHON","模板验证(XML合法性+在线/浏览器)","python fr_check.py <cpt>","R-004 VALIDATE",None),
("MC-014b","fr_preview.py","kfgj/fzpy/fr_preview.py","PYTHON","轻量预览/错误检测","python fr_preview.py <cpt>","R-004 VALIDATE",None),
("MC-014c","verify_cpt.py","kfgj/fzpy/verify_cpt.py","PYTHON","CPT 深度校验","python verify_cpt.py <cpt>","R-004 VALIDATE",None),
("MC-014d","final_verify.py","kfgj/fzpy/final_verify.py","PYTHON","交付前终验","python final_verify.py","R-004 VALIDATE",None),
("MC-014e","check_env.py","kfgj/fzpy/check_env.py","PYTHON","环境自检(JDK/FR/javac)","python check_env.py","环",None),
("MC-015","fr_exec.py","kfgj/fzpy/fr_exec.py","PYTHON","fr-agent /exec Nashorn 执行器","Python urllib 发 JSON 到 :19000","R-001~R-005",None),
("MC-018b","gen_fill_v2.py","gen_fill_v2.py","PYTHON","填报生成器主入口(单元格/参数面板工厂)","根目录工厂函数模板","R-001",None),
("MC-018c","gen_overview_v4.py","gen_overview_v4.py","PYTHON","Overview 树形报表生成器(v4)","根目录","R-001",None),
# 2026-08-12 复盘补登:SQL/模板工具
("MC-021","format_sql.py","kfgj/fzpy/format_sql.py","PYTHON","SQL 一键格式化(美化/缩进)","python format_sql.py","R-010",None),
("MC-022","template_snapshot.py","kfgj/fzpy/template_snapshot.py","PYTHON","模板快照(结构/属性/坐标 dump)","AI助手借鉴第6项","探查",None),
("MC-023","verify_sql.py","kfgj/fzpy/verify_sql.py","PYTHON","SQL 验证闭环(FR 宏拼接语法解析)","验证9/10通过","R-010",None),
("MC-024","db_schema.py","kfgj/fzpy/db_schema.py","PYTHON","表结构探查(对应 DatasetTools)","python db_schema.py","R-004",None),
("MC-025","layout_grid.py","kfgj/fzpy/layout_grid.py","PYTHON","栅格布局计算器","AI助手借鉴第5项","R-004",None),
("MC-026","fix_kpi_scroll.py","kfgj/fzpy/fix_kpi_scroll.py","PYTHON","KPI 卡片滚动条修复(行高26/28/26+列宽240/60)","示例驾驶舱_v3应用","R-009",None),
("MC-027","fix_bar_width.py","kfgj/fzpy/fix_bar_width.py","PYTHON","柱形图柱宽固定->自动(VanChartColumnPlotAttr)","示例驾驶舱_v3应用","R-007",None),
("MC-028","fix_chart_program_horizontal.py","kfgj/fzpy/fix_chart_program_horizontal.py","PYTHON","Program Top20 改横向条形图(isBar)","chart_program 系列","R-007",None),
("MC-029","fix_chart_program_axis.py","kfgj/fzpy/fix_chart_program_axis.py","PYTHON","横向条形图补轴交换(X=数值/Y=分类)","fix isBar 翻转后无数据","R-007",None),
("MC-030","fix_program_rotation_bu.py / fix_program_scroll.py / fix_program_second_chart.py / fix_program_series_case.py / restore_chart_program_vertical.py","kfgj/fzpy/(fix_program_*|restore_chart_program_vertical).py","PYTHON","Program Top20 图表修复组(旋转/滚动/第二图/系列/竖向恢复)","示例驾驶舱 chart_program 系列","R-007",None),
("MC-031","fix_cascade_sql.py","kfgj/fzpy/fix_cascade_sql.py","PYTHON","级联参数 SQL 修复","fix_cascade_sql.py","R-005",None),
("MC-032","optimize_param_panel.py","kfgj/fzpy/optimize_param_panel.py","PYTHON","参数面板布局优化","python optimize_param_panel.py","R-005",None),
("MC-033","set_write_web_attr.py","kfgj/fzpy/set_write_web_attr.py","PYTHON","填报 Web 属性设置","set_write_web_attr.py","R-005",None),
("MC-034","update_css.py","kfgj/fzpy/update_css.py","PYTHON","CSS 更新注入","update_css.py","R-005",None),
("MC-035","add_year_bu_controls.py","kfgj/fzpy/add_year_bu_controls.py","PYTHON","年份/BU 控件添加","add_year_bu_controls.py","R-005",None),
("MC-036","add_para_init_event.py","kfgj/fzpy/add_para_init_event.py","PYTHON","参数面板初始化事件添加","add_para_init_event.py","R-005",None),
("MC-037","fix_ci_ds.py / fix_ci_query.py / gen_demo_ci.py","kfgj/fzpy/(fix_ci_*|gen_demo_ci).py","PYTHON","示例项目 CI 数据集/查询修复+生成器","示例报表工程","R-001",None),
("MC-038","gen_fs2.py / gen_lta_detail.py / fix_lta.py","kfgj/fzpy/(gen_fs2|gen_lta_detail|fix_lta).py","PYTHON","FS2/LTA 填报表生成与修复","示例报表工程","R-001",None),
("MC-039","fix_formulas.py / fix_div_zero.py / fix_div_zero_all.py / fix_budget.py / fix_pact.py / fix_cdata_quotes.py / convert_excel_formula.py","kfgj/fzpy/(fix_formulas|fix_div_zero*|fix_budget|fix_pact|fix_cdata_quotes|convert_excel_formula).py","PYTHON","公式修复组(除零/预算/合同/CDATA/Excel公式转换)","示例报表工程","R-004",None),
("MC-040","fr_rules_doc.py / fr_rules_export.py","kfgj/fzpy/fr_rules_*.py","PYTHON","fr_check Layer 1.5 官方规则库(98条)","fr_check.py --no-rules 关闭","R-004 VALIDATE",None),
("MC-041","fix_fs2.py(gen_fs2 配套)","kfgj/fzpy/","PYTHON","FS2 相关修复","示例报表工程","R-004",None),
("MC-043","官方文档沉淀工具(27 个 gen/inject)","kfgj/tygs/官方文档沉淀工具/","PYTHON","官方能力无头生成/注入(级联/排序/图表/导出/权限)","README.md 有清单","R-004~R-009",None),
]

ENVIRONMENTS = [
("ENV-001","FineReport 设计器 10.0","软件","10.0.19","C:\\Program Files\\FineReport_10.0","在用","模板开发主环境(本机 C 盘,无 D 盘)"),
("ENV-002","fr-agent 注入通道","软件","18999/19000","http://localhost:18999 / :19000","在用","Java API 执行通道"),
("ENV-003","JDK8","软件","jdk8u432-b06(Amazon Corretto)","C:\\Program Files\\Amazon Corretto\\jdk1.8.0_432","在用","Nashorn 脚本运行;编译 Attacher 用独立 JDK"),
("ENV-004","Windows","硬件","11 + 150%缩放","1920x1080","在用","画布标准 1280x720 依据"),
("ENV-005","数据连接 demo_connection","连接","PostgreSQL","demo_ads 库","在用","示例驾驶舱 报表数据源"),
("ENV-006","fr_dev_kit 仓库","仓库","git v8.0812","Desktop\\fr_dev_kit_v8.0812","在用","知识库唯一入口(在线仓库为 hub)"),
("ENV-007","jcxt/js embedding","连接","text-embedding-v4","阿里云百炼 config.toml","在用","key 已内置 jcxt/js/config.toml(2026-08-11 起真实向量)"),
("ENV-008","FineReport 服务器","软件","10.0 8075","localhost:8075","在用","预览/导出 viewlet 通道"),
("ENV-009","FineReport 11.0","软件","11.0","C:\\FineReport_11.0","备用","FR11 对照环境(插件基线不同)"),
("ENV-010","项目数据库","连接","PostgreSQL","demo_connection 各业务表","在用","示例驾驶舱/示例项目报表 明细库(探针 fr_jdbc_probe 直连)"),
("ENV-011","浏览器预览","软件","Chrome 设备仿真","localhost:8075 viewlet","在用","移动端适配验证(doc-4637)"),
]

# 工艺(法)挂脚本(机): routing_no + step_no -> 机器号
ROUTING_MACHINE = [
 ("R-001",1,"MC-015"),  # fr_exec 发 Nashorn
 ("R-001",5,"MC-015"),
 ("R-002",1,"MC-015"),
 ("R-002",6,"MC-015"),
 ("R-003",1,"MC-015"),
 ("R-003",6,"MC-015"),
 ("R-004",1,"MC-015"),
 ("R-004",4,"MC-007"),  # 查询知识库确认禁全局 replace
 ("R-004",5,"MC-014"),  # fr_check 验证
 ("R-005",5,"MC-013"),  # param_panel_style CSS
 ("R-005",6,"MC-007"),

 ("R-006",2,"MC-015"),
 ("R-006",3,"MC-015"),
 ("R-006",7,"MC-015"),
 ("R-006",8,"MC-015"),
 ("R-006",9,"MC-015"),
 ("R-006",12,"MC-015"),
 ("R-007",1,"MC-007"),
 ("R-007",3,"MC-019"),
 ("R-008",2,"MC-015"),
 ("R-008",3,"MC-015"),
 ("R-009",4,"MC-007"),
 # 2026-08-12 复盘:新工艺挂脚本
 ("R-010",1,"MC-021"),  # format_sql SQL 一键格式化
 ("R-010",2,"MC-023"),  # verify_sql 验证
 ("R-011",1,"MC-015"),  # fr_exec 查 API 用法
 ("R-012",2,"MC-014"),  # fr_check 验证
]


ECHARTS_MAP = [
    ('bar', '分组柱状', '柱形图', 'P-0184', 'com.fr.plugin.chart.column.ColumnIndependentVanChart', 'series.stack 缺省 → vanChartPlotType=normal；xAxis.category → 分类轴；yAxis.value → 数值轴；barWidth → 系列固定宽度；barGap → 分类间隔；itemStyle.borderRadius → 系列圆角(radius=5)', '已验证', 'demo chart_oem/chart_bu 用；VALUE 分类+系列+值'),
    ('bar', '堆积', '堆积柱形图', 'P-0185', 'com.fr.plugin.chart.column.ColumnIndependentVanChart', "series.stack='x' → vanChartPlotType=stack；其余同分组柱状", '已验证', '克隆图表默认 stack 会按系列堆叠'),
    ('bar', '横向', '条形图', 'P-0186', 'com.fr.plugin.chart.bar.BarIndependentVanChart', 'xAxis.value + yAxis.category → 横向；FR: ColumnPlot.setAxisRotation(true) 或 BarPlot（X=数值 Y=分类）', '已验证', 'demo chart_top 用；轴方向是配置 DNA'),
    ('bar', '横向堆积', '堆积条形图', 'P-0187', 'com.fr.plugin.chart.bar.BarIndependentVanChart', '横向 + series.stack → BarPlot + STACK', '待验证', ''),
    ('line', '折线', '折线图', 'P-0189', 'com.fr.plugin.chart.line.LineIndependentVanChart', 'series.smooth → 平滑；lineStyle.dashed → 虚线；symbol 显示 → 数据点；图例位置 legend.position', '已验证', 'demo chart_trend 线系列'),
    ('line', '面积', '面积图', 'P-0190', 'com.fr.plugin.chart.area.AreaIndependentVanChart', 'series.areaStyle → 面积填充；其余同折线', '待验证', ''),
    ('line', '堆积面积', '堆积面积图', 'P-0191', 'com.fr.plugin.chart.area.AreaIndependentVanChart', 'areaStyle + stack → AreaPlot + STACK', '待验证', ''),
    ('pie', '饼图', '饼图', 'P-0188', 'com.fr.plugin.chart.pie.PieIndependentVanChart', 'series.radius → 内/外径；roseType → 玫瑰；label.formatter → 标签格式 {b}: {c}', '已验证', '环形图=饼图+Donut'),
    ('scatter', '散点', '散点图', 'P-0192', 'com.fr.plugin.chart.scatter.ScatterIndependentVanChart', 'xAxis/yAxis value → 双数值轴；symbolSize 固定 → 点大小', '待验证', ''),
    ('scatter', '三值(大小维)', '气泡图', 'P-0193', 'com.fr.plugin.chart.bubble.BubbleIndependentVanChart', '第三维(大小) → symbolSize 映射；FR 三值绑定 X/Y/大小', '待验证', ''),
    ('radar', '雷达', '雷达图', 'P-0194', 'com.fr.plugin.chart.radar.RadarIndependentVanChart', 'radar.indicator → 指标维度；series.data → 各指标值', '待验证', ''),
    ('funnel', '漏斗', '漏斗图', 'P-0195', 'com.fr.plugin.chart.funnel.FunnelIndependentVanChart', 'funnel.sort → 排序；funnel.gap → 间距；label → 转化率标签', '待验证', ''),
    ('treemap', '矩形树图', '矩形树图', 'P-0196', 'com.fr.plugin.chart.treemap.TreemapIndependentVanChart', 'treemap.levels → 层级；breadcrumb → 面包屑', '待验证', ''),
    ('wordcloud', '词云', '词云', 'P-0197', 'com.fr.plugin.chart.wordcloud.WordCloudIndependentVanChart', 'wordcloud.sizeRange → 字号范围；wordcloud.rotationRange → 旋转', '待验证', 'ECharts 词云是扩展图表'),
    ('graph', '力导向关系', '力学气泡图', 'P-0198', 'com.fr.plugin.chart.force.ForceIndependentVanChart', 'graph.force → 力导向；nodes/links → 节点关系；symbolSize → 气泡大小', '待验证', 'ECharts graph 力导向布局'),
    ('bar', '多系列嵌套', '多层柱形图', 'P-0199', 'com.fr.plugin.chart.multiLayerColumn.MultiLayerColumnIndependentVanChart', '多系列分组嵌套 → 多层柱（FR 特有嵌套分类）', '待验证', 'ECharts 无直接对应，近似多系列 bar'),
    ('bar+line', '柱线混合', '组合图（柱线图）', '-', 'MoreNameCDDefinition 多系列 + 系列级类型', "混合 series[bar,line] → 每系列可选柱/线；设计器'柱状图'类型下拉选'组合图'", '待验证', 'reportlets 无现成范例；ECharts 混合常见'),
    ('heatmap', '热力图', '热力图', '-', '-', 'visualMap → 色阶映射', '待验证', 'FR 需查插件'),
    ('map', '地图', '地图', '-', '-', 'geo/map 坐标 → FR 地图数据绑定', '待验证', ''),
    ('gauge', '仪表盘', '仪表盘', '-', '-', 'gauge.axisLine → 刻度盘', '待验证', ''),
    ('candlestick', 'K线图', 'K线图', '-', '-', 'candlestick → FR K线', '待验证', ''),
    ('boxplot', '箱线图', '箱线图', '-', '-', 'boxplot → FR 箱线', '待验证', ''),
    ('sankey', '桑基图', '桑基图', '-', '-', 'sankey → FR 桑基', '待验证', ''),
    ('sunburst', '旭日图', '旭日图', '-', '-', 'sunburst → FR 旭日', '待验证', ''),
    ('parallel', '平行坐标', '平行坐标图', '-', '-', 'parallelAxis → FR 平行坐标', '待验证', ''),
    ('pictorialBar', '象形柱图', '象形柱图', '-', '-', 'symbol 图形柱 → FR 象形柱(插件)', '待验证', ''),
    ('lines', '路径图', '路径图', '-', '-', 'lines → FR 路径图', '待验证', ''),
    ('themeRiver', '主题河流', '主题河流图', '-', '-', 'themeRiver → FR 主题河流', '待验证', ''),
    ('custom', '自定义', '自定义图', '-', '-', 'renderItem → FR 自定义图', '待验证', ''),
]

# 料的使用台账初始数据(WMS): (project, mat_no, role, count, note)
# role: PROJECT=项目直接使用 / WIP=半成品(项目内模板/生成产物)使用
# 2026-08-12 初值来源:扫描 ckzl/bb/外部依赖与归档声明.md示例驾驶舱项目/ ckzl/bb/外部依赖与归档声明.md2026-08/示例驾驶舱/ 示例报表工程/ 文档引用 + 人工校准
USAGE = [
    # ── 示例驾驶舱 项目(直接使用) ──
    ("示例驾驶舱","M-0006","PROJECT",5,"FRM 指南 SKILL 核心参考"),
    ("示例驾驶舱","M-0007","PROJECT",3,"FRM API 实测构造签名"),
    ("示例驾驶舱","M-0008","PROJECT",3,"驾驶舱端到端配方"),
    ("示例驾驶舱","M-0009","PROJECT",2,"v2 迭代与 demo 映射"),
    ("示例驾驶舱","M-0010","PROJECT",2,"样式基线"),
    ("示例驾驶舱","M-0011","PROJECT",3,"画布布局经验"),
    ("示例驾驶舱","M-0012","PROJECT",4,"VanChart 图表经验(柱高0根因)"),
    ("示例驾驶舱","M-0013","PROJECT",2,"图表类型调研"),
    ("示例驾驶舱","M-0014","PROJECT",2,"驾驶舱蓝图设计"),
    ("示例驾驶舱","M-0015","PROJECT",2,"端到端配方副本"),
    ("示例驾驶舱","M-0019","PROJECT",2,"WorkBuddy 调用模板"),
    ("示例驾驶舱","M-0022","PROJECT",2,"参考模板目录"),
    ("示例驾驶舱","M-0037","PROJECT",1,"项目经验自身"),
    # ── 示例驾驶舱 半成品(WIP):驾驶舱模板/生成产物使用 ──
    ("示例驾驶舱","M-0020","WIP",3,"cpt 空白骨架(生成器产出半成品用)"),
    ("示例驾驶舱","M-0021","WIP",6,"frm 空白骨架(驾驶舱 v1~v3 半成品用)"),
    ("示例驾驶舱","M-0010","WIP",1,"全局默认格式半成品基线"),
    ("示例驾驶舱","M-0042","WIP",1,"FRM 全局默认格式.ini 半成品配置"),
    ("示例驾驶舱","M-0025","WIP",1,"向量索引库(半成品检索)"),
    # ── 示例报表工程项目 ──
    ("示例报表工程","M-0036","PROJECT",29,"项目主体(权限配置报表)"),
    ("示例报表工程","M-0032","PROJECT",3,"ckzl/zsk/tbcw(排错参考)"),
    ("示例报表工程","M-0005","PROJECT",2,"参数面板格式化 API"),
    ("示例报表工程","M-0001","PROJECT",1,"主路由"),
    # ── 基础工具链(仓库级,跨项目通用) ──
    ("基础工具链","M-0001","PROJECT",32,"主路由全库引用"),
    ("基础工具链","M-0002","PROJECT",5,"pipeline 阶段文档"),
    ("基础工具链","M-0003","PROJECT",2,"夜学 API 速查"),
    ("基础工具链","M-0004","PROJECT",2,"API 验证记录"),
    ("基础工具链","M-0005","PROJECT",1,"参数面板 API 清单"),
    ("基础工具链","M-0017","PROJECT",17,"ckzl/zsk/gczsk README"),
    ("基础工具链","M-0018","PROJECT",17,"项目经验 README"),
    ("基础工具链","M-0025","PROJECT",1,"向量索引库"),
    ("基础工具链","M-0026","PROJECT",5,"KB 索引 yaml"),
    ("基础工具链","M-0027","PROJECT",5,"api_kb.sqlite 本体"),
    ("基础工具链","M-0041","PROJECT",4,"文档核验待办"),
    ("基础工具链","M-0044","PROJECT",17,"5M1E 总览 README"),
]

def build():
    if not os.path.exists(DB):
        print("先运行 build_kb.py 建立基础表"); sys.exit(1)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.executescript(SCHEMA_5M1E)
    cur.executemany("INSERT OR REPLACE INTO personnel(code,name,role,scope,note) VALUES(?,?,?,?,?)", PERSONNEL)
    cur.executemany("INSERT OR REPLACE INTO materials(mat_no,name,type,category,path,description,status,updated,source) VALUES(?,?,?,?,?,?,?,?,?)",
                    [(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8]) for m in MATERIALS])
    cur.executemany("INSERT OR REPLACE INTO machines(m_no,name,path,type,function,usage,related_routing,note) VALUES(?,?,?,?,?,?,?,?)",
                    [(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7]) for m in MACHINES])
    # echarts_fr_map 无业务唯一约束,先清空再插(防重复)
    cur.execute("DELETE FROM echarts_fr_map")
    cur.executemany("INSERT INTO echarts_fr_map(echarts_type,echarts_variant,fr_name,fr_part_no,fr_class,key_mapping,status,notes) VALUES(?,?,?,?,?,?,?,?)",
                    [(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7]) for m in ECHARTS_MAP])
    cur.executemany("INSERT OR REPLACE INTO environments(e_no,name,category,version,location,status,note) VALUES(?,?,?,?,?,?,?)", ENVIRONMENTS)
    # 料的使用台账(WMS): 先清空再插(保持源为唯一真值,幂等)
    cur.execute("DELETE FROM material_usage")
    cur.executemany("INSERT INTO material_usage(project,mat_no,role,count,note) VALUES(?,?,?,?,?)",
                    [(u[0],u[1],u[2],u[3],u[4]) for u in USAGE])
    # 聚合回 materials.usage_count / used_projects
    cur.execute("""UPDATE materials SET usage_count = COALESCE((SELECT SUM(count) FROM material_usage
                   WHERE material_usage.mat_no = materials.mat_no), 0)""")
    cur.execute("""UPDATE materials SET used_projects = (SELECT GROUP_CONCAT(DISTINCT project) FROM material_usage
                   WHERE material_usage.mat_no = materials.mat_no)""")
    # 工艺表加 machine 列并挂脚本（幂等：列已存在则跳过）
    cols = [r[1] for r in cur.execute("PRAGMA table_info(routing)").fetchall()]
    if "machine" not in cols:
        cur.execute("ALTER TABLE routing ADD COLUMN machine TEXT")
    for rno, step, mno in ROUTING_MACHINE:
        cur.execute("UPDATE routing SET machine=? WHERE routing_no=? AND step_no=?", (mno, rno, step))
    conn.commit()
    for t in ("personnel","materials","machines","environments","echarts_fr_map","material_usage"):
        print(t, cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
    print("routing 挂脚本工序:", cur.execute("SELECT count(*) FROM routing WHERE machine IS NOT NULL").fetchone()[0])
    print("料使用台账聚合: 有使用记录的物料数 =",
          cur.execute("SELECT COUNT(*) FROM materials WHERE usage_count > 0").fetchone()[0])
    conn.close()
    print("DB:", DB)

if __name__ == "__main__":
    build()
