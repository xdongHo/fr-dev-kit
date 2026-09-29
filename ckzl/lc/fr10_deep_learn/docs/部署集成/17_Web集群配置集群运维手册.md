<!--
KB_INDEX: {
  "title": "部署集成 - Web集群配置集群运维手册",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "部署集成",
    "集群运维手册",
    "Web 集群配置"
  ],
  "summary": "「部署集成」分页：集群运维手册（约 13 篇条目）；FR10 帮助文档「部署集成」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 部署集成 · Web集群配置集群运维手册

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §部署集成


## Web 集群配置 > 集群运维手册（13篇）

### 142. Linux 系统配置各个节点的时间一致性

- **doc-view ID**: 2727
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Linux 系统配置各个节点的时间一致性
- **核心概念**: ``` date #查看当前系统时间和日期 date -s 02/21/2019 #设置日期,例如将系统日期设定成 2019 年 02 月 21 日 date -s 19:21:45 #设置时分秒，例如将系统时间设定成 19 点 21 分 45 秒 hwclock -w #将当前时间和日期写入 BIOS，即设置为硬件时间，避免重启后失效 ``` 注意：手动设置时间会存在一定的误差，所以调整各个系统

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: ``` date #查看当前系统时间和日期 date -s 02/21/2019 #设置日期,例如将系统日期设定成 2019 年 02 月 21 日 date -s 19:21:45 #设置时分秒，例如将系统时间设定成 19 点 21 分 45 秒 hwclock -w #将当前时间和日期写入 BI
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: ``` date #查看当前系统时间和日期 date -s 02/21/2019 #设置日期,例如将系统日期设定成 2019 年 02 月 21 日 date -s 19:21:45 #设置时分秒，例如将系统时间设定成 19 点 21 分 45 秒 hwclock -w #将当前时间和日期写入 BI

**关键代码/公式/API：**
- 代码片段: `date #查看当前系统时间和日期 ⏎ date -s 02/21/2019 #设置日期,例如将系统日期设定成 2019 年 02 月 21 日 ⏎ date -s 19:21:45 #设置时分秒，例如将系统时间设定成 19 点 21 分 45 秒 ⏎ hwclock -w #将当前时间和日期写入 BIOS，即设置为硬件时间，避免重启后失效`
- 代码片段: `rpm -qa | grep ntp #检查命令`
- 代码片段: `rpm -e ntpdate-4.2.6p5-22.el7.x86_64 #删除 ntpdate`

### 143. vsftpd.conf 配置手册

- **doc-view ID**: 2790
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > vsftpd.conf 配置手册
- **核心概念**: ``` anonymous_enable=NO # 禁止匿名用户登录，默认是允许 local_enable=YES # 允许本地用户访问，默认就是 YES，不用改 write_enable=YES # 允许写入，默认是 YES，不用改 local_umask=022 # 默认的 umask 码，即上传后文件的权限掩码，不用改 anon_upload_enable=NO #匿名用户不可以上传文件 a

**业务场景四要素：**
- 统计指标方案: 如果启用，传输日志文件将以标准 xferlog 格式写入，如 wu-ftpd 所使用。这很有用，因为您可以重用现有的传输统计信息生成器 但是，默认格式更具可读性。此样式的日志文件的缺省位置是 /var/log/xferlog，但您可以使用 xferlog_file 设置进行 更改。
- 业务场景: 用于创建上载文件的权限。Umasks 应用于此值之上。如果您希望上传的文件可执行，您可能希望更改为 0777。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 此选项指定用于 SSL 加密连接的 DSA 证书的位置。

**关键代码/公式/API：**
- 代码片段: `anonymous_enable=NO # 禁止匿名用户登录，默认是允许 ⏎ local_enable=YES # 允许本地用户访问，默认就是 YES，不用改 ⏎ write_enable=YES # 允许写入，默认是 YES，不用改 ⏎ local_umask=022 # 默认的  umask 码，即上传后文件的权限掩码，不用改 ⏎ anon_upload_enable=NO #匿名用户不可以上`
- 公式: `chroot()`
- 公式: `sendfile()`

### 144. Linux 版集群运维手册

- **doc-view ID**: 2791
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Linux 版集群运维手册
- **核心概念**: 说明： 1）此运维手册适用操作系统：CentOS6.x 、CentOS7.x、RedHat6.x、RedHat7.x。2）此运维手册适用部署方式：按照帮助文档部署的集群环境。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 说明： 1）此运维手册适用操作系统：CentOS6.x 、CentOS7.x、RedHat6.x、RedHat7.x。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 说明： 1）此运维手册适用操作系统：CentOS6.x 、CentOS7.x、RedHat6.x、RedHat7.x。

