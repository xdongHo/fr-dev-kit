<!--
KB_INDEX: {
  "title": "注入错进程：18999/19000 被占、remote_tpl 返回空 md5 d41d8cd9",
  "stage": "error-case",
  "tags": ["fr-agent", "注入", "⭐高频", "错进程", "端口占用"],
  "keywords": ["inject", "18999", "19000", "d41d8cd9", "EmptyWorkResource", "ExecServer.stop", "loadAgent", "port-base", "远程设计"],
  "summary": "实战案例(2026-09): designer.bat 自动注入按'最新 java.exe PID'选进程错注入本地服务器进程(无窗口/WorkResource=EmptyWorkResource)占住 18999/19000 → 真设计器注不进、remote_tpl md5 静默返回空 md5 d41d8cd9 极易误判为生产文件被清空; 处置=错进程 agent 自释放端口+重注入真设计器; Attacher 只调 loadAgent 无 options → --port-base 无效"
}
-->

# 注入错进程：端口被占 + remote_tpl 返回空 md5（d41d8cd9…）

← [返回 tbcw 索引](README.md) · 来源：远程设计器读写实战（2026-09，个人版 CHANGELOG 通道节）

## 症状（三连）

1. `python kfgj/fr-agent/inject.py` 报注入成功，但 `:18999/status` 的工作簿是**空的**（`WorkResource=EmptyWorkResource`）——注入到了一个**无窗口的 java 进程**（本地服务器/预览子进程，类 `com.fr.start.Designer`）。
2. 真设计器随后再注：端口 18999/19000 已被占，注不进去。
3. 远程设计读写校验里 `remote_tpl` 的 md5 **静默返回 `d41d8cd98f00b204e9800998ecf8427e`**（空内容 md5）——极易误判为"生产模板被清空/损坏"，实为读的是空 WorkResource。

## 根因

- `designer.bat` 自动注入按「**最新的 java.exe PID**」选进程——本地起过服务器/预览时，最新 java.exe 恰是它们而非设计器主进程。
- **真设计器的辨认特征**：用**相对路径** `jrein\java` 启动（命令行不含 FineReport 绝对路径）；窗口标题匹配 `FineReport.*@`（PowerShell：`Get-Process | ? { $_.MainWindowTitle -match 'FineReport.*@' }`）。
- `Attacher` 只调 `vm.loadAgent(jar)`（**不带 options**）→ 注入参数里的 `--port-base` 无效——**端口被占时必须先释放**，换端口参数救不了。

## 处置（顺序固定）

```bash
# 1) 用错进程 agent 自己的 /exec 释放 19000，再 /shutdown 释放 18999
curl -X POST http://localhost:19000/exec -H "Content-Type: application/json"      -d '{"script":"var c=Java.type(\"fr.agent.ExecServer\");return \"stopping\""}'
curl -X POST http://localhost:18999/shutdown
# 2) 找真设计器 PID（窗口标题法）
powershell -NoProfile -Command "Get-Process java | ? { $_.MainWindowTitle -match 'FineReport.*@' } | select Id,MainWindowTitle"
# 3) 指定 PID 重新注入
python kfgj/fr-agent/inject.py --pid <真设计器PID>
```

## 防复发

- 注入后先 `curl :18999/status` 看 `workbook` 字段是否带真实模板路径/`@默认[本地目录]`——**空 WorkResource 立刻重注**，不要继续用。
- 任何"远端文件 md5 = d41d8cd9…"先怀疑**读到了空会话**，再怀疑文件损坏。
- 批量注入脚本选 PID 一律用**窗口标题/命令行双重校验**，不要用"最新 java.exe"。

> 来源：个人版版本变更 CHANGELOG「通道（远程设计器读写）」（2026-09 实战）；与 [kfgj/fr-agent/README.md](../../../kfgj/fr-agent/README.md)「错进程注入与端口占用」节互为索引。
