// 探针10: 带真实 callback 的 customLoad + 结果诊断
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

    var PTC = cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback");
    var PTR = cl.loadClass("com.fr.plugin.manage.control.PluginTaskResult");
    out.push("PluginTaskResult methods:");
    var m2 = PTR.getMethods();
    for (var i = 0; i < m2.length; i++) {
        if (m2[i].getDeclaringClass().getName().indexOf("PluginTaskResult") >= 0) {
            out.push("  " + m2[i]);
        }
    }

    var holder = { done: null };
    var cb = Java.extend(PTC, {
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
            holder.done = true;
        }
    });
    out.push("callback created: " + cb);

    var ctrl = PM.getMethod("getController").invoke(null);
    var customLoad = ctrl.getClass().getMethod("customLoad",
        cl.loadClass("com.fr.plugin.basic.PluginFolder"), PTC);
    customLoad.invoke(ctrl, folder, cb);
    out.push("customLoad invoked, waiting...");
    Thread.currentThread().sleep(5000);
    out.push("after sleep 5s");

    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + ctxs.size());
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
