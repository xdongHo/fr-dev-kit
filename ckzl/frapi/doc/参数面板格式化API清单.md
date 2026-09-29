<!--
KB_INDEX: {
    "title": "FR 10.0 Java API — 参数面板格式化脚本参考",
    "stage": "api-reference",
    "tags": [
      "API清单",
      "参数面板",
      "格式化",
      "Java"
    ],
    "keywords": [
      "ParameterUI",
      "BoundsAttr",
      "setDesignWidth",
      "控件定位",
      "保存"
    ],
    "summary": "参数面板格式化的 FR Java API 清单：读取→重排 bounds→设置面板尺寸→保存的完整方法签名"
  }
-->

# FR 10.0 Java API — 参数面板格式化脚本参考

> 提供给 Claude/其他 AI 编写脚本的 API 清单与注意事项。
> 标注 ⚠待核 的需在实际环境中反编译或 IDE 补全核对。

---

## 一、模板读写

> ⚠ **本文档为 API 层**，常量（CTRL_MIN/CTRL_MAX/GRID 等）与布局算法流程见《参数面板自动布局算法规范》。文档间用 § 号互相引用。
>
> 本文常量速查（完整定义见算法规范 §2）:
> | 常量 | 值 | 含义 |
> |------|-----|------|
> | `GRID` | 12 | 网格单位 |
> | `CTRL_H` | 24 | 控件高度 |
> | `CTRL_MIN` | 96 | 控件最小宽 |
> | `CTRL_MAX` | 220 | 控件最大宽 |
> | `BTN_MIN` | 72 | 按钮最小宽 |
> | `BTN_MAX` | 168 | 按钮最大宽 |
> | `PAD_V` | 12 | 面板上下边距 |
> | `ROW_GAP` | 12 | 行间距 |
> | `CTRL_GAP` | 24 | 列间距 |
> | `TREE_INDENT` | 18 | 树层级缩进 |

```java
com.fr.io.TemplateWorkBookIO
    static TemplateWorkBook readTemplateWorkBook(String path)
    static void writeTemplateWorkBook(FILE file, TemplateWorkBook wb)   // ⚠待核 参数类型

com.fr.main.TemplateWorkBook                 // 接口
com.fr.main.impl.WorkBook                    // .cpt 实现
com.fr.form.main.Form                        // .frm 实现
```

**初始化**: FR10 通常 `com.fr.runtime.FineRuntime.start()` + `EnvContext`。⚠待核。

---

## 二、参数面板容器

```java
// cpt 路线
com.fr.report.parameter.ReportParameterAttr  // ⚠ 包名待消歧:kit 内 com.fr.main.parameter.ReportParameterAttr 与 com.fr.report.parameter.ReportParameterAttr 两种写法并存,须 Class.forName 确认后择一,另一处标注「历史误记,勿用」(doc-4508);核准前生成器按双候选 Class.forName 兜底
    ParameterUI getParameterUI()
workBook.getReportParameterAttr()

// frm 路线
com.fr.form.main.parameter.FormParameterUI
    getParameterUI()

// 最终容器
com.fr.form.ui.container.WParameterLayout
    int getWidgetCount()
    Widget getWidget(int i)
    BoundsWidget getBoundsWidget(Widget w)
    int getDesignWidth() / void setDesignWidth(int)

// 面板尺寸（高度写入口在此，不在 Layout！）
com.fr.form.main.parameter.FormParameterUI
    java.awt.Dimension getDesignSize()
    void setDesignSize(java.awt.Dimension)
    // ⚠ setDesignSize() 和 setDesignWidth() 是两套独立 API，不互相同步
```

### 宽度/高度写入（已验证）

| 属性 | XML 标签 | 写入 API | 说明 |
|------|---------|---------|------|
| 宽度 | `Design_Width design_width="..."` | `WParameterLayout.setDesignWidth(int)` | |
| 宽度+高度 | `<DesignAttr width="..." height="...">` | `FormParameterUI.setDesignSize(Dimension)` | **高度唯一写入口** |

