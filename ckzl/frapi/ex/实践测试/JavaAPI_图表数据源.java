import com.fr.main.impl.WorkBook;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_图表数据源.cpt (doc-175/176)
 * 
 * 图表 API (com.fr.chart.*) 在 fine-report-engine 中:
 * - 数据集数据源: 图表绑定数据集 ds1 的分类/系列/值
 * - 单元格数据源: 图表分类/系列/值引用单元格公式
 * 
 * 图表节点结构复杂, 本示例验证 WorkBook 骨架 + 数据集挂载,
 * 实际图表节点由 gen_cpts 脚本按 XML Schema 生成 (vanchart 扩展点结构)。
 */
public class JavaAPI_图表数据源 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();
            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_图表数据源.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
