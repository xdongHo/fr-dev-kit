<!--
KB_INDEX: {
  "title": "Stage 1 · 环境自检 API 与部署治理",
  "stage": "pipeline",
  "tags": [
    "环境",
    "工具链",
    "编译",
    "FR安装"
  ],
  "keywords": [
    "环境自检",
    "FD纪律",
    "外联治理",
    "FSConfig",
    "Passport",
    "集群",
    "共享存储"
  ],
  "summary": "环境自检 API 面、绕开 Workspace 读模板的 FD 纪律、离线/内网外联治理、平台账号与身份认证（FSConfig/Passport）、集群与共享存储"
}
-->

# Stage 1 · 环境自检 API 与部署治理

> 本页为 [01_环境与工具链.md](01_环境与工具链.md) 拆分分篇 4/4（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](01_环境与工具链.md)。

---

## 17. 环境自检 API 面（doc-3475）

FR 自带 OS 探测 API（补在 doc-4510 已收的 `GeneralUtils.getVersion`/`ServerDetector`/`ClusterBridge` 之后，合成完整环境采集清单）：

- `com.fr.stable.os.Utils`（fine-core，4 个 public static）：`readProcess(String[])`/`mapFile(File,String)`/`readFile(File)` 三者 `throws Exception`，`getUname()` 不抛；
- `com.fr.stable.os.OperatingSystem`（**enum**）：`getOperatingSystem()/getOperatingSystem(boolean)/getOperatingSystem(String)/clearCache()/isWindows()/isMacos()/isLinux()/isUnix()`。

三条必写警告：

1. **同名对撞**——`com.fr.stable.OperatingSystem`（无 `.os` 包段）只有 `isWindows/isUnix/isMacOS`、**没有 `isLinux()`**；
2. `getUname()` 失败**返回 null**（exception_table 1 条，handler 只 logger.error，末尾 `aload_0; areturn`）；
3. `getOperatingSystem(boolean)` 有 static cache，首次调用在 Linux 上会 fork `uname -a` + `lsb_release -irc` + 每个 `Distro` 的 `CommandExistsType` 探测，**`clearCache()` 禁止进循环**。

> 来源: 帆软官方帮助 doc-3475

---

## 18. 绕开 Workspace 直接读模板的 FD 纪律（doc-3475）

`new WorkBook().readStream(new FileInputStream(f))`（doc-190 推荐的绕行写法，为避开 `EmptyWorkResource` 退化）**必须包 try-with-resources**。字节码核验：官方两个入口都安全——`TemplateWorkBookIO.readTemplateWorkBook` 的 `WorkResource.openStream` 后有 4 处 `InputStream.close` + 2 处 `Throwable.addSuppressed`（自带 try-with-resources）；`writeTemplateWorkBook` 全程 `ByteArrayOutputStream` → `WorkResource.write(String,byte[])` 不持 FD。**真正会累积 FD 的是手工 `new FileInputStream` / 直调 `SimpleWorkResource#openStream` 的那条绕行路径**——批量生成上千张模板时这是唯一的 FD 增长点。

批量入口另建议加开跑前断言（读 `/proc/self/limits` + `/proc/sys/fs/*`，不 fork）：`nofile ≥ 期望值 && nofile ≤ nr_open && nofile ≤ file-max`。

> 来源: 帆软官方帮助 doc-3475

---

## 19. 离线 / 内网部署下的外联治理（doc-2365）

FR 引擎会主动外联 `cloud.fanruan.com`，入口 `com.fr.general.CloudCenter`（fine-core，extends `com.fr.general.SiteCenter`，`TAG='SiteCenter'`、`TRY_LIMIT=5`，端点 `SITE_SOURCE` 4 个：`https://cloud.fanruan.com/config`、`:8443`、`http://…`、`:8090`）。三层治理按强度排：

1. `Configurations.update(new WorkerAdaptor(CloudCenterConfig.class){...})` + `CloudCenterConfig.getInstance().setOnline(false)`；
2. 注册 `com.fr.stable.fun.SiteTransformer` 插件（`implements Mutable`，3 个 abstract：`match(String)`/`transform()`/`transform(String)`，抽象实现 `com.fr.stable.fun.impl.AbstractSiteTransformer`，jar 内实现者 0 个）改写 URL——命中点在 `acquireByKind` 的 `fetch()` **之前**，是最硬的一层；
3. 出网防火墙。

**三条必须同时写进文档的坑**：

- (a) `CloudCenter$1#compute()` pc0 `iconst_1` 初值 true，只有 `ModuleRole.Config.isRunning()` 或 `ModuleContext.isDesignerStartup()` 才会去读配置 ⇒ **无头脚本两个分支都不进、恒判「已联网」，FineDB 里的 online=false 根本没被读**；
- (b) 同一开关有**三个互不同步的存储**——FineDB Conf（平台读）/ `${java.io.tmpdir}/cloudcenter/cloudcenter.properties`（设计器读，`readOnline()` 缺省 **"true"**，tmpdir 被清理即回落联网）/ 进程内 `ClearableLazyValue`（运行期读），`setOnline(Z)` pc1+pc13 只双写前两个；
- (c) 缓存失效链 `prepare()→listenConfig()→CloudCenterConfig.register(CloudCenter$2)→ValidateProxy…registerListener`，绕过 `Configurations.update` 或 `prepare()` 没跑过都不会 `drop()`。

