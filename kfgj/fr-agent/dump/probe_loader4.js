// 探针6: 从引擎上下文/线程找能加载 A.W.A 的 classloader
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var Thread = Java.type("java.lang.Thread");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");

    // 1. getContexts 找插件上下文
    try {
        var ctxs = PM.getMethod("getContexts").invoke(null);
        out.push("contexts: " + ctxs);
        if (ctxs != null && ctxs.size() > 0) {
            var ctx = ctxs.get(0);
            var ctxCls = ctx.getClass();
            out.push("ctx0 class: " + ctxCls + " loader=" + ctxCls.getClassLoader());
            // 尝试用 ctx 的 loader 加载 A.W.A
            try {
                var AWA = ctxCls.getClassLoader().loadClass("com.fr.plugin.A.W.A");
                out.push("A.W.A via ctx loader: " + AWA);
            } catch (e1) {
                out.push("ctx loader: no A.W.A (" + e1 + ")");
            }
        }
    } catch (e2) {
        out.push("getContexts failed: " + e2);
    }

    // 2. 线程扫描（引擎启动后可能有新线程）
    var HashSet = Java.type("java.util.HashSet");
    var seen = new HashSet();
    var threads = Thread.getAllStackTraces().keySet();
    var it = threads.iterator();
    var found = false;
    while (it.hasNext() && !found) {
        var t = it.next();
        var tcl = t.getContextClassLoader();
        if (tcl == null || seen.contains(tcl)) continue;
        seen.add(tcl);
        try {
            var c = tcl.loadClass("com.fr.plugin.A.W.A");
            out.push("A.W.A via thread " + t.getName() + " loader=" + tcl);
            out.push("  chain:");
            var l = tcl;
            while (l != null) { out.push("    " + l); l = l.getParent(); }
            found = true;
        } catch (e3) {}
    }
    if (!found) out.push("thread scan no A.W.A in " + seen.size() + " loaders");

    // 3. getResourcePool
    try {
        var pool = PM.getMethod("getResourcePool").invoke(null);
        out.push("resourcePool: " + pool + " cls=" + (pool == null ? "null" : pool.getClass()));
    } catch (e4) {
        out.push("resourcePool failed: " + e4);
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
