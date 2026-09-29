// Inspect the in-memory WorkBook114 content (read-only, no mutation)
var out = [];

function t(desc, fn) {
    try { out.push(desc + " = " + fn()); }
    catch (e) { out.push(desc + " -> ERR: " + e); }
}

var H = Java.type("com.fr.design.file.HistoryTemplateListCache");
var jt = H.getInstance().getCurrentEditingTemplate();

t("tpl.class", function () { return jt.getClass().getName(); });

// WorkBook -> sheet count
t("sheet.count", function () {
    var wb = jt.getTarget();
    return String(wb.getReportCount());
});

t("target.class", function () {
    var wb = jt.getTarget();
    return wb.getClass().getName();
});

// Dataset count (TableDataMap)
t("datasets", function () {
    var wb = jt.getTarget();
    try {
        var map = wb.getTableDataMap();
        var keys = map.keySet().toArray();
        var names = [];
        for (var i = 0; i < keys.length; i++) { names.push(String(keys[i])); }
        return names.length + " [" + names.join(", ") + "]";
    } catch (e) { return "getTableDataMap failed: " + e; }
});

// Parameters (ParameterUI / Parameter widgets)
t("parameters", function () {
    var wb = jt.getTarget();
    try {
        var ps = wb.getParameters();
        var names = [];
        for (var i = 0; i < ps.length; i++) { names.push(String(ps[i].getName())); }
        return ps.length + " [" + names.join(", ") + "]";
    } catch (e) { return "getParameters failed: " + e; }
});

// Parameter pane widgets (the actual controls on the panel)
t("paraPane.widgets", function () {
    var wb = jt.getTarget();
    try {
        var pp = wb.getParameterPane();
        if (pp == null) { return "no ParameterPane"; }
        var ws = pp.getWidgets();
        if (ws == null) { return "getWidgets() = null"; }
        var arr = [];
        for (var i = 0; i < ws.length; i++) {
            var w = ws[i];
            var nm = "";
            try { nm = String(w.getWidgetName()); } catch (e2) { nm = "?"; }
            arr.push(w.getClass().getSimpleName() + "#" + nm);
        }
        return ws.length + " -> " + arr.join(" | ");
    } catch (e) { return "paraPane failed: " + e; }
});

// Cell element count on first sheet
t("sheet0.cells", function () {
    var wb = jt.getTarget();
    var ec = wb.getReport(0);
    if (ec == null) { return "no sheet0"; }
    try {
        var it = ec.cellIterator();
        var n = 0;
        while (it.hasNext()) { it.next(); n++; if (n > 5000) break; }
        return String(n) + (n > 5000 ? "+ (truncated)" : "");
    } catch (e) { return "cellIterator failed: " + e; }
});

out.join("\n");
