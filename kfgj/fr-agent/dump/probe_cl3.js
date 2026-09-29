// 探针10b: Nashorn 接口实现语法修正
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var File = Java.type("java.io.File");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var pool = PM.getMethod("getResourcePool").invoke(null);
    var engineLoader = pool.getClass().getClassLoader();

    var AWA = engineLoader.loadClass("com.fr.plugin.A.W.A");
    var fileCtor = AWA.getDeclaredConstructor(File);
    fileCtor.setAccessible(true);
    var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/validate_enhance/fr-plugin-validate-enhance-1.0"));
    out.push("PluginFolder: " + folder);

    // Nashorn 接口实现
    var cb = new com.fr.plugin.manage.control.PluginTaskCallback({
        done: function(result) {
            out.push("callback done: " + result);
            try {
                var m = result.getClass().getMethod("isSuccess");
                out.push("  isSuccess: " + m.invoke(result));
            } catch (e1) {}
            try {
                var m3 = result.getClass().getMethod("getErrorCode");
                out.push("  errorCode: " + m3.invoke(result));
            } catch (e2) {}
            try {
                var m4 = result.getClass().getMethod("getErrorMessage");
                out.push("  errorMessage: " + m4.invoke(result));
            } catch (e3) {}
        }
    });
    out.push("callback created: " + cb);

    var ctrl = PM.getMethod("getController").invoke(null);
    out.push("controller: " + ctrl);
    var customLoad = ctrl.getClass().getMethod("customLoad",
        cl.loadClass("com.fr.plugin.basic.PluginFolder"),
        cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback"));
    customLoad.invoke(ctrl, folder, cb);
    out.push("customLoad invoked, sleeping 5s...");
    java.lang.Thread.sleep(5000);
    out.push("after sleep");

    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + ctxs.size());
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
