# -*- coding: utf-8 -*-
"""chart_skill.py — FR 图表生成器（echarts 类型 spec → FR 图表 XML / 整页 cpt）。

R39 标准组件技能库 ③。FR 图表本质是 ECharts 的 XML 配置（VanChart 容器 + Plot 类 +
ChartDefinition 数据绑定）。

证据链（三条，缺一不生成——不许编造）:
  E1 echarts_fr_map 29 条映射的 R1/R5 已核实修正版:
     _runs/night/R1/r2_echarts/results.jsonl + _runs/night/R5/REPORT-R2.md
  E2 in-repo 设计器图表模板 19 件: ckzl/hbfa/组件模板/图表组件-*.cpt
     （每件含完整 VanChart XML：GI/Plot/ChartDefinition，本技能据此做参数化改写）
  E3 绑定结构实测: MoreNameCDDefinition / OneValueCDDefinition / CustomDefinition /
     MeterReportDefinition 四种（本轮逐模板盘点，见 _SHAPE 枚举与 registry）

映射缺失/无模板的类型 → UNSUPPORTED 清单（明确原因，返回 SkillError，绝不编造 XML）。
数据绑定数据集由 dataset_skill 同契约 spec 生成（ORG+PERM+numeric 硬约束自动继承）。
"""
import datetime
import json
import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET

from _common import (REPO_ROOT, SkillError, load_semantic, now_stamp,
                     run_guardrails, tabledata_xml, workbook_cpt)

import dataset_skill

TPL_DIR = os.path.join(REPO_ROOT, "ckzl/hbfa", "组件模板")

# ---------------------------------------------------------------- 绑定结构枚举（E3）
MORE_NAME = "more_name"       # MoreNameCDDefinition: 类目列 + N 个 ChartSummaryColumn
ONE_VALUE = "one_value"       # OneValueCDDefinition: seriesName/valueName/function + 类目列
CUSTOM_MAP = "custom_map"     # CustomDefinition: DefinitionMapList(column/line 两个 MoreName)
METER = "meter"               # MeterReportDefinition: 值/目标两条公式 =SUM(ds.select(col))

