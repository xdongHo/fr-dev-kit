<!--
KB_INDEX: {
  "title": "kfgj/xlyl — 无服务器渲染验证工具（fr_render）",
  "stage": "render-preview",
  "tags": ["渲染", "预览", "验证", "headless", "无服务器", "G12"],
  "keywords": ["kfgj/xlyl", "render_check", "expect_manifest", "headless", "无服务器渲染", "G12", "Layer4", "断言", "VanChart", "FRM组件", "EmbeddedTableData", "backend", "RenderCLI", "injected"],
  "summary": "脱离 FR 服务器/设计器完整环境的渲染验证工具：期望清单提取(expect_manifest) + 可插拔渲染后端(render_check: manifest/java/injected) + guard G12 headless 通道。80 样本回归基线(38cpt+41frm, 39带图表, 84内嵌数据集免DB)。"
}
-->

# kfgj/xlyl — 无服务器渲染验证工具

> **立项背景（2026-08-22）**：现行验证只能"起服务器→浏览器人眼预览"，服务器加载无关内容耗资源、加密/平台架构造成干扰。
> **目标**：脱离服务器环境，对 cpt/frm 完成 **解析→(模拟数据)计算→HTML 渲染→结构化断言**。
> 与 web_kit 的分工：要**起真浏览器跑运行期体检**（JS 异常/空表格/控件重叠/必填校验/截图，需 FR 服务器）→ `web_kit/probe.py`（口语问法「交付前模拟真实浏览器打开页面过一遍」即它）；本文是**不起服务器**的离线渲染断言档位（G12 headless 通道）。

## 架构（三件套 + 可插拔后端）

```
模板.cpt/frm ──► expect_manifest.py ──► 期望清单(结构事实) ─┐
       │                                                   ├─► 断言(R1-R7) ─► JSON 报告
       └──► render backend ──────────► 渲染 HTML ──────────┘
            ├─ manifest   dry-run(零依赖,回归基线)
            ├─ java       独立 headless JVM(Phase 1, 探针A 定可行性)
            └─ injected   设计器 JVM fr-agent /exec(Phase 1, 探针B 定可行性)

kfgj/guard.py --render [--render-backend X] → G12 自动判定(PASS/FAIL/WARN回退人工)
```

## 用法

```bash
# 期望清单（零依赖）
python kfgj/xlyl/expect_manifest.py ckzl/hbfa --out manifest.json
python kfgj/xlyl/expect_manifest.py 模板.cpt --check 渲染产物.html   # 断言模式

# 编排层（backend 可插拔）
python kfgj/xlyl/render_check.py 模板.cpt --backend java
python kfgj/xlyl/render_check.py ckzl/hbfa --backend injected --html-dir out/

# guard G12 headless 通道（不传 --render = 原人工通道, 向后兼容）
python kfgj/guard.py --task create --cpt x.cpt --attest G08,G09,G11 --render
python kfgj/guard.py --task format --cpt x.cpt --attest G10 --render --render-backend injected
```

## 断言规则（R1-R7）

| # | 规则 | 判定 |
|---|------|------|
| R1 | 静态文本出现在输出 | cpt 高置信；frm 图表容器化场景降 WARN |
| R2 | 数据集痕迹（ds 名/数据引用） | WARN 级（导出形态依 backend） |
| R3 | sheet 名出现 | WARN 级 |
| R4 | 图表容器存在（svg/canvas/chart 痕迹） | FAIL 级（声明了图表却无容器=渲染失败） |
| R5 | HTML 文档形态（`<html/DOCTYPE`） | FAIL 级 |
| R6 | 输出体量 >500B | FAIL 级（防空渲染） |
| R7 | FRM 组件痕迹（类名 histogram 抽查） | WARN 级 |

## 回归基线

`samples_manifest.json`：ckzl/hbfa 80 样本（38 cpt + 41 frm）。
- 39 个带图表（VanChart 166 处）· 84 个 EmbeddedTableData（**免数据库**即可计算）
- 期望清单覆盖：单元格网格/数据集/图表/参数面板/FRM 组件树(类直方图+BoundsAttr 坐标)

## 探针结论（Phase 0 完成, 2026-08-22/24）

| 探针 | 路线 | 结论 |
|------|------|------|
| C 资产盘点 | — | ✅ 关键：`readTemplateWorkBook` 磁盘读不可用；Layer4/5 缺口确认；静默失败模式是渲染层断言核心猎物 |
| A 独立 JVM | java backend | ❌ **不可行**（`probeA_独立JVM渲染_否定结论.md`）。三重阻断：FineAssist 需 Attach API → FinePluginBridge 加密(magic 0x03030309) → EntityDao 需模块链。FR10/11 无差异 |
| B 注入设计器 | injected backend | ✅ **可行**（`probeB_注入渲染_肯定结论.md`）。`readStream → ActorFactory.getActor('page') → execute → PageRWorkBook` 全通；PDF/Excel 导出成功；内置 HTMLExporter 是 stub（HTML 需手动拼格）；单次往返 ~2.2s |

## 渲染链（最终实现）