**关键代码/公式/API：**
- 代码片段: `cd /usr/nginx/sbin #进入 sbin 目录`
- 代码片段: `./nginx #启动nginx`
- 代码片段: `./nginx -s stop #停止 Nginx`
- URL: `https://www.linuxidc.com/Linux/2016-07/133515.htm`

### 145. Nginx 开机自启动脚本

- **doc-view ID**: 2792
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > 开机自启动 > Nginx 开机自启动脚本
- **核心概念**: 虽然使用命令行可以对 Nginx 进行各种操作，比如启动等，但是还是不太方便，下面介绍在 Linux 下安装 Nginx 后，如何设置其开机自启动。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 虽然使用命令行可以对 Nginx 进行各种操作，比如启动等，但是还是不太方便，下面介绍在 Linux 下安装 Nginx 后，如何设置其开机自启动。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 虽然使用命令行可以对 Nginx 进行各种操作，比如启动等，但是还是不太方便，下面介绍在 Linux 下安装 Nginx 后，如何设置其开机自启动。

**关键代码/公式/API：**
- 代码片段: `vi /etc/init.d/nginx`
- 代码片段: `#!/bin/sh ⏎ # ⏎ # nginx - this script starts and stops the nginx daemon ⏎ # ⏎ # chkconfig:   - 85 15 ⏎ # description:  NGINX is an HTTP(S) server, HTTP(S) reverse \ ⏎ #               proxy and IMAP/PO`
- 代码片段: `nginx="/usr/nginx/sbin/nginx" ====>nginx执行程序的路径 ⏎ NGINX_CONF_FILE="/usr/nginx/conf/nginx.conf" ====>配置文件的路径`
- 公式: `HTTP(S)`
- 公式: `dirs()`
- 公式: `start()`
- 公式: `stop()`
- URL: `http://wiki.nginx.org/RedHatNginxInitScript`

### 146. Redis 开机自启动脚本

- **doc-view ID**: 2797
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > 开机自启动 > Redis 开机自启动脚本
- **核心概念**: 虽然使用命令行可以对redis进行各种操作，比如启动等，但是还是不太方便，本文介绍在Linux下安装Redis后，如何设置其开机自启动。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 虽然使用命令行可以对redis进行各种操作，比如启动等，但是还是不太方便，本文介绍在Linux下安装Redis后，如何设置其开机自启动。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 虽然使用命令行可以对redis进行各种操作，比如启动等，但是还是不太方便，本文介绍在Linux下安装Redis后，如何设置其开机自启动。

**关键代码/公式/API：**
- 代码片段: `vi /etc/init.d/redis`
- 代码片段: `#!/bin/sh ⏎ # chkconfig: 2345 10 90  ⏎ # description: Start and Stop redis ⏎ REDISPORT=7379 ⏎ EXEC=/usr/redis/redis-5.0.4/src/redis-server ⏎ CLIEXEC=/usr/redis/redis-5.0.4/src/redis-cli ⏎ PIDFILE=/var`
- 代码片段: `EDISPORT=7379 ====>默认为7379，若有调整请修改为实际的端口号 ⏎ EXEC=/usr/redis/redis-5.0.4/src/redis-server ====>Redis 服务的启动路径 ⏎ CLIEXEC=/usr/redis/redis-5.0.4/src/redis-cli ====>Redis 客户端的启动路径 ⏎ CONF="/usr/redis/redis-`

### 147. Nginx.conf 配置手册

- **doc-view ID**: 2815
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Nginx 配置 > Nginx.conf 配置手册
- **核心概念**: Nginx 部署后，需要修改nginx.conf文件才能使用。本文提供了两种配置方式： - 通用配置，常规即 HTTP 情况下只需要更改 IP 和端口即可使用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: Nginx 部署后，需要修改nginx.conf文件才能使用。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: Nginx 部署后，需要修改nginx.conf文件才能使用。

**关键代码/公式/API：**
- 代码片段: `#用户或者用户组 默认为nobody ⏎ #user  root; ⏎ #允许进程数量，建议设置为cpu核心数或者auto自动检测，注意Windows服务器上虽然可以启动多个processes，但是实际只会用其中一个 ⏎ worker_processes  auto; ⏎ #自动根据CPU数目绑定CPU亲缘性，nginx1.9.10及以上版本才能用 ⏎ #worker_cpu_affinity  `
- 代码片段: `#user  root; ⏎ ... ⏎ 省略部分参考http配置文件 ⏎ ... ⏎     worker_connections  1024; ⏎ } ⏎  ⏎ http { ⏎      #add_header access-control-allow-Origin *; ⏎      add_header access-control-allow-Headers X-Requested-W`
- 代码片段: `<Valve className="org.apache.catalina.valves.RemoteIpValve" ⏎ remoteIpHeader="X-Forwarded-For" ⏎ protocolHeader="X-Forwarded-Proto" ⏎ protocolHeaderHttpsValue="https"/>`
- 公式: `fall(fall_count)`
- 公式: `rise(rise_count)`
- URL: `http://FR.com`
- URL: `http://WBS.com`
- URL: `http://ip`

