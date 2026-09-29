# -*- coding: utf-8 -*-
"""追加 示例驾驶舱工艺路线 R-006~R-009 到 build_kb.py，挂脚本到 build_5m1e.py"""
import io, re
import os
BASE = os.path.dirname(os.path.abspath(__file__))

BK = os.path.join(BASE, "build_kb.py")
B5 = os.path.join(BASE, "build_5m1e.py")

NEW_ROUTING = '''
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",1,"JAVA_API",None,"前置: fr-agent 18999/19000 存活 + frm_blank_skeleton.xml + _test_chart.frm 源图表就位","环境确认"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",2,"JAVA_API","P-0069","Form.readStream(frm_blank_skeleton.xml) 读原生骨架（带 FormMobileAttr）","Form"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",3,"JAVA_API","P-0041","border.addNorth(new WParameterLayout()) 参数区 + setNorthSize(40)","参数区"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",4,"JAVA_API","P-0042","bodyFit.setContainerWidth/Height(1920,1080) 画布大小","Size"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",5,"JAVA_API","P-0043","absBody.setDesigningResolution(Dimension(1920,1080)) 设计分辨率","DesignResolution"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",6,"JAVA_API","P-0044","bodyFit.addWidget(new BoundsWidget(absBody, Rect(0,0,1920,1080))) 三层结构","absBody"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",7,"JAVA_API","P-0053","参数控件 ComboBox 年份/版本 + FormSubmitButton 查询按钮 addToPara（BoundsWidget 包装）","参数控件"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",8,"JAVA_API","P-0063","读 _test_chart.frm → srcChart.clone() × 4 → setWidgetName → 挂 absBody（new ChartEditor() 空壳 NPE）","4 图表"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",9,"JAVA_API","P-0034","addDB × 4: DBTableData + NameDatabaseConnection(demo_connection) + 参数宏 SQL → form.putTableData","4 数据集"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",10,"JAVA_API","P-0061","KPI 卡片 ElementCaseEditor × 4 + FormElementCase + CellGUIAttr.setShowAsHTML(true)","KPI 卡"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",11,"JAVA_API","P-0066","FU.valueOfPix 行高列宽显式设置（防 ElementCase 撑大滚动条）","尺寸"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",12,"JAVA_API","P-0068","form.export(FileOutputStream 绝对路径) 写盘（异常会截断0字节，先备份）",".frm"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",13,"VALIDATE","P-0069","Form.readStream 回读 getContainer()==WBorderLayout + absBody children + Designer 打开","验证"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",1,"PYTHON_ATTR",None,"Python 改图表绑定属性值: NameTableData 数据集名 / CategoryName / seriesName / valueName（禁全局 replace）","绑定"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",2,"PYTHON_ATTR",None,"图表标题 Formula 变体正则可改（纯 CDATA 正则静默失败）","标题"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",3,"VALIDATE",None,"JDBC 独立验证数据（fr_jdbc_probe.py）排除数据问题","数据在"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",4,"DESIGNER",None,"强制重开 Designer（JForm+addAndActivateJTemplate）+ 用户 F5 重新预览（旧缓存根因）","重开"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",5,"PYTHON_ATTR",None,"终极修复: OneValueCDDefinition 动态系列 → MoreNameCDDefinition 固定系列 + pivot SQL 宽表","柱高修复"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",6,"VALIDATE",None,"ET.parse 校验 + fr-agent 回读 NameTableData 指向新数据集 + Designer 打开","验证"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",1,"DESIGNER",None,"原版备份 _backup_copa_v1 带时间戳 + Copy-Item 克隆 v2（原版不动）","v2 副本"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",2,"JAVA_API","P-0061","渐变标题栏 ElementCaseEditor 替换 Label（background linear-gradient + 琥珀竖条）","标题栏"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",3,"JAVA_API","P-0062","KPI 卡片独立 ElementCaseEditor × 4（3×2 多格 HTML，非整段 div）","KPI 4 卡"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",4,"JAVA_API","P-0044","布局按 demo 百分比重排（bw.setBounds 精确改位置，禁 Python 全局替换）","布局"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",5,"PYTHON_ATTR",None,"参数面板放标题 Label 实现标题+筛选同行（Python 改 XML，setBounds ClassCastException）","标题Label"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",6,"PYTHON_ATTR",None,"init_css 追加 CSS（查询琥珀 #f3b042 / widgetname 大写匹配）","CSS"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",7,"VALIDATE",None,"用户手动调整后禁止重置画布三处（Size/DesignResolution/BoundsAttr），以用户调整为基准","验证"),
 ("R-009","FRM 样式收尾（全局默认格式）",1,"PYTHON_ATTR",None,"画布背景 #f5f5f5 + Form 默认 1280×720 三处一致","画布"),
 ("R-009","FRM 样式收尾（全局默认格式）",2,"PYTHON_ATTR",None,"图表取消原生标题 + 主题白 + 透明度80% + 圆角5 + 边框细线","图表基"),
 ("R-009","FRM 样式收尾（全局默认格式）",3,"PYTHON_ATTR",None,"图例右侧9号微软雅黑 + 标签 #,##0.00 + 系列宽30间隔20%圆角5 + 无网格线 + tooltip 9号","图表样式"),
 ("R-009","FRM 样式收尾（全局默认格式）",4,"PYTHON_ATTR",None,"图表标题 ElementCaseEditor HTML 块（▎ + #2563eb 18px 微软雅黑 + 行高44px）替代原生标题","标题块"),
 ("R-009","FRM 样式收尾（全局默认格式）",5,"PYTHON_ATTR",None,"WTitleLayout 外层+内层 border 圆角都要设（用户看到的是外层）","圆角"),
 ("R-009","FRM 样式收尾（全局默认格式）",6,"VALIDATE",None,"Designer 打开 + 预览确认（样式基线以 FRM全局默认格式.md 为准）","验证"),
]'''