> `Design_Width` 和 `DesignAttr width` 是同一份数据的两种序列化，改一处两处同步。高度只有 `DesignAttr height`。两个 API 必须分别调用：

```java
// 宽度 + 高度，两步缺一不可
layout.setDesignWidth(avail);
formParameterUI.setDesignSize(new Dimension(avail, designH));
```

**踩坑点**：
- 只调 `setDesignWidth` → 高度不更新
- 只调 `setDesignSize` → 宽度两份一致没问题，但 Dimension 里的 width 必须和 avail 一致，否则两处宽度值打架
- 先写 `setDesignWidth(avail)`，再用同一个 `avail` 构造 `Dimension` 写高度，最安全

---

## 三、坐标尺寸读写

```java
com.fr.form.ui.container.WAbsoluteLayout.BoundsWidget
    java.awt.Rectangle getBounds()
    void setBounds(Rectangle r)
```

**这是唯一的坐标写入口。**

---

## 四、控件类型全列表

### Widget 基类（必用）
```java
com.fr.form.ui.Widget
    String getWidgetName() / void setWidgetName(String)
    int getListenerSize()
    com.fr.form.event.Listener getListener(int i)
```

### 输入类
| 类 | 说明 |
|---|------|
| `com.fr.form.ui.TextEditor` | 文本输入 |
| `com.fr.form.ui.NumberEditor` | 数字输入 |
| `com.fr.form.ui.Password` | 密码 |
| `com.fr.form.ui.TextArea` | 多行文本 |
| `com.fr.form.ui.DateEditor` | 日期选择 |
| `com.fr.form.ui.FileEditor` | 文件上传 |
| `com.fr.form.ui.MultiFileEditor` | 多文件上传 |
| `com.fr.form.ui.ListEditor` | 列表编辑 |
| `com.fr.form.ui.RegexFieldEditor` | 正则校验 |
| `com.fr.form.ui.TreeEditor` | 树形控件 |
| `com.fr.form.ui.TreeComboBoxEditor` | 下拉树 |

### 选择类
| 类 | 说明 |
|---|------|
| `com.fr.form.ui.ComboBox` | 单选下拉 |
| `com.fr.form.ui.ComboCheckBox` | 多选下拉 |
| `com.fr.form.ui.CheckBox` / `CheckBoxGroup` | 复选框 |
| `com.fr.form.ui.Radio` / `RadioGroup` | 单选框 |

### 显示类
| 类 | 说明 |
|---|------|
| `com.fr.form.ui.Label` | 文本标签 |

### 按钮类
| 类 | 包 | 说明 |
|---|-----|------|
| `FormSubmitButton` | `com.fr.form.parameter` | 查询按钮（内置） |
| `FreeButton` | `com.fr.form.ui` | 自由按钮（JS 动作） |
| `Button` | `com.fr.form.ui` | 普通按钮 |
| `ToggleButton` | `com.fr.form.ui` | 切换按钮 |

### 内嵌块（特殊处理）
| 类 | 说明 |
|---|------|
| `com.fr.form.ui.ElementCaseEditor` | 内嵌报表块 |
| `com.fr.form.ui.ChartEditor` | 图表块 |

> 这两个不该参与行打包——尺寸是作者刻意设定的，被 clamp 到 220 会直接毁掉。
> **处理规则**: 识别后标记为 `PRESERVE`，保留原 bounds 原样写回，只参与重叠检测。这是「坐标纯输出」原则唯一需要开的例外口子。

### 树控件宽度
`TreeEditor` / `TreeComboBoxEditor` 宽度算法与普通下拉不同，需要加层级缩进余量 `TREE_INDENT`，漏判会走 `OTHER` 分支被兜到 `CTRL_MIN = 96`，树内容一定截断。

### 插件
| 类 | 全限定名 |
|---|---------|
| `YearControl` | `com.fr.plugin.widget.year.YearControl` |

> **instanceof 顺序**: ComboCheckBox 与 ComboBox 有继承关系（⚠待核方向），必须先判子类。FormSubmitButton 也在 Button 体系内，同理先判它。

---