### 148. Nginx 配置短域名

- **doc-view ID**: 2853
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Nginx 配置 > Nginx 配置短域名
- **核心概念**: 用户搭建集群环境后，希望减短访问工程的网址长度，例如：访问 http://192.168.1.23 可直接跳转到 http://192.168.1.23/webroot/decision。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 用户搭建集群环境后，希望减短访问工程的网址长度，例如：访问 http://192.168.1.23 可直接跳转到 http://192.168.1.23/webroot/decision。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 用户搭建集群环境后，希望减短访问工程的网址长度，例如：访问 http://192.168.1.23 可直接跳转到 http://192.168.1.23/webroot/decision。

**关键代码/公式/API：**
- 代码片段: `server { ⏎     listen 90; ⏎     server_name localhost; ⏎      ⏎     #匹配/ 转到/webroot/decision上； ⏎     #^(.*)$表示/后任意部分，除非和其它location匹配否则一律转向/webroot/decision，如果无需这样可以修改这里location或者rewrite的正则； ⏎     #per`
- URL: `http://192.168.1.23`
- URL: `http://192.168.1.23/webroot/decision`
- URL: `http://crm`

### 149. Web 集群数据库可配置项说明文档

- **doc-view ID**: 2855
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Web 集群数据库可配置项说明文档
- **核心概念**: 本文介绍 fine_conf_entity 表中集群相关的字段及含义。注：部分字段使用默认值时，在数据库表中是查询不到的，需要插入该字段及自定义的值。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 本文介绍 fine_conf_entity 表中集群相关的字段及含义。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 本文介绍 fine_conf_entity 表中集群相关的字段及含义。

### 150. Nginx 增加主动检查健康机制

- **doc-view ID**: 2911
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Nginx 配置 > Nginx 增加主动检查健康机制
- **核心概念**: 请根据本文逻辑自行推断自己对应的安装路径。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 请根据本文逻辑自行推断自己对应的安装路径。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 请根据本文逻辑自行推断自己对应的安装路径。

**关键代码/公式/API：**
- 代码片段: `/usr/local/nginx/sbin/nginx -V`
- 代码片段: `wget http://nginx.org/download/nginx-1.x.x.tar.gz`
- 代码片段: `tar zxvf nginx-1.x.x.tar.gz #解压安装包 ⏎ unzip ngx_healthcheck_module-master.zip #解压安装包 ⏎ cd /usr/nginx/nginx-1.x.x #进入解压目录 ⏎ patch -p1 < /usr/nginx/ngx_healthcheck_module-master/nginx_healthcheck_for_ngi`
- URL: `http://nginx.org/download/nginx-1.x.x.tar.gz`

### 151. Linux下Tomcat开机自启动

- **doc-view ID**: 2934
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > 开机自启动 > Linux下Tomcat开机自启动
- **核心概念**: 本文介绍 Linux 系统安装 Tomcat 后，设置开机自启动的方法。注：Tomcat 设置开机自启动后，日志路径会变化，建议指定日志路径。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 本文介绍 Linux 系统安装 Tomcat 后，设置开机自启动的方法。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 本文介绍 Linux 系统安装 Tomcat 后，设置开机自启动的方法。

**关键代码/公式/API：**
- 代码片段: `vi /etc/init.d/tomcat`
- 代码片段: `#!/bin/bash  ⏎ # tomcat startup script for the Tomcat server  ⏎ # chkconfig: 35 80 20  ⏎ # description: start the tomcat deamon  ⏎ #prog=tomcat  ⏎ #EDISPORT=8080  ⏎ #默认为 8080，若有调整请修改为实际的端口号 ⏎ #EXEC=/u`
- 代码片段: `CATALANA_HOME=/usr/tomcat/ ====> tomcat/bin/目录下catalana.sh 的根目录`

### 152. Redis 集群开机自启动脚本

