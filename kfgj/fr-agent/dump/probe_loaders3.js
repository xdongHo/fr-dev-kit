// 探针3b: 找 PluginManager 的 classloader（用 getSystemClassLoader）
var out = [];
var Thread = Java.type("java.lang.Thread");
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var sysCl = ClassLoader.getSystemClassLoader();
    out.push("SystemClassLoader: " + sysCl);
    try {
        var c = sysCl.loadClass("com.fr.plugin.PluginManager");
        out.push("FOUND via SysClassLoader: " + c + " (loader=" + c.getClassLoader() + ")");
    } catch (e) {
        out.push("SysClassLoader: no");
    }
    try {
        var des = sysCl.loadClass("com.fr.start.Designer");
        out.push("Designer loaded by: " + des.getClassLoader());
        var dcl = des.getClassLoader();
        try {
            var c2 = dcl.loadClass("com.fr.plugin.PluginManager");
            out.push("FOUND via Designer loader: " + c2 + " -> " + c2.getClassLoader());
        } catch (e2) {
            out.push("Designer loader: no");
        }
    } catch (e3) {
        out.push("Designer not loadable: " + e3);
    }
    // 线程扫描
    var HashSet = Java.type("java.util.HashSet");
    var seen = new HashSet();
    var threads = Thread.getAllStackTraces().keySet();
    var it = threads.iterator();
    var found = false;
    while (it.hasNext() && !found) {
        var t = it.next();
        var cl = t.getContextClassLoader();
        if (cl == null || seen.contains(cl)) continue;
        seen.add(cl);
        try {
            var c3 = cl.loadClass("com.fr.plugin.PluginManager");
            out.push("FOUND via thread " + t.getName() + " -> " + c3 + " loader=" + c3.getClassLoader());
            found = true;
        } catch (e4) {}
    }
    if (!found) out.push("thread scan: not found in " + seen.size() + " loaders");
    out.push("done");
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
