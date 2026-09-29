---
keywords: [定时调度, 排序, 联动, 邮件, 集群, 自定义函数, 移动端, 插件, 皮肤, 画布, 边界外, 理解级, 专项路由, 每天凌晨自动跑, 凌晨, 执行计划, 定时推送, 定时任务, Cron]
---
<!--
KB_INDEX: {
  "title": "任务路由-专项主题",
  "stage": "root",
  "tags": [
    "路由",
    "专项主题",
    "边界外"
  ],
  "keywords": [
    "定时调度",
    "排序",
    "联动",
    "邮件",
    "集群",
    "自定义函数",
    "移动端",
    "插件",
    "皮肤",
    "画布",
    "边界外",
    "理解级",
    "专项路由"
  ],
  "summary": "专项主题路由表+kit边界外主题清单+非核心目录速查（原 AGENTS.md §3 后半+§3.1+§6 非核心行，2026-08-20 v3 拆出）。查专项功能路由或判定主题是否 kit 边界外时读",
  "trigger": "何时用：任务命中定时调度/排序/联动/邮件/集群/插件/皮肤等专项关键词，或需判定主题是否kit边界外",
  "when_not": "何时不用：日常主干开发任务（走AGENTS.md主干路由）时"
}
-->

# 任务路由-专项主题

> **本文从 AGENTS.md v2 §3 后半（专项路由行）+ §3.1（kit 边界外清单）+ §6（非核心目录行）拆出**（2026-08-20 v3 瘦身重构）。
> **何时读**：任务命中下方专项关键词（定时调度/权限/排序/联动/邮件/集群/插件/皮肤/画布等），或需判定主题是否属 kit 边界外（判【理解】级）时。
> 日常开发主干路由见 `AGENTS.md` §3。

---

## 1. 专项主题路由表

