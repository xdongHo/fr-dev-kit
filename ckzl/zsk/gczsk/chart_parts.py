# -*- coding: utf-8 -*-
"""图表类型零件（16 种设计器用户可见图表类型 + VanChart 支撑类）"""

EXTRA_PARTS = [
    ('P-0184', '柱形图', 'com.fr.plugin.chart.column.ColumnIndependentVanChart', 'new ColumnIndependentVanChart()', 'CHART', '柱状图（分组，X=分类 Y=数值）', '-', 'VanChart', 'vanChartPlotType=normal；ColumnPlot', '实测', 1),
    ('P-0185', '堆积柱形图', 'com.fr.plugin.chart.column.ColumnIndependentVanChart', 'new ColumnIndependentVanChart()', 'CHART', '堆积柱状图（vanChartPlotType=stack）', '-', 'VanChart', 'STACK 类型，克隆图表默认 stack 会按系列堆叠', '实测', 1),
    ('P-0186', '条形图', 'com.fr.plugin.chart.bar.BarIndependentVanChart', 'new BarIndependentVanChart()', 'CHART', '横向条形图（X=数值 Y=分类）', '-', 'VanChart', 'ColumnPlot.setAxisRotation(true) 等价；demo chart_top 用', '实测', 1),
    ('P-0187', '堆积条形图', 'com.fr.plugin.chart.bar.BarIndependentVanChart', 'new BarIndependentVanChart()', 'CHART', '横向堆积条形图', '-', 'VanChart', 'BarPlot + STACK', '文档', 0),
    ('P-0188', '饼图', 'com.fr.plugin.chart.pie.PieIndependentVanChart', 'new PieIndependentVanChart()', 'CHART', '饼图（分类占比）', '-', 'VanChart', '环形图=饼图 plus Donut 类型', '实测', 1),
    ('P-0189', '折线图', 'com.fr.plugin.chart.line.LineIndependentVanChart', 'new LineIndependentVanChart()', 'CHART', '折线图（趋势）', '-', 'VanChart', 'demo chart_trend 线系列', '实测', 1),
    ('P-0190', '面积图', 'com.fr.plugin.chart.area.AreaIndependentVanChart', 'new AreaIndependentVanChart()', 'CHART', '面积图', '-', 'VanChart', '-', '文档', 0),
    ('P-0191', '堆积面积图', 'com.fr.plugin.chart.area.AreaIndependentVanChart', 'new AreaIndependentVanChart()', 'CHART', '堆积面积图', '-', 'VanChart', 'AreaPlot + STACK', '文档', 0),
    ('P-0192', '散点图', 'com.fr.plugin.chart.scatter.ScatterIndependentVanChart', 'new ScatterIndependentVanChart()', 'CHART', '散点图（XY 数值分布）', '-', 'VanChart', '-', '文档', 0),
    ('P-0193', '气泡图', 'com.fr.plugin.chart.bubble.BubbleIndependentVanChart', 'new BubbleIndependentVanChart()', 'CHART', '气泡图（三值：X/Y/大小）', '-', 'VanChart', '-', '文档', 0),
    ('P-0194', '雷达图', 'com.fr.plugin.chart.radar.RadarIndependentVanChart', 'new RadarIndependentVanChart()', 'CHART', '雷达图（多指标对比）', '-', 'VanChart', '-', '文档', 0),
    ('P-0195', '漏斗图', 'com.fr.plugin.chart.funnel.FunnelIndependentVanChart', 'new FunnelIndependentVanChart()', 'CHART', '漏斗图（转化率）', '-', 'VanChart', '-', '文档', 0),
    ('P-0196', '矩形树图', 'com.fr.plugin.chart.treemap.TreemapIndependentVanChart', 'new TreemapIndependentVanChart()', 'CHART', '矩形树图（层级占比）', '-', 'VanChart', '-', '文档', 0),
    ('P-0197', '词云', 'com.fr.plugin.chart.wordcloud.WordCloudIndependentVanChart', 'new WordCloudIndependentVanChart()', 'CHART', '词云（文本频率）', '-', 'VanChart', '-', '文档', 0),
    ('P-0198', '力学气泡图', 'com.fr.plugin.chart.force.ForceIndependentVanChart', 'new ForceIndependentVanChart()', 'CHART', '力学气泡图（力导向关系）', '-', 'VanChart', '-', '文档', 0),
    ('P-0199', '多层柱形图', 'com.fr.plugin.chart.multiLayerColumn.MultiLayerColumnIndependentVanChart', 'new MultiLayerColumnIndependentVanChart()', 'CHART', '多层柱形图（嵌套分类）', '-', 'VanChart', '-', '文档', 0),
    ('P-0200', 'ChartTypeManager', 'com.fr.chart.ChartTypeManager', 'ChartTypeManager.getInstance()', 'CHART', '图表类型注册表', '-', '-', 'listChartTypes() 枚举全部类型', '实测', 1),
    ('P-0201', 'VanChartColumnPlot', 'com.fr.plugin.chart.column.VanChartColumnPlot', 'new VanChartColumnPlot(boolean, VanChartPlotType)', 'CHART', '柱状图 Plot', '(旋转?, 类型)', 'Plot', 'setAxisRotation(true)=横向条形；轴方向是配置 DNA', '实测', 1),
    ('P-0202', 'VanChartPlotType', 'com.fr.plugin.chart.column.VanChartPlotType', 'NORMAL / STACK / STACK_BY_PERCENT / CUSTOM', 'CHART', 'Plot 类型枚举', '-', '-', 'normal=分组 stack=堆积', '实测', 1),
    ('P-0203', 'BarIndependentVanChart', 'com.fr.plugin.chart.bar.BarIndependentVanChart', 'new BarIndependentVanChart()', 'CHART', '条形图核心类（无插件）', '-', 'VanChart', 'XML plot class com.fr.plugin.chart.bar.*', '实测', 1),
    ('P-0204', 'VanChartPlot', 'com.fr.plugin.chart.common.VanChartPlot', '-', 'CHART', 'VanChart Plot 基类', '-', 'Plot', '定位 WTitleLayout→ChartEditor→Chart→Plot 改属性', '实测', 1),
]
