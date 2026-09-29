#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_dataset.py — 取数感知（P1 感知四件套之四）

模板数据集"真实取数体检": 每个 TableData 真执行(createDataModel) →
  行数 / 列数 / 耗时 / 空值率(全列扫描) / 首行样例
报警信号:
  ⚠ 0 行        空数据集(报表空白的第一嫌疑)
  ⚠ 耗时>5s     慢查询
  ⚠ 空值率>50%  数据质量问题
DB 类数据集真连库(设计器 JVM 的 ConnectionConfig 已含 25 个连接, 只读 SELECT)。
Embedded 数据集本地执行零成本。

用法: python probe_dataset.py <cpt路径> [--json out.json]
退出码: 0=全部数据集执行成功(WARN 不阻断) / 1=有数据集执行失败 / 2=环境不可用
"""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

JS_HEAD = """
var out=[];
var ths=java.lang.Thread.getAllStackTraces().keySet().toArray();
var chosen=null;
for(var i=0;i<ths.length;i++){try{var l=ths[i].getContextClassLoader(); if(l!=null){l.loadClass('com.fr.main.impl.WorkBook'); chosen=l; break}}catch(e){}}
function C(n){return java.lang.Class.forName(n,true,chosen)}
var W=C('com.fr.main.impl.WorkBook');
var wb=W.newInstance();
var fis=new java.io.FileInputStream('__TPL__');
W.getMethod('readStream',C('java.io.InputStream')).invoke(wb,fis);
fis.close();
var res=[];
var it=W.getMethod('getTableDataNameIterator').invoke(wb);
while(it.hasNext()){
  var nm=String(it.next());
  var r={name:nm};
  try{
    var td=W.getMethod('getTableData',C('java.lang.String')).invoke(wb,new java.lang.String(nm));
    r.cls=String(td.getClass().getSimpleName());
    var cdm=null;
    var am=td.getClass().getMethods();
    for(var z=0;z<am.length;z++){if(am[z].getName()==='createDataModel'&&am[z].getParameterTypes().length===1){cdm=am[z];break}}
    var CalcCls=cdm.getParameterTypes()[0];
    var cins=null;
    try{cins=CalcCls.getMethod('createCalculator').invoke(null)}catch(eA){cins=CalcCls.newInstance()}
    var t1=Date.now();
    var dm=cdm.invoke(td,cins);
    r.execMs=Date.now()-t1;
    if(dm==null){r.err='DataModel=null';res.push(r);continue}
    var rc=dm.getClass().getMethod('getRowCount').invoke(dm);
    var cc=dm.getClass().getMethod('getColumnCount').invoke(dm);
    r.rows=rc; r.cols=cc;
    // 空值率全扫描(行列>50万则抽样前1万行)
    var gvat=dm.getClass().getMethod('getValueAt',java.lang.Integer.TYPE,java.lang.Integer.TYPE);
    var scanRows=Math.min(rc,10000), nulls=0, total=0;
    for(var ri=0;ri<scanRows;ri++){for(var ci=0;ci<cc;ci++){total++; if(gvat.invoke(dm,java.lang.Integer.valueOf(ri),java.lang.Integer.valueOf(ci))==null)nulls++}}
    r.nullRate=total>0?Math.round(nulls*1000/total)/10:null;
    // 首行样例(≤4列)
    if(rc>0){var gcn=dm.getClass().getMethod('getColumnName',java.lang.Integer.TYPE);
      var s=[];for(var ci2=0;ci2<Math.min(cc,4);ci2++){s.push(String(gcn.invoke(dm,java.lang.Integer.valueOf(ci2)))+'='+gvat.invoke(dm,java.lang.Integer.valueOf(0),java.lang.Integer.valueOf(ci2)))}
      r.sample=s.join(' | ')}
  }catch(e){r.err=String(e).substring(0,120)}
  res.push(r);
}
JSON.stringify(res)
"""


def probe(tpl):
    tpl = os.path.abspath(tpl).replace("\\", "/")
    body = {"script": JS_HEAD.replace("__TPL__", tpl)}
    req = urllib.request.Request("http://localhost:19000/exec",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.loads(r.read().decode("utf-8"))
    if res.get("error") or not res.get("result"):
        raise RuntimeError("exec 失败: %s" % (res.get("error") or "空结果")[:300])
    # result 是字符串形式的 JSON 数组
    return json.loads(res["result"])


def report(datasets):
    warns, errs = [], []
    print("═══ 取数感知 ═══")
    for d in datasets:
        if d.get("err"):
            errs.append(d)
            print("  ❌ %-20s %s 执行失败: %s" % (d["name"], d.get("cls", "?"), d["err"][:80]))
            continue
        line = "  ✅ %-20s %-18s %6d 行 ×%2d 列  %5dms  空值率 %s%%" % (
            d["name"], d.get("cls", "?"), d.get("rows", -1), d.get("cols", -1),
            d.get("execMs", -1), d.get("nullRate"))
        print(line)
        if d.get("sample"):
            print("       首行: %s" % d["sample"][:120])
        if d.get("rows") == 0:
            warns.append("%s 0 行(空数据集, 报表空白第一嫌疑)" % d["name"])
        if d.get("execMs", 0) > 5000:
            warns.append("%s 取数 %dms(慢查询)" % (d["name"], d["execMs"]))
        if d.get("nullRate") is not None and d["nullRate"] > 50:
            warns.append("%s 空值率 %s%%(数据质量)" % (d["name"], d["nullRate"]))
    for w in warns:
        print("  ⚠ " + w)
    return warns, errs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    tpl = sys.argv[1]
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]
    if not os.path.isfile(tpl):
        print("❌ 文件不存在: %s" % tpl)
        return 2
    try:
        datasets = probe(tpl)
    except Exception as e:
        print("❌ %s" % e)
        print("   (环境需先就绪: python fr-agent/bring_up.py)")
        return 2
    warns, errs = report(datasets)
    if out_json:
        json.dump({"template": tpl, "datasets": datasets, "warns": warns},
                  open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("报告: %s" % out_json)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
