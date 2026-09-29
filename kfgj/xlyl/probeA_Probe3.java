import java.io.*;
import java.util.*;
import java.lang.reflect.*;

/**
 * FR Headless Probe v3 — 尝试绕过完整 FR 运行时初始化
 * 
 * 策略：
 * 1. 直接用 WorkBook.readStream 但先初始化 WorkContext
 * 2. 如果不行，尝试找到不需要 ConfigurationActivator 的读取路径
 * 3. 尝试直接实例化 WorkSheet 并手动填充
 */
public class Probe3 {

    static StringBuilder report = new StringBuilder();
    
    static void log(String msg) {
        System.out.println(msg);
        report.append(msg).append("\n");
    }

    // ============ 尝试不同的初始化策略 ============
    static boolean tryInitWithWorkContext() {
        log("\n========== 初始化策略 1: WorkContext.switchTo ==========");
        try {
            String webInfPath = "C:\\Program Files\\FineReport_10.0\\webapps\\webroot\\WEB-INF";
            
            // 先 checkIn
            Class<?> simpleWorkCls = Class.forName("com.fr.workspace.simple.SimpleWork");
            Method checkIn = simpleWorkCls.getMethod("checkIn", String.class);
            checkIn.invoke(null, webInfPath);
            log("  SimpleWork.checkIn 成功");
            
            // 验证
            Class<?> workContextCls = Class.forName("com.fr.workspace.WorkContext");
            Method getCurrent = workContextCls.getMethod("getCurrent");
            Object current = getCurrent.invoke(null);
            Method getPath = current.getClass().getMethod("getPath");
            String path = (String) getPath.invoke(current);
            log("  WorkContext.getCurrent().getPath() = " + path);
            
            // 尝试启动 ConfigurationActivator
            log("\n  尝试启动 ConfigurationActivator...");
            try {
                Class<?> moduleContextCls = Class.forName("com.fr.general.ModuleContext");
                Method startModule = moduleContextCls.getMethod("startModule", String.class);
                startModule.invoke(null, "com.fr.config.ConfigurationActivator");
                log("  ✅ ConfigurationActivator 启动成功");
                return true;
            } catch (Exception e) {
                log("  ❌ ConfigurationActivator 启动失败: " + e.getMessage());
                if (e.getCause() != null) log("    Cause: " + e.getCause().getMessage());
            }
            
            return true; // checkIn 成功了
        } catch (Exception e) {
            log("  ❌ 初始化失败:");
            printException(e, 5);
            return false;
        }
    }

