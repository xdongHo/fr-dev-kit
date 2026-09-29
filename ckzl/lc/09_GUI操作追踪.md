<!--
KB_INDEX: {
    "title": "Stage 9: GUI 操作追踪",
    "stage": "pipeline",
    "tags": [
      "GUI",
      "AWT",
      "JavaAgent",
      "事件"
    ],
    "keywords": [
      "AWT事件",
      "注入Agent",
      "组件路径",
      "事件JSON"
    ],
    "summary": "通过动态注入 Java Agent 捕获 Designer AWT 事件并映射到 Java API 的方法论（fr-agent 配套）"
  }
-->

# Stage 9: GUI 操作追踪

> 来源: `ckzl/gf/FR_HEADLESS_GUIDE.md` 流水线拆分

---

## 23. GUI 操作追踪 — FR Java API 映射

> 📁 `fr-agent/` — 完整源码和工具

### 23.1 概述

通过动态注入 Java Agent 到运行中的 FR Designer JVM，捕获 AWT 原始事件（鼠标/键盘/焦点/窗口），解析 Swing 组件路径并映射到 FR Java API 类名。用于确定「用户点击 X 按钮 → 对应什么 Java 方法」。

### 23.2 工作流

```
① FR Designer 正常启动（桌面快捷方式）
② python fr-agent/inject.py          # 自动找 PID 并注入 Agent
③ 在 Designer 中执行操作
④ python fr-agent/trace3.py   # 查看事件缓冲区
⑤ 根据事件中的 comp.cls 确定 FR Java 类
⑥ 用 /eval 端点查看该类的方法签名
```

### 23.3 Agent 架构

| 组件 | 类 | 说明 |
|------|-----|------|
| 入口 | `FrAgent.java` | premain/agentmain，EDT invokeLater 注册监听器 |
| 事件录制 | `EventRecorder.java` | 线程安全循环缓冲区（10000 条），AWTEventListener |
| 组件解析 | `ComponentResolver.java` | Swing 组件 → 可读路径 + FR 类名映射 |
| HTTP API | `CommandServer.java` | 13 个端点，端口 18999 |
| 动作回放 | `ActionPlayer.java` | java.awt.Robot 精确回放 |
| 注入器 | `Attacher.java` | 独立程序，VirtualMachine.attach() 动态注入 |

### 23.4 HTTP API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/ping` | GET | Agent 存活 + PID |
| `/status` | GET | 事件数 / 录制状态 / 工作簿名 |
| `/events?n=N` | GET | 取 N 条 AWT 事件（含组件路径 + FR API） |
| `/eval` | POST | 反射 FR 类 → 列出方法签名 |
| `/tree` | GET | 导出当前组件树 |
| `/record/start` | POST | 开始录制（实验性） |
| `/record/stop` | POST | 停止录制（实验性） |

### 23.5 事件 JSON 结构

```json
{
  "type": "MOUSE_CLICKED",
  "ts": 1785724950780,
  "comp": {
    "cls": "com.fr.design.gui.ibutton.UIButton",
    "path": "DesignerFrame/.../UIToolbar/UIButton[增加]",
    "fr": "com.fr.design.gui.ibutton.UIButton"
  },
  "sx": 8, "sy": 769,
  "btn": 1, "mod": 1024
}
```

### 23.6 已验证的映射示例

| 用户操作 | FR 组件 | Java 类 |
|----------|---------|---------|
| 点击"增加"按钮 | `UIButton[增加]` | `com.fr.design.gui.ibutton.UIButton` |
| 打开数据库查询 | `DIALOG[数据库查询]/SQLEditPane` | `com.fr.design.data.source.datasource.SQLEditPane` |
| 粘贴 SQL (Ctrl+V) | `SQLEditPane KEY_PRESSED` | `SQLEditPane.setText()` / `paste()` |
| 点击执行按钮 | `XUIButton` | `SQLEditPane.preview()` |
| 查看预览结果 | `DIALOG[预览]/JScrollPane` | `com.fr.design.data.datapane.preview.PreviewTablePane` |
| 选择数据连接下拉 | `UIComboBox` | `com.fr.design.gui.icombobox.UIComboBox` |

### 23.7 编译与注入命令

```powershell
# 编译（需要 Amazon Corretto JDK 8）
cd fr-agent
.\build.cmd

# 一键注入（自动找 FR PID）
python inject.py

# 查看事件
python _check_trace.py

# 反射 FR 类方法
python fr_agent_client.py eval com.fr.design.data.source.datasource.SQLEditPane
```

### 23.8 陷阱

- **只能注入一次**：重复注入会因旧 HTTP 服务器占 18999 端口而失败。如需重新注入，必须重启 FR Designer。
- **启动方式**：只支持动态注入（`VirtualMachine.attach()`），不支持 `-javaagent`（FR License 验证失败 → FinePluginBridge ClassFormatError → 闪退）。
- **EDT 注册时序**：监听器在 premain 中通过 `EventQueue.invokeLater` 注册，需要约 2 秒的延迟才能生效。Agent 代码中的 `Thread.sleep(2000)` 确保服务器启动时监听器已就绪。
- **事件缓冲区**：最大 10000 条，用 `/events?n=N` 控制返回数量。
- **组件路径为 "?"**：表示 `ComponentResolver.resolvePath()` 未找到匹配的 FR 类映射，可检查 `ComponentResolver.java` 中的 `FR_KNOWN_CLASSES` 映射表。

---

