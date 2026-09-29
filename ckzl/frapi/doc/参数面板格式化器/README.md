<!--
KB_INDEX: {
  "title": "参数面板格式化器（FR Java API 版）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["ParamPanelFormatter", "java", "Designer", "API", "XML", "lib"],
  "summary": "> 2026-08-05 新增。目的：用 FR Java API 操作模板对象完成参数面板格式化， > 替代 Python 正则脚本（正则改 XML 易损坏模板完整性）。"
}
-->

# 参数面板格式化器（FR Java API 版）

> 2026-08-05 新增。目的：用 FR Java API 操作模板对象完成参数面板格式化，
> 替代 Python 正则脚本（正则改 XML 易损坏模板完整性）。

## 文件

| 文件 | 说明 |
|------|------|
| `ParamPanelFormatter.java` | 格式化器（watermark 默认 + label 分支） |

## 用法

```bash
# 编译（需 FR lib）
javac -encoding UTF-8 -cp "<FR_HOME>/webapps/webroot/WEB-INF/lib/*" ParamPanelFormatter.java

# 运行
java -cp "<FR_HOME>/webapps/webroot/WEB-INF/lib/*;." ParamPanelFormatter <cpt路径> [watermark|label]
```

逻辑：读模板 → 按原 y 分组重排控件 bounds（水印式 180px 均布 / Label 式配对）→
按钮右对齐 40px → `layout.setDesignWidth(panelW)` + `ui.setDesignSize(Dimension)`（两步缺一不可）→ 保存。

## ⚠ 运行环境限制（2026-08-05 实测）

`TemplateWorkBookIO` 磁盘读写依赖 **FR web 会话环境**：

| 尝试 | 结果 |
|------|------|
| fr-agent `/exec`（Nashorn, Designer JVM）直接 `readTemplateWorkBook(路径)` | `Fine-Engine_NS_Exception_ReadError`（所有报表一致，与文件无关） |
| 先 `new ConfigurationActivator().start()` 再读 | `cannot find extra session`（缺 web 会话） |
| `FineRuntime.start()` 后再读 | 同上 ReadError |

**可行运行通道（待落地）**：
- **a)** FR 报表服务器(webroot) web 环境下经 servlet/自定义类加载运行（环境完整）；
- **b)** fr-agent 扩展：Designer 打开目标模板后，经 Designer API 取**内存工作簿对象**
  格式化，再由 Designer 保存（避开磁盘读，见 fr-agent README）；
- **c)** 离线安全校验/格式化用 `fmt_panel_safe.py`（坐标级 XML 替换，改前改后 XML 校验 +
  备份 + 幂等自检，结构零改动）。

## 与 py 脚本的分工

| 场景 | 工具 |
|------|------|
| 离线快速格式化（不依赖 FR 环境） | `fmt_panel_safe.py`（推荐日常用） |
| 需要 FR 引擎语义（字体测宽/字典测宽/插件降级） | `ParamPanelFormatter.java`（环境就绪后） |
| 历史全量批处理 | `batch_optimize_cpt.py`（⚠ 有拆网格坑，慎用） |
