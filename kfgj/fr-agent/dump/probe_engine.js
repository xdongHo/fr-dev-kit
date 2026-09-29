// 探针1: 引擎状态 + customLoad 签名
var out = [];
var Thread = Java.type("java.lang.Thread");
var C = function(n) { return Thread.currentThread().getContextClassLoader().loadClass(n); };
try {
    var PM = C("com.fr.plugin.PluginManager");
    out.push("PluginManager loaded");
    var getController = PM.getMethod("getController");
    var ctrl = getController.invoke(null);
    out.push("controller: " + ctrl);
    if (ctrl != null) {
        var cls = ctrl.getClass();
        out.push("controller class: " + cls.getName());
        var methods = cls.getMethods();
        for (var i = 0; i < methods.length; i++) {
            var m = methods[i];
            if (m.getName().toLowerCase().indexOf("load") >= 0) {
                out.push("method: " + m.getName() + "(" + m.getParameterTypes().toString() + ")");
            }
        }
    }
    try {
        var isRunning = PM.getMethod("isEngineRunning");
        out.push("isEngineRunning: " + isRunning.invoke(null));
    } catch (e) {
        out.push("isEngineRunning: n/a (" + e + ")");
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
