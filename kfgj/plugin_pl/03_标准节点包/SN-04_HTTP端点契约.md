<!-- KB_INDEX: {"title":"SN-04 HTTP 端点契约","stage":"pipeline-node","tags":["标准节点","开发","端点"],"keywords":["SN-04","HttpHandler","单段路径","URL参数","403","404鉴别"],"summary":"端点契约标准节点：单段路径/参数全放URL/认证声明/403协议/三层404鉴别，拦截 P01(设计侧)/P09。"} -->

# SN-04 HTTP 端点契约（S3 开发）

**类型**：标准节点（确定性，机器+清单）｜**拦截**：P01 复发链的设计侧（参数传递纪律）、P09 路径族冲突
**输入**：端点清单｜**输出**：端点契约表｜**机器检查**：sn_gate `C09`（getPath 单段）、`C10`（POST body 依赖 WARN）

## 检查清单

- [ ] **每个 HttpHandler `getPath()` 单段**（FR 框架限制，多路由走 query/form 参数——demo_plugin_repo 三件套实测定律；sn_gate `C09`）
- [ ] **参数优先放 URL 查询串，不依赖请求体解析**（P01 首发根因：XHR `send(string)` 默认 text/plain → Servlet 不解析 → getParameter null；demo_plugin_repo v2.1.6 修法：参数放 URL + 显式表单头双保险）
- [ ] 前端 POST 必带显式 `Content-Type`（`application/x-www-form-urlencoded` 或 `application/json`）且服务端**不依赖容器 body 解析**（`readBodyJson` 手解流为正面实践，aicopilot feedback）
- [ ] **认证显式声明**：`isPublic()=false + needAdmin()=true` 或公开端点（本机 127.0.0.1 + CORS 说明）；每个端点写清"谁能调"
- [ ] **错误协议统一**：403 → `{"ok":false,"code":"PRO_REQUIRED",...}` 式 JSON（fail-closed）；未知 jobId → 404 + 机器可读 code（`JOB_NOT_FOUND`）
- [ ] **三层 404 鉴别法**入运维手册（demo_plugin_repo §10）：FR 平台页 ~2636B=路由失败；Tomcat 原生页 ~740B=handler 已执行定位失败；SPA index ~46KB=URL 不在任何路由
- [ ] 端点命名走身份表路径族（P09：双插件同段名直接冲突，全局命名空间）
- [ ] worker 线程**不得持有 HttpServletRequest**（异步任务在提交线程解析 roots/参数后传入，demo_plugin_repo ProgressHub 实战）
- [ ] CORS/代理环境：直达本机端点（127.0.0.1）与决策端点双通道时，先测**浏览器真实链路**（与 SN-08 G-BROWSER 联动）

## 端点契约表模板

| 端点 | 方法+路径 | 参数（全部在 URL？） | 认证 | 成功/错误协议 | 谁调 |
|---|---|---|---|---|---|
| /<名>batch | POST | format/mode/extras/paths/lang（form+URL 双通道） | admin | 200 附件流 / 403 PRO_REQUIRED / 404 JOB_NOT_FOUND | 前端 |

## 反例

- P01：demo_plugin_repo 异步进度通道 v2.1.3 上线，命令行回归全绿，v2.1.6 才在浏览器路径炸出 jobId 全 null——**契约表里"参数在 URL"一栏当时不存在**。
- P09：demo_plugin_repo 与标准版 HttpHandler 段名冲突属全局命名空间，双装即冲突。

## v1.1 增补（复刻实践 2026-09-15）

- [ ] 契约表参数位置改两列表述（P30，D 代理对照实况修正）：**标识类参数**（jobId/path/op/lang）→ URL 查询串（不依赖 body 解析，代理剥头也活）；**业务类参数**（format/mode/extras/paths）→ body 表单 + **显式 Content-Type**。"参数全在 URL"是过度简化，双保险的精确形态=两类分治。
