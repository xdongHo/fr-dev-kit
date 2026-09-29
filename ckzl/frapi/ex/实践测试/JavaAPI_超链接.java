import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.main.impl.WorkBook;
import com.fr.report.worksheet.WorkSheet;
import com.fr.io.TemplateWorkBookIO;
import com.fr.js.NameJavaScriptGroup;
import com.fr.js.NameJavaScript;
import com.fr.js.JavaScriptImpl;

/**
 * JavaAPI_超链接.cpt (doc-947)
 * 
 * 已验证 API (javap 实测):
 * - com.fr.js.NameJavaScriptGroup (超链接组; FR10 无 HyperlinkGroup 类)
 *   - 构造: new NameJavaScriptGroup(NameJavaScript)
 * - com.fr.js.NameJavaScript (包装: NameJavaScript(JavaScript))
 * - com.fr.js.JavaScriptImpl (JavaScript 接口实现: JavaScriptImpl(String))
 * - AbstractCellElement.setNameHyperlinkGroup(NameJavaScriptGroup) 挂载
 * 
 * XML 对应: <CellElement><NameHyperlinkGroup><JavaScript>...
 */
public class JavaAPI_超链接 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();
            WorkSheet sheet = new WorkSheet();
            workbook.addReport(sheet);

            // 单元格 + 超链接（JS 打开新窗口）
            DefaultTemplateCellElement cell = new DefaultTemplateCellElement(0, 0, "点击打开百度");
            JavaScriptImpl js = new JavaScriptImpl("window.open('http://www.baidu.com')");
            NameJavaScript link = new NameJavaScript(js);
            NameJavaScriptGroup group = new NameJavaScriptGroup(link);
            cell.setNameHyperlinkGroup(group);
            sheet.addCellElement(cell);

            // 普通单元格
            DefaultTemplateCellElement cell2 = new DefaultTemplateCellElement(0, 1, "普通单元格");
            sheet.addCellElement(cell2);

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_超链接.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
