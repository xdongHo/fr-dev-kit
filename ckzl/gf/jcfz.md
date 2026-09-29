---
keywords: [排序, 打印, 权限, 图表, 定时调度, 联动, 公式, 扩展图表]
---
<!--
KB_INDEX: {
  "title": "任务决策树-扩展分支(官方文档沉淀)",
  "stage": "root",
  "tags": [
    "非核心",
    "决策树",
    "官方文档沉淀"
  ],
  "keywords": [
    "排序",
    "打印",
    "权限",
    "图表",
    "定时调度",
    "联动",
    "公式",
    "扩展图表"
  ],
  "summary": "从 AGENTS.md §2 拆出的官方文档持续学习沉淀的决策分支:排序/打印/权限/图表/定时调度/联动/公式/扩展图表等。日常开发按需查对应分支。",
  "trigger": "何时用：排序/打印/权限/图表/定时调度/联动/公式/扩展图表等细分场景决策",
  "when_not": "何时不用：主干任务（从零创建/修改/排查/查API）走AGENTS.md §2时"
}
-->

# 任务决策树 — 扩展分支（官方文档沉淀 · 按需读取）

> 本文是从 `AGENTS.md` §2 拆出的「2026-08 官方文档持续学习沉淀」决策分支。
> 主干决策树（从零创建/修改/排查/追踪/查API）仍在 AGENTS.md §2；遇到排序/打印/权限/图表/定时调度等细分场景时来查本文对应分支。

## 模板侧四域直答

### 数据排序怎么选型（排序）？
方向固定简单排序 → 数据集 ORDER BY(doc-903)；运行期切方向且允许重查库 → 扩展后排序(ckzl/lc/03 排序小节,doc-2684)。
业务顺序表/拼音/汉字数字 → SQL 侧排序列(映射表,doc-3622/3309/3717)；图表排序 → 能 SQL 排序就不用 sortChart(doc-2332)。

### 报表怎么直接打印（打印）？
生成打印入口(按钮+JS) → doc-1071 的 Button+Listener+JavaScriptImpl 三件套(Java API 路径)。
打印结果不对(截断/重叠/错页) → 先判根因层(纸张/字体/环境),模板侧只能预防(doc-4508)。
打印起不来(软件/端口/浏览器/跨域) → 无 .cpt 落点,直接给环境结论。

### 点一行另一块跟着变（联动）先判什么？
先判模板类型: .cpt 用「联动单元格/悬浮元素」(按单元格坐标); .frm 用「当前决策报表对象」(按 WidgetName)。
再判驱动源: 图表轮播(仅扩展图表+粒子计数器走刷新联动) vs 用户点击(超链)(doc-3556/2857)。
图表↔报表块跨块刷新 → 必须 getChart().dataRefresh() 显式触发(铁律 N)。

### 定时调度需求怎么分族（定时调度）？
先分族再动手(用户目标语: 每天自动跑/跑批/计划任务/报表自动生成/定时发邮件)。
调度公式/参数配置(doc-3315,模板+调度配置,可无头落地)；四步配置总纲/前置校验(doc-2208)；运行期排障(doc-3185)。
管理/授权权限(doc-4158/4159,平台侧 GUI,不可生成) —— agent 不应产出权限管理 XML。

**2026-08 增补分支（官方文档持续学习沉淀）**：

```
├─ 需求含「点 A 刷新 B」(联动)
│   ├─ 单元格→图表(.cpt) → ckzl/lc/03 超链小节(联动单元格/悬浮元素,按坐标,doc-3556/4207)
│   ├─ 组件→组件(.frm)   → ckzl/lc/07_FRM决策报表.md(doc-2857)
│   └─ 图表↔报表块跨块刷新 → 必须 getChart().dataRefresh() 显式触发(铁律 N)
│
├─ 需求含「排序」
│   ├─ 方向固定简单排序 → 数据集 ORDER BY(doc-903)
│   ├─ 运行期切方向且允许重查库 → 扩展后排序(ckzl/lc/03 排序小节,doc-2684)
│   ├─ 业务顺序表/拼音/汉字数字 → SQL 侧排序列(映射表,doc-3622/3309/3717)
│   └─ 图表排序 → 能 SQL 排序就不用 sortChart(doc-2332)
│
├─ 需求含「预览/导出按钮/工具栏」
│   ├─ 先定预览方式: 分页预览(默认)/填报预览/数据分析(doc-135)
│   └─ 用 direct/export 大数据导出按钮 → 预览方式锁死分页预览(doc-3342)
│
└─ 需求含「图表样式微调」
    ├─ 先判能否 SQL 侧解决(排序/过滤)
```

**2026-08-08 增补分支（官方文档持续学习沉淀）**：

