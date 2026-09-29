// 探针4: 引擎状态 + A.W.A 构造器
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    out.push("PluginManager loaded: " + PM);
    var hasStarted = PM.getMethod("hasStarted");
    out.push("hasStarted: " + hasStarted.invoke(null));
    // getController
    var getController = PM.getMethod("getController");
    var ctrl = getController.invoke(null);
    out.push("controller: " + ctrl);
    // A.W.A 构造器
    try {
        var AWA = cl.loadClass("com.fr.plugin.A.W.A");
        out.push("A.W.A loaded: " + AWA + " (loader=" + AWA.getClassLoader() + ")");
        var ctors = AWA.getDeclaredConstructors();
        for (var i = 0; i < ctors.length; i++) {
            out.push("ctor: " + ctors[i]);
        }
    } catch (e) {
        out.push("A.W.A load FAIL: " + e);
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
