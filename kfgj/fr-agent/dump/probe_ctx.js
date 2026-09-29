// 探针8: customLoad 后检查插件上下文状态
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + (ctxs == null ? "null" : ctxs.size()));
    if (ctxs != null) {
        for (var i = 0; i < ctxs.size(); i++) {
            var ctx = ctxs.get(i);
            out.push("ctx[" + i + "]: " + ctx);
            try {
                out.push("  running: " + ctx.getClass().getMethod("isRunning").invoke(ctx));
            } catch (e1) {}
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
