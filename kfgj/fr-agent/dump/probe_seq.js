// 探针12: customLoad function.sequence（之前成功样本）+ 后续等待检查
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
var File = Java.type("java.io.File");
var Thread = Java.type("java.lang.Thread");
try {
    var cl = ClassLoader.getSystemClassLoader();
    var PM = cl.loadClass("com.fr.plugin.manage.PluginManager");
    out.push("hasStarted: " + PM.getMethod("hasStarted").invoke(null));
    var pool = PM.getMethod("getResourcePool").invoke(null);
    var engineLoader = pool.getClass().getClassLoader();

    var AWA = engineLoader.loadClass("com.fr.plugin.A.W.A");
    var fileCtor = AWA.getDeclaredConstructor(File.class);
    fileCtor.setAccessible(true);
    var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/function_sequence/fine-plugin-com.fr.plugin.function.sequence-2.0.2"));
    out.push("PluginFolder: " + folder);

    var ctrl = PM.getMethod("getController").invoke(null);
    out.push("controller: " + ctrl);
    var customLoad = ctrl.getClass().getMethod("customLoad",
        cl.loadClass("com.fr.plugin.basic.PluginFolder"),
        cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback"));
    customLoad.invoke(ctrl, folder, null);
    out.push("customLoad invoked, sleeping 8s...");
    Thread.sleep(8000);

    var ctxs = PM.getMethod("getContexts").invoke(null);
    out.push("contexts size: " + ctxs.size());
    if (ctxs.size() > 0) {
        for (var i = 0; i < ctxs.size(); i++) {
            var ctx = ctxs.get(i);
            out.push("  ctx[" + i + "]: " + ctx);
            try {
                out.push("    isRunning: " + ctx.getClass().getMethod("isRunning").invoke(ctx));
            } catch (e1) {
                out.push("    isRunning probe fail: " + e1);
            }
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