- **doc-view ID**: 2935
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > 开机自启动 > Redis 集群开机自启动脚本
- **核心概念**: redis-cluster 文件修改说明： 请根据实际情况修改配置文件中的以下圈红内容 redis-cluster 文件配置说明： ``` REDISPORT=(7000 7001 7002 7003 7004 7005) EXEC=/usr/local/bin/redis-server CLIEXEC=/usr/local/bin/redis-cli PASSWD=admin123456 for

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: redis-cluster 文件修改说明： 请根据实际情况修改配置文件中的以下圈红内容 redis-cluster 文件配置说明： ``` REDISPORT=(7000 7001 7002 7003 7004 7005) EXEC=/usr/local/bin/redis-server CLIEX
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: redis-cluster 文件修改说明： 请根据实际情况修改配置文件中的以下圈红内容 redis-cluster 文件配置说明： ``` REDISPORT=(7000 7001 7002 7003 7004 7005) EXEC=/usr/local/bin/redis-server CLIEX

**关键代码/公式/API：**
- 代码片段: `#!/bin/sh ⏎ # chkconfig:   2345 90 10 ⏎ # description:  Redis is a persistent key-value database ⏎   ⏎ # 相关配置项，应该根据实际环境信息进行改动，包括for循环中的PIDFILE和CONF ⏎ REDISPORT=(7000 7001 7002 7003 7004 7005) ⏎ EXEC=/`
- 代码片段: `chmod +x /etc/init.d/redis-cluster`
- 代码片段: `chkconfig --add redis-cluster  # 注册为系统服务 ⏎ chkconfig redis-cluster on  # 开机自启动 ⏎ service redis-cluster stop  # 关闭 redis 集群 ⏎ service redis-cluster start  # 启动 redis 集群`
- 公式: `for((i=0;i<${#REDISPORT[@]};i++)`

### 153. Redis 运维手册

- **doc-view ID**: 2951
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > Redis 运维手册
- **核心概念**: 使用 config 命令可以对Redis 的配置参数进行热修改，这样就不需要重启，如下所示： ``` config get * # 获得所有的配置项的key 127.0.0.1:7379> config get maxmemory maxmemory 4294967296 # 改变redis的内存，推荐内存大小为 4G， 单位为byte 127.0.0.1:7379> maxmemory 4294

**业务场景四要素：**
- 统计指标方案: 127.0.0.1:7379> dbsize # 当前数据库的key的数量
- 业务场景: 使用 config 命令可以对Redis 的配置参数进行热修改，这样就不需要重启，如下所示： ``` config get * # 获得所有的配置项的key 127.0.0.1:7379> config get maxmemory maxmemory 4294967296 # 改变redis的内存，
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 使用 config 命令可以对Redis 的配置参数进行热修改，这样就不需要重启，如下所示： ``` config get * # 获得所有的配置项的key 127.0.0.1:7379> config get maxmemory maxmemory 4294967296 # 改变redis的内存，

**关键代码/公式/API：**
- 代码片段: `config get *   # 获得所有的配置项的key  ⏎ 127.0.0.1:7379> config get maxmemory  ⏎ maxmemory 4294967296    # 改变redis的内存，推荐内存大小为 4G， 单位为byte ⏎ 127.0.0.1:7379> maxmemory 4294967296 ⏎ config get *   # 查看  ⏎ 127.0.`
- 代码片段: `info  #查看redis的使用情况 ⏎ 127.0.0.1:7379> info ⏎ # Server ⏎ redis_version:2.8.13  # Redis 服务器版本 ⏎ redis_mode:standalone  # 运行模式是单机状态，redis集群时是cluster nodes ⏎ os:Linux3.5.0-48-generic x86_64  # 服务器的宿主操作系统 `
- 代码片段: `./redis-cli -p 端口 -a 密码  # 本地启动Redis客户端，可以进行查看key值，删除key值，检查redis状态等操作，如果端口是6379的话可以省略 ⏎ ./redis-cli -h ip -p 端口 -a 密码  # 远程连接Redis服务，ip和端口为要连接的Redis服务，如果端口是6379的话可以省略`
- URL: `http://www.redis.cn/commands.html`

### 154. F5 BIG-IP 安全漏洞通报

- **doc-view ID**: 3553
- **路径**: 部署集成 > Web 集群配置 > 集群运维手册 > F5 BIG-IP 安全漏洞通报
- **核心概念**: F5 BIG-IP 是美国 F5 公司的一款集成了网络流量管理、应用程序安全管理、负载均衡等功能的应用交付平台。F5 BIG-IP 中存在安全漏洞。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: F5 BIG-IP 是美国 F5 公司的一款集成了网络流量管理、应用程序安全管理、负载均衡等功能的应用交付平台。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: F5 BIG-IP 是美国 F5 公司的一款集成了网络流量管理、应用程序安全管理、负载均衡等功能的应用交付平台。

---
