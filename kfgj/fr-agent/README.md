<!--
KB_INDEX: {
    "title": "fr-agent — GUI 操作追踪 Agent",
    "stage": "gui-tracing",
    "tags": [
      "fr-agent",
      "GUI追踪",
      "注入",
      "HTTP API"
    ],
    "keywords": [
      "inject",
      "18999",
      "19000",
      "events",
      "exec",
      "AWT事件",
      "Java Access Bridge"
    ],
    "summary": "fr-agent 使用手册：注入 Designer JVM、/status /events /exec API、事件流→Java API 追踪流程"
  }
-->

﻿# FR Agent — GUI操作追踪工具

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

### 常见问法：想知道同事在设计器里点了哪些菜单/按钮？能把操作录下来回放吗？

- 「把操作录下来 / 操作录制 / 回放同事做了什么」→ 本工具即 **GUI 操作追踪**：注入 Designer JVM 后 `curl localhost:18999/events` 拉事件流（鼠标点击/菜单动作/控件焦点），逐事件映射 Java API，见「快速开始」「自动注入」。
- 「事件 JSON 长什么样 / 怎么映射成代码」→ `ckzl/lc/09_GUI操作追踪.md` §事件 JSON 结构 + 映射示例；双机/双版本端口见「双 FR 共存」。

## 快速开始
```bash
python inject.py            # FR10: 自动找 FR PID 并注入 Agent
python inject_fr11.py       # FR11: 自动找 FR11 PID 并注入（2026-08-22 实测可用）
python trace3.py            # 查看缓冲区事件（/events 拉取，过滤出 SQL/菜单类动作）
```

## HTTP API (localhost:18999)
| 端点 | 用途 |
|------|------|
| /ping | Agent 存活检查 |
| /status | 事件数/Recording/工作簿 |
| /events?n=N | 取 N 条 AWT 事件 |
| /eval | 反射 FR 类方法 |
| /exec | Nashorn 脚本执行（端口 19000） |
| /shutdown | 停止 agent（释放 18999） |
| /tree | 导出组件树 |
| /click /type /shortcut | GUI 自动化（未稳定） |

## 自动注入（designer.bat）

`C:\Program Files\FineReport_10.0\bin\designer.bat` 已改造为**自动注入**：

```
Phase 1: start designer_core.bat（后台启动 Designer）
Phase 2: 轮询 tasklist 等 java.exe 出现 → 等 15s GUI 初始化
Phase 3: 轮询 localhost:8075 HTTP 就绪
Phase 4: build.cmd → 编译 AttachAgent → AttachAgent <PID> fr-agent.jar
         ├─→ :18999  fr-agent（AWT tracing + /eval + /tree）
         └─→ :19000  ExecServer（/exec Nashorn 执行）
```

**注意**：如果直接启动 `designer.exe` 或旧版 `designer.bat`，agent 不会自动注入，
需手动运行 `python fr-agent/inject.py`。

> **PID 自动定位已修复（2026-08-28 实测）**
>
> 旧版按「CommandLine 含 `FineReport`」找进程，会**稳定命中错误进程**。本机实测同时存在 3 个 java 进程，且是个陷阱：
>
> | PID | 身份 | CommandLine 含 `FineReport`？ |
> |-----|------|------------------------------|
> | 13156 | designer.bat wrapper | ✅ 含（绝对路径） |
> | 37984 | AI Copilot 插件子进程（`plugin-com.fr.plugin.aicopilot`） | ✅ 含 |
> | **36292** | **Designer 主进程（真身）** | ❌ **不含**（用相对路径 `.\jre\bin\java` 启动） |
>
> 即：真正的设计器进程恰恰是唯一不带 `FineReport` 字样的那个，旧算法必错。
> 现改为按**主窗口标题**匹配 `FineReport.*@`，实测稳定命中：
> `FineReport 10.0.19 release 2024-05-09 @默认[本地目录]    mem://WorkBook114`
> - 标题里 `mem://WorkBook114` = **未保存的新建报表**；已保存的模板此处显示相对路径
> - 拿不准时用 `--pid` 手动指定：`python inject.py --pid 36292`
> - ⚠️ 旧文档写的「MainWindowTitle 含『日志』」是误判——那是日志窗口，不是主窗口

## 执行 JS 探查（exec_js.py）

无 GUI 读取 Designer 运行时状态（当前模板/数据集/参数面板控件数等）：

