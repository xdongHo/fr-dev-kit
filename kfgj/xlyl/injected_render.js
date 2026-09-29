// injected_render.js — 设计器 JVM 注入渲染器（fr-agent /exec, 探针B验证链）
// 占位符: __TEMPLATE__(cpt/frm绝对路径) __OUT__(产物json绝对路径) — 由 render_check.py 替换
// 产物: JSON {ok, template, resultClass, sheetCount, sheets:[{name, cells:[{c,r,cs,rs,t,v}]}]}
var out = [];
function esc(s) { // JSON 字符串转义
    var r = '"';
    for (var i = 0; i < s.length; i++) {
        var ch = s.charAt(i), code = s.charCodeAt(i);
        if (ch === '"') r += '\\"';
        else if (ch === '\\') r += '\\\\';
        else if (ch === '\n') r += '\\n';
        else if (ch === '\r') r += '\\r';
        else if (ch === '\t') r += '\\t';
        else if (code < 32) r += '\\u' + ('000' + code.toString(16)).slice(-4);
        else r += ch;
    }
    return r + '"';
}
try {
    var FIS = Java.type('java.io.FileInputStream');
    var FOS = Java.type('java.io.FileOutputStream');
    var File = Java.type('java.io.File');
    var HashMap = Java.type('java.util.HashMap');
    var JString = java.lang.String;
    // 类加载器探测: 服务器 JVM 的 FR 引擎在 WebappClassLoader(HTTP线程的TCCL不是它),
    // 但 webapp 工作线程的 TCCL 必然持有 → 枚举全部线程逐一探测
    var ENGINE_PROBE = 'com.fr.main.impl.WorkBook';
    var _seen = {}, _cands = [];
    function _addLoader(l) {
        if (l == null) return;
        var id = String(java.lang.System.identityHashCode(l));
        if (!_seen[id]) { _seen[id] = true; _cands.push(l); }
    }
    var _threads = java.lang.Thread.getAllStackTraces().keySet().toArray();
    for (var _ti = 0; _ti < _threads.length; _ti++) {
        try { _addLoader(_threads[_ti].getContextClassLoader()); } catch (_e1) {}
    }
    _addLoader(java.lang.ClassLoader.getSystemClassLoader());
    var _chosen = null;
    for (var _li = 0; _li < _cands.length; _li++) {
        try { _cands[_li].loadClass(ENGINE_PROBE); _chosen = _cands[_li]; break; } catch (_e0) {}
    }
    if (_chosen == null) { throw new Error('FR 引擎类不可达: ' + ENGINE_PROBE + ' (试了 ' + _cands.length + ' 个类加载器)'); }
    var C = function(n) { return java.lang.Class.forName(n, true, _chosen); };
    var SC = C('java.lang.String');
    var TPL = '__TEMPLATE__';
    var isFrm = TPL.slice(-4).toLowerCase() === '.frm';
    var json = null;
    var T0 = Date.now();          // 性能感知: 各阶段耗时(ms)进 JSON
    var T = { loadMs: 0, execMs: 0, extractMs: 0, totalMs: 0 };

    // ═══ 共享: 组件树 walk (frm 主体 / cpt 参数面板 复用) ═══
    function widgetName(w) {
        try { var wn = w.getClass().getMethod('getWidgetName').invoke(w); return wn == null ? null : String(wn); } catch (e) { return null; }
    }
    function boundsOf(w) {
        // BoundsWidget 的 bounds 走 getBounds() → Rectangle 公共字段 x/y/width/height
        try {
            var rect = w.getClass().getMethod('getBounds').invoke(w);
            if (rect != null) {
                var rc = rect.getClass();
                return { x: rc.getField('x').getInt(rect), y: rc.getField('y').getInt(rect),
                         w: rc.getField('width').getInt(rect), h: rc.getField('height').getInt(rect) };
            }
        } catch (eB) {}
        // 降级: getX/getY/getWidth/getHeight 独立 getter
        var b = {};
        var okb = false;
        var wmm = w.getClass().getMethods();
        for (var q = 0; q < wmm.length; q++) {
            var mn = wmm[q].getName();
            if (wmm[q].getParameterTypes().length !== 0) continue;
            if (mn === 'getX') { b.x = wmm[q].invoke(w); okb = true; }
            else if (mn === 'getY') { b.y = wmm[q].invoke(w); }
            else if (mn === 'getWidth') { b.w = wmm[q].invoke(w); }
            else if (mn === 'getHeight') { b.h = wmm[q].invoke(w); }
        }
        return okb ? b : null;
    }
    function walk(container, depth, arr) {
        if (container == null || depth > 12) return;
        var cc = null;
        var cmm = container.getClass().getMethods();
        for (var q = 0; q < cmm.length; q++) {
            if (cmm[q].getName() === 'getWidgetCount' && cmm[q].getParameterTypes().length === 0) cc = cmm[q];
        }
        if (cc == null) return;
        var n = cc.invoke(container);
        var INT_CLASS = java.lang.Integer.TYPE;
        for (var i = 0; i < n; i++) {
            // getWidget 有多重载(int/String/...) → 按 int 参数精确定位
            var w = null;
            var wmm = container.getClass().getMethods();
            for (var q2 = 0; q2 < wmm.length; q2++) {
                var mm2 = wmm[q2];
                if (mm2.getName() === 'getWidget' && mm2.getParameterTypes().length === 1
                    && mm2.getParameterTypes()[0] === INT_CLASS) {
                    w = mm2.invoke(container, java.lang.Integer.valueOf(i)); break;
                }
            }
            if (w == null) break;
            var cls = String(w.getClass().getName());
            var nm2 = widgetName(w);
            var b = boundsOf(w);
            arr.push('{"cls":' + esc(cls) + ',"name":' + (nm2 == null ? 'null' : esc(nm2)) +
                     (b ? ',"x":' + b.x + ',"y":' + b.y + ',"w":' + b.w + ',"h":' + b.h : '') + '}');
            // BoundsWidget 是包装器 → 展开 getWidget() 内层真实控件
            if (cls.indexOf('BoundsWidget') >= 0) {
                try {
                    var inner = w.getClass().getMethod('getWidget').invoke(w);
                    if (inner != null && String(inner.getClass().getName()).indexOf('BoundsWidget') < 0) {
                        var icls = String(inner.getClass().getName());
                        var inm = widgetName(inner);
                        arr.push('{"cls":' + esc(icls) + ',"name":' + (inm == null ? 'null' : esc(inm)) +
                                 (b ? ',"x":' + b.x + ',"y":' + b.y + ',"w":' + b.w + ',"h":' + b.h : '') +
                                 ',"inner":true}');
                        walk(inner, depth + 1, arr);
                    }
                } catch (ign3) {}
            }
            walk(w, depth + 1, arr); // 布局容器递归
        }
    }

    // ═══ cpt 网格真实尺寸: getColumnWidth/getRowHeight(FU) → px(÷38100, 见 单位换算实证.md) ═══
    function _grid_size_json(sheet, maxCol, maxRow) {
        try {
            var gCW = sheet.getClass().getMethod('getColumnWidth', java.lang.Integer.TYPE);
            var gRH = sheet.getClass().getMethod('getRowHeight', java.lang.Integer.TYPE);
            var cw = [], rh = [];
            for (var ci = 0; ci < maxCol; ci++) {
                try { cw.push(Math.round(gCW.invoke(sheet, java.lang.Integer.valueOf(ci)).getLen() / 3810) / 10); } // FU/38100=px, 0.1px 精度
                catch (eC) { cw.push(0); }
            }
            for (var ri = 0; ri < maxRow; ri++) {
                try { rh.push(Math.round(gRH.invoke(sheet, java.lang.Integer.valueOf(ri)).getLen() / 3810) / 10); }
                catch (eR) { rh.push(0); }
            }
            return ',"colW":[' + cw.join(',') + '],"rowH":[' + rh.join(',') + ']';
        } catch (eG) { return ''; }
    }

    if (isFrm) {
        // ═══ FRM 路线: Form.readStream → getContainer → 递归组件树物化 ═══
        var FC = C('com.fr.form.main.Form');
        var f = FC.newInstance();
        var fisF = new FIS(TPL);
        FC.getMethod('readStream', C('java.io.InputStream')).invoke(f, fisF);
        fisF.close();
        T.loadMs = Date.now() - T0;
        out.push('[1] frm loaded');
        var widgets = [];
        var cont = FC.getMethod('getContainer').invoke(f);
        walk(cont, 0, widgets);
        T.extractMs = Date.now() - T0 - T.loadMs;
        out.push('[2] widget tree: ' + widgets.length + ' widgets');
        T.totalMs = Date.now() - T0;
        json = '{"ok":true,"kind":"frm","template":' + esc(TPL) +
               ',"rootContainer":' + esc(String(cont.getClass().getName())) +
               ',"widgetCount":' + widgets.length +
               ',"timing":' + JSON.stringify(T) +
               ',"widgets":[' + widgets.join(',') + ']}';
    } else {
        // ═══ CPT 路线: WorkBook.readStream → execute → ResultWorkBook 逐格 ═══
        var wbClass = C('com.fr.main.impl.WorkBook');
        var wb = wbClass.newInstance();
        var fis = new FIS(TPL);
        wbClass.getMethod('readStream', C('java.io.InputStream')).invoke(wb, fis);
        fis.close();
        out.push('[1] loaded');
        T.loadMs = Date.now() - T0;

        var actor = C('com.fr.stable.ActorFactory').getMethod('getActor', SC).invoke(null, new JString('page'));
        var rwb = wbClass.getMethod('execute', C('java.util.Map'), C('com.fr.report.stable.fun.Actor'))
                         .invoke(wb, new HashMap(), actor);
        out.push('[2] executed -> ' + rwb.getClass().getName());
        T.execMs = Date.now() - T0 - T.loadMs;

        var sheetsJson = [];
        var n = 0;
        var ms = rwb.getClass().getMethods();
        for (var i = 0; i < ms.length; i++) {
            if (ms[i].getName() === 'getReportCount' && ms[i].getParameterTypes().length === 0) {
                n = ms[i].invoke(rwb); break;
            }
        }
        if (!n || n < 1) n = 1;
        var INT_CLASS = java.lang.Integer.TYPE;
        for (var s = 0; s < n; s++) {
            var sheet = rwb.getClass().getMethod('getReport', INT_CLASS).invoke(rwb, s);
            var sname = 'sheet' + s;
            try { sname = String(sheet.getClass().getMethod('getTemplateReportName').invoke(sheet)); } catch (ign) {}
            var cells = [];
            var iter = sheet.getClass().getMethod('cellIterator').invoke(sheet);
            var ncells = 0;
            var maxCol = 0, maxRow = 0;
            var fontHisto = {}; // 样式感知: 每格实际应用字体(名+pt)直方图; 悬空样式在此现形(全默认=可疑)
            while (iter.hasNext()) {
                var cell = iter.next();
                var cm = cell.getClass().getMethods();
                var col = 0, row = 0, cs2 = 1, rs2 = 1, val = null, typ = 'str';
                for (var j = 0; j < cm.length; j++) {
                    var m = cm[j], nm = m.getName();
                    if (m.getParameterTypes().length !== 0) continue;
                    if (nm === 'getColumn') col = m.invoke(cell);
                    else if (nm === 'getRow') row = m.invoke(cell);
                    else if (nm === 'getColumnSpan') cs2 = m.invoke(cell);
                    else if (nm === 'getRowSpan') rs2 = m.invoke(cell);
                    else if (nm === 'getValue') val = m.invoke(cell);
                }
                var sval = null;
                if (val != null) {
                    var vcn = String(val.getClass().getName());
                    if (vcn.indexOf('Chart') >= 0) { typ = 'chart'; sval = String(val.getClass().getSimpleName()); }
                    else { sval = String(val); }
                }
                cells.push('{"c":' + col + ',"r":' + row + ',"cs":' + cs2 + ',"rs":' + rs2 +
                           ',"t":"' + typ + '","v":' + (sval == null ? 'null' : esc(sval)) + '}');
                ncells++;
                if (col + cs2 > maxCol) maxCol = col + cs2;
                if (row + rs2 > maxRow) maxRow = row + rs2;
                try {
                    var st = cell.getClass().getMethod('getStyle').invoke(cell);
                    if (st != null) {
                        var fo = st.getClass().getMethod('getFRFont').invoke(st);
                        if (fo != null) {
                            var fk = String(fo.getFontName()) + ' ' + fo.getSize2D() + 'pt' + (fo.isBold() ? ' B' : '');
                            fontHisto[fk] = (fontHisto[fk] || 0) + 1;
                        }
                    }
                } catch (ignF) {}
            }
            var fontsArr = [];
            for (var fk2 in fontHisto) fontsArr.push('{"f":' + esc(fk2) + ',"n":' + fontHisto[fk2] + '}');
            sheetsJson.push('{"name":' + esc(sname) + ',"cellCount":' + ncells + ',"cells":[' + cells.join(',') + ']' +
                            (fontsArr.length ? ',"fonts":[' + fontsArr.join(',') + ']' : '') +
                            _grid_size_json(sheet, maxCol, maxRow) + '}');
            out.push('[3] sheet' + s + ' "' + sname + '": ' + ncells + ' cells');
        }
        // [3.5] 参数面板控件树(ReportParameterAttr → FormParameterUI → getParaContainer → walk)
        var paramsJson = '';
        try {
            var rpa = wbClass.getMethod('getReportParameterAttr').invoke(wb);
            if (rpa != null) {
                var pui = rpa.getClass().getMethod('getParameterUI').invoke(rpa);
                if (pui != null) {
                    var pcont = pui.getClass().getMethod('getParaContainer').invoke(pui);
                    if (pcont != null) {
                        var pwidgets = [];
                        walk(pcont, 0, pwidgets);
                        if (pwidgets.length > 0) {
                            paramsJson = ',"params":[' + pwidgets.join(',') + ']';
                            out.push('[3.5] param panel: ' + pwidgets.length + ' entries');
                        }
                    }
                }
            }
        } catch (ignP) {}
        T.extractMs = Date.now() - T0 - T.loadMs - T.execMs;
        T.totalMs = Date.now() - T0;
        json = '{"ok":true,"kind":"cpt","template":' + esc(TPL) +
               ',"resultClass":' + esc(String(rwb.getClass().getName())) +
               ',"sheetCount":' + n +
               ',"timing":' + JSON.stringify(T) +
               ',"sheets":[' + sheetsJson.join(',') + ']' + paramsJson + '}';
    }

    // [4] 落盘
    var outFile = new File('__OUT__');
    outFile.getParentFile() && outFile.getParentFile().mkdirs();
    var fos = new FOS(outFile);
    fos.write(new JString(json).getBytes('UTF-8'));
    fos.close();
    out.push('[4] json written: ' + outFile.length() + ' bytes');
    out.push('=== RENDER COMPLETE ===');
} catch (e) {
    out.push('RENDER ERROR: ' + e.toString());
    // 反射场景真实死因在 cause 链(InvocationTargetException 只是包装) — 逐层剥开
    var c = e;
    while (c != null) {
        var cc = c.getCause ? c.getCause() : null;
        if (cc == null) break;
        out.push('  caused by: ' + cc.toString());
        c = cc;
    }
    var st = e.getStackTrace ? e.getStackTrace() : null;
    if (st != null) for (var k = 0; k < Math.min(st.length, 6); k++) out.push('  at ' + st[k].toString());
}
out.join('\n');
