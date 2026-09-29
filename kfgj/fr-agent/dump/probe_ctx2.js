// 探针9: 重查 contexts（customLoad 后）
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
                out.push("  isRunning: " + ctx.getClass().getMethod("isRunning").invoke(ctx));
                out.push("  getMarker: " + ctx.getClass().getMethod("getMarker").invoke(ctx));
            } catch (e1) {
                out.push("  probe fail: " + e1);
            }
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
