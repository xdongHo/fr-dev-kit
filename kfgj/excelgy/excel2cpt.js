/*
 * excel2cpt.js — 流程 F 第②步：Excel 骨架 → cpt（无头，不开 GUI，等价设计器"文件→打开Excel→另存为"）
 *
 * 实测类路径（2026-09-29 设计器 JVM 反射验证，FR 10.0.19）：
 *   - com.fr.io.importer.ExcelReportImporterFactory.createExcelImporter(String)  静态工厂，按文件分发
 *     → .xls  : com.fr.io.importer.ExcelReportImporter       (POI HSSF)
 *     → .xlsx : com.fr.io.importer.Excel2007ReportImporter   (POI XSSF, com.fr.third.v2)
 *   - 两者的 generateWorkBookByStream(InputStream) 同签名 → com.fr.main.impl.WorkBook
 *   - doc-view-737 配方：importer.generateWorkBookByStream(fis) → wb.export(fos)
 *
 * 行列映射：整簿转换无平移，cpt 行号 = Excel 行 - 1（见 ckzl/zsk/xtgt/patterns/复杂模板改造协议.md）
 * 转换后必做：转换清源（同协议第①步——清空格式格/坏 definedNames/外部引用）
 *
 * 用法（设计器已注入 fr-agent 后）：
 *   1. 改下方 INPUT / OUTPUT 两个路径（用正斜杠）
 *   2. python kfgj/fr-agent/exec_js.py kfgj/excelgy/excel2cpt.js
 */
(function () {
    // 路径约定：默认取用户目录流程F工作区（换机零改动）；也可用 -Dfr.excel2cpt.input 覆盖
var USER_HOME = java.lang.System.getProperty("user.home");
var INPUT  = USER_HOME + "/.fr_dev_kit/projects/流程F_HFM_V2/骨架.xlsx";
    var OUTPUT = USER_HOME + "/.fr_dev_kit/projects/流程F_HFM_V2/骨架.cpt";

    var File = Java.type("java.io.File");
    var FileInputStream = Java.type("java.io.FileInputStream");
    var FileOutputStream = Java.type("java.io.FileOutputStream");
    var Factory = Java.type("com.fr.io.importer.ExcelReportImporterFactory");

    var inFile = new File(INPUT);
    if (!inFile.exists()) {
        return "[excel2cpt] ❌ 输入不存在: " + INPUT;
    }
    var outFile = new File(OUTPUT);
    var parent = outFile.getParentFile();
    if (parent !== null && !parent.exists()) {
        parent.mkdirs();
    }

    var t0 = java.lang.System.currentTimeMillis();
    // 工厂 createExcelImporter(String) 不按路径分发（实测仍回 HSSF 版）→ 按扩展名自行分发
    var importer;
    if (INPUT.toLowerCase().endsWith(".xlsx")) {
        importer = new (Java.type("com.fr.io.importer.Excel2007ReportImporter"))();
    } else {
        importer = new (Java.type("com.fr.io.importer.ExcelReportImporter"))();
    }
    var fis = new FileInputStream(inFile);
    var wb = importer.generateWorkBookByStream(fis);
    fis.close();
    if (wb === null) {
        return "[excel2cpt] ❌ generateWorkBookByStream 返回 null";
    }

    var fos = new FileOutputStream(outFile);
    wb.export(fos);
    fos.close();

    var info = "";
    try { info = " sheets=" + wb.getReportCount(); } catch (e) { info = " sheets=?"; }

    return "[excel2cpt] ✅ importer=" + importer.getClass().getSimpleName() +
           " " + INPUT + " -> " + OUTPUT +
           " (" + outFile.length() + " bytes," + info +
           ", " + (java.lang.System.currentTimeMillis() - t0) + "ms)";
})();