```
├─ 需求含「排序」补充分支（排序方案五选一/八选一判据）
│   ├─ 每分组独立状态/点某组不影响其它组 → 扩展后排序+数组状态参数(SPLIT/REMOVEARRAY/ADD2ARRAY/JOINARRAY,doc-2487)
│   ├─ 多列先后排序(ORDER BY A,B 模板等价) → 位权复合键(doc-2528);排序列全为原生字段且方向固定 → 一律下沉 SQL
│   ├─ 业务枚举顺序(华东华北…) → SQL 字典表 JOIN / 内置数据集顺序表+inarray(doc-3622);项≤5 才用公式内枚举
│   ├─ 拼音排序 → SQL 侧拼音列(MySQL CONVERT gbk/拼音字典/pypinyin 维表);必须运行期切方向才用 StringPinyin(插件依赖,doc-3309)
│   ├─ 汉字数字/罗马数字 → 数值 seq 列 + NUMTO 渲染(排序键与显示形态分离,首选,doc-3717)
│   └─ 图表排序 → 能 SQL 排序就不用 sortChart;交互属性工具栏勾「排序」优先于 JS(doc-1695)
│
├─ 需求含「打印」
│   ├─ 生成打印入口(按钮+JS) → doc-1071 的 Button+Listener+JavaScriptImpl 三件套(Java API 路径)
│   ├─ 打印结果不对(截断/重叠/错页) → 先判根因层(纸张/字体/环境),模板侧只能预防(doc-4508)
│   └─ 打印起不来(软件/端口/浏览器/跨域) → 无 .cpt 落点,直接给环境结论
│
├─ 需求含「图表特效/条件显示」
│   └─ 前端渲染特效(闪烁动画) → Java API 仅到「条件显示容器」(ConditionCollection/ConditionAttr),特效本身无 com.fr.* 类,禁止虚构 API(doc-1701)
│
├─ 数据源未就绪也要敢构建
│   └─ 数据源类型差异全部收敛在 <TableData> 节点,消费侧与数据源类型无关 → 先用 EmbeddedTableData 跑通模板结构,后期替换真实数据源(doc-1938/1985)
│
├─ 需求属「平台运行期能力」(定时调度任务/目录权限/平台管理)
│   └─ 直接回答「Java 侧交付 .cpt,调度/权限走决策系统 Web 控制台」,不再逐篇论证;模板含 $fine_username 过滤时须注明「按默认用户组单独生成结果」开关属平台侧(doc-663/4149/697)
│
├─ 需求含「决策报表/表单/组件」→ .frm 链路
│   └─ 读写走 com.fr.form.main.FormIO(readForm/writeForm(IOFile,String)),禁止套 TemplateWorkBookIO;body 加控件走 form.getContainer().addWidget + CRBoundsWidget 包壳(doc-918/645)
│
└─ 需求含「数据连接/账号密码」→ Java API 可构建
    └─ JDBCDatabaseConnection(driver,url,user,password) + testConnection + Configurations.update(ConnectionConfig.addConnectionWithoutCheck) 注册;必须显式 setDriver(默认值是已移除的 ODBC 桥)(doc-2406/2699)
```

**2026-08-09 增补分支（官方文档持续学习沉淀）**：