```bash
python exec_js.py probe_workbook_content.js   # 查当前模板内容
python exec_js.py probe_open_templates.js     # 查打开了哪些模板
python exec_js.py -                           # 从 stdin 读 JS
```

依赖 `/exec`（19000）。配合 `/status` 的 `workbook` 字段可判断当前模板是否已保存到磁盘——
**未保存模板无法解析 XML，改模板前务必确认已保存**。

### 常见问法：公式怎么验证/试算一个公式对不对？
- 问法「验证公式合法性 / 公式试算 / 公式模拟计算」→ 用 `eval_formula.js`（FR Calculator 引擎
  evalValue 求值，判 Primitive 三态，收尾闸门 G09 实现件）：
  `python exec_js.py eval_formula.js`；自定义公式→编辑该文件 formulas 数组
  （或 `python exec_js.py -` 从 stdin 传入仿写的求值脚本）。
  raw 通道: `curl -X POST http://localhost:19000/exec -d @<(python -c "import json;print(json.dumps({'script':open(r'fr-agent/eval_formula.js',encoding='utf-8').read()}))")`
  前提: Designer 已运行且注入成功（/exec 19000 可用），无需 WorkBook/Workspace。
  出处: fr-agent/eval_formula.js 头注（借鉴 FR AI 助手 FormulaTools「模拟计算」）。

## 编译
```cmd
build.cmd  # 需要 Amazon Corretto JDK 8
```

## FR11 注入（inject_fr11.py，2026-08-22 实测）

FR11（`C:\FineReport_11.0`）与 FR10 注入机制相同（agentmain 动态 attach fr-agent.jar），
但有三处差异（详见 `ckzl/lc/fr11_knowledge/fr11_knowledge_复核报告_2026-08-22.md` §三）：

1. **Attacher 必须用 FR11 自带 JRE 跑**：`C:\FineReport_11.0\jre\bin\java.exe` + 自带 `jre\lib\tools.jar`
   （OpenJDK 8u191-redhat，tools.jar 齐全；混用其他 JDK 会 attach 失败/jvm.dll 报错）
2. **PID 精确匹配** `FineReport_11.0` + `com.fr.start`——双 FR 共存时防注错进程
3. 设计器主类 `com.fr.start.Designer`，`--start` 参数可自动拉起 `bin\designer.bat`

```bash
python inject_fr11.py --start                # 拉起设计器并注入
python inject_fr11.py --exec "java.lang.Class.forName('com.fr.stable.fun.LocaleFinder').getName()"
```

实测记录：PID 13972 注入成功（18999/19000 双端口 OK），
`InterProviderFactory.getProvider().getLocText(...)` 运行时真实返回中文译文——
FR11 JVM 内反射探测 API 存在性/真实调用的标准手法。

## 双 FR 共存（FR10 + FR11 同机）

**问题**：FR10 和 FR11 的 agent 都默认绑定 18999/19000 端口，同时运行会冲突。

**解决方案**：通过系统属性覆盖端口，FR11 使用 19100/19101。

### 注入命令

```bash
# FR10（默认端口 18999/19000）
python inject.py

# FR11（使用 19100/19101，避开 FR10）
python inject_fr11.py --port-base 19100

# FR11 自定义端口（如 19200/19201）
python inject_fr11.py --port-base 19200

# 通过环境变量配置（优先级低于 --port-base）
set FR_AGENT_PORT_BASE=19100
python inject_fr11.py
```

### 端口验证

```bash
# 检查 FR10 agent
curl http://localhost:18999/ping

# 检查 FR11 agent
curl http://localhost:19100/ping

# 运行脚本（FR10 用 19000，FR11 用 19101）
curl -X POST http://localhost:19000/exec -d '{"script":"1+1"}'
curl -X POST http://localhost:19101/exec -d '{"script":"1+1"}'
```

### Python 客户端使用

```python
# FR10 客户端（默认 18999）
python fr_agent_client.py ping

# FR11 客户端（需改 AGENT_URL 或传参）
# 编辑 fr_agent_client.py 第 25 行：
# AGENT_URL = "http://localhost:19100"
```

## 陷阱
- 每次只能注入一次（端口绑定旧 JVM）
- 重注入需重启 FR Designer（已加载类不会被新 JAR 覆盖）
- `-javaagent` 会导致 FR License 验证失败 → 只用动态注入
- 事件缓冲区上限 10000 条
- 双 FR 共存时，FR11 必须使用 `--port-base 19100` 或更高，避免与 FR10 冲突