# ---------------------------------------------------------------- 类型注册表（E1+E2 交叉）
# key: (echarts_type, variant)  →  dict(tpl=模板文件, shape=绑定结构, plot=Plot 类, opts=改写项)
# 证据: E1 map_id / E2 模板实测 plot 类。wordCloud 大小写按 R5 REPORT-R2 证据#10 修正。
REGISTRY = {
    ("bar", "分组柱状"):    dict(tpl="图表组件-柱形.cpt", shape=MORE_NAME, plot="VanChartColumnPlot", map_id=1),
    ("bar", "堆积"):        dict(tpl="图表组件-柱形.cpt", shape=MORE_NAME, plot="VanChartColumnPlot", map_id=2, opts={"stack": True}),
    ("bar", "横向"):        dict(tpl="图表组件-柱形.cpt", shape=MORE_NAME, plot="VanChartColumnPlot", map_id=3, opts={"isbar": True}),
    ("bar", "横向堆积"):    dict(tpl="图表组件-柱形.cpt", shape=MORE_NAME, plot="VanChartColumnPlot", map_id=4, opts={"stack": True, "isbar": True}),
    ("line", "折线"):       dict(tpl="图表组件-折线.cpt", shape=MORE_NAME, plot="VanChartLinePlot", map_id=5),
    ("line", "面积"):       dict(tpl="图表组件-面积.cpt", shape=MORE_NAME, plot="VanChartAreaPlot", map_id=6),
    ("line", "堆积面积"):   dict(tpl="图表组件-面积.cpt", shape=MORE_NAME, plot="VanChartAreaPlot", map_id=7, opts={"stack": True}),
    ("pie", "饼图"):        dict(tpl="图表组件-饼图.cpt", shape=ONE_VALUE, plot="PiePlot4VanChart", map_id=8),
    ("scatter", "散点"):    dict(tpl="图表组件-散点.cpt", shape=MORE_NAME, plot="VanChartScatterPlot", map_id=9),
    ("scatter", "三值(大小维)"): dict(tpl="图表组件-气泡.cpt", shape=MORE_NAME, plot="VanChartBubblePlot", map_id=10),
    ("radar", "雷达"):      dict(tpl="图表组件-雷达.cpt", shape=MORE_NAME, plot="VanChartRadarPlot", map_id=11),
    ("funnel", "漏斗"):     dict(tpl="图表组件-漏斗.cpt", shape=MORE_NAME, plot="VanChartFunnelPlot", map_id=12),
    ("treemap", "矩形树图"): dict(tpl="图表组件-矩形树图.cpt", shape=MORE_NAME, plot="VanChartTreeMapPlot", map_id=13),
    ("wordCloud", "词云"):  dict(tpl="图表组件-词云.cpt", shape=MORE_NAME, plot="VanChartWordCloudPlot", map_id=14),
    ("bar+line", "柱线混合"): dict(tpl="图表组件-组合.cpt", shape=CUSTOM_MAP, plot="VanChartCustomPlot", map_id=17),
    ("heatmap", "热力图"):  dict(tpl="图表组件-热力图.cpt", shape=MORE_NAME, plot="VanChartHeatMapPlot", map_id=18),
    ("boxplot", "箱线图"):  dict(tpl="图表组件-箱线.cpt", shape=MORE_NAME, plot="VanChartBoxPlot", map_id=22),
    ("gauge", "仪表盘"):    dict(tpl="图表组件-仪表盘.cpt", shape=METER, plot="VanChartGaugePlot", map_id=20),
    ("custom", "自定义"):   dict(tpl="图表组件-组合.cpt", shape=CUSTOM_MAP, plot="VanChartCustomPlot", map_id=29),
    # ---- FR 原生额外类型（不在 echarts_fr_map 29 条内，E2 模板在库，明确标注 FR-native）----
    ("multiPie", "多层饼"): dict(tpl="图表组件-多层饼.cpt", shape=MORE_NAME, plot="VanChartMultiPiePlot", map_id=None),
    ("gantt", "甘特"):      dict(tpl="图表组件-甘特.cpt", shape=MORE_NAME, plot="VanChartGanttPlot", map_id=None),
    ("structure", "结构树"): dict(tpl="图表组件-结构树.cpt", shape=MORE_NAME, plot="VanChartStructurePlot", map_id=None),
}
# echarts_fr_map 原行 'wordcloud'（全小写，E1 R5 报告定性为会静默取空的错名）→ 归一化
_TYPE_ALIAS = {"wordcloud": "wordCloud"}

# ---------------------------------------------------------------- 暂不支持清单（不许编造）
# 每条给出原因与证据出处；resolve() 命中时原样返回给调用方。
UNSUPPORTED = {
    ("map", "地图"):            "模板在库但绑定含 VanMapDefinition+matchResult 区域匹配域配置（地图域数据），自动重写无证据，暂不支持",
    ("drillmap", "钻取地图"):    "同 map：DrillMap 绑定含 matchResult，暂不支持（E2 模板在库）",
    ("graph", "力导向关系"):     "STALE：ForceIndependentVanChart 在 FR10 全部 jar 不存在（E1 map15，CNFE+zipfile 双验）",
    ("bar", "多系列嵌套"):       "STALE：MultiLayerColumnIndependentVanChart 不存在；FR 近似物为多层饼图 multiPie（非等价，E1 map16）",
    ("candlestick", "K线图"):    "R1 判 STALE（无 Candlestick/KLine 类）；R5 提出 charttypes.StockIndependentChart 线索但未定案——按保守口径暂不支持（E1 map21 两泳道分歧待裁决）",
    ("sankey", "桑基图"):        "R1 判无运行时 Plot（仅设计器面板）；R5 判 sankeychart 插件通道——无 in-repo cpt XML 模板，暂不支持（E1 map23）",
    ("sunburst", "旭日图"):      "R1 判 STALE；R5 判 fr-plugin-echarts 插件通道——无 in-repo cpt XML 模板，暂不支持（E1 map24）",
    ("parallel", "平行坐标"):    "两泳道均无 FR10 证据（仅 ParallelogramMarker 无关类），暂不支持（E1 map25）",
    ("lines", "路径图"):         "FR 通道=地图+AttrLineEffect 飞线条件，非独立图型，暂不支持（E1 map27）",
    ("themeRiver", "主题河流"):  "两泳道均无 FR10 证据，暂不支持（E1 map28）",
    ("pictorialBar", "象形柱图"): "插件 pictorialBarHill（Provider 架构，非 VanChart 族），无 in-repo cpt XML 模板，暂不支持（E1 map26）",
}

