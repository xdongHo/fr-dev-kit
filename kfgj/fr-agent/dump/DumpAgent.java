import java.lang.instrument.*;
import java.io.*;
import java.security.*;

/**
 * JVMTI dump agent v3 — 截获 defineClass 前的明文字节，带完整异常日志
 */
public class DumpAgent {
    static void log(File outDir, String msg) {
        try {
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write(msg + "\n");
            fw.close();
        } catch (Exception e) {}
    }

    public static void agentmain(String args, Instrumentation inst) {
        final File outDir = new File(args == null || args.trim().isEmpty()
                ? "D:/fr_plugin_dump" : args.trim());
        outDir.mkdirs();
        log(outDir, "=== agentmain v3 called, retransform=" + inst.isRetransformClassesSupported() + " ===");
        try {
            inst.addTransformer(new ClassFileTransformer() {
                public byte[] transform(ClassLoader loader, String className,
                        Class<?> classBeingRedefined, ProtectionDomain pd, byte[] classfileBuffer) {
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
                }
            });
            log(outDir, "transformer registered OK");
        } catch (Throwable t) {
            StringWriter sw = new StringWriter();
            t.printStackTrace(new PrintWriter(sw));
            log(outDir, "addTransformer FAILED: " + sw.toString());
        }
    }
}