**injected backend（主路线）**：`injected_render.js`（占位符模板）
- [1] 解析：`com.fr.main.impl.WorkBook.readStream(FileInputStream)`（设计器 JVM 已初始化，天然绕过探针A三重阻断）
- [2] 计算：`com.fr.stable.ActorFactory.getActor('page')`（注意：在 com.fr.stable 不在 fun 包）→ `execute(Map, Actor)` → `PageRWorkBook`
- [3] 遍历：`getReport(Integer.TYPE)`（**原始类型必须用 Integer.TYPE，forName 不支持**）→ `cellIterator` 逐格 {c,r,cs,rs,t,v}
- [4] 产物：**结构化 JSON**（单元格级数据——最强断言载体，优于 HTML 正则与 Excel）
- 坑：设计器 JVM 的 CWD ≠ 驱动进程 → 模板/产物路径必须**绝对路径**

**断言器三级路由**（render_check.py 按产物扩展名自动选）：
| 产物 | 断言器 | 强度 |
|------|--------|------|
| `.json`（injected） | `json_assert.py` J1-J5 | 单元格级（J3 专猎"图表静默不渲染"） |
| `.xls/.xlsx` | `excel_assert.py` X1-X5 | 单元格级（FR 导出的 .xls 实为 OOXML，按魔数分流） |
| `.html`（skeleton） | R1-R7 | 正则级 |

## 架构决策（Phase 0 收敛）

1. **java backend 判死**（探针A否定）；**injected 主押**（探针B肯定+本机独立复现）；**skeleton 兜底**（纯Python离线布局）；server backend 备选未实现。
2. **期望侧/渲染侧解耦**：manifest 纯 Python 提取，后端只产物，断言器按产物类型路由。
3. **ENV/FAIL 分离**：后端缺失/超时=ENV（guard 降级 WARN 回退人工）；断言不过=FAIL。
4. **自研渲染引擎不做**（500+ XML 节点 + 500+ 公式 + VanChart 私有格式）。

## 设计决策记录

1. **期望侧与渲染侧解耦**：manifest 提取纯 Python（路线无关），后端只管产物（JSON/Excel/HTML），断言器按产物类型路由——后端可替换、可并行发展。
2. **ENV/FAIL 分离**：后端缺失/超时/不可达 = ENV（guard 降级 WARN 回退人工），渲染成功但断言不过 = FAIL（真失败）。
3. **图表断言取保守策略**：引擎侧 HTML 只含容器+JS 引用，视觉断言需无头浏览器（Layer 5 范畴，本期不做，R4 以容器存在为准）。
4. **测试集天然免 DB**：骨架样本全用 EmbeddedTableData，渲染计算无需数据库连接。

## 验收记录（2026-08-22, 本机 FR11 设计器 JVM + fr-agent）

| 验收项 | 结果 |
|--------|------|
| 80 样本全量回归（injected） | ✅ **80/80 渲染成功, 0 FAIL**（39 cpt 全计算渲染 + 41 frm 组件树物化; WARN 均为真实环境事实: J5 sheet 名降级 / J7-J8 插件未装） |
| 单样本往返 | ~2.2s（探针B实测） |
| guard G12 headless 通道 | ✅ cpt/frm 双形态 PASS（`--render --render-backend injected`） |
| 静默失败猎手验证 | ✅ J8 实捕 `WidgetErrorMarker`：骨架模板声明的 RHIframe 插件控件在未装插件的 FR11 上被静默替换——**立项目标场景首战命中** |

## 已验证导出 API 速查（injected 路线，探针B 实测）

| 类 | 方法 | 状态 | 用途 |
|----|------|------|------|
| `com.fr.io.exporter.PDFExporter` | `export(OutputStream, ResultWorkBook)` | ✅ 46KB 落盘 ~11.5s | 人工审阅交付物 |
| `com.fr.io.exporter.ExcelExporter` | `export(OutputStream, ResultWorkBook)` | ✅ 39KB 落盘 ~11.5s | 人工审阅/excel_assert 断言 |
| `com.fr.io.exporter.HTMLExporter` | `export(...)` | ❌ **stub**（"Not support yet!"） | FR 的 HTML 走 Web 请求管线，注入式不可复用 |
| （本工具 JSON 产物） | injected_render.js 逐格物化 | ✅ ~2.2s | **自动断言首选**（单元格级数据直出） |

> FR 导出的 `.xls` 实为 OOXML（ZIP 魔数），openpyxl 按魔数改名可读（excel_assert.py 已处理）。

## 已知边界

1. **cpt sheet 名**：ResultWorkBook 侧无公开 getter，J5 降级 WARN（XML 层由 fr_check 覆盖）。
2. **frm 图表视觉**：FRM 渲染=组件树物化（结构层）；图表像素级视觉验证属 Layer 5，需无头浏览器，未做。
3. **FR 内置 HTMLExporter 是 stub**（"Not support yet!"）——JSON 产物路线反而是更优解（单元格级数据直出）。
4. **设计器 JVM 依赖**：injected 需设计器运行中（`python fr-agent/inject_fr11.py --start` 一键拉起+注入）；设计器未开时 guard G12 自动降级 WARN 回退人工通道。

## 关联

- `kfgj/guard.py` G12 headless 通道（--render）· `kfgj/EXEC_CONTRACT.md` G12 定义
- `kfgj/fzpy/fr_check.py` Layer 1/1.5/2/3（本工具补 Layer 4）
- `kfgj/fzpy/template_snapshot.py`（纯 Python XML 解析的先例与基础）
