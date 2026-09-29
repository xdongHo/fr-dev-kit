<!--
KB_INDEX: {
    "title": "公式函数不存在致no function found刷屏分析",
    "stage": "error-analysis",
    "tags": [
      "错误案例",
      "🔥新沉淀",
      "公式",
      "高亮条件",
      "函数白名单"
    ],
    "keywords": [
      "no function found",
      "ISNUMBER",
      "NVL",
      "公式函数",
      "引擎注册表",
      "com/fr/function",
      "fr_check盲区",
      "语法合法但函数不存在",
      "Excel函数迁移",
      "check_cpt_integrity.py",
      "高亮条件",
      "条件属性"
    ],
    "summary": "高亮条件公式写 AND(ISNUMBER($$$),$$$>0.002)，FR10 引擎 187 个注册函数类中根本没有 ISNUMBER（Excel 思维迁移陷阱）——XML 合法+fr_check 通过但每次计算服务端刷 no function found（实测单日 6120 条），单元格高亮静默失效；三层证据定位法（jar 扫描/官方清单/日志计数）、NVL($$$,0)>0.002 替换样板与公式函数白名单检查工具化（check_cpt_integrity.py 检查2；2026-09-06/07 示例实际表/预算 各 204 处实战）"
  }
-->

# 公式函数不存在致 no function found 刷屏分析

> 实战来源：2026-09-06/07 示例报表工程/明细报表 示例实际表.cpt / 示例预算表.cpt，条件属性/高亮条件公式各 204 处使用 `ISNUMBER`，FR10 引擎无此函数。
> 检查工具源起 `kfgj/fzpy\check_cpt_integrity.py`（2026-09-07 三合一完整性体检，本文 §5 有用法）。

---

## 1. 现象

模板正常打开、不弹任何错误；带高亮条件的单元格（如"超0.2%黄底"）**高亮静默失效**。服务端日志被同一句刷屏：

```
no function found ... ISNUMBER
```

实测**单日 6120 条**（每格每次计算都撞一次）。而落盘前两道常规校验全绿：`ET.parse` XML 合法、`fr_check.py` 通过——**"语法合法 + fr_check 通过"但"函数根本不存在"**。

## 2. 根因与盲区本质

高亮条件公式把 Excel 函数名直接搬进了 FR：

```xml
<Condition class="com.fr.data.condition.FormulaCondition">
<Formula>
<![CDATA[AND(ISNUMBER($$$), $$$ > 0.002)]]></Formula>
</Condition>
```

`AND` 是引擎注册函数（有），`ISNUMBER` **不是**（没有）。FR 公式与 Excel 函数名只是"部分像"，ISNUMBER/SUMIF/VLOOKUP/IFERROR 等 Excel 高频名在 FR10 引擎里并不都存在（判空对应品是 `ISNULL`，空值参与比较前的归零习惯写法是 `NVL(x,0)`）。

**盲区本质**：`fr_check` 校验公式**语法**（括号闭合、`$$$` 引用等），**不校验函数名是否在引擎注册表内**——"语法合法但函数不存在"是检查盲区。引擎对未知函数也不抛模板级异常，只在每次求值时记一条 `no function found` 并按空处理，于是高亮失效且无弹窗，只剩日志刷屏一条线索。

## 3. 定位方法：三层证据 + 引擎函数清单

1. **日志归因**：从服务端日志抓 `no function found` 行，取函数名（本例 `ISNUMBER`），同时拿到量级（每日 6120 条 = 每格每次计算撞一次，可反推受影响格子数级）。
2. **jar 全扫描（引擎注册表实证）**：FR10 引擎函数 = `WEB-INF\lib` 各 jar 中 `com/fr/function/` 包的顶层注册类。实测 32 个 lib jar（209 含 plugins）共 **187 个顶层函数类**，无 `ISNUMBER`：

   ```python
   import zipfile, glob
   names = set()
   for jp in glob.glob(r'...\WEB-INF\lib\*.jar'):
       z = zipfile.ZipFile(jp)
       names |= {n[:-6].rsplit('/',1)[-1] for n in z.namelist()
                 if n.startswith('com/fr/function/') and n.endswith('.class') and '$' not in n}
   print('ISNUMBER' in names)   # False
   print('NVL' in names)        # True
   ```

