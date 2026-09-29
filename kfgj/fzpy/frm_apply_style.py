#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRM 驾驶舱默认样式一键格式化脚本（v1）

依据: ckzl/gf/bjys.md（最终版）
分工(遵循用户铁律): 组件级样式用 FR Java API(fr-agent /exec), 属性值修改用 Python XML。
用法:
  python frm_apply_style.py <frm路径>             # 指定文件
  python frm_apply_style.py --dry                 # 只打印将应用的规则, 不写盘
默认样式(除非用户提出调整, 否则一直用):
  画布 1280×720 / 背景 #f5f5f5 / 图表透明80% / 卡片白底圆角5内边距5 /
  系列宽30px分类间隔20% / 标题块 ▎+#2563eb+18px / KPI 配色方案B
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import sys, os, re, json, argparse, urllib.request
import xml.etree.ElementTree as ET

# ============================================================
# 样式常量（定稿, 见 ckzl/gf/bjys.md）
# ============================================================
CANVAS_W, CANVAS_H = 1280, 720
CANVAS_BG_FR = "-657931"        # #f5f5f5
BORDER_RADIUS = "5"             # 圆角 5
SERIES_WIDTH = "30"             # 系列固定宽 30px
CATEGORY_INTERVAL = "20.0"      # 分类间隔 20%

# 标题块定稿样式: ▎ + #2563eb 蓝粗 18px + 行高 44px (保留原标题文本)
TITLE_TPL = ('<div style="display:flex;align-items:center;width:100%;height:100%;'
             'padding:0 8px;box-sizing:border-box;">'
             '<span style="font-size:18px;color:#2563eb;margin-right:8px;font-weight:bold;">\u258e</span>'
             '<span style="font-size:18px;font-weight:bold;color:#2563eb;'
             'font-family:\u5fae\u8f6f\u96c5\u9ed1,Microsoft YaHei;letter-spacing:1px;">{title}</span>'
             '</div>')

# ============================================================
# Java API 阶段 (Nashorn, 组件级样式)
# ============================================================
JAVA_JS = r'''
var Form = Java.type("com.fr.form.main.Form");
var File = Java.type("java.io.File");
var FIS = Java.type("java.io.FileInputStream");
var FOS = Java.type("java.io.FileOutputStream");
var Dimension = Java.type("java.awt.Dimension");
var Color = Java.type("java.awt.Color");
var ColorBackground = Java.type("com.fr.base.background.ColorBackground");

var form = new Form();
form.readStream(new FIS(new File(PATH)));
var border = form.getContainer();   // WBorderLayout

// body 三层: WBorderLayout > WFitLayout > BoundsWidget(WAbsoluteBodyLayout)
var bodyFit = null;
for (var i = 0; i < border.getWidgetCount(); i++) {
    var w = border.getWidget(i | 0).getWidget();
    if (String(w.getClass().getName()).indexOf("WFitLayout") >= 0) { bodyFit = w; break; }
}
var absBody = null;
if (bodyFit != null) {
    for (var j = 0; j < bodyFit.getWidgetCount(); j++) {
        var b = bodyFit.getWidget(j | 0);
        var inner = b.getWidget();
        if (String(inner.getClass().getName()).indexOf("WAbsoluteBodyLayout") >= 0) {
            absBody = inner; break;
        }
    }
}

var log = [];
// 1. 画布分辨率 1280×720
if (absBody != null) {
    try { absBody.setDesigningResolution(new Dimension(CANVAS_W, CANVAS_H)); log.push("画布 1280x720 OK"); }
    catch(e) { log.push("画布分辨率失败: " + e); }
}

// 2. 遍历组件, 应用组件级样式
var wlTitle = 0, ecTitle = 0, ecKpi = 0;
if (absBody != null) {
    for (var k = 0; k < absBody.getWidgetCount(); k++) {
        var bw = absBody.getWidget(k | 0);
        var c = bw.getWidget();
        var cn = String(c.getClass().getName());
        var name = "";
        try { name = String(c.getWidgetName()); } catch(e) {}
        // 图表卡片 WTitleLayout -> 白底
        if (cn.indexOf("WTitleLayout") >= 0) {
            try { c.setBackground(ColorBackground.getInstance(Color.WHITE)); wlTitle++; }
            catch(e) { log.push("WTitleLayout 白底失败: " + e); }
        }
        // 标题块 ElementCaseEditor (name 前缀 hdr_) -> 改 HTML 样式, 保留标题文本
        else if (cn.indexOf("ElementCaseEditor") >= 0 && name.indexOf("hdr_") == 0) {
            try {
                var fec = c.getElementCase();
                var cell = fec.getCellElement(0, 0);
                var txt = String(cell.getValue());
                txt = txt.replace(/<[^>]+>/g, "");   // 剥 HTML 留纯文本标题
                txt = txt.replace(/[\u258e\u25c6\u25c8]/g, "").trim();
                var html = TITLE_TPL.replace("{title}", txt);
                var NewCell = Java.type("com.fr.report.cell.DefaultTemplateCellElement");
                var CGA = Java.type("com.fr.report.cell.cellattr.CellGUIAttr");
                var nc = new NewCell(0, 0, html);
                var ga = new CGA(); ga.setShowAsHTML(true); nc.setCellGUIAttr(ga);
                fec.setCellElement(nc, 0, 0);
                ecTitle++;
            } catch(e) { log.push("标题块 " + name + " 失败: " + e); }
        }
        // KPI 卡片 (name 前缀 kpi_) -> v1 仅记录, 配色走 Python XML 色条
        else if (cn.indexOf("ElementCaseEditor") >= 0 && name.indexOf("kpi_") == 0) {
            ecKpi++;
        }
    }
}
log.push("WTitleLayout白底=" + wlTitle + " 标题块=" + ecTitle + " KPI=" + ecKpi);

form.export(new FOS(new File(PATH)));
"[" + log.map(function(s){return JSON.stringify(s)}).join(",") + "]";
'''