_FUNCTIONS = {
    "sum": "com.fr.data.util.function.SumFunction",
    "first": "com.fr.plugin.chart.base.FirstFunction",
    "count": "com.fr.data.util.function.CountFunction",
}


# ---------------------------------------------------------------- 查询接口
def supported_types():
    """→ {(type, variant): {plot, map_id, tpl, shape}}（README/工具发现用）。"""
    return {k: {"plot": v["plot"], "map_id": v["map_id"], "tpl": v["tpl"], "shape": v["shape"]}
            for k, v in REGISTRY.items()}


def unsupported_types():
    """→ 暂不支持清单 {(type, variant): 原因}（映射缺失时明确返回，不许编造）。"""
    return dict(UNSUPPORTED)


def resolve(echarts_type, variant=None):
    """echarts 类型名(+变体) → 注册表条目。查无映射 → SkillError（附支持/暂不支持全清单）。"""
    t = _TYPE_ALIAS.get(echarts_type, echarts_type)
    if variant is None:
        cands = [(k, v) for k, v in REGISTRY.items() if k[0] == t]
        if len(cands) == 1:
            return cands[0][0], cands[0][1]
    else:
        if (t, variant) in REGISTRY:
            return (t, variant), REGISTRY[(t, variant)]
    # 未命中 → 明确报告（支持清单 + 暂不支持清单）
    unsup = {k: v for k, v in UNSUPPORTED.items() if k[0] == t}
    if unsup:
        raise SkillError(f"图表类型 [{t}/{variant}] 暂不支持——原因: " + "；".join(unsup.values()) +
                         f"\n支持清单: {sorted(f'{a}/{b}' for a, b in REGISTRY)}")
    raise SkillError(f"图表类型 [{t}/{variant}] 无映射（既不在支持清单也不在暂不支持清单，"
                     f"即 echarts_fr_map 29 条之外）。\n支持: {sorted(f'{a}/{b}' for a, b in REGISTRY)}"
                     f"\n暂不支持: {sorted(f'{a}/{b}' for a, b in UNSUPPORTED)}")


# ---------------------------------------------------------------- spec 校验
def validate_spec(spec, sem):
    if not isinstance(spec, dict):
        raise SkillError("spec 必须是 dict")
    if not spec.get("echarts_type"):
        raise SkillError("spec.echarts_type 必填")
    ds = spec.get("dataset")
    if not ds:
        raise SkillError("spec.dataset 必填（数据绑定 spec，dataset_skill 同契约）")
    b = spec.get("binding") or {}
    shape_ok = False
    for key in ("category", "values", "value", "target"):
        if key in b:
            shape_ok = True
    if not shape_ok:
        raise SkillError("spec.binding 需要 category/values（more_name|one_value|custom_map）"
                         "或 value/target（meter/仪表盘）")
    values = b.get("values") or ([b["value"]] if b.get("value") else [])
    for v in values:
        if v.get("function") and v["function"] not in _FUNCTIONS \
                and not str(v["function"]).startswith("com.fr."):
            raise SkillError(f"function [{v['function']}] 只允许内置别名 "
                             f"{sorted(_FUNCTIONS)} 或完整 com.fr.* 类名（不许编造）")
    # 绑定列 ⊆ 数据集输出列（数据集级校验委托 dataset_skill）
    dvalidate = dataset_skill.validate_spec(ds, sem)
    fields = set(ds.get("fields") or [])
    cat = b.get("category")
    if cat and cat not in fields:
        raise SkillError(f"binding.category [{cat}] 不在数据集 fields {sorted(fields)}")
    for v in values:
        if v.get("field") and v["field"] not in fields:
            raise SkillError(f"binding 值列 [{v['field']}] 不在数据集 fields {sorted(fields)}")
    if b.get("target") and b["target"] not in fields:
        raise SkillError(f"binding.target [{b['target']}] 不在数据集 fields {sorted(fields)}")
    return dvalidate


