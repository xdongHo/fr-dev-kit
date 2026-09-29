<!-- KB_INDEX: {"title":"SN-03 工程骨架与 plugin.xml 门","stage":"pipeline-node","tags":["标准节点","开发","plugin.xml"],"keywords":["SN-03","plugin.xml","四道门","资源路径","BOM","改名残留"],"summary":"工程骨架标准节点：scaffold 生成 + plugin.xml 四道门（BOM/jartime/active/FunctionRecorder）+ 资源路径形式总表 + 改名残留机器检查，拦截 P04/P09/P10。"} -->

# SN-03 工程骨架与 plugin.xml 门（S3 开发·入口）

**类型**：标准节点（确定性，**机器检查**）｜**拦截**：P04 FR 资源路径形式（复发链）、P09 身份冲突、P10 批量改名连锁损坏
**输入**：架构一页纸｜**输出**：工程骨架 + 合规 plugin.xml｜**机器检查**：sn_gate `C01-C06, C08`

## 检查清单

### 3.1 骨架生成（一条命令，不手搓）

```powershell
python kfgj/plugin_pl\scripts\sn_scaffold.py --id com.fr.plugin.<名> --version 0.1.0 --vendor <域> --out <工程根>
```

生成：`plugin.xml`（无 BOM）、`build.cmd`、`src/`、`web/js`+`web/css`、`test/`、`docs/`、`sn_gate.config.json`（预填残留检查）、`README.md`。

### 3.2 plugin.xml 四道门（aicopilot 实战口径）

- [ ] **无 BOM**（UTF-8 无 BOM；sn_gate `C02`）
- [ ] `<jartime>` ≥ 2024-01-01（FR10 装载校验；sn_gate `C03`）
- [ ] `<active>yes</active>`
- [ ] 扩展点 class 全部真实存在（sn_gate `C04` 解析 extra-decision/extra-designer/extra-core 的 class 属性回查 src）
- [ ] `function-recorder` / `lifecycle-monitor` 按需声明（aicopilot 两者都有）

### 3.3 资源路径形式总表（P04 复发链，唯一权威表）

| 位置 | 形式 | 正例 | 反例 |
|---|---|---|---|
| Java `ScriptPath.build()/StylePath.build()`（类路径资源） | **斜杠，且不带前导 `/`** | `com/fr/plugin/<名>/web/js/x.js` | ❌ `com.fr.plugin.<名>.web.js.x.js` |
| JS/HTML/XML 里的 HTTP URL（`/webroot/decision/plugin/private/...`） | **点** | `.../private/com.fr.plugin.<名>/endpoint` | ❌ 斜杠形式（handlerMap.get 返回 null → 平台 404） |
| 插件类加载器 `getResourceAsStream` | **禁前导斜杠**；稳妥方案=部署时解包到用户目录用 File 读 | `getResourceAsStream("com/fr/...")` | ❌ `getResourceAsStream("/绝对路径")`（aicopilot v0.14.4 白帧事故） |
| Spring `@RequestMapping` | 注意**无尾斜杠**形态单独核对 | `@RequestMapping("/url/<名>")` | ❌ 替换规则只写了带尾斜杠形式导致漏改（demo_plugin_repo §9） |
| HttpHandler `getPath()` | **必须单段**（不含 `/`） | `"/<名>batch"` | ❌ `"/a/b"` |

- 机器检查：sn_gate `C05`（前导斜杠 getResourceAsStream）、`C06`（ScriptPath/StylePath 形式）、`C09`（getPath 单段，容许单个前导斜杠——aicopilot 实测 FR 兼容 `/ai_feedback`）
- `C08` 残留检查口径：关注**包名/类名字符串**残留；若命中来自目录路径文案（如硬编码的开发机路径），应同时转 `C12` 环境路径硬编码处理，两个检查项的处置动作不同
- 兜底口诀（demo_plugin_repo 实战）：`grep -rn "com[./]fr[./]plugin[./]<名>[^p]" src plugin.xml` + `grep -rn '"/url/<名>[^p]' src/` + `grep -rn 'plugin/private/com/' web/`（应为零命中）

### 3.4 批量改名纪律（P10）

- [ ] 多条替换规则**长模式优先**排序（先 `com.fr.plugin.demo_plugin_repo` 后 `com.fr.plugin.frdoc`）
- [ ] 正则点号转义：`com\.fr\.plugin\.frdoc\b(?!pro)`；点形式/斜杠形式分开写两条显式规则
- [ ] 替换后必跑残留 grep（`C08` 配置预填），产物含链式损坏（`propro`）即回滚

## 反例

- P04：demo_plugin_repo 第二轮"点杠修复"把 JS URL 的点形式也改成斜杠——修一个坑挖一个坑；aicopilot 前导斜杠导致 9 帧全 null。
- P10：demo_plugin_repo 批量改名产生 22 处 `demo_plugin_repopro`。

## v1.1 增补（复刻实践 2026-09-15）

- [ ] **C13 包声明与目录一致性**（新机器检查项，已实施）：每个 .java 的 package 声明必须与 src 下实际路径一致——javac 对目录错位零报错（P29，C2 现场发现），靠编译抓不住。
- [ ] C06 口径修订：文件名扩展名点号合法（`frdoc.js`），只有目录段含点（点形式包名）或前导斜杠才违规（实践断点-3：v1.0 曾误报 frdoc.js）。
- [ ] 身份表增补"类→包位置清单"（P33）：复刻/迁移时 ProgressHub 在根包、LicenseHandler 在 pro 包这类位置信息必须随身份表落盘，派单书按清单分配。