    // ============ STEP 1: 模板解析 ============
    static Object tryParseTemplate(String cptPath) {
        log("\n========== STEP 1: 模板解析 ==========");
        log("模板路径: " + cptPath);

        // 方案 A: WorkBook.readStream
        try {
            log("[1A] 尝试 new WorkBook().readStream(InputStream)...");
            Class<?> wbClass = Class.forName("com.fr.main.impl.WorkBook");
            Object wb = wbClass.newInstance();
            Method readStream = wbClass.getMethod("readStream", InputStream.class);
            
            FileInputStream fis = new FileInputStream(cptPath);
            readStream.invoke(wb, fis);
            fis.close();

            log("  ✅ readStream 成功!");
            return wb;

        } catch (Exception e) {
            log("  ❌ readStream 失败:");
            Throwable cause = e.getCause();
            if (cause != null) {
                log("    Cause: " + cause.getClass().getName() + ": " + cause.getMessage());
                if (cause.getCause() != null) {
                    log("    Root cause: " + cause.getCause().getClass().getName() + ": " + cause.getCause().getMessage());
                }
            } else {
                printException(e, 5);
            }
        }

        // 方案 B: 反射调用 WorkBook 内部方法
        try {
            log("\n[1B] 尝试反射调用 WorkBook 内部读取方法...");
            Class<?> wbClass = Class.forName("com.fr.main.impl.WorkBook");
            Object wb = wbClass.newInstance();
            
            // 列出所有方法
            log("  WorkBook 方法:");
            for (Method m : wbClass.getMethods()) {
                String name = m.getName().toLowerCase();
                if (name.contains("read") || name.contains("load") || name.contains("stream") || name.contains("xml")) {
                    StringBuilder sig = new StringBuilder("    " + m.getReturnType().getSimpleName() + " " + m.getName() + "(");
                    Class<?>[] params = m.getParameterTypes();
                    for (int i = 0; i < params.length; i++) {
                        if (i > 0) sig.append(", ");
                        sig.append(params[i].getSimpleName());
                    }
                    sig.append(")");
                    log(sig.toString());
                }
            }
            
            // 尝试 readXMLable 或类似方法
            for (Method m : wbClass.getMethods()) {
                if (m.getName().equals("readXMLable") || m.getName().equals("readStream")) {
                    Class<?>[] params = m.getParameterTypes();
                    log("  尝试调用: " + m.getName() + "(" + Arrays.toString(params) + ")");
                    
                    if (params.length == 1 && params[0] == InputStream.class) {
                        try {
                            FileInputStream fis = new FileInputStream(cptPath);
                            m.invoke(wb, fis);
                            fis.close();
                            log("  ✅ " + m.getName() + " 成功!");
                            return wb;
                        } catch (Exception e2) {
                            log("  ❌ " + m.getName() + " 失败: " + e2.getMessage());
                        }
                    }
                }
            }
        } catch (Exception e) {
            log("  ❌ 反射调用失败:");
            printException(e, 5);
        }

        // 方案 C: TemplateWorkBookIO (需要 ConfigurationActivator)
        try {
            log("\n[1C] 尝试 TemplateWorkBookIO.readTemplateWorkBook...");
            Class<?> twbioCls = Class.forName("com.fr.io.TemplateWorkBookIO");
            Method readMethod = twbioCls.getMethod("readTemplateWorkBook", String.class);
            Object wb = readMethod.invoke(null, cptPath);
            log("  ✅ readTemplateWorkBook 成功: " + (wb != null ? wb.getClass().getName() : "null"));
            return wb;
        } catch (Exception e) {
            log("  ❌ readTemplateWorkBook 失败:");
            Throwable cause = e.getCause();
            if (cause != null) {
                log("    Cause: " + cause.getClass().getName() + ": " + cause.getMessage());
            }
        }

        return null;
    }

    // ============ STEP 2: 模板计算(执行) ============
    static Object tryExecute(Object wbObj) {
        log("\n========== STEP 2: 模板计算(执行) ==========");
        if (wbObj == null) {
            log("  ⚠ 跳过: WorkBook 为 null");
            return null;
        }

        // 查找 ActorFactory
        Object actor = null;
        String[] actorFactoryCandidates = {
            "com.fr.io.exporter.ActorFactory",
            "com.fr.report.stable.fun.ActorFactory",
            "com.fr.report.export.ActorFactory",
        };
        
        for (String afCls : actorFactoryCandidates) {
            try {
                Class<?> afClass = Class.forName(afCls);
                Method getActor = null;
                try {
                    getActor = afClass.getMethod("getActor", String.class);
                } catch (NoSuchMethodException e) {
                    continue;
                }
                
                for (String actorType : new String[]{"page", "write", "view", "simple"}) {
                    try {
                        actor = getActor.invoke(null, actorType);
                        log("  ✅ ActorFactory.getActor(\"" + actorType + "\") = " + actor.getClass().getName());
                        break;
                    } catch (Exception e) {
                        log("  ActorFactory.getActor(\"" + actorType + "\") 失败: " + e.getMessage());
                    }
                }
                if (actor != null) break;
            } catch (ClassNotFoundException e) {}
        }

        if (actor != null) {
            try {
                log("\n[2A] 尝试 WorkBook.execute(Map, Actor)...");
                Method execute = findMethod(wbObj.getClass(), "execute");
                if (execute != null) {
                    Map params = new HashMap();
                    Object result = execute.invoke(wbObj, params, actor);
                    log("  ✅ execute 成功!");
                    log("  ResultWorkBook 类型: " + result.getClass().getName());
                    tryGetMethod(result, "getReportCount", "  Result 报表块数");
                    return result;
                }
            } catch (Exception e) {
                log("  ❌ execute 失败:");
                printException(e, 8);
            }
        }

        // 模板级导出
        try {
            log("\n[2B] 尝试 WorkBook.export(OutputStream) (模板级)...");
            Method exportMethod = findMethod(wbObj.getClass(), "export");
            if (exportMethod != null) {
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                Object result = exportMethod.invoke(wbObj, baos);
                log("  模板级 export 结果: " + result + ", 字节数: " + baos.size());
                return wbObj;
            }
        } catch (Exception e) {
            log("  ❌ 模板级 export 失败:");
            printException(e, 5);
        }

        return null;
    }