# ---------------------------------------------------------------- 模板手术
_CELL_O_RE = re.compile(r"<O t=\"CC\">", re.S)


def _load_chart_o(tpl_file):
    """设计器模板 → <O t="CC">…</O> 图表块（ET 自检）。"""
    path = os.path.join(TPL_DIR, tpl_file)
    if not os.path.exists(path):
        raise SkillError(f"图表模板缺失: {path}（E2 证据库被破坏？）")
    txt = open(path, encoding="utf-8").read()
    start = txt.find('<O t="CC">')
    if start < 0:
        raise SkillError(f"模板 {tpl_file} 无 <O t=\"CC\"> 图表块")
    c_end = txt.find("</C>", start)
    o_end = txt.rfind("</O>", start, c_end)
    frag = txt[start:o_end + 4]
    try:
        ET.fromstring(frag.encode("utf-8"))
    except ET.ParseError as e:
        raise SkillError(f"模板 {tpl_file} 图表块解析失败: {e}")
    return frag


def _sub(pattern, repl, text, count=0, flags=re.S):
    out, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        raise SkillError(f"模板手术落空: {pattern[:60]}")
    return out


def _more_name_cd(ds, binding):
    cols = "".join(f'<ChartSummaryColumn name="{v["field"]}" function="{_FUNCTIONS.get(v.get("function", "sum"), v.get("function"))}" '
                   f'customName="{v.get("name", v["field"])}"/>' for v in binding["values"])
    return ('<ChartDefinition><MoreNameCDDefinition>'
            '<Top topCate="-1" topValue="-1" isDiscardOtherCate="false" isDiscardOtherSeries="false" '
            'isDiscardNullCate="false" isDiscardNullSeries="false"/>'
            f'<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[{ds}]]></Name></TableData>'
            f'<CategoryName value="{binding.get("category", "无")}"/>{cols}'
            '</MoreNameCDDefinition></ChartDefinition>')


def _one_value_cd(ds, binding):
    v = binding["values"][0]
    fn = _FUNCTIONS.get(v.get("function", "sum"), v.get("function"))
    return (f'<ChartDefinition><OneValueCDDefinition seriesName="{v.get("name", "系列")}" '
            f'valueName="{v["field"]}" function="{fn}">'
            '<Top topCate="-1" topValue="-1" isDiscardOtherCate="false" isDiscardOtherSeries="false" '
            'isDiscardNullCate="false" isDiscardNullSeries="false"/>'
            f'<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[{ds}]]></Name></TableData>'
            f'<CategoryName value="{binding.get("category", "无")}"/>'
            '</OneValueCDDefinition></ChartDefinition>')


def _custom_cd(ds, binding):
    """CustomDefinition：DefinitionMap key=column/line 各一 MoreNameCDDefinition。"""
    keys = [v.get("key", "column" if i == 0 else "line") for i, v in enumerate(binding["values"])]
    maps = []
    for v in binding["values"]:
        cols = ('<ChartSummaryColumn name="%s" function="%s" customName="%s"/>'
                % (v["field"], _FUNCTIONS.get(v.get("function", "sum"), v.get("function")),
                   v.get("name", v["field"])))
        maps.append(f'<DefinitionMap key="{v.get("key", keys.pop(0))}">'
                    '<MoreNameCDDefinition>'
                    '<Top topCate="-1" topValue="-1" isDiscardOtherCate="false" isDiscardOtherSeries="false" '
                    'isDiscardNullCate="false" isDiscardNullSeries="false"/>'
                    f'<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[{ds}]]></Name></TableData>'
                    f'<CategoryName value="{binding.get("category", "无")}"/>{cols}'
                    '</MoreNameCDDefinition></DefinitionMap>')
    return ('<ChartDefinition><CustomDefinition><DefinitionMapList>'
            + "".join(maps) + '</DefinitionMapList></CustomDefinition></ChartDefinition>')


