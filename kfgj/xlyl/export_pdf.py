#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_pdf.py — injected JVM 真引擎渲染导出 PDF（演示/人工审阅用）"""
import json
import os
import sys
import urllib.request

tpl = os.path.abspath(sys.argv[1]).replace("\\", "/")
out_pdf = os.path.abspath(sys.argv[2]).replace("\\", "/")

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

    var pdfExporter = C('com.fr.io.exporter.PDFExporter').newInstance();
    var outFile = new File('__OUT__');
    outFile.getParentFile() && outFile.getParentFile().mkdirs();
    var fos = new FOS(outFile);
    pdfExporter.getClass().getMethod('export', C('java.io.OutputStream'), C('com.fr.main.workbook.ResultWorkBook'))
               .invoke(pdfExporter, fos, rwb);
    fos.close();
    out.push('[3] PDF 已导出: ' + outFile.length() + ' bytes');
    out.push('=== EXPORT COMPLETE ===');
} catch (e) {
    out.push('ERROR: ' + e.toString());
    var st = e.getStackTrace ? e.getStackTrace() : null;
    if (st != null) for (var k = 0; k < Math.min(st.length, 5); k++) out.push('  at ' + st[k].toString());
}
out.join('\\n');
""".replace("__TPL__", tpl).replace("__OUT__", out_pdf)

req = urllib.request.Request("http://localhost:19000/exec",
                             data=json.dumps({"script": JS}).encode("utf-8"),
                             headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as r:
    res = json.loads(r.read().decode("utf-8"))
print(res.get("result") or res.get("error"))
sys.exit(0 if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 1000 else 1)