    // ============ STEP 3: 导出 HTML ============
    static void tryExportHTML(Object resultOrWb, String outPath) {
        log("\n========== STEP 3: 导出 HTML ==========");
        if (resultOrWb == null) {
            log("  ⚠ 跳过: 无可用对象");
            return;
        }

        // 扫描导出器
        String[] exporterCandidates = {
            "com.fr.io.exporter.HtmlExporter",
            "com.fr.io.exporter.HTMLExporter",
            "com.fr.web.exporter.HtmlExporter",
            "com.fr.web.exporter.HTMLExporter",
            "com.fr.report.export.HtmlExporter",
            "com.fr.report.export.HTMLExporter",
            "com.fr.io.exporter.ExcelExporter",
            "com.fr.io.exporter.Excel2007Exporter",
            "com.fr.io.exporter.PDFExporter",
            "com.fr.io.exporter.WordExporter",
            "com.fr.io.exporter.CSVExporter",
            "com.fr.io.exporter.TextExporter",
            "com.fr.io.exporter.ImageExporter",
            "com.fr.io.exporter.EmbeddedTableDataExporter",
        };

        log("[3A] 扫描导出器类...");
        List<String> foundExporters = new ArrayList<>();
        for (String clsName : exporterCandidates) {
            try {
                Class<?> cls = Class.forName(clsName);
                foundExporters.add(clsName);
                log("  ✅ " + clsName);
                for (Method m : cls.getMethods()) {
                    if (m.getName().equals("export")) {
                        Class<?>[] params = m.getParameterTypes();
                        StringBuilder sig = new StringBuilder("     export(");
                        for (int i = 0; i < params.length; i++) {
                            if (i > 0) sig.append(", ");
                            sig.append(params[i].getSimpleName());
                        }
                        sig.append(")");
                        log(sig.toString());
                    }
                }
            } catch (ClassNotFoundException e) {}
        }

        // 尝试 HTML 导出
        for (String clsName : foundExporters) {
            if (!clsName.toLowerCase().contains("html")) continue;
            try {
                Class<?> cls = Class.forName(clsName);
                Object exporter = cls.newInstance();
                for (Method m : cls.getMethods()) {
                    if (!m.getName().equals("export")) continue;
                    Class<?>[] params = m.getParameterTypes();
                    if (params.length == 2 && params[0] == OutputStream.class) {
                        try {
                            FileOutputStream fos = new FileOutputStream(outPath);
                            m.invoke(exporter, fos, resultOrWb);
                            fos.close();
                            File f = new File(outPath);
                            log("  ✅ HTML 导出成功: " + outPath + " (" + f.length() + " bytes)");
                            return;
                        } catch (Exception e) {
                            log("  export 调用失败: " + e.getMessage());
                        }
                    }
                }
            } catch (Exception e) {}
        }

        // 尝试 PDF 导出
        log("\n[3B] 尝试 PDF 导出...");
        for (String clsName : foundExporters) {
            if (!clsName.toLowerCase().contains("pdf")) continue;
            try {
                Class<?> cls = Class.forName(clsName);
                Object exporter = cls.newInstance();
                for (Method m : cls.getMethods()) {
                    if (!m.getName().equals("export")) continue;
                    Class<?>[] params = m.getParameterTypes();
                    if (params.length == 2 && params[0] == OutputStream.class) {
                        try {
                            String pdfPath = outPath.replace(".html", ".pdf");
                            FileOutputStream fos = new FileOutputStream(pdfPath);
                            m.invoke(exporter, fos, resultOrWb);
                            fos.close();
                            File f = new File(pdfPath);
                            log("  ✅ PDF 导出成功: " + pdfPath + " (" + f.length() + " bytes)");
                            return;
                        } catch (Exception e) {
                            log("  PDF export 失败: " + e.getMessage());
                        }
                    }
                }
            } catch (Exception e) {}
        }

        // XML 导出
        log("\n[3C] 尝试 XML 导出...");
        try {
            Method exportMethod = findMethod(resultOrWb.getClass(), "export");
            if (exportMethod != null) {
                String xmlPath = outPath.replace(".html", ".xml");
                FileOutputStream fos = new FileOutputStream(xmlPath);
                exportMethod.invoke(resultOrWb, fos);
                fos.close();
                File f = new File(xmlPath);
                log("  XML 导出: " + xmlPath + " (" + f.length() + " bytes)");
            }
        } catch (Exception e) {
            log("  XML 导出失败: " + e.getMessage());
        }
    }

