// 探针15: Proxy callback + customLoad 完整重放（validate.enhance）
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var File = Java.type("java.io.File");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    var pool = PM.getMethod("getResourcePool").invoke(null);
    var engineLoader = pool.getClass().getClassLoader();

    var AWA = engineLoader.loadClass("com.fr.plugin.A.W.A");
    var fileCtor = AWA.getDeclaredConstructor(File.class);
    fileCtor.setAccessible(true);
    var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/validate_enhance/fr-plugin-validate-enhance-1.0"));
    out.push("PluginFolder created");

    var PTC = cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback");
    var Proxy = Java.type("java.lang.reflect.Proxy");
    var InvocationHandler = Java.type("java.lang.reflect.InvocationHandler");
    var Array = Java.type("java.lang.reflect.Array");
    var ifaces = Array.newInstance(cl.loadClass("java.lang.Class"), 1);
    ifaces[0] = PTC;
    var handler = new InvocationHandler({
        invoke: function(proxy, method, args) {
            if (method.getName() == "done") {
                out.push(">>> CALLBACK done fired!");
                if (args != null && args.length > 0 && args[0] != null) {
                    var r = args[0];
                    out.push("  result class: " + r.getClass().getName());
                    var ms = r.getClass().getMethods();
                    for (var i = 0; i < ms.length; i++) {
                        var m = ms[i];
                        if (m.getParameterTypes().length == 0 && m.getDeclaringClass().getName().indexOf("PluginTaskResult") >= 0) {
                            try { out.push("  " + m.getName() + ": " + m.invoke(r)); } catch (ee) { out.push("  " + m.getName() + " threw: " + ee); }
                        }
                    }
                }
            }
            return null;
        }
    });
    var cb = Proxy.newProxyInstance(cl, ifaces, handler);
    out.push("callback proxy created");

    var ctrl = PM.getMethod("getController").invoke(null);
    var customLoad = ctrl.getClass().getMethod("customLoad",
        cl.loadClass("com.fr.plugin.basic.PluginFolder"),
        cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback"));
    customLoad.invoke(ctrl, folder, cb);
    out.push("customLoad returned, sleeping 10s...");
    java.lang.Thread.sleep(10000);
    out.push("awake");

    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + ctxs.size());
    if (ctxs.size() > 0) {
        for (var i = 0; i < ctxs.size(); i++) {
            out.push("  ctx: " + ctxs.get(i));
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
