var result = "";
try {
  // Nashorn 需要 Java.type
  var Class = Java.type("java.lang.Class");
  var cls = Class.forName("com.fr.plugin.ExtraClassManager");
  var pd = cls.getProtectionDomain();
  var cs = pd.getCodeSource();
  result += "ExtraClassManager source: " + (cs != null ? cs.getLocation() : "null") + "\n";

  // 获取 PluginManager
  try {
    var pmCls = Class.forName("com.fr.plugin.PluginManager");
    var pmMethods = pmCls.getDeclaredMethods();
    for (var i = 0; i < pmMethods.length && i < 15; i++) {
      result += "PM: " + pmMethods[i] + "\n";
    }
  } catch(e) { result += "PM: " + e + "\n"; }

  // 获取 Bridge/PluginBridge
  try {
    var bridgeCls = Class.forName("bridge.FinePluginBridge");
    result += "Bridge found\n";
    var bMethods = bridgeCls.getDeclaredMethods();
    for (var i = 0; i < bMethods.length && i < 10; i++) {
      result += "Bridge: " + bMethods[i] + "\n";
    }
  } catch(e) { result += "Bridge: " + e + "\n"; }

  // 尝试获取 ClassLoader 列表
  try {
    var sysCl = Class.forName("java.lang.ClassLoader");
    var getCC = sysCl.getDeclaredMethod("getClassLoader", Class.class);
    getCC.setAccessible(true);
    var loader = getCC.invoke(null, cls);
    result += "Loader: " + loader + "\n";
    result += "Loader class: " + loader.getClass().getName() + "\n";

    // 获取该 loader 加载的所有类
    var fld = loader.getClass().getDeclaredField("classes");
    fld.setAccessible(true);
    var classes = fld.get(loader);
    if (classes != null) {
      var it = classes.iterator();
      var count = 0;
      while (it.hasNext() && count < 10) {
        var c = it.next();
        result += "  loaded: " + c.getName() + "\n";
        count++;
      }
      result += "  total: " + classes.size() + "\n";
    }
  } catch(e) { result += "Loader: " + e + "\n"; }

} catch(e) { result += "Error: " + e.toString(); }
result;
