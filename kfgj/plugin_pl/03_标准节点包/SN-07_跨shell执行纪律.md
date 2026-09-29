<!-- KB_INDEX: {"title":"SN-07 跨 shell 执行纪律","stage":"pipeline-node","tags":["标准节点","开发","PowerShell"],"keywords":["SN-07","PowerShell","cmd","中文编码","命令模板"],"summary":"跨shell纪律标准节点：PS5 陷阱速查卡 + 三条固定命令模板，拦截复发链 P03。"} -->

# SN-07 跨 shell 执行纪律（S3 开发，全程适用）

**类型**：标准节点（确定性，清单）｜**拦截**：P03 复发链（demo_plugin_repo curl CJK / aicopilot java -D 被拆、curl -d 中文损坏）
**输入**：—｜**输出**：本工程 `docs/shell速查.md`（从本模板抄）

## 检查清单

- [ ] **命令只允许从模板抄，不允许现拼**（复发根因：教训是"知识"不是"命令模板"，每次现写重新踩——两次复发全是现拼命令）
- [ ] 三条固定模板已抄入工程速查并验证可跑：
  ```powershell
  # T1 发中文 JSON（PS5 curl -d 会转义损坏中文 → 必须 --data-binary @file）
  curl.exe -s -X POST "http://127.0.0.1:18765/api/feedback" --data-binary "@payload.json" -H "Content-Type: application/json"
  # T2 跑带 -D 的 java（PS 会拆 -D 参数 → 必须 cmd /c 整体包）
  cmd /c "java -Dfile.encoding=UTF-8 -cp out;lib\* org.junit.runner.JUnitCore TestSuite"
  # T3 git push 跳过凭据助手链（GCM 弹不可见交互框挂死 → 内嵌令牌 URL 也会被拦）
  git -c credential.helper= push origin master
  ```
- [ ] 中文进 URL/form → `[System.Web.HttpUtility]::UrlEncode($s,[Text.Encoding]::UTF8)`（PS5 专属，demo_plugin_repo 实战）
- [ ] PS 里 `git @{u}` 不识别 → 写全 `origin/master`
- [ ] GBK 控制台乱码：读**退出码**不读"脸"（输出乱码≠失败）
- [ ] curl 下载用重定向 `> file`，不 `-o` 写特殊路径（write error 23，demo_plugin_repo E2E 实战）
- [ ] 能用 Python/Java 发包就不用 PS 发包（demo_plugin_repo/aicopilot 共同收敛结论：HTTP 全走 Java/Python）

## 反例

- P03：同一类"PS5 中文/参数"问题在两款插件至少出现 4 次——每次都是"当时知道，现拼时忘了"。**模板化是唯一有效解**。

## v1.1 增补（复刻实践 2026-09-15）

- [ ] **源码对拍一律文件级断言，禁止从控制台/回显抄录字面量**（P27，A/C2/D 三路实践内独立复发 3 次）：exec 回显存在 DLP 掩码（`new`/`Secret123`→`***`）与 GBK 吞码点（✔➕◉→`?`）两类失真，抄录产物编译不报错但内容已错。对策：比对用 python 读文件做哈希/计数断言，回显只看退出码与行数。
