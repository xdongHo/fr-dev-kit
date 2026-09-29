import com.fr.main.impl.WorkBook;
import com.fr.base.Parameter;
import com.fr.form.main.parameter.FormParameterUI;
import com.fr.form.ui.TextEditor;
import com.fr.main.parameter.ReportParameterAttr;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_模板参数.cpt (doc-157)
 * 
 * 已验证 API (javap 实测):
 * - com.fr.base.Parameter (注意: 在 com.fr.base 包, 非 com.fr.report.parameter)
 *   - Parameter(String, Object) 构造
 * - com.fr.form.ui.TextEditor + setWidgetName (Widget 基类)
 * - com.fr.form.main.parameter.FormParameterUI (ParameterUI 接口的实现类)
 * - com.fr.main.parameter.ReportParameterAttr + setParameterUI(ParameterUI)
 * - AbstractTemplateWorkBook.setReportParameterAttr(ReportParameterAttr) (注意: 非 addParameter)
 * 
 * XML 对应: <Parameters><Parameter name="地区" class="java.lang.String">华东</Parameter>
 *           <ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
 */
public class JavaAPI_模板参数 {
    public static void main(String[] args) {
        try {
            // 1. 创建模板参数
            Parameter param = new Parameter("地区", "华东");

            // 2. 创建参数面板控件
            TextEditor textEditor = new TextEditor();
            textEditor.setWidgetName("地区");

            // 3. 创建参数面板并添加控件
            FormParameterUI paramUI = FormParameterUI.createDefaultParameterUI();
            paramUI.setCellWidgets(new com.fr.form.ui.CellWidget[] {
                new com.fr.form.ui.CellWidget(textEditor, null, new java.awt.Rectangle(0, 0, 100, 20), null)
            });

            // 4. 挂到工作簿（setReportParameterAttr, 非 addParameter）
            ReportParameterAttr attr = new ReportParameterAttr();
            attr.setParameterUI(paramUI);
            WorkBook workbook = new WorkBook();
            workbook.setReportParameterAttr(attr);

            // 5. 写出 .cpt
            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_模板参数.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
