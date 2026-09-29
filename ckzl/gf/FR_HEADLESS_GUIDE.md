<!--
KB_INDEX: {
    "title": "FR Headless 模板开发指南 — 主路由",
    "stage": "root",
    "tags": [
      "主路由",
      "铁律",
      "任务路由表",
      "流水线全景"
    ],
    "keywords": [
      "铁律A-AD",
      "任务路由表",
      "水印式布局",
      "一键格式化",
      "DeleteConfig",
      "级联SQL"
    ],
    "summary": "FR 模板开发知识库总入口：全局铁律 A-AH（A-K 核心 + L-AH 专项）+ 任务路由表 + 流水线全景；收尾强制项见 kfgj/EXEC_CONTRACT.md"
  }
-->

# FR Headless 模板开发指南 — 主路由

> FineReport 10.0 模板开发知识库总入口。
>
> **本文档是路由器，不是百科全书。** 只包含全局铁律和任务分发逻辑。
> 具体细节按需进入对应文件夹的 README 阅读——**避免阅读无关文档，聚焦当前任务。**
>
> 🔒 **v2 执行契约**：本文铁律是「知识层」（写什么、怎么写）；任务收尾的「动作层」强制项
> （备份/XML校验/fr_check/SQL闭环/公式验证/快照/断链等 12 条闸门）由 `kfgj/guard.py` 机器执行，
> 见 [kfgj/EXEC_CONTRACT.md](kfgj/EXEC_CONTRACT.md)。**铁律告诉你该怎么写，契约保证你该做的都做了。**

---

## 如何使用本指南

```
你要做什么？
    │
    ├─ 从零创建模板 ──────────→ 查「任务路由表」第 1-6 行，按流水线顺序读对应分支
    ├─ 修改/格式化已有模板 ────→ 查「任务路由表」第 7-8 行
    ├─ 追踪 GUI 操作到 API ───→ 读 fr-agent/README.md
    ├─ 排查报错 ──────────────→ 查「任务路由表」第 9 行
    └─ 查 API 包名/方法签名 ───→ 读 ckzl/frapi/doc/README.md
```

---

## 任务路由表

> 根据当前任务，只读必要的分支。每行的「→ 进入」指向该分支的 README。

| # | 任务 | 流水线阶段 | → 进入哪个分支 README |
|---|------|-----------|---------------------|
| 1 | 理解需求、确定报表类型(查看/填报/导入) | 需求分析 | [ckzl/zsk/xqfx/README.md](ckzl/zsk/xqfx/README.md) |
| 2 | 设计数据集 SQL、字段映射、级联参数 | 数据建模 | [ckzl/lc/02_数据建模.md](ckzl/lc/02_数据建模.md) |
| 3 | 构建报表单元格、样式、行高 | 报表构建 | [ckzl/lc/03_报表构建.md](ckzl/lc/03_报表构建.md) |
| 4 | 参数面板控件、布局、级联 | 参数面板 | [ckzl/lc/04_参数面板.md](ckzl/lc/04_参数面板.md) |
| 5 | 填报提交、JS 交互、工具栏 | 填报与交互 | [ckzl/lc/05_填报与交互.md](ckzl/lc/05_填报与交互.md) |
| 6 | CSS 注入、Web 属性配置 | Web 呈现 | [ckzl/lc/06_Web呈现层.md](ckzl/lc/06_Web呈现层.md) |
| 7 | 批量格式化(字体/布局/行高/SQL美化)、**参数面板一键格式化** | 后处理 | [kfgj/tygs/索引目录.md](kfgj/tygs/索引目录.md) |
| 8 | FRM 决策报表/驾驶舱 | 特殊模板 | [ckzl/lc/07_FRM决策报表.md](ckzl/lc/07_FRM决策报表.md) |
| 9 | 排查报错、调试、技术选型 | 验证 | [ckzl/lc/08_技术选型与调试.md](ckzl/lc/08_技术选型与调试.md) + [ckzl/zsk/tbcw/README.md](ckzl/zsk/tbcw/README.md) |
| 10 | 追踪 Designer GUI 操作→Java API | 调试辅助 | [fr-agent/README.md](fr-agent/README.md) |
| 11 | 查 FR Java 类/方法签名 | API 参考 | [ckzl/frapi/doc/README.md](FR%20JAVA%20核心API文档/README.md) |
| 12 | 查帆软官方文档/社区/SDK | 外部资源 | [ckzl/zsk/frwd/资源索引.md](ckzl/zsk/frwd/资源索引.md) |
| 13 | 数据分析、字段映射、SQL 设计 | 数据分析 | [ckzl/zsk/sjfx/README.md](ckzl/zsk/sjfx/README.md) |
| 14 | 模板测试、浏览器预览验证 | 测试 | [ckzl/zsk/csff/README.md](ckzl/zsk/csff/README.md) |

