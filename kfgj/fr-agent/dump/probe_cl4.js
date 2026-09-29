// 探针10c: Java.type 接口实现 + customLoad
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var File = Java.type("java.io.File");
var PTC = Java.type("com.fr.plugin.manage.control.PluginTaskCallback");
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

    var cb = new PTC({
        done: function(result) {
            out.push("callback done: " + result);
            try { out.push("  isSuccess: " + result.getClass().getMethod("isSuccess").invoke(result)); } catch (e1) {}
            try { out.push("  errorCode: " + result.getClass().getMethod("getErrorCode").invoke(result)); } catch (e2) {}
            try { out.push("  errorMessage: " + result.getClass().getMethod("getErrorMessage").invoke(result)); } catch (e3) {}
        }
    });
    out.push("callback created");

    var ctrl = PM.getMethod("getController").invoke(null);
    var customLoad = ctrl.getClass().getMethod("customLoad",
        cl.loadClass("com.fr.plugin.basic.PluginFolder"),
        cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback"));
    customLoad.invoke(ctrl, folder, cb);
    out.push("customLoad invoked, sleeping 6s...");
    java.lang.Thread.sleep(6000);

    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + ctxs.size());
    if (ctxs.size() > 0) {
        for (var i = 0; i < ctxs.size(); i++) {
            out.push("  ctx[" + i + "]: " + ctxs.get(i));
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
