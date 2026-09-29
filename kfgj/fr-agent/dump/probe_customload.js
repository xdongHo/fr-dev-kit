// 探针7: 用 resourcePool 的引擎 loader 构造 PluginFolder + customLoad
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var pool = PM.getMethod("getResourcePool").invoke(null);
    var engineLoader = pool.getClass().getClassLoader();
    out.push("engine loader: " + engineLoader);
    out.push("chain:");
    var l = engineLoader;
    while (l != null) { out.push("  " + l); l = l.getParent(); }

    // A.W.A 构造器
    var AWA = engineLoader.loadClass("com.fr.plugin.A.W.A");
    out.push("A.W.A: " + AWA);
    var ctors = AWA.getDeclaredConstructors();
    var fileCtor = null;
    for (var i = 0; i < ctors.length; i++) {
        var c = ctors[i];
        out.push("ctor: " + c);
        var pts = c.getParameterTypes();
        if (pts.length == 1 && pts[0].getName() == "java.io.File") fileCtor = c;
    }
    if (fileCtor != null) {
        fileCtor.setAccessible(true);
        var File = Java.type("java.io.File");
        var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/validate_enhance/fr-plugin-validate-enhance-1.0"));
        out.push("PluginFolder created: " + folder);

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