## 五、读取 JS 动作（按钮排序）

```java
com.fr.form.event.Listener
    String getEventName()
    com.fr.js.JavaScript getAction()

com.fr.js.JavaScriptImpl
    String getContent()                        // ✅ 已确认
```

匹配建议：用语义特征（"导出报表调用"/"校验写回调用"），不精确匹配函数名。排序判错无害（按钮多/少不会崩），宁松勿紧。

### 按钮文案获取（✅ 已验证部分场景，兜底逻辑保留）
`FormSubmitButton.getText()` 继承自 `Button`，返回 `String`。实际模板里文案通常有值（如 `"Query"`），但空值时 `getText()` 返回 `null` 还是 `""` 未复现到——因为样本本身不为空。兜底逻辑覆盖两种空值，去掉无益只增加回归风险：
```java
String text = (w instanceof FormSubmitButton) ? nullSafe(((FormSubmitButton) w).getText()) : "";
if (text.isEmpty() && w instanceof FormSubmitButton) text = "查询";   // 默认文案兜底
```

---

## 六、候选值测宽（可选）

```java
com.fr.data.Dictionary                         // 接口
com.fr.data.impl.TableDataDictionary
comboBox.getDictionary()                       // ⚠待核 方法名
```

**强烈建议**: 候选值测宽做成可选能力。⚠运行期取字典值需要数据连接可用，脚本跑在无数据源环境会直接抛异常。

**catch 范围**: 必须覆盖整个取值链路（含连接失败、超时），不只是 `NoSuchMethodError`。失败即静默回退，不要阻塞格式化流程。

**回退值 156px 推导**: `(CTRL_MIN + CTRL_MAX) / 2 = (96 + 220) / 2 = 158`，量化到 12 的倍数 → **156**。调了 `CTRL_MIN/MAX` 后这个数要同步重算。

---

## 七、字体测量

```java
com.fr.base.FRFont
    static FRFont getInstance(String name, int style, float size)

com.fr.base.GraphHelper                         // 先查有没有现成测宽方法
    // 若有就优先用，因为它和 FR 自身渲染口径一致
```

若 `GraphHelper` 上没有现成方法，AWT 兜底（无头环境）：

```java
-Djava.awt.headless=true

static double measureText(String text, java.awt.Font font) {
    java.awt.Graphics2D g = PROBE.createGraphics();
    try {
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, ...);
        return g.getFontMetrics(font).getStringBounds(text, g).getWidth();
    } finally { g.dispose(); }
}
```

防漂移: 预生成字符宽度表，运行时查表——最稳，推荐跨环境复现场景。

---

## 八、插件可用性检测

```java
// 最简单的方式
try {
    Class.forName("com.fr.plugin.widget.year.YearControl");
    return true;
} catch (ClassNotFoundException e) {
    return false;
}
```

> ⚠ **重要限制**: 只能判「类在不在 classpath」，不能判「插件是否被禁用」。
> 后果：插件被禁用时类仍在 classpath 上，`Class.forName` 返回 true → 不降级 → 模板照写 `YearControl` → **运行时打不开**。这是真实会发生的坑。

如有 `com.fr.plugin.manage.PluginManager` / `PluginContexts` 可用则优先，否则至少用 `Class.forName` 时带日志告警。

### 降级时机（⚠ 必须在测宽之前）
插件不可用时，`YearControl` 降级为单选下拉（`ComboBox`），宽度从 96 调到 **108**（多出下拉箭头位 12px）。**降级必须在 `measureAll(ir)` 之前完成**（对应算法规范 §3.5），否则测宽用的是降级前的 96，写回后控件偏窄显示不全。

---

## 九、脚本骨架（六阶段）

