// 探针2: 找到能加载插件引擎类的 classloader
var out = [];
var Thread = Java.type("java.lang.Thread");
var HashSet = Java.type("java.util.HashSet");
try {
    var seen = new HashSet();
    var threads = Thread.getAllStackTraces().keySet();
    var it = threads.iterator();
    while (it.hasNext()) {
        var t = it.next();
        var cl = t.getContextClassLoader();
        if (cl == null || seen.contains(cl)) continue;
        seen.add(cl);
        try {
            var c = cl.loadClass("com.fr.plugin.PluginManager");
            out.push("FOUND via thread " + t.getName() + " -> loader " + cl);
            out.push("  loader chain:");
            var l = cl;
            while (l != null) {
                out.push("    " + l);
                l = l.getParent();
            }
        } catch (e) {
            // 该 loader 找不到，继续
        }
    }
    out.push("--- 也试试 system classloaders ---");
    var appCl = Class.forName("java.lang.String").getClassLoader();
    var sysCl = appCl.getParent();
    try {
        sysCl.loadClass("com.fr.plugin.PluginManager");
        out.push("FOUND via SystemClassLoader");
    } catch (e) { out.push("SystemClassLoader: no"); }
    try {
        appCl.loadClass("com.fr.plugin.PluginManager");
        out.push("FOUND via AppClassLoader");
    } catch (e) { out.push("AppClassLoader: no"); }
    out.push("done. " + seen.size() + " distinct context loaders scanned");
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
