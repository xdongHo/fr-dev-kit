// 探针13: 检查插件加载的其他入口 + 引擎日志 flush
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    // getContext(String)
    try {
        var ctx1 = PM.getMethod("getContext", cl.loadClass("java.lang.String")).invoke(null, "com.fr.plugin.validate.enhance");
        out.push("getContext(validate.enhance): " + ctx1);
    } catch (e1) {
        out.push("getContext(String) fail: " + e1);
    }
    // PluginMarker 构造
    try {
        var Marker = cl.loadClass("com.fr.plugin.context.PluginMarker");
        out.push("PluginMarker: " + Marker);
        var create = Marker.getMethod("create", cl.loadClass("java.lang.String"), cl.loadClass("java.lang.String"));
        var mk = create.invoke(null, "com.fr.plugin.validate.enhance", "1.0");
        out.push("marker: " + mk);
        var ctx2 = PM.getMethod("getContext", cl.loadClass("com.fr.plugin.context.PluginMarker")).invoke(null, mk);
        out.push("getContext(marker): " + ctx2);
    } catch (e2) {
        out.push("marker path fail: " + e2);
    }
    // 引擎资源池 dump：看看加载器列表
    try {
        var pool = PM.getMethod("getResourcePool").invoke(null);
        out.push("pool: " + pool);
        var ms = pool.getClass().getMethods();
        for (var i = 0; i < ms.length; i++) {
            out.push("  pool method: " + ms[i].getName());
        }
    } catch (e3) {
        out.push("pool fail: " + e3);
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