⇒ **验收断言写 `CloudCenter.getInstance().isDisable()`，不能写 `CloudCenterConfig.isOnline()`**。另附外发字段清单备合规问询：token（`md5Encode(UTC+8 当日 yyyy-MM-dd,"","MD5")`）、os、arch、jdk、client、username/ak（读 `${java.io.tmpdir}/market/passport.properties`）、`?edition=ProductConstants.VERSION`。

> ⚠️ `fetch()` 用的 `NamedThreadFactory("CloudCenter")` 线程**无 setDaemon**——无头 main 触发过就会拖住 JVM 退出（症状「脚本跑完不退出」极难归因）。
> 来源: 帆软官方帮助 doc-2365

---

## 20. 平台账号与身份认证（FSConfig / Passport）（doc-2365）

已字节码实读的链路（FR 10.0.19 / build 2024.03.19）：

1. 配置类 `com.fr.decision.config.FSConfig`（fine-decision-10.0.jar），双槽——遗留全局槽 `getPassport()/setPassport(Passport)`（`<init>` 默认 `new DefaultPassport()`，**非 null**）与现役多源槽 `getPassport(OperationType)/setPassport(OperationType, AbstractPassport)/removePassport(OperationType)/getPassports()`（`ObjectMapConf`，默认空 LinkedHashMap，**无回落到遗留槽的分支**）；
2. 用户源 = `com.fr.decision.authority.base.constant.type.operation.{ManualOperationType,SyncOperationType}.KEY`（GUI「导入、添加的用户」/「同步的用户」）；
3. 三种认证 `com.fr.decision.authorize.impl.{DefaultPassport,LdapPassport,HttpPassport}`，`markType()` = `default/ldap/http`；
4. 写一律包 `Configurations.update(new WorkerAdaptor(FSConfig.class){...})`；
5. **铁律：`removePassport(x)` 与 `setPassport(x, …)` 必须同事务成对**——`CommonAuthenticController#doAuthentication` pc36 `getPassport` → pc54 `checkTicket` 中间无 `ifnull`，缺失即该用户源全员登录 NPE；
6. 验收 = `invalidatePassports()` → `getPassport(src).markType()` **比值**（不是判空——`Passports.buildTarget` 未命中静默 `new DefaultPassport()`）→ 两个 OperationType 都非 null。

> 「成对写入」一条是可直接把生产环境搞成全员无法登录的破坏性操作，属最高优先级铁律。完整证据与复现命令见 `practice/topic_702_java/README.md`。
> 来源: 帆软官方帮助 doc-2365

---

## 21. 集群与共享存储（ClusterService / 状态服务器 / 文件服务器）（doc-1191）

已字节码实读的链路（FR 10.0.19 / build 2024.03.19，证据与复现命令见 `practice/topic_2948_java/README.md`）：

1. 唯一入口 `com.fr.decision.webservice.v10.cluster.ClusterService.getInstance()`（fine-decision-10.0.jar，相关方法全 public、**不吃 HttpServletRequest**）；
2. 固定顺序 **外接库迁移 → `setStatusService(StatusServiceBean)` → `setFileService(FileServiceBean)` → `openCluster()`**——`openCluster` 三道门依次是 `MigrationContext.isAlreadyTransferred()` / `DetectorUtils.build(StateServerConfig.getType()).testConnection()` / `FineFileServer.isOpen()&&validateSavedConfig()`，不过即抛 `DecisionNotTransferredException`/`StatusServiceConnectionException`/`FileServiceConnectionException`；
3. **密码铁律：`config.put("password", TransmissionTool.encrypt(明文))`**——Service 层对非 `"********"` 的值无条件 `TransmissionTool.decrypt` 一次，传明文必然 AUTH 失败；掩码 `"********"` 只在 host+port 与已存配置一致时（`RedisDetector#isConfigurationMatch`）才回落库里密码，否则字面量当密码用；
4. 键名取值域：`StateSeverTypeConstant` = `redis/redis_cluster/standalone`，Redis config 仅 `host/port/password` 三键（缺一即 return false），FTP config = `CommonRepoConfig` 六常量 `protocol/host/port/**username**/password/charset`，`DecCst$Cluster$FileServer` = `FTP/SFTP`（写错静默兜底 FTP）；
5. 验收断言 `ClusterBridge.isClusterMode()` + `StateServerConfig.getType()` **比值** + `RedisConfig` 回读 + `getAllClusterNodes().size()`，**不要用「decision 页面能打开 / 页面上出现节点」**（doc-822 `deployOk` 一次性闩锁）；
6. `closeCluster()` 不对称，只关开关、不关状态/文件服务器。
7. **Redis 实例层(doc-2646)**:集群交付脚本除 `ClusterService.setStatusService` 之外,还需交付状态服务器**本身的 Redis 实例**(集群注册后 FR 只连不建);Redis 实例层交付物 = 实例安装/哨兵或集群拓扑/`requirepass` 密码(与步骤 3 的 `TransmissionTool.encrypt` 值对应)/持久化策略。Redis 集群安装配置属 kit 边界外(见 ckzl/gf/zxzt.md 边界外清单),无头脚本只负责"连上"不负责"搭建"。

> ⚠️ 集群态直接改变 kit 最核心的假设：文件服务器开启后 `WorkResource` 指向 FTP 而非本地磁盘，doc-2804 定下的「跨出抽象层用 `java.io.File` 交叉验证 .cpt 落盘」在集群下会**假阴性**。
> 来源: 帆软官方帮助 doc-1191