def _meter_cd(ds, binding):
    v, t = binding["value"], binding["target"]
    return (f'<ChartDefinition><MeterReportDefinition>'
            '<Top topCate="-1" topValue="-1" isDiscardOtherCate="false" isDiscardOtherSeries="false" '
            'isDiscardNullCate="false" isDiscardNullSeries="false"/>'
            '<MeterDefinition201109 meterType="0"/>'
            '<meterDefinitionName><O><![CDATA[]]></O></meterDefinitionName>'
            f'<meterDefinitionValue><O t="XMLable" class="com.fr.base.Formula"><Attributes>'
            f'<![CDATA[=SUM({ds}.select({v}))]]></Attributes></O></meterDefinitionValue>'
            f'<meterDefinitionTarget><O t="XMLable" class="com.fr.base.Formula"><Attributes>'
            f'<![CDATA[=SUM({ds}.select({t}))]]></Attributes></O></meterDefinitionTarget>'
            '</MeterReportDefinition></ChartDefinition>')


_CD_BUILDERS = {MORE_NAME: _more_name_cd, ONE_VALUE: _one_value_cd,
                CUSTOM_MAP: _custom_cd, METER: _meter_cd}


def _rewrite_cd(frag, shape, ds, binding):
    """整体替换 ChartDefinition 区（模板残留演示绑定一并清除）。"""
    builder = _CD_BUILDERS[shape]
    new_cd = builder(ds, binding)
    return _sub(r"<ChartDefinition>.*?</ChartDefinition>", new_cd.replace("\\", "\\\\"), frag, count=1)


def _rewrite_title(frag, title):
    """标题改写（确定性两步，防回溯误吞）：
    1. 定位 <Title4VanChart><Title>…</Title> 跨度，把跨度内第一个 <O…>…</O>
       （实测两种形态：公式 O（柱形/饼图）/ 纯文本 O（折线等））替换为纯文本标题 O；
    2. TitleVisible false→true（模板若已 true 则原样）。"""
    m = re.search(r"<Title4VanChart>\s*<Title>.*?</Title>", frag, re.S)
    if not m:
        raise SkillError("模板手术落空: 无 <Title4VanChart><Title> 区")
    span = m.group(0)
    new_span, n = re.subn(r'<O(?:\s+t="XMLable"\s+class="com\.fr\.base\.Formula")?>.*?</O>',
                          "<O><![CDATA[" + title.replace("\\", "\\\\") + "]]></O>",
                          span, count=1, flags=re.S)
    if n == 0:
        raise SkillError("模板手术落空: 标题 O 改写（Title 区无 O 元素）")
    new_span = new_span.replace('<TitleVisible value="false"', '<TitleVisible value="true"')
    return frag[:m.start()] + new_span + frag[m.end():]


def _rewrite_plot_opts(frag, opts):
    if opts.get("stack"):
        frag = _sub(r'vanChartPlotType="normal"', 'vanChartPlotType="stack"', frag, count=1)
    if opts.get("isbar"):
        # E1 map3: 条形=VanChartColumnPlot(isBar=true)，属性在 VanChartColumnPlotAttr 实测在位
        frag = _sub(r'isBar="false"', 'isBar="true"', frag, count=1)
    return frag


def _strip_richtext_placeholders(frag):
    """模板富文本提示框/数据表演示内容含前端占位符 ${VALUE}/${CATEGORY}/${NAME}/${SERIES}/${SIZE}
    （FR tooltip richText / DataSheet seriesLabel 语法，非 cpt 模板参数）——G2 会误判为未声明参数引用。
    归一化为设计器缺省空形态（同模板文件内存在 content=""/seriesLabel 缺省空值例）。"""
    return re.sub(r'((?:content|initParamsContent|seriesLabel)=")[^"]*\$\{[A-Z_]+\}[^"]*"', r'\1"', frag)


