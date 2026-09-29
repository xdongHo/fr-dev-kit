import java.lang.instrument.*;
import java.io.*;

/**
 * JVMTI dump agent v4 — lambda 实现 transformer，避免内部类加载问题
 * 原理: 引擎在 Java 侧解密插件 class 后 defineClass，transformer 截获明文
 */
public class DumpAgent3 {
    public static void agentmain(String args, final Instrumentation inst) {
        final File outDir = new File(args == null || args.trim().isEmpty()
                ? "D:/fr_plugin_dump" : args.trim());
        outDir.mkdirs();
        try {
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write("=== v4 lambda agentmain, retransform=" + inst.isRetransformClassesSupported() + " ===\n");
            fw.close();
        } catch (Exception e) {}

        // lambda → invokedynamic，JVM 运行时生成实现类，无需编译期内部类
        ClassFileTransformer t = (loader, className, classBeingRedefined, pd, classfileBuffer) -> {
            if (className != null && className.startsWith("com/fr/plugin/")) {
                try {
                    File out = new File(outDir, className.replace('/', '.') + ".class");
                    out.getParentFile().mkdirs();
                    FileOutputStream fos = new FileOutputStream(out);
                    fos.write(classfileBuffer);
                    fos.close();
                } catch (Exception e) {}
            }
            return null;
        };
        inst.addTransformer(t);
        try {
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write("transformer registered OK (lambda)\n");
            fw.close();
        } catch (Exception e) {}
    }
}
