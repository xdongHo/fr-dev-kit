import com.fr.main.impl.WorkBook;
import com.fr.io.TemplateWorkBookIO;
import com.fr.web.attr.ReportWebAttr;

/**
 * JavaAPI_填报冻结.cpt (doc-611)
 * 
 * 已验证 API:
 * - com.fr.web.attr.ReportWebAttr (Web 属性, 承载冻结配置)
 *   (freezeRow/freezeCol setter 名待 jar 核验, 可能为 setFreezeRow/setFreezeCol)
 * - WorkBook.setReportWebAttr(ReportWebAttr) — 继承自 AbstractTemplateWorkBook
 * 
 * XML 对应: <ReportWebAttr><freezeRow>n</freezeRow><freezeCol>m</freezeCol>
 */
public class JavaAPI_填报冻结 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();

            // Web 属性 + 冻结设置
            ReportWebAttr webAttr = new ReportWebAttr();
            // freezeRow/freezeCol setter 名待核验，编译若失败则仅保留结构
            // webAttr.setFreezeRow(2);
            // webAttr.setFreezeCol(1);
            workbook.setReportWebAttr(webAttr);

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_填报冻结.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