def build_chart_o(spec, sem=None):
    """spec → 改写后的 <O t="CC">…</O> 图表块字符串（ET 校验过）。"""
    sem = sem or load_semantic()
    (t, variant), entry = resolve(spec["echarts_type"], spec.get("variant"))
    frag = _load_chart_o(entry["tpl"])
    frag = _strip_richtext_placeholders(frag)
    ds_name = spec["dataset"]["name"]
    binding = spec.get("binding") or {}
    frag = _rewrite_cd(frag, entry["shape"], ds_name, binding)
    frag = _rewrite_plot_opts(frag, entry.get("opts") or {})
    if spec.get("title"):
        frag = _rewrite_title(frag, spec["title"])
    frag = _sub(r'<UUID uuid="[^"]*"', f'<UUID uuid="{uuid.uuid4().hex}"', frag, count=1)
    if "${" in frag:
        raise SkillError(f"图表块仍残留 ${{}} 引用（模板 {entry['tpl']} 出现未登记占位符），"
                         f"按纪律拒绝产出，请把该占位符补入 _strip_richtext_placeholders 证据清单")
    ET.fromstring(frag.encode("utf-8"))   # 手术后兜底
    return frag, entry


def build_chart_cell(spec, sem=None, cell=None):
    """spec → 图表单元格 <C> XML（缺省 c=0 r=6 跨 21×49，与模板画布同构）。"""
    frag, _ = build_chart_o(spec, sem)
    cell = cell or spec.get("cell") or {"c": 0, "r": 6, "cs": 21, "rs": 49}
    return (f'<C c="{cell.get("c", 0)}" r="{cell.get("r", 6)}" cs="{cell.get("cs", 21)}" '
            f'rs="{cell.get("rs", 49)}" s="0">{frag}<PrivilegeControl/><Expand/></C>')


# ---------------------------------------------------------------- 整页产物
def build(spec, sem=None, report_name="chart", out=None):
    """spec → (cpt_text, meta)。数据集(ORG+PERM) + 图表单元格 + 参数声明。
    guardrails G1-G4 0 错才返回。"""
    sem = sem or load_semantic()
    validate_spec(spec, sem)
    frag, entry = build_chart_o(spec, sem)
    ds_spec = dict(spec["dataset"])
    td, sql = dataset_skill.build_tabledata(ds_spec, sem)
    names = dataset_skill.declared_params(ds_spec, sem)
    cell_xml = build_chart_cell(spec, sem)
    doc = workbook_cpt(report_name, cell_xml, td, sem, param_names=names)
    blocking, _ = run_guardrails(doc, sem)
    if blocking:
        raise SkillError("chart_skill 产物未过 guardrails:\n" +
                         "\n".join(f'  [{e["gate"]}] {e["rule"]}: {e["message"]}' for e in blocking))
    if out:
        dump(out, doc)
    meta = {"type": f'{spec["echarts_type"]}/{spec.get("variant", "")}',
            "plot": entry["plot"], "map_id": entry["map_id"], "tpl": entry["tpl"],
            "shape": entry["shape"], "dataset": ds_spec["name"]}
    return doc, meta


def dump(out, doc):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if os.path.exists(out):
        bak = out + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.replace(out, bak)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    ET.parse(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python chart_skill.py '<spec.json>' [out.cpt] | --types | --unsupported")
        raise SystemExit(2)
    if sys.argv[1] == "--types":
        print(json.dumps({f"{a}/{b}": v for (a, b), v in supported_types().items()},
                         ensure_ascii=False, indent=1))
        raise SystemExit(0)
    if sys.argv[1] == "--unsupported":
        print(json.dumps({f"{a}/{b}": v for (a, b), v in unsupported_types().items()},
                         ensure_ascii=False, indent=1))
        raise SystemExit(0)
    spec = json.loads(sys.argv[1])
    try:
        doc, meta = build(spec)
    except SkillError as e:
        print(f"SKILL REJECT: {e}")
        raise SystemExit(1)
    print(json.dumps(meta, ensure_ascii=False))
    if len(sys.argv) > 2:
        dump(sys.argv[2], doc)
        print(f"WROTE: {sys.argv[2]}  ({now_stamp()})")
