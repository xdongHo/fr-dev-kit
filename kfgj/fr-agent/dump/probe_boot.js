// 探针5: 引导引擎 + customLoad 解密插件
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var FR = cl.loadClass("com.fr.runtime.FineRuntime");
    out.push("FineRuntime loaded");

    // 1. 引导引擎
    FR.getMethod("start").invoke(null);
    out.push("FineRuntime.start() done");

    // 2. 检查引擎状态
    var hasStarted = PM.getMethod("hasStarted").invoke(null);
    out.push("hasStarted: " + hasStarted);

    if (!hasStarted) {
        PM.getMethod("startEngine").invoke(null);
        out.push("startEngine() called");
        hasStarted = PM.getMethod("hasStarted").invoke(null);
        out.push("hasStarted after startEngine: " + hasStarted);
    }

    // 3. 反射构造 PluginFolder (A.W.A 的 A(File))
    var AWA = cl.loadClass("com.fr.plugin.A.W.A");
    out.push("A.W.A loaded: " + AWA + " loader=" + AWA.getClassLoader());
    var ctors = AWA.getDeclaredConstructors();
    var fileCtor = null;
    for (var i = 0; i < ctors.length; i++) {
        var c = ctors[i];
        out.push("ctor: " + c);
        var pts = c.getParameterTypes();
        if (pts.length == 1 && pts[0].getName() == "java.io.File") fileCtor = c;
    }
    if (fileCtor == null) {
        out.push("NO File ctor found");
    } else {
        fileCtor.setAccessible(true);
        var File = Java.type("java.io.File");
        var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/validate_enhance/fr-plugin-validate-enhance-1.0"));
        out.push("PluginFolder created: " + folder);

        // 4. customLoad
        var ctrl = PM.getMethod("getController").invoke(null);
        out.push("controller: " + ctrl);
        var customLoad = ctrl.getClass().getMethod("customLoad",
            cl.loadClass("com.fr.plugin.basic.PluginFolder"),
            cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback"));
        customLoad.invoke(ctrl, folder, null);
        out.push("customLoad() invoked OK");
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
