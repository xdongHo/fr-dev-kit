// 探针3: 找 PluginManager 的 classloader（修正版）
var out = [];
var Thread = Java.type("java.lang.Thread");
var StringCls = Java.type("java.lang.String");
try {
    var appCl = StringCls.class.getClassLoader();
    var sysCl = appCl.getParent();
    out.push("String classloader: " + appCl);
    out.push("System classloader: " + sysCl);
    try {
        var c = appCl.loadClass("com.fr.plugin.PluginManager");
        out.push("FOUND via AppClassLoader: " + c + " (loader=" + c.getClassLoader() + ")");
    } catch (e) {
        out.push("AppClassLoader: no (" + e + ")");
    }
    // fine-core 也可能由设计器的 URLClassLoader 加载（designer.bat classpath）
    // 试试从已加载类找：com.fr.start.Designer 的 loader
    try {
        var des = appCl.loadClass("com.fr.start.Designer");
        out.push("Designer loaded by: " + des.getClassLoader());
        var dcl = des.getClassLoader();
        try {
            var c2 = dcl.loadClass("com.fr.plugin.PluginManager");
            out.push("FOUND via Designer loader: " + c2 + " -> " + c2.getClassLoader());
        } catch (e2) {
            out.push("Designer loader: no (" + e2 + ")");
        }
    } catch (e3) {
        out.push("Designer not in AppClassLoader: " + e3);
        // 遍历线程找 Designer
        var HashSet = Java.type("java.util.HashSet");
        var seen = new HashSet();
        var threads = Thread.getAllStackTraces().keySet();
        var it = threads.iterator();
        while (it.hasNext()) {
            var t = it.next();
            var cl = t.getContextClassLoader();
            if (cl == null || seen.contains(cl)) continue;
            seen.add(cl);
            try {
                var c3 = cl.loadClass("com.fr.plugin.PluginManager");
                out.push("FOUND via thread " + t.getName() + " -> " + c3 + " loader=" + c3.getClassLoader());
                break;
            } catch (e4) {}
        }
    }
    out.push("scan done");
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
