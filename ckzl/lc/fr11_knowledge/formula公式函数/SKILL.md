<!--
KB_INDEX: {
  "title": "FR11 公式与函数 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["formula", "FR11", "公式", "层次坐标", "value", "references"],
  "summary": "--- name: fr11-formula description: 何时使用：编写 FR11 公式（formula）与函数（function）、层次坐标、动态格间运算、自定义函数，或排查公式报错、环比同比累计占比计算时使用。触发词：函数"
}
-->

---
name: fr11-formula
description: 何时使用：编写 FR11 公式（formula）与函数（function）、层次坐标、动态格间运算、自定义函数，或排查公式报错、环比同比累计占比计算时使用。触发词：函数、公式、层次坐标、SUM/IF/value/sql、seq、公式编辑器。
compatibility: FR11
---

# FR11 公式与函数 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/formula公式函数/references/formula_summary.md`；完整文档条目大表（doc-view ID + 标题 + 核心概念 + API）见本目录 `references\formula_summary.md`。

## 主题速览
- 关键词频次：函数 49 篇、公式 15 篇、单元格 9、自定义 9，层次坐标与各类函数概述是主干。
- 全类共 164 篇文档，doc-view ID 覆盖 116~5089，其中 39 篇提及 11.0.x 子ckzl/bb，0 篇解析失败。
- 覆盖：常用/数学/文本/日期/数组/逻辑等函数概述、层次坐标专题、动态格间运算、自定义函数与新计算引擎。

## 核心结论
- 报表执行分两步：报表计算（SQL 传库取数→扩展/汇总/关联/公式运算）与页面转换（XML→HTML），公式优化需分别对应这两个阶段。
- 层次坐标是复杂报表核心：相对层次坐标描述目标格与当前格位置关系，绝对层次坐标精确定位扩展后数据，&Cellx 取扩展位置；比较/占比/环比/累计/条件汇总等动态格间运算均基于它。
- 11.0.4 起推荐函数替代层次坐标老写法：ACCSUM 求累计、MOM 算环比、PROPORTION 算占比、SORT 排名、SUMIFS/COUNTIFS 条件求和/计数；注意层次坐标函数只支持单元格计算，不支持 sheet、水印、JS 引用、参数默认值。
- 页合计用 sum({Cell}) 且需设重复结尾行；组合计用 sum(Cell) 并把父格设为分组字段所在单元格。
- 坑点：加号拼接数字字符串会变成数字相加（如 001+1201110 得 1201111），应改用 CONCATENATE；浮点求和精度误差（123456.409999996 类）用 round() 按位四舍五入；average() 不支持日期，需 datetonumber()→average()→todate() 中转。
- 序号：seq() 或 =&cell，所在单元格必须设置父格才生效；week() 逻辑与 Excel 一致，星期天为一周第一天，一年第一周须从周日开始。
- 填报插入/删除行会触发公式重计算，而数组函数、层次坐标、条件筛选函数不支持重计算，可能出现结果与预期不一致。
- 取数函数选择：value() 按条件直接取数据集行列；ds1.find() 免遍历直接检索，比 SELECT 类数据集函数快；sql() 函数免建数据集直连库取值；map() 先检索模板数据集再检索服务器数据集。
- 自定义函数：实现 com.fr.script.AbstractFunction 的 run(Object[])，经「服务器>函数管理器」加载后可当公式使用；run 内 getCalculator().getCurrentColumnRow() 可获取公式所在单元格。
- 报错要点：单元格计算死循环（错误代码 11300003）多因公式直接/间接引用自身；11.0.2 起公式含回车/tab 时无法精准返回错误位置，光标默认回到首位。

## 关键 API 与版本要点
- 11.0.1：公式编辑框新增「输入提示」「关闭前检查」，最外层可调整大小；11.0.3：多 sheet/多报表块模板的公式报错可定位到具体 sheet/报表块。
- 11.0.4：新增 ENDOFMONTH、ISWORKDAY、NUMTOZH；ACCSUM/SUMIFS/COUNTIFS/PROPORTION/MOM/SORT 函数上市；TOIMAGE 支持 jpg/png/bmp 分格式缓存，避免导出体积暴涨。
- 11.0.5：新增 TEXTGETNUM、ENBYSTRNUM、GCD、LCM；「导出/编辑结果时保留公式」支持导出 Excel 保留公式（仅原样导出，不支持分页/分页分Sheet导出）。
- 11.0.7：ACCSUM/COUNTIFS/SUMIFS 适配图表模块；11.0.12：新计算引擎下新增冻结「结尾区域」。
- 常用 API：TOIMAGE(path[,缓存,宽,高])、treelayer(树对象, 层级, 返回类型, 分隔符)、value(数据集,列号[,条件])、NVL 返回第一个非空值、LET 定义局部变量简化长公式。

## 深入查询
遇到本主题具体问题，读取 `references\formula_summary.md` 查 doc-view 原始条目与 ID。