    // ============ 辅助方法 ============
    static Method findMethod(Class<?> cls, String name) {
        for (Method m : cls.getMethods()) {
            if (m.getName().equals(name)) {
                return m;
            }
        }
        return null;
    }

    static void tryGetMethod(Object obj, String methodName, String label) {
        try {
            Method m = obj.getClass().getMethod(methodName);
            Object result = m.invoke(obj);
            log(label + ": " + result);
        } catch (Exception e) {}
    }

    static void printException(Throwable e, int maxLines) {
        StringWriter sw = new StringWriter();
        e.printStackTrace(new PrintWriter(sw));
        String[] lines = sw.toString().split("\n");
        for (int i = 0; i < Math.min(maxLines, lines.length); i++) {
            log("    " + lines[i]);
        }
        Throwable cause = e.getCause();
        if (cause != null) {
            log("    --- Caused by: " + cause.getClass().getName() + ": " + cause.getMessage());
        }
    }

    // ============ MAIN ============
    public static void main(String[] args) throws Exception {
        log("=== FR Headless Probe v3 ===");
        log("Java: " + System.getProperty("java.version"));
        log("JVM: " + System.getProperty("java.vm.name"));
        log("时间: " + new java.util.Date());

        String cptPath = args.length > 0 ? args[0] : "C:\Users\<你的用户名>\Desktop\\fr_dev_kit_v2\\ckzl/hbfa\\cpt骨架\\two_rows.cpt";
        String outDir = args.length > 1 ? args[1] : System.getenv("TEMP") + "\\fr_headless_probe\\out";
        new File(outDir).mkdirs();

        log("\n模板: " + cptPath);
        log("输出目录: " + outDir);

        // 初始化
        tryInitWithWorkContext();

        // STEP 1
        Object wb = tryParseTemplate(cptPath);

        // STEP 2
        Object result = tryExecute(wb);

        // STEP 3
        tryExportHTML(result != null ? result : wb, outDir + File.separator + "probe_output.html");

        log("\n=== Probe 完成 ===");
        
        // 写报告
        String reportPath = System.getenv("TEMP") + "\\fr_headless_probe\\probe_report.txt";
        try (PrintWriter pw = new PrintWriter(new FileWriter(reportPath))) {
            pw.print(report.toString());
        }
        log("报告已写入: " + reportPath);
    }
}
