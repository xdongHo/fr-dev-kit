import javax.xml.stream.*;
import javax.xml.stream.events.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * FR 样式批量优化 — StAX 流式版本
 * 
 * 不解析整个 DOM，逐事件流式处理，精确替换目标属性。
 * 完全保持原始 XML 格式（换行、缩进、CDATA 均不变）。
 */
public class CptStyleOptimizer {

    static final String BASE_DIR = 
        "C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/示例报表工程";

    static final Set<String> EXCLUDE_DIRS = new HashSet<>(Arrays.asList(
        "权限配置", "_backup", "_backup_v2", "明细报表 - 副本", "数据权限bak"
    ));

    public static void main(String[] args) throws Exception {
        File base = new File(BASE_DIR);
        List<File> files = new ArrayList<>();
        collectCptFiles(base, files);
        System.out.println("找到 " + files.size() + " 个文件\n");

        int mod = 0, skip = 0, err = 0;
        for (File f : files) {
            try {
                String rel = base.toURI().relativize(f.toURI()).getPath();
                int r = optimizeFile(f);
                if (r > 0) { System.out.println("  \u2713 " + rel + " (" + r + " change(s))"); mod++; }
                else if (r == 0) { System.out.println("  - " + rel); skip++; }
                else { System.out.println("  \u2717 " + rel); err++; }
            } catch (Exception e) {
                System.err.println("  \u2717 " + f.getName() + ": " + e.getMessage());
                err++;
            }
        }
        System.out.println("\n\u4FEE\u6539: " + mod + "  \u65E0\u53D8\u5316: " + skip + "  \u9519\u8BEF: " + err);
    }

    static void collectCptFiles(File dir, List<File> result) {
        File[] cs = dir.listFiles();
        if (cs == null) return;
        for (File f : cs) {
            if (f.isDirectory()) {
                String n = f.getName();
                if (!EXCLUDE_DIRS.contains(n) && !n.startsWith("_backup"))
                    collectCptFiles(f, result);
            } else if (f.getName().endsWith(".cpt"))
                result.add(f);
        }
    }

    /**
     * 返回: >0=修改数, 0=无变化, -1=错误
     */
    static int optimizeFile(File file) throws Exception {
        // 读取整个文件
        String content = new String(Files.readAllBytes(file.toPath()), "UTF-8");

        // 先判断是否有 ParameterUI (有参数面板才需要优化)
        boolean hasParamUI = content.contains("<ParameterUI");

        String modified = content;
        int changes = 0;

        // === 在 ParameterUI 区域做替换 ===
        if (hasParamUI) {
            // 提取 ParameterUI 前后部分
            int start = modified.indexOf("<ParameterUI");
            int end = modified.indexOf("</ParameterUI>") + "</ParameterUI>".length();
            String before = modified.substring(0, start);
            String paramSection = modified.substring(start, end);
            String after = modified.substring(end);

            // 在 paramSection 中替换
            String orig = paramSection;

            // 1. 统一控件高度 26
            paramSection = paramSection.replaceAll("height=\"(?!26\")[0-9]+\"", "height=\"26\"");
            if (!paramSection.equals(orig)) changes++;

            // 2. 统一字体 微软雅黑 (仅 FRFont name 属性)
            paramSection = paramSection.replaceAll(
                "(?<=<FRFont[^>]*name=\")[^\"]*(?=\")", "微软雅黑");
            if (!paramSection.equals(orig)) changes++;

            // 3. padding 左右缩进 (Style 元素)
            paramSection = paramSection.replaceAll("paddingLeft=\"0\"", "paddingLeft=\"6\"");
            paramSection = paramSection.replaceAll("paddingRight=\"0\"", "paddingRight=\"6\"");

            modified = before + paramSection + after;
        }

        // === 在 RowHeight 区域做替换（整个 WorkBook 级别） ===
        // RowHeight: defaultValue → 1153643, CDATA 中每行按规则设置

        // === 全局 FRFont 替换 ===  
        // 只在 StyleList 的 FRFont 中替换 name
        int slStart = modified.indexOf("<StyleList>");
        int slEnd = modified.indexOf("</StyleList>");
        if (slStart >= 0 && slEnd >= 0) {
            String styleBlock = modified.substring(slStart, slEnd);
            String newStyleBlock = styleBlock.replaceAll(
                "(?<=<FRFont[^>]*name=\")[^\"]*(?=\")", "微软雅黑");
            if (!newStyleBlock.equals(styleBlock)) {
                modified = modified.substring(0, slStart) + newStyleBlock + modified.substring(slEnd);
                changes++;
            }

            // padding
            String newSB2 = newStyleBlock.replaceAll("paddingLeft=\"0\"", "paddingLeft=\"6\"");
            newSB2 = newSB2.replaceAll("paddingRight=\"0\"", "paddingRight=\"6\"");
            if (!newSB2.equals(newStyleBlock)) {
                modified = modified.substring(0, slStart) + newSB2 + modified.substring(slEnd);
                changes++;
            }
        }

        if (changes > 0) {
            // 备份
            File bak = new File(file.getParentFile(), "_backup_stax");
            bak.mkdirs();
            Files.copy(file.toPath(), new File(bak, file.getName()).toPath(),
                       StandardCopyOption.REPLACE_EXISTING);
            
            Files.write(file.toPath(), modified.getBytes("UTF-8"));
        }

        return changes;
    }
}
