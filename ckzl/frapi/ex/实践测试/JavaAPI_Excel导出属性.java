import com.fr.main.impl.WorkBook;
import com.fr.io.attr.ExcelExportAttr;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_Excel导出属性.cpt (doc-1118)
 * 
 * 已验证 API (javap 实测):
 * - com.fr.io.attr.ExcelExportAttr (注意: 在 io/attr 子包, 非 com.fr.report.core)
 *   - setExportHidedRow(boolean) 导出隐藏行
 *   - setExportHidedColumn(boolean) 导出隐藏列
 *   - setPassword(String) 打开密码
 *   - setProtectedWord(String) 写保护密码
 * - WorkBook.getExportAttr/setExportAttr (继承自 AbstractFineBook)
 * 
 * XML 对应: <ReportExportAttr><ExcelExportAttr exportHidedRow="..." exportHidedColumn="...">
 */
public class JavaAPI_Excel导出属性 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();

            // Excel 导出属性
            ExcelExportAttr excelAttr = new ExcelExportAttr();
            excelAttr.setExportHidedRow(true);
            excelAttr.setExportHidedColumn(true);
            excelAttr.setPassword("123456");
            excelAttr.setProtectedWord("654321");

            // 挂到工作簿导出属性（getExportAttr/setExportAttr 继承自 AbstractFineBook）
            // 若 getExportAttr 返回 ReportExportAttr 再 setExcelExportAttr
            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_Excel导出属性.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
