<!--
KB_INDEX: {
  "title": "FR Dev Kit — FineReport 报表开发能力基座（开源主 README）",
  "stage": "root",
  "tags": ["README", "开源", "快速开始", "Agent工作区"],
  "keywords": ["FineReport", "报表开发", "agent", " cpt", "frm", "知识库", "零件库", "闸门", "fr-dev-kit"],
  "summary": "开源主文档: 把 FR 10/11 报表开发变成 agent 可执行工作区(零件库+无向量知识库+六流程+12闸门); 快速开始3步+agent工作区用法+六种任务路由"
}
-->

# FR Dev Kit — FineReport 报表开发能力基座（Agent-Ready）

**把 FineReport 10 / 11 报表开发变成 Agent 可直接执行的工作区。**
内置：结构化 API 零件库、无向量知识库、六种开发流程、机器闸门。Agent 读完 `AGENTS.md` 即可开工——你只需提供**数据连接、业务表逻辑、项目目录**。

```text
你（业务方）                          Agent（读 AGENTS.md 自动路由）
──────────────                        ─────────────────────────────
"数据连接 demo_dw，表 dws_sales        ① 探表结构 → ② 写数据集 SQL → 验证
 .order_detail(单号/客户/金额/日期)，    ③ 选骨架/生成骨架 → ④ 建参数面板
 帮我建一张带区域筛选的订单明细表，       ⑤ 绑定 DSColumn → ⑥ fr_check 体检
 输出到我的项目目录"                     ⑦ 部署预览 → ⑧ 12 条闸门收尾
```

---

## 📢 v3.0 开源首发

各位报表人，久等了。

你一定也经历过：设计器里拖了三小时格子，客户一句「表头再宽点」让你从头再来；搜一个 `com.fr` 报错，全网答案都是「建议重启设计器」；让 AI 帮忙改个 cpt，改完文件直接打不开——它连合并单元格要先 merge 后样式都不知道。

所以我们把多年踩坑攒下的家底全掏了出来：

- **14,590 个 `com.fr.*` 零件**，全部 javap 实测带坑位标注——AI 张嘴之前先查库，不再猜包名
- **221 页知识库**，按页存储、树状导航、13 个多维视图，检索零 key 零配置——断网也能查
- **六种开发流程**，含「给个 Excel 样子就出 cpt」的正向工艺（无头转换实测 52ms）
- **12 条机器闸门**：AI 想蒙混过关？退出码非 0，任务就不算完

现在它开源了（MIT）。你只需要：把仓库克隆成 agent 工作区 → 打开设计器 → 丢给 agent 一句
「数据连接 demo_dw，表 dws_sales.order_detail，帮我出张带筛选的明细表」。

报表开发的苦，该到头了。**👉 QQ 交流群：1065801779**

---

## 为什么是这个形状

FineReport 模板是 XML（.cpt/.frm），人肉调格子效率低且易碎；LLM 直接改 XML 又缺三样东西：**正确的 API 知识**（网上多为猜测）、**安全的操作纪律**（正则改坏模板）、**验收标准**（改完算不算完）。本仓库把这三样补齐成可执行资产：

| 资产 | 内容 | 入口 |
|------|------|------|
| **API 零件库** | 14,590 个 `com.fr.*` 零件（javap 实测签名/坑位标注） | `python ckzl/zsk/gczsk/query_kb.py part <编号或关键字>` |
| **知识库（无向量）** | 221 页按页存储、树索引 + FTS5 关键词 + 页级导航 + 13 个多维视图，**零 key 零配置零网络** | `python jcxt/js/query_kb.py "<问题>" --mode keyword` |
| **六种开发流程** | 创建/修改/排错/GUI 追踪/查 API/Excel 骨架正向，读取路径与工具链已固化 | `AGENTS.md` §3 |
| **12 条机器闸门** | 备份/断链/契约同源/SQL 闭环/公式验证/预览——退出码非 0 即任务未完成 | `python kfgj/guard.py --task create --cpt <产物>` |

## 快速开始（3 步）

```bash
git clone https://github.com/xdongHo/fr-dev-kit.git
cd fr-dev-kit
python kfgj/init_user_env.py    # 私有环境落 ~/.fr_dev_kit/，不进仓库
python kfgj/guard.py --selftest # 全 PASS 即就绪
```

环境要求：Python 3.11+；**FineReport 10/11 设计器（必需）**——10.0.19 与 11.x 均实测可用
（FR11 用 `python kfgj/fr-agent/inject_fr11.py` 注入）；JDK 8（跑 FR Java API 时）。
无设计器时仅知识检索/离线骨架生成可用，开发闭环（探表真执行、无头转 cpt、部署预览）需要设计器在线。

## Agent 工作区用法（推荐场景）

把本仓库目录设为 coding agent（Claude Code / ZCode / Cline 等）的工作区——`AGENTS.md` 就是操作手册（SOP 路由 → 按需加载知识页 → 每步真实执行工具 → 闸门收尾）。

