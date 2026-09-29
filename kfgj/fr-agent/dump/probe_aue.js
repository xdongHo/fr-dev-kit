// 探针11: 直接实例化插件类加载器 A.U.E（绕过 customLoad 注册）
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var File = Java.type("java.io.File");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var pool = PM.getMethod("getResourcePool").invoke(null);
    var engineLoader = pool.getClass().getClassLoader();

    // 插件类加载器 A.U.E
    var AUE = engineLoader.loadClass("com.fr.plugin.A.U.E");
    out.push("A.U.E: " + AUE);
    var ctors = AUE.getDeclaredConstructors();
    for (var i = 0; i < ctors.length; i++) {
        out.push("ctor: " + ctors[i]);
    }
    var methods = AUE.getDeclaredMethods();
    for (var j = 0; j < methods.length; j++) {
        out.push("method: " + methods[j]);
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