```
├─ 需求含「联动/组件 A 变化带动 B」
│   ├─ 先判模板类型: .cpt 用「联动单元格/悬浮元素」(按单元格坐标); .frm 用「当前决策报表对象」(按 WidgetName)
│   └─ 再判驱动源: 图表轮播(仅扩展图表+粒子计数器走刷新联动) vs 用户点击(超链)(doc-3556/2857)
│
├─ 需求含「排序」追加判据(第 5/6/7/8 条支路；用户目标语: 排序乱序/序号乱序/扩展后排序/顺序错乱)
│   ├─ 按被点击列排序(十字交叉表) → 扩展后排序 + EVAL 绝对层次坐标 `B2[;B1:$index]`(doc-1782)
│   ├─ 排序键是业务顺序表 → 内置数据集顺序表 + inarray(带 =0 未命中兜底 9999)(doc-3622)
│   ├─ 分类维度按拼音排 → 优先 SQL 侧拼音列;必须运行期切方向才用 StringPinyin(常用函数集合插件依赖)(doc-3309)
│   └─ 汉字数字/罗马数字/自定义编码 → 数值 seq 列 ORDER BY + NUMTO 渲染(排序键与显示形态分离,首选);跳号数据禁止照抄官方公式(doc-3717)
│
├─ 需求含「定时调度」—— 先分族再动手(用户目标语: 每天自动跑/跑批/计划任务/报表自动生成/定时发邮件)
│   ├─ 调度公式/参数配置(doc-3315,模板+调度配置,可无头落地)
│   ├─ 四步配置总纲/前置校验(doc-2208);运行期排障(doc-3185)
│   └─ 管理/授权权限(doc-4158/4159,平台侧 GUI,不可生成) —— agent 不应产出权限管理 XML
│
├─ 需求属「权限」—— 四分法
│   ├─ 参数驱动(doc-865,SQL 内联系统参数/条件属性公式,轻量,可无头)
│   ├─ 声明式角色可见性(doc-866,PrivilegeControl 锚点,较重,可无头)
│   ├─ 行级数据权限(plant/工厂数据隔离,实战验证,可无头) —— 见下方「行级数据权限模式」专节
│   └─ 平台权限表(doc-4158/4159,不可生成);先有目录「查看」权限,模板内细粒度才有意义;优先参数驱动,跨列/隐藏整行列用 866,可叠加
│
├─ 需求含「隔行变色」
│   ├─ 纯隔行 → row()%2 即可
│   └─ 隐藏行后隔行 → SEQ()+隐藏标志复合条件公式(方案一),禁 row()%2 与前端 JS 方案(doc-2365)
│
├─ 需求含「扩展图表」(三维地球/流向地图/轮播联动/轮播条形图/弧形柱形图)
│   ├─ 装配侧(建图/绑数据集/绑字段/刷新开关/超链组/落单元格) → 有完整引擎侧 API: com.fr.chart.charttypes.ChartTypeManager + com.fr.extended.chart.*(49 类在 fine-report-engine,不需要装插件即可编译链接)(doc-2664/3135)
│   ├─ 样式侧(颜色风格/渐变/内径占比/值轴最大/背景不透明) → 插件私有子类,引擎零 setter,走「设计器存模板→读回改→写回」diff 路径;判据: com.fr.extended.chart.* 里没有的 setter 就是插件私有
│   └─ 轮播条形图等「伪装成核心图表的扩展图表」→ 显式隔离,禁止丢进核心图表生成器(不支持条件属性/自定义标签样式)(doc-3836)
│
├─ 需求含「图表样式微调」→ 统一归类「设计期样式 XML」走样式预设层生成,不要手点设计器(doc-4138)
│
├─ 需求含「破坏性运维类 API」(更新 jar/回滚/删备份/建用户 CLEAR/重置密码)
│   ├─ UpdateService#updateJar/rollback/deleteBackup、UpdateExecutor#execute、ModuleBackupProvider#rollback —— blast radius 是整个工程 jar 与备份链,失败信号极弱(两层吞异常+异步返回)
│   ├─ SystemConfig#setServerInitStatus(非"success")、UserService#importUsers(CLEAR)、resetUserPasswordEncryption —— 后果不可逆且零提示
│   └─ 一律【必须人工确认,禁止脚本自动调用】(doc-1163)
│
├─ 需求含「远程工作目录/远程设计」→ 确定性能力边界: 无头不可用
│   └─ 运行时 jar 里 Workspace 只有 4 个本地实现(isLocal 恒 true),远程实现在设计器 jar;唯一可用 API 是 FineWorkspaceConnector.testConnection(连通性判定);改远端工程须先同步/挂载到本地再 checkIn;无头批改不参与远程设计模板锁(doc-195/2365)
│
├─ 需求属「平台管理类」(LDAP 认证/用户同步/角色权限/部门职务) → 路由到「平台运维/Web 控制台」
│   └─ 属 com.fr.decision.* 平台体系,不在无头报表构建范围;除非是报表里读取同步用户数据(那是数据集 SQL 的事)(doc-4343/2365)
│
├─ 需求含「全屏」→ 同名词消歧,三链正交不可合并
│   ├─ 模板块级开关 ElementCaseMobileAttr#setAllowFullScreen(默认 false)/ChartMobileAttr(默认 true) → .cpt
│   ├─ 图表工具栏 VanChartTools#setFullScreen → ChartCollection
│   └─ 平台级按钮样式 FullScreenButtonConfig → FineDB 无 XML(doc-4039)
│
└─ 需求含「公式/函数」→ 公式回归的最轻路径(单测用)
    └─ com.fr.script.Calculator.createCalculator().evalValue("<公式串>") 即可求值,无需 WorkBook/Workspace;断言先判 com.fr.stable.Primitive 三态(NULL/ERROR_VALUE/ERROR_NAME),!=null 恒真(doc-810/1191)
```

### 排序后序号乱序/顺序错乱怎么修？（排序乱序）
常见问法：排序乱序/序号乱序/顺序错乱/扩展后排序/升序降序 —— 判据即上方三组「需求含排序」分支（方向固定→ORDER BY doc-903；运行期切向→扩展后排序 doc-2684；分组/多列/拼音/汉字数字→doc-2487/2528/3309/3717）；典型症状案例 次级知识 WQ-CELL-0004