| 关键词/任务 | → 读取文件 |
|-------------|-----------|
| **华为云DWS数仓(连接规范/表设计/调优/错误码/版本升级)** | 内容已归档（数仓团队职责，与报表开发无关；原 dwc 知识目录已于 2026-09-29 迁出至用户目录 kit_archive，不再随套件分发） |
| **定时调度(模板/调度配置)** | `ckzl/lc/08_技术选型与调试.md` 调度章节 + doc-2208(四步总纲)→ doc-3315(`${}` 位置铁律)→ doc-3185(运行期排障) |
| **定时调度/计划任务(平台管理/权限；用户目标语: 每天自动跑/跑批/报表自动生成/自动推送/定时发邮件)** | ⚠跨模块依赖，平台侧配置（doc-4158/4159），不可无头生成 |
| **定时调度(邮件通知；用户目标语: 自动发邮箱/发送邮件/报表推送/定时发邮件/smtp/mail 通知/发件人公式)** | ⚠跨模块依赖，平台侧任务配置（doc-684），发件人/收件人/主题/附件不在 .cpt 内；按条件发送邮件给不同用户 doc-5009(param_control_summary)，定时调度支持的公式 doc-3315(formula_summary)；⚠「发件人写公式」具体配置做法库内未证（审计08 A9-017 备案为缺口，待专卡） |
| **定时调度(动态收件人/飞书推送；用户目标语: 按部门推负责人/推送指定人/飞书通知/钉钉通知)** | 收件人动态化见 doc-695(示例二·不同的人不同内容)+doc-4432；飞书通道 11.0.9+ 定时调度通知（doc-1387）+飞书管理插件（doc-4357）；平台侧配置，收件人不在 .cpt 内 |
| **权限(模板内容细粒度)** | `ckzl/lc/03_报表构建.md` 权限节点 + doc-866（可无头生成，落 .cpt XML） |
| **权限(参数驱动)** | doc-865：SQL 内联系统参数 / 条件属性公式，落 .cpt、可无头生成、轻量 |
| **权限(行级数据隔离/plant工厂权限)** | `ckzl/gf/xjqx.md`；三层防护：SQL WHERE 权限子查询 + FormulaCondition 提交条件 + TopVerifier 校验提示；`$fine_username` + auth_base_权限映射表 + config_user_role 两表驱动 |
| **排序(简单静态升降序；用户目标语: 排序乱序/序号乱序/扩展后排序/顺序错乱)** | 数据集 `ORDER BY`（doc-903）；需运行期切方向 → 扩展后排序 `ckzl/lc/03_报表构建.md` 排序小节（doc-2684） |
| **排序(业务顺序/拼音/汉字数字)** | SQL 侧排序列（业务顺序表 / 拼音列 / 汉字数字映射表），见 `ckzl/lc/02_数据建模.md` 排序选型 |
| **联动(单元格↔图表/.cpt)** | `ckzl/lc/03_报表构建.md` 超链小节（联动单元格/悬浮元素，按单元格坐标，doc-3556/4207） |
| **联动(.frm 组件联动)** | `ckzl/lc/07_FRM决策报表.md`（当前决策报表对象，按组件名，doc-2857） |
| **预览方式判定** | `ckzl/lc/06_Web呈现层.md` 预览章节（分页/填报/数据分析三方式，doc-135）；大数据导出按钮锁死分页预览（doc-3342） |
| **移动端交付自检/移动端适配(用户目标语: 移动端填报/手机端适配)** | `ckzl/lc/08_技术选型与调试.md` + Chrome 设备仿真验证 viewlet 链接（doc-4637） |
| **自定义提交按钮** | `ckzl/lc/05_填报与交互.md` §9（doc-596） |
| **下拉树/部门树/树形下拉/TreeComboBoxEditor** | `ckzl/lc/04_参数面板.md` 下拉树小节（自动构建 doc-1042 / 普通分层 doc-1050 / 极速分层 doc-1990） |
| **树数据集/组织树/本ID父ID/二维表转树** | `ckzl/lc/02_数据建模.md` 树数据集小节（doc-126）；与下拉树成对生成（数据侧+消费侧） |
| **控件默认值/下拉树默认全选/JOINARRAY** | `ckzl/lc/04_参数面板.md` 控件默认值配方（doc-1939）；默认选中第 1 项用 `=sql(conn,sql,1,1)`（doc-1862） |
| **填报保留显示值/失焦显示名字不显示 ID** | `ckzl/lc/03_报表构建.md` 单元格形态 CellGUIAttr.setPresent（doc-1026） |
| **下拉框嵌在报表正文单元格里做查询** | `ckzl/lc/04_参数面板.md` 或 `ckzl/lc/05` 单元格控件查询小节（doc-1828） |
| **限制输入长度/maxlength/手机号 11 位** | `ckzl/lc/05_填报与交互.md` 控件输入限长小节（doc-1816）；⚠该方案是输入体验非数据校验，移动端/API/批量导入三条路径绕过 |
| **分组内排序/每分组各自升降序** | `ckzl/lc/03_报表构建.md` 数组状态参数范式 + 排序五选一表（doc-2487） |
| **多列排序/先按 A 再按 B/组内二次排序** | `ckzl/lc/03_报表构建.md` 位权复合键范式（doc-2528）；原生字段且方向固定 → 下沉 SQL |
| **大数据量/百万级明细导出、导出很慢或超时** | `ckzl/lc/06_Web呈现层.md` 三类 Excel 导出选型表（doc-2597/4524）；directExportToExcel 跳过报表计算 |
| **打印（入口/结果/环境三层）** | `ckzl/lc/05_填报与交互.md` 打印按钮（doc-1071）+ `ckzl/lc/08` 打印故障分层表（doc-4508） |
| **决策平台权限/给 N 个用户开权限** | `com.fr.decision.authority.AuthorityContext` 链（doc-773/2199），非改 .cpt；`setUserAuthorityValue/clearUserAuthorityValue/doesUserHaveAuthority` |
| **决策报表(.frm)读写/装配** | `com.fr.form.main.FormIO`（doc-918/4068/645），禁止套 TemplateWorkBookIO |
| **平台配置层/全局生效设置（配色/导出系数/语言）** | 配置侧交付物（fine_conf_entity / Configurations.update），不在 .cpt（doc-2699） |
| **自定义函数/函数管理器** | `com.fr.script.AbstractFunction`（doc-2188/2122），包名必须 `com.fr.function`，服务器+设计器各部署一份 |
| **移动端功能版本轴** | 交付清单必写 App 版本 + HTML5 插件版本下限（doc-3274：App≥10.4.61、HTML5 插件≥10.4.975） |
| **SQL 防注入(覆盖面/配置)** | `ckzl/lc/02_数据建模.md` §8.6（doc-2219）：`EscapeSqlHelper` 只拦 DBTableData 参数，存储过程/内置/文件数据集与 `sql()` 公式不经过；改配置走 `ConfigService#setPSIConfig` |
| **自定义函数(完整链路；用户目标语: 自定义函数注册/函数注册/写好函数类后注册生效)** | `com.fr.script.AbstractFunction`(run(Object[]))+ `com.fr.file.FunctionConfig`/`com.fr.stable.script.FunctionDef` 注册（包 `Configurations.update`）；类简单名必须全大写；注册完先求值才生效，改名须重启（doc-2016/1840/2122） |
| **邮件/消息推送族** | 路由关键词「邮件正文图片 / EmailSendProvider / ExportImageProcessor / EmailPreviewType / bodyImage / CacheConfig.cacheDirectory / actorName」（doc-2547/1086）；actorName 取值：调度侧 {default,page,view,form,write_plus}、Web 侧 {page,view,preview} |
| **设计器启动失败/闪退/FineDB 冲突/tools.jar/jar 不匹配/降级启动** | practice/topic_1342_java/README.md 症状→API 对照表；判断「工程是否降级启动」唯一判据 `DeploymentService.getInstance().getErrorType() != ErrorType.DEFAULT`（doc-1342/1163） |
| **平台运维/决策系统 UI（智能运维/云端运维等）** | 直接判【理解】级，Java API 构建要点写「无(纯理解级内容)」、跳过 practice（doc-2789/1163）；部署/运维/系统配置类（SFTP/集群安装/JVM 内存）同理（doc-3574）；集群路由锚点(用户目标语: 配置集群/集群部署/单机并发不够/7x24/Nginx/Redis/外置库) → 深度内容见 ckzl/lc/fr11_knowledge/deploy-cluster部署集群 与 次级知识 WQ-DEP-0004 |
| **平台账号与身份认证(FSConfig/Passport)** | `ckzl/lc/01_环境与工具链.md` 平台账号小节（doc-702/2365）：`removePassport` 与 `setPassport` 必须同事务成对，缺失即该用户源全员登录 NPE |
| **集群与共享存储(ClusterService)** | `ckzl/lc/01_环境与工具链.md` 集群小节（doc-2948/1191）：`ClusterService.getInstance()` 固定顺序 外接库迁移→setStatusService→setFileService→openCluster；密码必须 `TransmissionTool.encrypt(明文)`；文件服务器开启后 WorkResource 指 FTP、「java.io.File 交叉验证落盘」假阴性 |
| **离线/内网外联治理(CloudCenter)** | `ckzl/lc/01_环境与工具链.md` §19（doc-2205/2365）：`CloudCenterConfig.setOnline(false)` 对无头进程恒不生效（`CloudCenter$1.compute` 无头两个分支都不进）；验收断言写 `CloudCenter.getInstance().isDisable()` |
| **可视化报表/图表/驾驶舱开发** | `ckzl/hbfa/`（60 套骨架:cpt20+frm自适应20+frm绝对20,每套=模板文件+配置 JSON）;开发此类需求**先从此目录选骨架**再填组件;**架构原则:cpt=单元格内嵌图表(可导出图片),frm=网页框IframeEditor组件化(体积小/解耦/单元开发)**;详见其 README |

