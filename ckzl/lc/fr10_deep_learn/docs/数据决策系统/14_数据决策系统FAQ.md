<!--
KB_INDEX: {
  "title": "数据决策系统 - 数据决策系统FAQ",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "数据决策系统",
    "数据决策系统FAQ"
  ],
  "summary": "「数据决策系统」分页：数据决策系统FAQ（约 4 篇条目）；FR10 帮助文档「数据决策系统」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 数据决策系统 · 数据决策系统FAQ

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §数据决策系统


## 数据决策系统FAQ（4篇）

### 154. 修改报表访问路径中的 Servlet 应用名

- **doc-view ID**: 823
- **路径**: 数据决策系统 > 数据决策系统FAQ > 修改报表访问路径中的 Servlet 应用名
- **核心概念**: 10.0 报表工程中，模板访问地址为：http://ip:post/ProjectName/decision/view/report?viewlet=GettingStarted.cpt ProjectName：10.0 默认为 webroot，9.0默认为 WebReport IP：服务器所在 IP 地址 post：为服务器端口 ProjectName：工程名 GettingStarted.cp

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 10.0 报表工程中，模板访问地址为：http://ip:post/ProjectName/decision/view/report?viewlet=GettingStarted.cpt ProjectName：10.0 默认为 webroot，9.0默认为 WebReport IP：服务器所在 I
- 人员岗位: 管理员登录数据决策系统，点击「管理系统>系统管理>常规」，修改 Servlet 路径名，将 decision 改成 Report，点击「保存」。如下图所示：
- 功能应用场景: 10.0 报表工程中，模板访问地址为：http://ip:post/ProjectName/decision/view/report?viewlet=GettingStarted.cpt ProjectName：10.0 默认为 webroot，9.0默认为 WebReport IP：服务器所在 I

**关键代码/公式/API：**
- URL: `http://ip`
- URL: `http://localhost`

### 155. 报表平台中报没有找到模板文件

- **doc-view ID**: 986
- **路径**: 数据决策系统 > 数据决策系统FAQ > 报表平台中报没有找到模板文件
- **核心概念**: 在数据决策系统目录查看模板时，提示：错误代码:11300004 没有找到模板文件:xxx模板。如下图所示： 通过某个超链访问模板时提示：错误代码:11300004 没有找到模板文件:xxx模板。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 在数据决策系统目录查看模板时，提示：错误代码:11300004 没有找到模板文件:xxx模板。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: 在数据决策系统目录查看模板时，提示：错误代码:11300004 没有找到模板文件:xxx模板。

**关键代码/公式/API：**
- 公式: `open(FR.cjkEncode(url)`
- JS API: `window.open`
- URL: `http://localhost`

### 156. PUT、DELETE请求转成POST插件

- **doc-view ID**: 3901
- **路径**: 数据决策系统 > 数据决策系统FAQ > PUT、DELETE请求转成POST插件
- **核心概念**: 数据决策系统中的请求很多都是 PUT、DELETE 请求。但是部分用户环境禁用了 PUT、DELETE请求，导致平台一些请求不正常。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 数据决策系统中的请求很多都是 PUT、DELETE 请求。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: 数据决策系统中的请求很多都是 PUT、DELETE 请求。

**关键代码/公式/API：**
- SQL: `DELETE 请求。`
- SQL: `DELETE 请求转成 POST 请求。`
- SQL: `DELETE 请求是否被禁用，都会强制转换为 POST 请求。`

### 157. FineReport外网地址

- **doc-view ID**: 4033
- **路径**: 数据决策系统 > 数据决策系统FAQ > FineReport外网地址
- **核心概念**: 报表服务器若部署在内网环境下，某些需要外网的场景功能无法使用。本文将简单介绍部分功能需要开通的外网端口，用户可根据需要自行开通网络白名单。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 报表服务器若部署在内网环境下，某些需要外网的场景功能无法使用。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: 报表服务器若部署在内网环境下，某些需要外网的场景功能无法使用。

**关键代码/公式/API：**
- 代码片段: `-Dhttp.proxyHost= http 协议代理服务器主机名 ⏎ -Dhttp.proxyPort= http 协议代理服务器端口号 ⏎ -Dhttps.proxyHost= https 协议代理服务器主机名 ⏎ -Dhttps.proxyPort= https 协议代理服务器主机名`
- 代码片段: `set "JAVA_OPTS=-Dhttp.proxyHost=http协议代理服务器主机 -Dhttp.proxyPort=http协议代理服务器端口号 -Dhttps.proxyHost=https协议代理服务器端口号 -Dhttps.proxyPort=https协议代理服务器端口号"`
- 代码片段: `JAVA_OPTS="$JAVA_OPTS -Dhttp.proxyHost=http协议代理服务器主机名 -Dhttp.proxyPort=http协议代理服务器端口号 -Dhttps.proxyHost=https协议代理服务器主机名 -Dhttps.proxyPort=https协议代理服务器端口号"`
- URL: `https://cloud.fanruan.com`
- URL: `https://market.fanruan.com`
- URL: `http://shop.finereport.com`
- URL: `http://bbs.fanruan.com`

---
