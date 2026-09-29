<!--
KB_INDEX: {
  "title": "FR11 安装调研报告（基于离线文档）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "安装", "Linux", "去重收敛", "Windows"],
  "summary": "> 数据源：`D:fr11_docsdoc-view-{did}.html`（FR11 离线文档，gb2312） > 文档数：21 篇（标题含 安装/部署环境/环境准备/系统要求/配置要求） > 生成时间：2026-08-26"
}
-->

# FR11 安装调研报告（基于离线文档）

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，gb2312）
> 文档数：21 篇（标题含 安装/部署环境/环境准备/系统要求/配置要求）
> 生成时间：2026-08-26

---

## 1. 工程部署环境要求（doc-view-4409 原文）

| 类别 | 要求 |
|------|------|
| 操作系统 | Linux：Centos 6.5-6.9 / 7.0-7.4、RedHat 6.5-6.9 / 7.0-7.4、Ubuntu 10.04.4、Amazon Linux 2018.03；Windows Server 2008 / 2012 |
| 网络 | 公网 10M+ 同网段；内网无带宽要求 |
| 内存 | 服务器 16G+；JVM 建议 8G+（不超过 32G，过大会导致 FullGC 时间过长） |
| 磁盘 | 根目录空余 40G+；/usr 15G+（日志默认路径） |
| 数据目录 | .FineReport110 文件夹所在盘需留空余（Windows 在 C:\Users\<用户名>，Linux root 在 /root 下） |
| 容器 | 建议用服务器部署包（内置 Oracle OpenJDK，无需装 Tomcat/JDK）；不支持 OpenLogic OpenJDK |
| 中文 | Linux 部署需确认系统有中文语言包（doc-view-2028） |

## 2. 集群环境要求（doc-view-2642 原文）

- JDK 1.8 且小版本 JDK8u102+；一套集群不支持一台服务器部署多个集群节点工程
- Nginx 作负载均衡：并发需求 <300 可部署在 Windows Server，>300 不建议（Windows Server 上 Nginx 不能支撑较高并发）
- 两节点集群基础方案：Nginx + Tomcat + Redis + FTP；有条件建议三者分服务器部署
- Redis/Nginx 依赖 GCC 编译环境（gcc -v 检查，yum install gcc gcc-c++）；Linux 安装 FTP 需 root
- 通信检测：Linux 用集群环境检测工具或 ping；Windows 用 ping / telnet

## 3. FVS 插件安装要求（doc-view-4188 原文）

- FVS 大屏编辑模式插件：JAR 2021-11-15 起、插件 V1.0.0；11.0.4/V1.3.0 起 jxbrowser 6.23 / 7.22
- 需 FineReport License 注册购买对应功能（doc-view-4222 注2）

## 4. 文档条目（21 篇；其中 12 条已收敛为指针，全文见对应权威收录页）

> 去重收敛（2026-09-29 去重收敛）：与 deploy-cluster 拆分页 / mobile / fvs 完全重复的 12 条条目已指针化；本报告保留 §1-§3 综合结论与 9 条独有/有差异条目原文。

### doc-view-69｜设计器安装
- **doc-view ID**：69
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-69)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-189｜报表安装目录结构
- **doc-view ID**：189
- **核心概念**：11.0.9新增 customLib 文件夹 2）FineReport.Reuse 文件夹迁移至 %FR_HOME%\WEB-INF\local 下 3）border_images 文件夹迁移至 %FR_HOME%\WEB-INF\local 下
- **FR11版本要点**：11.0.9新增 customLib 文件夹；11.0.101）删除 engine、charmapsvg、shadow 文件夹；注：11.0.9 及以后版本新增文件夹

### doc-view-1620｜App下载安装及使用
- **doc-view ID**：1620
- **已收敛指针**：条目全文见 [../mobile移动端/references/01_App客户端.md](../../mobile移动端/references/01_App客户端.md#doc-view-1620)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-2028｜Linux系统安装中文语言包
- **doc-view ID**：2028
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-2028)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-2642｜集群环境准备
- **doc-view ID**：2642
- **核心概念**：已知负载均衡 Nginx 在 Windows Server 上不能支撑较高并发，所以对于使用 Nginx 作为负载均衡的方案，若并发需求低于 300，则在 Linux 系统和 Windows Server 上均能正常部署使用集群，若并发需求超过 300，则不建议在 Windows Server 上部署集群，否则会出现并发问题。 LinuxCentos6  Centos 6.5、Centos 6.6、Centos 6.7、Centos 6.8、Centos 6.9 Centos

