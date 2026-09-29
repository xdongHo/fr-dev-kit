// 探查 Designer 当前打开的模板列表（只读，不修改任何状态）
var out = [];

function tryGet(desc, fn) {
    try { out.push(desc + " = " + fn()); }
    catch (e) { out.push(desc + " -> ERR: " + e); }
}

// 1) 当前编辑模板
tryGet("current.path", function () {
    var C = Java.type("com.fr.design.file.HistoryTemplateListCache");
    var jt = C.getInstance().getCurrentEditingTemplate();
    return jt == null ? "NONE" : String(jt.getPath());
});

// 2) 当前模板是否已保存/脏标记
tryGet("current.dirty", function () {
    var C = Java.type("com.fr.design.file.HistoryTemplateListCache");
    var jt = C.getInstance().getCurrentEditingTemplate();
    if (jt == null) return "NONE";
    try { return String(jt.isSaved ? jt.isSaved() : "n/a"); }
    catch (e2) { return "no isSaved(): " + e2; }
});

// 3) 历史模板列表（最近打开）
tryGet("history.list", function () {
    var C = Java.type("com.fr.design.file.HistoryTemplateListCache");
    var inst = C.getInstance();
    var m = null;
    // 尝试常见 getter
    ["getHistoryTemplates", "getTemplateList", "getRecentTemplates", "getAllTemplates"].forEach(function (name) {
        try { if (typeof inst[name] === "function") { var v = inst[name](); if (v != null) m = (m || "") + name + ":" + v + "; "; } } catch (e) {}
    });
    return m == null ? "no getter" : m;
});

// 4) Designer 主frame / 打开的模板标签页
tryGet("designer.frames", function () {
    var F = Java.type("java.awt.Frame");
    var fs = F.getFrames();
    var names = [];
    for (var i = 0; i < fs.length; i++) {
        try { names.push(fs[i].getTitle()); } catch (e) {}
    }
    return names.join(" | ");
});

// 5) 工作簿类型判定
tryGet("workbook.class", function () {
    var C = Java.type("com.fr.design.file.HistoryTemplateListCache");
    var jt = C.getInstance().getCurrentEditingTemplate();
    return jt == null ? "NONE" : String(jt.getClass().getName());
});

out.join("\n");
