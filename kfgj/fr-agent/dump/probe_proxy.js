// 探针14: 定位 ClassCastException + 尝试 Proxy callback
var out = [];
var ClassLoader = Java.type("java.lang.ClassLoader");
try {
    var cl = ClassLoader.getSystemClassLoader();
    out.push("1. sysCl: " + cl);
    var PTC = cl.loadClass("com.fr.plugin.manage.control.PluginTaskCallback");
    out.push("2. PTC class: " + PTC);
    var Proxy = Java.type("java.lang.reflect.Proxy");
    var InvocationHandler = Java.type("java.lang.reflect.InvocationHandler");
    out.push("3. Proxy: " + Proxy);
    var Array = Java.type("java.lang.reflect.Array");
    var ifaces = Array.newInstance(cl.loadClass("java.lang.Class"), 1);
    ifaces[0] = PTC;
    out.push("4. ifaces array created");
    var handler = new InvocationHandler({
        invoke: function(proxy, method, args) {
            out.push("CALLBACK: " + method.getName() + " args=" + args);
            if (args != null && args.length > 0) {
                var r = args[0];
                out.push("  result: " + r);
                try { out.push("  isSuccess: " + r.getClass().getMethod("isSuccess").invoke(r)); } catch (e1) { out.push("  isSuccess n/a: " + e1); }
                try { out.push("  errorCode: " + r.getClass().getMethod("getErrorCode").invoke(r)); } catch (e2) { out.push("  errorCode n/a: " + e2); }
                try { out.push("  errorMessage: " + r.getClass().getMethod("getErrorMessage").invoke(r)); } catch (e3) { out.push("  errorMessage n/a: " + e3); }
            }
            return null;
        }
    });
    out.push("5. handler created");
    var cb = Proxy.newProxyInstance(cl, ifaces, handler);
    out.push("6. callback proxy: " + cb);
} catch (e) {
    out.push("ERROR at: " + e);
    out.push(e.stack);
}
out.join("\n");