---

## 1.1 专项七域速答（问句式,检索友好）

### 报表怎么定时自动跑（定时调度/计划任务）？
模板侧调度公式可无头(doc-3315/2208/3185)；平台侧任务与邮件通知不可无头(doc-4158/4159/684)。
落点：ckzl/lc/08 调度章节。

### 表内数据怎么按金额升降序排序（排序）？
方向固定下沉 SQL ORDER BY(doc-903)；运行期切方向才用扩展后排序(doc-2684)。
业务顺序/拼音/汉字数字走 SQL 排序列(doc-3622/3309/3717)。

### 点一行下面明细自动跟着变（联动）怎么做？
.cpt 联动单元格/悬浮元素按坐标(doc-3556/4207)；.frm 当前决策报表对象按 WidgetName(doc-2857)。
跨块刷新必须 getChart().dataRefresh()。

### 报表怎么定时发邮件给领导（邮件/消息推送）？
平台侧定时任务配置(doc-684)，发件人/主题/附件不在 .cpt；词源 EmailSendProvider/doc-2547/1086。
用户目标语：自动发邮箱/报表推送/smtp。

### 报表服务器集群部署注意什么（集群）？
安装运维属边界外；模板侧 ClusterService 固定顺序+TransmissionTool.encrypt(doc-2948/1191)。
深度内容 ckzl/lc/fr11_knowledge/deploy-cluster部署集群。

