"""生成新类名 DumpAgent + 编译打包 + attach 一条龙
用法: python dump_attach.py <pid> [输出目录]
绕过 JVM 同名 agent 类缓存: 每次生成 DumpAgentXXXX 随机后缀类名
"""
import os, sys, random, subprocess, time

DUMP_DIR = r"<工具包根目录>(个人版)\fr-agent\dump"
JDK = r"D:\jdk8\jdk8u432-b06\bin"
FR_JRE = r"D:\FineReport_10.0\jre\bin"
ATTACHER_CP = r"<工具包根目录>(个人版)\fr-agent"
FR_PID = sys.argv[1] if len(sys.argv) > 1 else "18684"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else r"D:\fr_plugin_dump"

suffix = "%04d" % random.randint(1000, 9999)
cls = "DumpAgent" + suffix
jar = cls + ".jar"
mf = "manifest_" + suffix + ".txt"

src = f'''import java.lang.instrument.*;
import java.io.*;

public class {cls} {{
    public static void agentmain(String args, final Instrumentation inst) {{
        final File outDir = new File(args == null || args.trim().isEmpty()
                ? "D:/fr_plugin_dump" : args.trim());
        outDir.mkdirs();
        try {{
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write("=== {cls} v4-lambda attached, retransform=" + inst.isRetransformClassesSupported() + " ===\\n");
            fw.close();
        }} catch (Exception e) {{}}
        ClassFileTransformer t = (loader, className, classBeingRedefined, pd, classfileBuffer) -> {{
            if (className != null && className.startsWith("com/fr/plugin/")) {{
                try {{
                    File out = new File(outDir, className.replace('/', '.') + ".class");
                    out.getParentFile().mkdirs();
                    FileOutputStream fos = new FileOutputStream(out);
                    fos.write(classfileBuffer);
                    fos.close();
                }} catch (Exception e) {{}}
            }}
            return null;
        }};
        inst.addTransformer(t);
        try {{
            FileWriter fw = new FileWriter(new File(outDir, "_agent_log.txt"), true);
            fw.write("transformer registered OK\\n");
            fw.close();
        }} catch (Exception e) {{}}
    }}
}}
'''

java_path = os.path.join(DUMP_DIR, cls + ".java")
with open(java_path, "w", encoding="utf-8") as f:
    f.write(src)
with open(os.path.join(DUMP_DIR, mf), "w") as f:
    f.write(f"Agent-Class: {cls}\n")

# 编译
r = subprocess.run([os.path.join(JDK, "javac.exe"), "-encoding", "UTF-8",
                    os.path.join(DUMP_DIR, cls + ".java")],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("COMPILE FAIL:", r.stderr)
    sys.exit(1)
# 打包（只打主类，用相对路径避免 jar 内绝对路径）
r = subprocess.run([os.path.join(JDK, "jar.exe"), "cfm",
                    os.path.join(DUMP_DIR, jar), os.path.join(DUMP_DIR, mf),
                    cls + ".class"], cwd=DUMP_DIR,
                   capture_output=True, text=True)
if r.returncode != 0:
    print("JAR FAIL:", r.stderr)
    sys.exit(1)

# attach
log_file = os.path.join(OUT_DIR, "_agent_log.txt")
if os.path.exists(log_file):
    os.remove(log_file)
r = subprocess.run([os.path.join(FR_JRE, "java.exe"), "-cp",
                    ATTACHER_CP + ";D:/FineReport_10.0/jre/lib/tools.jar",
                    "Attacher", FR_PID, os.path.join(DUMP_DIR, jar), OUT_DIR],
                   capture_output=True, text=True, timeout=60)
print("attach stdout:", r.stdout.strip())
print("attach stderr:", r.stderr.strip())
time.sleep(2)
if os.path.exists(log_file):
    print(open(log_file, encoding="utf-8", errors="replace").read())
print(f"agent class: {cls}, jar: {jar}")