---
## 全局铁律（所有任务通用，必须遵守）

> 铁律正文已拆分至 **[铁律速查.md](铁律速查.md)**（A-K 核心档 + L-AH 专项档，2026-09-29 拆分：本文件回归纯路由，执行任何任务前先读铁律速查）。

| 档 | 节 | 主题 |
|---|---|---|
| A **核心档** | [A. 文件操作安全](铁律速查.md#A-文件操作安全) |  |
| B **核心档** | [B. DSColumn 默认配置](铁律速查.md#B-DSColumn%20默认配置) |  |
| C **核心档** | [C. 字体与样式](铁律速查.md#C-字体与样式) |  |
| D **核心档** | [D. 级联参数 SQL](铁律速查.md#D-级联参数%20SQL) |  |
| E **核心档** | [E. 填报提交](铁律速查.md#E-填报提交) |  |
| F **核心档** | [F. 参数面板布局](铁律速查.md#F-参数面板布局) |  |
| G **核心档** | [G. 按钮控件](铁律速查.md#G-按钮控件) |  |
| H **核心档** | [H. 脚本与编码](铁律速查.md#H-脚本与编码) |  |
| I **核心档** | [I. CSS 注入](铁律速查.md#I-CSS%20注入) |  |
| J **核心档** | [J. 参数 XML 格式](铁律速查.md#J-参数%20XML%20格式) |  |
| K **核心档** | [K. FR Java API 能力（2026-08-07 实测更新）](铁律速查.md#K-FR%20Java%20API%20能力（2026-08-07%20实测更新）) |  |
| L | [L. 排序与父子格（扩展）](铁律速查.md#L-排序与父子格（扩展）) |  |
| M | [M. 移动端与引擎互斥](铁律速查.md#M-移动端与引擎互斥) |  |
| N | [N. 联动与图表 JS](铁律速查.md#N-联动与图表%20JS) |  |
| O | [O. 按钮与工具栏](铁律速查.md#O-按钮与工具栏) |  |
| P | [P. 定时调度生成](铁律速查.md#P-定时调度生成) |  |
| Q | [Q. 权限](铁律速查.md#Q-权限) |  |
| R | [R. XML 生成卫生](铁律速查.md#R-XML%20生成卫生) |  |
| S | [S. 引擎与格式边界](铁律速查.md#S-引擎与格式边界) |  |
| T | [T. 数据连接与 HTML](铁律速查.md#T-数据连接与%20HTML) |  |
| U | [U. JS 生成卫生（前端交互 JS）](铁律速查.md#U-JS%20生成卫生（前端交互%20JS）) |  |
| V | [V. 日期与公式](铁律速查.md#V-日期与公式) |  |
| W | [W. 配置层与平台类](铁律速查.md#W-配置层与平台类) |  |
| X | [X. 导出与产物边界](铁律速查.md#X-导出与产物边界) |  |
| Y | [Y. 读文档元规则](铁律速查.md#Y-读文档元规则) |  |
| Z | [Z. 控件与事件](铁律速查.md#Z-控件与事件) |  |
| AA | [AA. 工作目录与可写性（2026-08-09 新增）](铁律速查.md#AA-工作目录与可写性（2026-08-09%20新增）) |  |
| AB | [AB. 字面量清单与编码形态（2026-08-09 新增）](铁律速查.md#AB-字面量清单与编码形态（2026-08-09%20新增）) |  |
| AC | [AC. JS 生成与服务端渲染（2026-08-09 新增）](铁律速查.md#AC-JS%20生成与服务端渲染（2026-08-09%20新增）) |  |
| AD | [AD. 配置存类全名与插件边界（2026-08-09 新增）](铁律速查.md#AD-配置存类全名与插件边界（2026-08-09%20新增）) |  |
| AE | [AE. 复现强制（2026-09-06 新增，R65 情报 A4）](铁律速查.md#AE-复现强制（2026-09-06%20新增，R65%20情报%20A4）) |  |
| AF | [AF. 字节对成对同步（2026-09-15 新增，夜间批次 波实测）](铁律速查.md#AF-字节对成对同步（2026-09-15%20新增，夜间批次%20波实测）) |  |
| AG | [AG. 执行棒三件套（2026-09-15 新增，夜间批次 波多棒实证）](铁律速查.md#AG-执行棒三件套（2026-09-15%20新增，夜间批次%20波多棒实证）) |  |
| AH | [AH. rebuild≠live（2026-09-15 新增，夜间批次/A21 实证）](铁律速查.md#AH-rebuild≠live（2026-09-15%20新增，夜间批次/A21%20实证）) |  |

> 两档口径与来源说明见铁律速查.md 卷首。

## 流水线全景图

```
需求分析 ──→ 数据建模 ──→ 报表构建 ──→ 参数面板 ──→ 填报与交互 ──→ Web呈现 ──→ 验证测试
    │            │            │            │            │            │            │
    ▼            ▼            ▼            ▼            ▼            ▼            ▼
需求分析        pipeline     pipeline     pipeline     pipeline     pipeline     ckzl/zsk/csff
方法/          02 数据建模  03 报表构建  04 参数面板  05 填报交互  06 Web呈现   /README.md
README.md                                                              +通用格式化
                                                                       脚本(后处理)
```

### 各阶段分支入口

| 阶段 | 主指导 | 辅助/工具 | 错误参考 |
|------|--------|----------|---------|
| 需求分析 | [ckzl/zsk/xqfx/README.md](ckzl/zsk/xqfx/README.md) | — | — |
| 数据建模 | [ckzl/lc/02_数据建模.md](ckzl/lc/02_数据建模.md) | [ckzl/zsk/sjfx/README.md](ckzl/zsk/sjfx/README.md) | [ckzl/zsk/tbcw/README.md](ckzl/zsk/tbcw/README.md) |
| 报表构建 | [ckzl/lc/03_报表构建.md](ckzl/lc/03_报表构建.md) | [ckzl/frapi/doc/README.md](FR%20JAVA%20核心API文档/README.md) | 同上 |
| 参数面板 | [ckzl/lc/04_参数面板.md](ckzl/lc/04_参数面板.md) | [kfgj/tygs/索引目录.md](kfgj/tygs/索引目录.md) | 同上 |
| 填报与交互 | [ckzl/lc/05_填报与交互.md](ckzl/lc/05_填报与交互.md) | — | 同上 |
| Web呈现 | [ckzl/lc/06_Web呈现层.md](ckzl/lc/06_Web呈现层.md) | — | 同上 |
| FRM决策报表 | [ckzl/lc/07_FRM决策报表.md](ckzl/lc/07_FRM决策报表.md) | — | 同上 |
| 后处理(格式化) | [kfgj/tygs/索引目录.md](kfgj/tygs/索引目录.md) | [kfgj/fzpy/README.md](kfgj/fzpy/README.md) | — |
| 验证测试 | [ckzl/zsk/csff/README.md](ckzl/zsk/csff/README.md) | [ckzl/lc/08_技术选型与调试.md](ckzl/lc/08_技术选型与调试.md) | [ckzl/zsk/tbcw/README.md](ckzl/zsk/tbcw/README.md) |
| GUI追踪 | [fr-agent/README.md](fr-agent/README.md) | — | — |

---

## 文件夹总览

| 文件夹 | 角色 | README |
|--------|------|--------|
| **ckzl/lc/** | 流水线知识（9 阶段拆分指南） | [README.md](ckzl/lc/README.md) |
| **kfgj/tygs/** | 批量格式化工具(CPT/FRM) | [索引目录.md](kfgj/tygs/索引目录.md) |
| **kfgj/fzpy/** | 一次性工具脚本(除零/级联/CSS等) | [README.md](kfgj/fzpy/README.md) |
| **fr-agent/** | GUI 操作追踪 Agent | [README.md](fr-agent/README.md) |
| **ckzl/frapi/ex/** | Java API 示例代码 | [README.md](FR%20JAVA%20API%20示例/README.md) |
| **ckzl/frapi/doc/** | javap 验证的 API 签名 | [README.md](FR%20JAVA%20核心API文档/README.md) |
| **ckzl/zsk/tbcw/** | 错误案例与归档 | [README.md](ckzl/zsk/tbcw/README.md) |
| **ckzl/zsk/csff/** | 模板验证方法论 | [README.md](ckzl/zsk/csff/README.md) |
| **ckzl/zsk/sjfx/** | 字段映射/SQL 设计 | [README.md](ckzl/zsk/sjfx/README.md) |
| **ckzl/zsk/xqfx/** | 需求→开发规格转化 | [README.md](ckzl/zsk/xqfx/README.md) |
| **ckzl/zsk/frwd/** | 官方资源入口+凭据 | [资源索引.md](ckzl/zsk/frwd/资源索引.md) |
| **scwj/mb/** | 生成器产出落地目录 | [README.md](scwj/mb/README.md) |
| **FR_HEADLESS_GUIDE_Ver历史备份/** | 历史版本归档 | — |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| Ver0.1–Ver0.6 | 2026-07 ~ 2026-08 | 逐步积累的完整知识库（1238行单文件） |
| **Ver1.0** | **2026-08-04** | **重构为三级路由体系：主路由器 + 分支README + 细节文件；流水线9阶段拆分** |
| **Ver1.1** | **2026-08-05** | ①F段新增「水印无 Label」默认方案 + 一键格式化脚本入口/踩坑/适用边界；②新增坐标级安全格式化 `fmt_panel_safe.py`（推荐）；③FR Java API 格式化器（需 web 会话）；④知识库整理：归档 fr-agent 开发期脚本、修伪目录 README、补 KB_INDEX、统一 stage |
| **Ver1.2** | **2026-08-08** | 新增全局铁律 U–Z：U JS 生成卫生 / V 日期与公式 / W 配置层与平台类 / X 导出与产物边界 / Y 读文档元规则 / Z 控件与事件（来源：帆软官方帮助 doc-1108/2369/2487/4068/3531/2699/2336/567/4508/3713/2238/1816/1985/1213 等 2026-08-07~08 夜间学习） |
| **Ver1.3** | **2026-08-09** | 新增全局铁律 AA–AD：AA 工作目录与可写性 / AB 字面量清单与编码形态（int 九形态+getter 三态+FU 换算表）/ AC JS 生成与服务端渲染 / AD 配置存类全名与插件边界（来源：帆软官方帮助 doc-1342/2804/195/1953/576/4039/4063/1191/810/4086/3475/1086/2637/2219 等 2026-08-09 夜间学习） |

---

## 问法入口（命中率作战 DIGE3 2026-09-12）

> 问：LicenseContext ClassNotFound / ClassNotFoundException: com.fr.license.selector.LicenseContext 报错要处理吗？
> → **不用，可忽略**。独立 JVM（非 Designer 注入）跑 FR Java 时 License/环境不可用，export 报此错属许可校验缺席噪声，文件正常生成（铁律 K「独立 Java（非注入）」行）。
> 详见 ckzl/lc/01_环境与工具链.md §0.2、ckzl/zsk/tbcw/README.md 错误索引。
> 与「独立 JVM 报错可忽略」不是同一问——本文件才是该报错处置口径的载体。