```java
public void format(String templatePath, int availWidth) {
    TemplateWorkBook wb = TemplateWorkBookIO.readTemplateWorkBook(templatePath);
    FormParameterUI ui = resolveParamUI(wb);             // ⚠ 取 ParameterUI 对象，不是 Layout
    WParameterLayout layout = (WParameterLayout) ui.getContainer();
    if (layout == null) return;

    // 阶段一：降级检测 + IR 构建（坐标只用于排序，排序后丢弃）
    //        含 YEAR 降级 (§8) 和 PRESERVE 标记 (§4)
    List<Field> ir = buildIR(layout);
    Set<String> idsBefore = idSet(ir);                  // §8.2 第 6 条：不丢控件断言基线

    // 阶段二~五
    measureAll(ir);                                      // 降级必须在测宽之前
    List<List<Field>> rows = packRows(filters(ir));      // PRESERVE 不参与行打包
    ColumnMetrics cols = alignColumns(rows);
    assignFilterBounds(rows, cols);
    ButtonPlacement bp = placeButtons(actions(ir), rows, cols);

    // 阶段五之后、designH 之前：PRESERVE 块平移（依赖 rows 已排完）
    placePreserveBlocks(ir, rows);

    // 阶段六：验证 → 写入
    // PRESERVE 块排在所有普通行之下，designH 取普通行与保留块的最大值
    int designH = Math.max(
        PAD_V * 2 + rows.size() * CTRL_H + (rows.size() - 1) * ROW_GAP,
        maxPreserveBottom(ir) + PAD_V);
    assertLayoutValid(ir, idsBefore, avail, designH);   // 失败即抛，不回写
    applyToTemplate(layout, ui, ir, avail, designH);     // 唯一步写入: width→Layout, height→ui
    TemplateWorkBookIO.writeTemplateWorkBook(toFILE(templatePath), wb);
}
```

### `idsBefore` 说明
**这不是幂等校验**，是「不丢控件」断言：写回前比对字段集是否完全一致，防止某个筛选项在打包/对齐过程中被静默丢掉。幂等校验是另一回事——跑完两遍比对输出文件 MD5（见第十节第 4 条），发生在 `format()` 之外。两者防的失效模式不同：前者防丢控件，后者防「有人偷偷加了读旧坐标做决策的逻辑」。

### Label 配对规则
1. 同一视觉行内（y 差 < CTRL_H）找左侧最近 Label
2. 水平间距 > CTRL_GAP × 2 不配对
3. 一个 Label 只能配对一次，冲突报错
4. 命名约定匹配优先（如 `lbl_dept` ↔ `dept`），坐标兜底

### PRESERVE 块位置规则
PRESERVE 块（内嵌报表/图表）不参与行打包，**一律排在所有普通行之下**。普通行从 `PAD_V` 起算，PRESERVE 块整体平移到最后一行的 `y + CTRL_H + ROW_GAP` 位置——这样重叠检测天然通过，避免保留原 y 与新布局行撞上。

### 写入两步法（宽度→Layout，高度→ParameterUI）

```java
void applyToTemplate(WParameterLayout layout, FormParameterUI ui,
                     List<Field> ir, int avail, int designH) {
    for (Field f : ir) {
        setBounds(layout, f.ref, f.ctrlRect());
        if (f.labelRef != null) setBounds(layout, f.labelRef, f.labelRect());
    }
    // 宽度
    layout.setDesignWidth(avail);
    // 高度（唯一写入口，必须在 ParameterUI 上）
    ui.setDesignSize(new Dimension(avail, designH));
}
```

---

## 十、工程注意事项

1. **备份**: 改模板前先备份，加 `--dry-run` 模式
2. **文件锁**: 设计器打开模板时脚本行为不确定，先全部关闭
3. **版本兼容**: `writeTemplateWorkBook` 会按当前引擎版本重写，可能升级模板格式
4. **幂等验证**: 同一模板连跑两次，比较输出文件 MD5——抓住所有「坐标又被当输入用了」的回归
5. **候选值测宽**: 设为可选，失败不阻塞；catch 覆盖整个取值链路（连接失败/超时/NoSuchMethod）
6. **树控件宽度**: `TreeEditor`/`TreeComboBoxEditor` 需加 `TREE_INDENT` 层级缩进余量
7. **内嵌块**: `ElementCaseEditor`/`ChartEditor` 标记 `PRESERVE`，原样保留，只参与重叠检测