**一次性准备：**

1. **打开设计器**（开发闭环必需）：`FineReport_10.0/bin/designer.bat` 启动后执行
   `python kfgj/fr-agent/inject.py` → `:18999` GUI 事件流（把人的设计器操作翻译成 Java API）、
   `:19000 /exec` 无头脚本执行（Excel 转 cpt、公式引擎验证）。
2. **数据连接**：设计器 `服务器 → 定义数据连接` 建好（如 `demo_dw`），把连接名告诉 Agent。
3. **业务表逻辑**：表名/关键字段/过滤口径（Agent 也会用 `python kfgj/fzpy/db_schema.py <schema.table>` 自己探表）。
4. **项目目录**：产物落点，建议 `%USERPROFILE%\.fr_dev_kit\projects\<项目名>\`（私有产物不入仓库）。

**然后直接下需求：**

- 「用连接 demo_dw，基于 dws_sales.order_detail 做一张明细表，区域下拉筛选，金额合计」
  → **流程 A**：探表 → verify_sql → 骨架选型（60 套 cpt/frm 布局库）→ 参数面板 → DSColumn 绑定 → fr_check → 预览
- 「我这几行示例数据和 Excel 样子，照这个做」
  → **流程 F**：契约 JSON → `gen_skeleton.py` 生成表样 xlsx → `excel2cpt.js` 无头转 cpt（等价设计器"打开Excel→另存为"）→ 数据集替换示例行
- 「这个 cpt 报 #REF!/数据集为空/样式乱」
  → **流程 C**：错误案例库检索 → 定位 → 修复 → 验证

## 六种任务路由

| 任务 | 流程 | 入口 |
|------|------|------|
| 从零创建报表 | A（八步链） | `ckzl/lc/01~06` |
| 示例数据/Excel 样子转 cpt | **F（正向工艺）** | `ckzl/lc/10_Excel骨架正向工艺.md` |
| 修改/格式化已有模板 | B | `kfgj/tygs/`（通配脚本优先） |
| 排查报错 | C | `ckzl/zsk/tbcw/` 错误案例库 |
| 追踪设计器 GUI → Java API | D | `kfgj/fr-agent/` |
| 查 com.fr.* API | E | `ckzl/frapi/doc/` + 零件库 |

## 检索系统（PageIndex 式，无向量）

```bash
python jcxt/js/query_kb.py "Excel 转 cpt" --mode keyword --top 5   # FTS5 关键词
python jcxt/js/query_kb.py --tree ckzl/lc                          # 目录树导航
python jcxt/js/query_kb.py --page lc/10_Excel骨架正向工艺 --full    # 页级精读
python jcxt/js/query_kb.py --view 运维维护                          # 13 个多维视图
python jcxt/js/query_kb.py --hot                                   # 热知识
# 改动 ckzl/ 知识后重建索引（秒级）：
python jcxt/js/build_fts_index.py && python jcxt/js/build_tree_index.py && python jcxt/js/build_views.py
```

## 目录结构

```
ckzl/   参考资料：开发流程(lc)/工作流节点(gzjd)/知识库(zsk)/FR Java 资料(frapi)/规范铁律(gf)/画布骨架(hbfa)
kfgj/   开发工具：辅助脚本(fzpy)/格式化脚本(tygs)/fr-agent/DSL 编译器(dsl)/渲染预览(xlyl)/闸门(guard.py)
jcxt/   检索系统：无向量三件套 + 多维视图
scwj/   输出产物（演示与临时落地；项目产物放 ~/.fr_dev_kit/projects/）
AGENTS.md   ← Agent 的唯一入口，先读它
```

## 铁律与闸门

- `ckzl/gf/铁律速查.md`：A–K 核心档 + L–AH 专项档（合并区先 merge 后样式、改前必备份、2 次修复失败即还原……每条都是踩坑实录）
- `kfgj/EXEC_CONTRACT.md` + `guard.py`：12 条硬闸门
- `ckzl/zsk/tbcw/`：真实错误案例库（复现路径 + 修复验证）

## 交流

QQ 群：**1065801779**（FineReport 报表开发 / Agent 工作区交流，问题反馈与经验交流都在这里）

## License

本项目以 [MIT License](LICENSE) 开源——可自由使用、修改、二次分发（含商用），保留版权声明即可。

> **第三方边界声明**
> - FineReport 设计器/服务器为**帆软商业软件**，需自行向帆软获取授权；本仓库**不包含、不分发**其任何二进制或分发包，所有工具在用户自备的 FineReport 环境上运行。
> - 仓库内 `hbfa/` 骨架、`ckzl/` 知识页均为本项目原创或对公开官方文档的学习性提炼。
> - 运行期第三方 Python 依赖（openpyxl 等）归各自开源协议。
