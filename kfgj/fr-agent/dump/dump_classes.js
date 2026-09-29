var result = "";
try {
  // 方案1: 通过 ProtectionDomain.CodeSource 获取已加载类的来源
  var cls = Class.forName("com.fr.plugin.ExtraClassManager");
  var pd = cls.getProtectionDomain();
  var cs = pd.getCodeSource();
  result += "ExtraClassManager source: " + (cs != null ? cs.getLocation() : "null") + "\n";

  // 方案2: 遍历所有已加载类，找插件类
  var allLoaded = java.lang.instrument.Instrumentation;
  // 没有直接访问 Instrumentation

  // 方案3: 通过 PluginManager 获取插件类加载器
  try {
    var pmCls = Class.forName("com.fr.plugin.PluginManager");
    result += "PluginManager found\n";
    var methods = pmCls.getDeclaredMethods();
    for (var i = 0; i < methods.length && i < 20; i++) {
      result += "  " + methods[i] + "\n";
    }
  } catch(e) { result += "PluginManager: " + e + "\n"; }

  // 方案4: 通过 FineRuntime 获取类加载器
  try {
    var frCls = Class.forName("com.fr.start.FineRuntime");
    result += "FineRuntime found\n";
    var methods = frCls.getDeclaredMethods();
    for (var i = 0; i < methods.length && i < 10; i++) {
      result += "  " + methods[i] + "\n";
    }
  } catch(e) { result += "FineRuntime: " + e + "\n"; }

  // 方案5: 尝试用 sun.misc.Unsafe 获取字节码
  try {
    var unsafeCls = Class.forName("sun.misc.Unsafe");
    unsafeCls.getDeclaredField("theUnsafe").setAccessible(true);
    var unsafe = unsafeCls.getDeclaredField("theUnsafe").get(null);
    result += "Unsafe obtained\n";
  } catch(e) { result += "Unsafe: " + e + "\n"; }

} catch(e) { result += "Error: " + e.toString(); }
result;