3. **官方清单比对**：帆软帮助文档函数清单（如 doc-842 等 NVL 条目所在函数总表）中亦无 ISNUMBER——三层证据（日志/jar/文档）闭环，排除"版本差异/插件函数"的可能。

清单提取与比对已工具化：`check_cpt_integrity.py` 检查2（`--fr-home` 实时扫 jar 生成白名单缓存，无 jar 时用内嵌名单），公式按词法提取"标识符+`(`"函数名（大小写不敏感比对，FR 公式 `year(now())` 即 `YEAR`/`NOW`），不在注册表内的逐函数报次数、格位与例句。

## 4. 修复：NVL 归零替换法

判空后比较的场景，用引擎函数 `NVL(x, 归零值)` 替代 `ISNUMBER` 守卫（NVL 为官方文档 doc-842 收录函数）：

```xml
<!-- ❌ 修前：ISNUMBER 不存在，高亮静默失效 -->
AND(ISNUMBER($$$), $$$ > 0.002)

<!-- ✅ 修后：空值归零再比较，正数照常触发 -->
NVL($$$, 0) > 0.002
```

要点：
- `$$$` 引用本格，`NVL($$$,0)` 把空值/非数归 0，比较语义与"是数字且大于阈值"等价（本报表场景下格子只会是数值或空）；
- 示例实际表/预算 **各 204 处**已批量替换，修后 `check_cpt_integrity.py` 检查2 PASS、日志不再刷 `no function found`；
- 若场景需要显式区分"非数字"，FR 侧可用 `ISNULL`+类型转换组合，不要照搬 Excel 名。

## 4.5 判数问法正解（别名：判断是否数字 ISNUMBER / 条件属性判数）
- FR 引擎无 ISNUMBER（§2 根因, §3 三层证据）。判数/判空正解按序:
  1. 归零比较: `NVL($$$,0) > 阈值`（§4 实证样板, 高亮/条件公式通用）
  2. 纯判空: `ISNULL(x)`（引擎对应品）
  3. 写前白名单自检: check_cpt_integrity.py 检查2 / jar com/fr/function/ 扫描（§3 定位法）
- LEN/正则等文本判数式为社区旁路、本库未实测备案——采用前先过 fr-agent/eval_formula.js 引擎验证。

## 5. 预防

1. **落盘前公式函数白名单检查（工具化已实现）**：`python check_cpt_integrity.py <a.cpt> --fr-home <FR根>`，检查2 对全部 `<Formula>` 与 `com.fr.base.Formula` 单元格值公式提取函数名逐一比对引擎注册表，未注册即 FAIL 并给格位；生成器/批量改写脚本应在落盘前调用，FAIL 即不落盘。
2. **fr_check 待补规则（登记 R-0004，未实现）**：公式函数名 ∈ 引擎注册表校验——白名单可由 `com/fr/function/` 扫描生成缓存（工具已带 2026-09-07 内嵌 181 名降级名单）。
3. **Excel 思维迁移警告（写公式纪律）**：FR 公式函数名与 Excel 只是"部分重叠"，写任何不常用于 FR 的函数名前，先查引擎清单（§3 一段脚本 10 秒出结果），不凭 Excel 记忆落笔。

## 6. 触发案例

从 Excel 报表迁移/仿制公式时最高发：条件属性、高亮条件、数据列过滤公式里用 `ISNUMBER`/`ISERROR` 等 Excel 味函数名。2026-09-06/07 示例实际表.cpt / 示例预算表.cpt 的"超0.2%黄底"高亮条件（各 204 处 `AND(ISNUMBER($$$), $$$ > 0.002)`）即此模式；同批修好的 `NVL($$$,0) > 0.002` 为正确参照。