### 自定义函数怎么注册生效（自定义函数）？
AbstractFunction+com.fr.function+类名全大写(doc-2188/2016)；服务器+设计器双部署。
注册后先求值，改名须重启(doc-2016/1840/2122)。

### 报表在手机上显示不对怎么适配（移动端）？
版本轴 App≥10.4.61/HTML5≥10.4.975(doc-3274)；全屏三链正交(doc-4039)；Chrome 设备仿真验证(doc-4637)。
钉钉/微信集成属边界外(doc-2461/1981)。

## 2. kit 边界外主题清单（平台配置/部署运维/移动端集成,一律【理解】级）

> 2026-08-09 全量学习后收敛:以下主题均为**决策平台侧配置或运维/OS/App 客户端行为**,主体不在 .cpt/.frm XML 内,无头工具链**不可直接生成**——遇到即按【理解】级处理(Java API 要点=「无(纯理解级内容)」,跳过实践),仅登记可编程落点。判定口诀:**先问「功能注册在平台还是模板?」→ 平台 → 查下表**。

| 主题族 | 判定关键词 | 说明与可编程落点 |
|---|---|---|
| **许可/注册(License)** | 注册管理/公有云认证/授权解绑迁移 | 决策平台注册管理功能(doc-2459);可编程落点:license 文件路径 `%FR_HOME%\webroot\WEB-INF\resources\` |
| **插件授权/注册** | 插件购买/license 上传 | 帆软市场商务 + 平台注册管理>版本信息上传(doc-1633) |
| **用户/权限同步** | 同步用户/服务器数据集→FineDB | 平台运行期管理;可编程落点:自定义密码加密类 `com.fr.decision.privilege.encr.*`(继承 AbstractPasswordValidator,doc-704/875) |
| **角色/模板认证** | 模板认证/权限判定 | 服务端功能,权限存 finedb,按部门/角色/用户判定;普通权限与授权权限 10.0.18 解耦(doc-849) |
| **单点登录/认证集成** | CAS/SSO/LDAP/数字签名/登录锁定 | 部署集成 + 平台运行期配置(doc-1433/845/280/849/3510);CAS 的 web.xml filter loginUrl/validateUrl 主机名须与证书一致 |
| **平台日志/使用统计** | 访问统计/模板热度/性能监控/管理日志 | 数据存 LogDB `fine_record_execute` 表,查看/导出均在平台 Web 界面(doc-2224) |
| **平台短信/通知** | 短信平台/消息推送 | 依赖功能点注册(未注册报 11100016「您使用了未注册的功能——短信平台」)(doc-2214) |
| **移动端集成(钉钉/企业微信/微信)** | 钉钉管理/企业微信集成 | 插件配置 + 外部开放平台配置(CorpID/Secret/代理服务器)(doc-2461/1981);「钉钉/微信」关键词默认纯理解级 |
| **App 客户端行为** | 主题模式/越狱检测/登录页/打包证书 | App V10.4.80+ 客户端 UI/安全行为;「移动 App 登录页」是平台 Configuration 而非 .cpt XML(doc-3534/3510/4127/3539) |
| **地图配置** | 地图/图表资源族 | 决策系统管理端 + `WEB-INF\assets` JSON 资源(区域/点边界、GIS 图层),平台侧部署资源不可 .cpt 生成;JSON 命名:名称-area 与名称-point 两种后缀成对落 `assets\map\geographic\<目录>`(doc-2110) |
| **平台主题/外观插件** | 天空主题等 UI 主题插件 | 决策系统 UI 主题插件,管理入口平台侧(doc-3353) |
| **服务器部署运维** | Tomcat 自启/Nginx/Redis/语言包/集群安装 | 纯运维/OS 层(doc-2934/2813/2870/2028/3574);Linux C6 init.d/chkconfig、C7 systemd;Nginx/Redis 集群安装属 kit 边界外 |
| **平台会话层/登录续期** | 刷新登录状态插件 | 平台会话层功能(doc-3641) |

**判「无 API」收敛条件(doc-665)**:平台类文档(主题=数据决策系统/平台配置/部署运维)必须先按 `find <功能名>` 扫 `fine-decision-10.0.jar` 与 `fine-*` 相关 jar 确认无对应类,才能写「无(纯理解级内容)」;扫到类则登记类名+方法(如 `com.fr.decision.privilege.encr.*`)。

**登录页外观配置的 API 落点(doc-3367,平台类但可无头)**:引擎侧 `com.fr.decision.config.AppearanceConfig`(单例 + `Configurations.update(Worker)` 三段式);GUI 设计产物不可无头复现,但 `LoginPageProvider` 扩展点 + 切换 `loginType/loginPageId` 可无头完成;`setLoginImgId(String)` 等附件型 setter 同时写 FineDB 与附件仓库(`AttachUtil.saveAttach(...,"login_bg",...)`),验收补 `AttachmentHelper.hasAttachment("login_bg")`;`LoginAppearanceType` 是 `IntegerType` 枚举。

---

## 3. 非核心目录速查（📦偶尔用，按需读）

| 文件夹/文件 | 角色 | 大模型何时进入 |
|--------|------|--------------|
| `kfgj/tygs/官方文档沉淀工具/` | 官方文档 doc-编号→功能 知识映射表(脚本已归档,知识已并入 fr_rules_doc/export 规则层) | 按 doc 编号反查知识点时(README 有映射表) |
| `ckzl/frapi/ex/` | Java 代码示例 | 需要看 Java 示例时 |
| `ckzl/zsk/frwd/` | 官方资源 | 需要查帆软文档时 |
| `scwj/mb/` | 生成器产出落地 | 生成模板后暂存 |
| `FR_HEADLESS_GUIDE_Ver历史备份/` | 历史版本归档 | 一般不进入 |
| `jcxt/js/` | 章节级语义检索工具（query_kb.py） | 知道主题不知章节时（AGENTS.md §1.7） |
| `ckzl/zsk/gczsk/` | 人机料法环 5M1E 结构化知识库（SQLite:零件 14588/BOM 3589/工艺 12 路线/机 52/料 43/环 11/人 2） | 查 com.fr.* API/装配关系/现成脚本/工艺路线时（AGENTS.md §1.8,`python ckzl/zsk/gczsk/query_kb.py`） |
| `kfgj/env.md` | 开发环境恢复指南 | 换电脑/环境自检/工具缺失时（外部依赖清单+工具清单+恢复流程） |

---

### 排序后序号乱序怎么修？（排序乱序）
常见问法：排序乱序/序号乱序/顺序错乱/扩展后排序 —— 路由见上方「排序(简单静态升降序)」「排序(业务顺序/拼音/汉字数字)」「分组内排序」「多列排序」各行；运行期切方向 `ckzl/lc/03_报表构建.md` 排序小节（doc-2684）；典型症状案例 WQ-CELL-0004

---

### 报表在手机/移动端上怎么适配？（移动端适配）
常见问法：移动端适配/手机端适配/移动端填报/移动端交付自检 —— 路由见上方「移动端交付自检/移动端适配」行（`ckzl/lc/08_技术选型与调试.md` + Chrome 设备仿真，doc-4637）与「移动端功能版本轴」行（App≥10.4.61、HTML5 插件≥10.4.975，doc-3274）；深度内容 `ckzl/lc/fr11_knowledge/mobile移动端`

---

### 自定义函数写好后怎么注册才生效？（自定义函数注册）

---

### 单机并发不够或要求 7x24 时集群怎么配置？（集群配置）
常见问法：集群配置/配置集群/集群部署/单机并发不够/7x24/Nginx/Redis/外置库 —— 平台侧部署运维，判【理解】级路由见上方「平台运维/决策系统 UI」「集群与共享存储(ClusterService)」行（doc-3574/2948）；深度内容 `ckzl/lc/fr11_knowledge/deploy-cluster部署集群` 与 次级知识 WQ-DEP-0004

---

### 报表完成后怎么自动发邮箱给领导？（邮件通知）
常见问法：邮件通知/自动发邮箱/发送邮件/报表推送/定时发邮件/smtp/mail 通知 —— 平台侧定时调度任务配置，路由见上方「定时调度(邮件通知)」行（doc-684），发件人/收件人/主题/附件不在 .cpt 内；报表内邮件分发见 `ckzl/lc/05_填报与交互.md` §12.2（EmailJavaScript，doc-4195）

### 定时调度能按部门只推给部门负责人吗？通知走飞书行不行？
常见问法：动态推送人/按部门推负责人/推送指定人/飞书通知 —— 收件人动态化参考 doc-695（示例二）+doc-4432；飞书通道需 11.0.9+（doc-1387）与飞书管理插件（doc-4357）；"提交时触发一次调度"走开放平台 API，属平台侧边界外（理解级），本 kit 不展开。

---

### 常见问法：怎么设置定时调度/每天自动跑/定时发送报表？（定时调度配置）
常见问法：定时调度/定时任务/怎么设置定时调度/每天自动跑/每天凌晨自动跑/定时发送报表/定时推送/执行计划/调度周期/跑批/计划任务/报表自动生成/自动推送 —— 调度任务定义（基本设置/调度周期/本地文件/文件处理）在决策系统平台侧 GUI 配置，不进 .cpt XML（doc-4158/4159，路由见上方「定时调度/计划任务(平台管理/权限)」行）；无头可落地的模板侧约束与 Java 装配链见 `ckzl/lc/08_技术选型与调试.md` §14（四步总纲 doc-2208 → `${}` 位置铁律 doc-3315 → 运行期排障 doc-3185）：

| 真实问法 | 动作 | 出处 |
|---------|------|------|
| 定时任务执行计划/调度周期怎么配（每天凌晨自动跑）？ | 平台侧 GUI 配置为主；无头生成走 Java 装配链：`ScheduleTask`(setTaskName/setTemplatePath/setTriggerGroup/setUserGroup/setScheduleOutput) + `TriggerGroup#setTriggers` + `CronExpressionTrigger#setCronExpression` 定 Cron 周期，落库 `ScheduleTaskService.getInstance().addTask(用户名,ScheduleTask)`（⚠无单参重载，updateTask 才单参双参都有） | ckzl/lc/08 §14.8（doc-3531） |
| 定时推送的执行条件公式怎么写？ | 调度公式直接引用 .cpt 物理单元格坐标（如 `D5<20000`），受限子集可引用 `${today()}` 等系统函数、不是任意 JS；⚠坐标改版漂移=公式恒 false 静默失效 | ckzl/lc/08 §14.2（doc-688/3315） |
| 定时结果能发到哪些渠道（邮件/短信/挂载/FTP）？ | 六通道对照：邮件 doc-683/684、平台通知 doc-4432、短信（独有 `=$taskname`/`=$time` 公式，与 `${...}` 混写静默失效）doc-2210、客户端 doc-1387、挂载 doc-2209、FTP doc-682；各通道公式语法互不通用 | ckzl/lc/08 §14.4 |
| 附件怎么自动上传到 FTP/SFTP 服务器？ | 默认写 SFTP（V10.0.18+ 官方推荐，端口 22、密钥认证）；FTP 保存路径相对路径优先（`/` 前缀坑仅 FTP 适用）；两者规则不能互用 | ckzl/lc/08 §14.5（doc-682/3573） |
| 挂载名称写 `${today()}` 为什么不生效？ | 挂载名称禁公式（写成 `${...}` 不报错、只当字面量目录名），文件名称才允许公式 | ckzl/lc/08 §14.3（doc-2209/3315） |
| 预览正常、定时任务一跑就报错？ | 模板前置四约束：参数全有默认值/不依赖前端交互控件（`_g()` 调度渲染不可用）/慢 SQL 受 `taskTimeout` 限制/按用户分发需 `$fine_username`（doc-663）；排障入口 doc-3185 | ckzl/lc/08 §14.6 |

---

*本文为 AGENTS.md v3 kernel 的卫星文件；最后更新 2026-08-20（v3 拆分）。*
