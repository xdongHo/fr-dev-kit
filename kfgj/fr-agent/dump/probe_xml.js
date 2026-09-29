// 探针17: 手动验证 PluginFolder.getXmlAsStream + ClassPathHolder 方法
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
    var folder = fileCtor.newInstance(new File("D:/fr_plugin_dump/plugin_work/function_sequence/fine-plugin-com.fr.plugin.function.sequence-2.0.2"));

    // getXmlAsStream
    var is = folder.getClass().getMethod("getXmlAsStream").invoke(folder);
    out.push("getXmlAsStream: " + is);
    if (is != null) {
        var bytes = [];
        var b = is.read();
        while (b != -1 && bytes.length < 200) { bytes.push(b); b = is.read(); }
        out.push("xml head: " + java.lang.String.valueOf(bytes));
    }
    // ClassPathHolder 接口方法
    var CPH = cl.loadClass("com.fr.plugin.basic.ClassPathHolder");
    out.push("ClassPathHolder methods:");
    var cms = CPH.getMethods();
    for (var i = 0; i < cms.length; i++) {
        out.push("  " + cms[i]);
    }
    // folder 的所有 getter
    var fms = folder.getClass().getMethods();
    out.push("A.W.A methods:");
    for (var j = 0; j < fms.length; j++) {
        var m = fms[j];
        if (m.getParameterTypes().length == 0 && !m.getName().startsWith("getClass")) {
            try {
                out.push("  " + m.getName() + "(): " + m.invoke(folder));
            } catch (ee) {
                out.push("  " + m.getName() + "(): threw " + ee);
            }
        }
    }
} catch (e) {
    out.push("ERROR: " + e);
    out.push(e.stack);
}
out.join("\n");