# 在 ROUTING 列表最后一行后面插入（即 "下拉箭头" 行后）
src = open(BK, encoding="utf-8").read()
anchor = '("R-005","参数面板按 CPT 规则",6,"PYTHON_ATTR",None,"RAAttr 空→Python 替换为 delimiter=",\'"," isArray="4" 才有箭头","下拉箭头"),\n]'
# 实际文件里 anchor 带转义，先搜索更宽松的模式
m = re.search(r'\("R-005",[^\n]*下拉箭头[^\n]*\)[^\n]*\n\]', src)
if not m:
    print("anchor not found"); raise SystemExit(1)
src = src[:m.start()] + m.group(0).replace("]", NEW_ROUTING + "\n]", 1) + src[m.end():]
open(BK, "w", encoding="utf-8").write(src)
print("build_kb.py ROUTING 已追加 R-006~R-009")

# build_5m1e.py: ROUTING_MACHINE 追加
src5 = open(B5, encoding="utf-8").read()
new_machine = '''
 ("R-006",2,"MC-015"),
 ("R-006",3,"MC-015"),
 ("R-006",7,"MC-015"),
 ("R-006",8,"MC-015"),
 ("R-006",9,"MC-015"),
 ("R-006",12,"MC-015"),
 ("R-007",1,"MC-007"),
 ("R-007",3,"MC-019"),
 ("R-008",2,"MC-015"),
 ("R-008",3,"MC-015"),
 ("R-009",4,"MC-007"),
]'''
m5 = re.search(r'\("R-005",6,"MC-007"\)[^\n]*\n\]', src5)
if not m5:
    print("machine anchor not found"); raise SystemExit(1)
src5 = src5[:m5.start()] + m5.group(0).replace("]", new_machine, 1) + src5[m5.end():]
open(B5, "w", encoding="utf-8").write(src5)
print("build_5m1e.py ROUTING_MACHINE 已追加")