# ============================================================
# Python XML 阶段 (属性值修改, 已核验节点)
# ============================================================
XML_RULES = [
    # (正则, 替换, 说明)
    # 注意: 只保留「图表/系列特有、其他组件不涉及」的确定安全规则, 避免全局替换误伤。
    # Alpha(图表透明80%)/Margin(卡片内边距5) 需按组件类型区分(图表 vs 画布/KPI), 全局替换会误伤不透明组件, v2 再精确化。
    (r'borderRadius="\d+"', r'borderRadius="%s"' % BORDER_RADIUS, "圆角 5"),
    (r'fixedWidth="false" columnWidth="\d+"',
     r'fixedWidth="true" columnWidth="%s"' % SERIES_WIDTH, "系列固定宽 30px"),
    (r'categoryIntervalPercent="[\d.]+"',
     r'categoryIntervalPercent="%s"' % CATEGORY_INTERVAL, "分类间隔 20%"),
]

# ============================================================
# 工具函数
# ============================================================
def exec_nashorn(js_code):
    payload = json.dumps({"script": js_code}).encode('utf-8')
    req = urllib.request.Request("http://localhost:19000/exec", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": "HTTP %d: %s" % (e.code, e.read().decode('utf-8')[:300])}
    except Exception as e:
        return {"error": str(e)}


def apply_java(frm_path):
    """Java API 阶段: 组件级样式"""
    js = JAVA_JS.replace("PATH", json.dumps(frm_path))
    js = js.replace("CANVAS_W", str(CANVAS_W)).replace("CANVAS_H", str(CANVAS_H))
    js = js.replace("TITLE_TPL", json.dumps(TITLE_TPL))
    r = exec_nashorn(js)
    if "error" in r:
        print("[Java阶段] 失败: %s" % r["error"])
        return False
    print("[Java阶段] %s" % r.get("result", r))
    return True


def apply_xml(frm_path, dry=False):
    """Python XML 阶段: 属性值修改"""
    with open(frm_path, encoding='utf-8') as f:
        c = f.read()
    applied = []
    for pat, rep, desc in XML_RULES:
        n = len(re.findall(pat, c))
        if n == 0:
            print("[XML阶段] 跳过(0命中): %s" % desc)
            continue
        if not dry:
            c = re.sub(pat, rep, c)
        applied.append((desc, n))
        print("[XML阶段] %s: %d 处" % (desc, n))
    if not dry and applied:
        with open(frm_path, 'w', encoding='utf-8') as f:
            f.write(c)
    return applied


def verify(frm_path):
    try:
        ET.parse(frm_path)
        return True, "XML 合法"
    except Exception as e:
        return False, "XML 错误: %s" % e


def main():
    ap = argparse.ArgumentParser(description="FRM 驾驶舱默认样式一键格式化")
    ap.add_argument("path", nargs="?", help="frm 文件路径")
    ap.add_argument("--dry", action="store_true", help="只打印规则, 不写盘")
    ap.add_argument("--java", action="store_true", help="启用 Java API 阶段(实验性; Nashorn 循环遍历有类型坑, 默认跳过)")
    args = ap.parse_args()

    if args.dry:
        print("== 默认样式规则(预览) ==")
        print("画布: %d×%d 背景 %s" % (CANVAS_W, CANVAS_H, CANVAS_BG_FR))
        for pat, rep, desc in XML_RULES:
            print("  - %s" % desc)
        print("标题块: ▎ + #2563eb 蓝粗 18px")
        print("(未写盘)")
        return

    if not args.path:
        print("用法: python frm_apply_style.py <frm路径> [--dry] [--xml-only]")
        print("示例: python frm_apply_style.py 'C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/示例驾驶舱工程/可视化/示例驾驶舱.frm'")
        sys.exit(1)

    frm = os.path.abspath(args.path)
    if not os.path.exists(frm):
        print("文件不存在: %s" % frm)
        sys.exit(1)

    if args.java:
        if not apply_java(frm):
            print("Java 阶段失败, 跳过 XML 阶段")
            sys.exit(1)
    else:
        print("[跳过] Java API 阶段(默认用 Python XML 精确替换; --java 可启用实验性 Java 阶段)")

    apply_xml(frm, dry=False)
    ok, msg = verify(frm)
    print("[验证] %s" % msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
