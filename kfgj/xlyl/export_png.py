#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_png.py — injected JVM 真引擎渲染导出 PNG（P1 视觉感知层）

给 agent 装"眼睛": 真引擎绘制的页面位图 → 可直接 read_image 观察判断
(布局观感/颜色/字号/图表渲染, 补足 JSON 结构感知没有的语义层)。
ImageExporter 实证签名(与 PDFExporter 同构): export(OutputStream, ResultWorkBook)。

用法: python export_png.py <cpt路径> [out.png] [--open]
"""
import json
import os
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
tpl = os.path.abspath(sys.argv[1]).replace("\\", "/")
out_png = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-")
                          else os.path.splitext(sys.argv[1])[0] + ".png").replace("\\", "/")

JS = """
var out = [];
try {
    var C = function(n) { return java.lang.Class.forName(n, true, java.lang.Thread.currentThread().getContextClassLoader()); };
    var FIS = Java.type('java.io.FileInputStream');
    var FOS = Java.type('java.io.FileOutputStream');
    var File = Java.type('java.io.File');
    var HashMap = Java.type('java.util.HashMap');
    var JString = Java.type('java.lang.String');
    var SC = C('java.lang.String');

    var wbClass = C('com.fr.main.impl.WorkBook');
    var wb = wbClass.newInstance();
    var fis = new FIS('__TPL__');
    wbClass.getMethod('readStream', C('java.io.InputStream')).invoke(wb, fis);
    fis.close();
    out.push('[1] 模板已解析');

    var actor = C('com.fr.stable.ActorFactory').getMethod('getActor', SC).invoke(null, new JString('page'));
    var rwb = wbClass.getMethod('execute', C('java.util.Map'), C('com.fr.report.stable.fun.Actor'))
                     .invoke(wb, new HashMap(), actor);
    out.push('[2] 引擎已计算 -> ' + rwb.getClass().getName());

    var exporter = C('com.fr.io.exporter.ImageExporter').getConstructor(SC).newInstance(new JString('png'));
    var outFile = new File('__OUT__');
    outFile.getParentFile() && outFile.getParentFile().mkdirs();
    var fos = new FOS(outFile);
    exporter.getClass().getMethod('export', C('java.io.OutputStream'), C('com.fr.main.workbook.ResultWorkBook'))
            .invoke(exporter, fos, rwb);
    fos.close();
    out.push('[3] PNG 已导出: ' + outFile.length() + ' bytes');
    out.push('=== EXPORT COMPLETE ===');
} catch (e) {
    out.push('ERROR: ' + e.toString());
    var st = e.getStackTrace ? e.getStackTrace() : null;
    if (st != null) for (var k = 0; k < Math.min(st.length, 5); k++) out.push('  at ' + st[k].toString());
}
out.join('\\n');
""".replace("__TPL__", tpl).replace("__OUT__", out_png)

req = urllib.request.Request("http://localhost:19000/exec",
                             data=json.dumps({"script": JS}).encode("utf-8"),
                             headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=180) as r:
    res = json.loads(r.read().decode("utf-8"))
print(res.get("result") or res.get("error"))

if not (os.path.exists(out_png) and os.path.getsize(out_png) > 1000):
    sys.exit(1)
# 魔数校验: PNG=89504E47, JPEG=FFD8 (ImageExporter 可能按配置出 JPEG)
with open(out_png, "rb") as f:
    magic = f.read(4)
kind = "PNG" if magic.startswith(b"\x89PNG") else ("JPEG" if magic.startswith(b"\xff\xd8") else "未知:" + magic.hex())
print("格式=%s 大小=%d bytes → %s" % (kind, os.path.getsize(out_png), out_png))
if "--open" in sys.argv:
    subprocess.Popen(["cmd", "/c", "start", "", out_png])