### doc-view-2644｜Linux系统安装配置Nginx
- **doc-view ID**：2644
- **已收敛指针**：条目全文见 [01_集群与负载均衡.md](01_集群与负载均衡.md#doc-view-2644)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-2645｜Linux系统安装配置FTP
- **doc-view ID**：2645
- **核心概念**：定时任务完成后，希望把生成的附件上传到其他服务器的 FTP 上面，需要提前准备已配置的 FTP 服务器。 配置开启集群 若选择文件服务器共享，协议选择 FTP 时，需要提前准备已配置的 FTP 服务器。 VSFTP 是一个基于 GPL 发布的类 Unix 系统上使用的 FTP 服务器软件，它的全称是 Very Secure FTP，从名称上可以看出安全性是编写 VSFTP 的初衷，除了这与生俱来的安全特性以外，高速与高稳定性也是 VSFTP 的两个重要特点。

### doc-view-2646｜Linux系统安装配置单机Redis
- **doc-view ID**：2646
- **核心概念**：Redis 是一个开源的底层使用 C 语言编写的 Key-Value 存储数据库。学习视频：Linux系统安装配置Redis Redis 在 Web 集群中用来做状态服务器，主要用于存储缓存登录、模板锁、 SessionID、WebSocket 等，发挥并对所有的访问和操作进行验证的作用。 安装 Redis 时需对源码包编译，此步骤依赖 gcc 编译器，如果没有 gcc 环境，则需要自行安装，联网安装命令 yum install gcc gcc-c++ ，如下所示：

### doc-view-2813｜Windows系统安装配置Nginx
- **doc-view ID**：2813
- **核心概念**：Nginx 作为负载均衡在 Linux 系统上具备很好的并发性能，并且占用极小的内存。但是在 Windows 系统上并不支撑较高并发，所以在 Windows 系统上选用 Nginx 作为负载均衡，需要考虑并发情况。 若并发需求低于 300，部署集群仅以热备为目的，可选用 Nginx 作为负载均衡，若并发需求超过 300，则不建议使用 Nginx，须换用其他负载均衡。 详情见 Nginx 官方说明：http://nginx.org/en/docs/windows.html

### doc-view-2816｜Windows系统安装配置单机Redis
- **doc-view ID**：2816
- **已收敛指针**：条目全文见 [01_集群与负载均衡.md](01_集群与负载均衡.md#doc-view-2816)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-2870｜Linux系统安装配置Redis集群
- **doc-view ID**：2870
- **核心概念**：1）Redis 集群结构：N 个平权主节点（master），每个主节点对应 M 个从节点（slave）。 注：因为投票机制，N 须为奇数。必须要 3 个或以上的主节点，否则在创建集群时会失败，并且当存活的节点数小于总节点数的一半时，整个集群就无法提供服务了。 2）Redis 集群投票机制：服务器之间通过互相的 ping-pong 判断是否节点可以连接上。如果有一半以上的节点去 ping 一个节点的时候没有回应，集群就认为这个节点宕机了。此时该主节点对应的从节点上升为主节点。当

### doc-view-2896｜Windows系统安装配置Traefik
- **doc-view ID**：2896
- **已收敛指针**：条目全文见 [01_集群与负载均衡.md](01_集群与负载均衡.md#doc-view-2896)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-3645｜Linux 系统安装设计器
- **doc-view ID**：3645
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-3645)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-3999｜服务器安装字体
- **doc-view ID**：3999
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-3999)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-4097｜微信钉钉集成环境准备
- **doc-view ID**：4097
- **已收敛指针**：条目全文见 [../mobile移动端/references/02_微信钉钉集成.md](../../mobile移动端/references/02_微信钉钉集成.md#doc-view-4097)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-4188｜FVS插件安装及配置要求
- **doc-view ID**：4188
- **已收敛指针**：条目全文见 [../fvs-dashboard大屏/references/fvs_dashboard_summary.md](../../fvs-dashboard大屏/references/fvs_dashboard_summary.md#doc-view-4188)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-4409｜FineReport工程部署环境准备
- **doc-view ID**：4409
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-4409)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-4532｜部署环境异常
- **doc-view ID**：4532
- **核心概念**：在进行服务器部署时，会出现部署失败的情况，「部署环境异常」属于原因之一，用户可在 部署向导页面 中查看并修复问题。其中，「部署环境异常」这个原因又被分为不同情况，本文将介绍具体报错及解决方案。报错页面如下图所示： 注1：这里以 Tomcat 为例进行演示，其他容器同样为拷贝到对应的容器的 lib 下。 注2：%JAVA_HOME%/jdk/lib 下的 tools.jar 为部署服务器本地 JAVA_HOME 里面的文件，不是开发计算机本地。

### doc-view-4812｜第三方插件安装失败说明
- **doc-view ID**：4812
- **已收敛指针**：条目全文见 [02_服务器部署与安装.md](02_服务器部署与安装.md#doc-view-4812)（权威收录页）；本报告不再重复原文（2026-09-29 去重收敛）。

### doc-view-4840｜数据门户插件安装说明
- **doc-view ID**：4840
- **核心概念**：数据门户插件功能变更 数据门户是帆软软件推出的统一数据查询入口的功能。 本文将简单介绍插件的安装和使用方法。
- **FR11版本要点**：11.0.7V1.0-；11.0.8V1.1-；11.0.8V1.6新增内置门户demo

### doc-view-4914｜设计器安装常见问题
- **doc-view ID**：4914
- **核心概念**：本文主要概述设计器安装时常见的问题及解决方案。 问题描述：**在 windows8 或 windows10 系统下，安装 FineReport 软件可能会提示有风险，阻止安装该软件，弹窗提示：这种类型的文件可能会危害你的计算机原因分析：**SmartScreen 筛选器是 Internet Explorer 中的一种帮助检测仿冒网站的功能，SmartScreen 筛选器还可以帮助阻止安装恶意软件。安装 FineReport 出现上面这个提示是因为系统将其误认为是恶意软件或者破

## 5. 常见安装问题入口

- doc-view-4532 部署环境异常、doc-view-4914 设计器安装常见问题、doc-view-4812 第三方插件安装失败说明、doc-view-4840 数据门户插件安装说明