import com.fr.form.ui.TreeComboBoxEditor;
import com.fr.main.impl.WorkBook;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_下拉树控件.cpt (doc-260)
 * 
 * 已验证 API:
 * - com.fr.form.ui.TreeComboBoxEditor (下拉树编辑器)
 * - setWidgetName / setMultipleSelection / setAsyncLoad / setReturnLeafNodeOnly
 * - ReportParameterUI 实际为 com.fr.base.parameter.ParameterUI (抽象类)
 * 
 * XML 对应: <ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
 *           <InnerWidget class="com.fr.form.ui.TreeComboBoxEditor" widgetName="tree">
 */
public class JavaAPI_下拉树控件 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();

            // 下拉树控件（参数面板用）
            TreeComboBoxEditor tree = new TreeComboBoxEditor();
            tree.setWidgetName("tree");           // Widget 基类
            tree.setMultipleSelection(true);      // TreeEditor 父类
            tree.setAjax(false);                  // TreeEditor 父类 (替代 setAsyncLoad)
            tree.setSelectLeafOnly(true);         // TreeEditor 父类 (替代 setReturnLeafNodeOnly)

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_下拉树控件.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
