import java.lang.instrument.*;
import java.io.*;

public class DumpAgent8119 {
    public static void agentmain(String args, final Instrumentation inst) {
        final File outDir = new File(args == null || args.trim().isEmpty()
                ? "D:/fr_plugin_dump" : args.trim());
        outDir.mkdirs();
        try {
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write("=== DumpAgent8119 v4-lambda attached, retransform=" + inst.isRetransformClassesSupported() + " ===\n");
            fw.close();
        } catch (Exception e) {}
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
            fw.write("transformer registered OK\n");
            fw.close();
        } catch (Exception e) {}
    }
}
