import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.report.cell.cellattr.CellExpandAttr;
import com.fr.main.impl.WorkBook;
import com.fr.report.worksheet.WorkSheet;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_单元格扩展.cpt (doc-140)
 * 
 * 已验证 API (javap 实测 fine-report-engine-10.0.jar):
 * - com.fr.report.cell.cellattr.CellExpandAttr (注意: 在 cellattr 子包, 非 com.fr.report.cell)
 *   - setDirection(byte) 扩展方向 (Vertical_EXTENDABLE/Horizontal_EXTENDABLE/None_EXTENDABLE)
 *   - setExtendable(byte) 可扩展性
 *   - setOrder(int) / setSortFormula(String) 扩展后排序
 * - com.fr.report.cell.DefaultTemplateCellElement(int, int)
 * - com.fr.main.impl.WorkBook / com.fr.report.worksheet.WorkSheet
 * - com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(TemplateWorkBook, String)
 */
public class JavaAPI_单元格扩展 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();
            WorkSheet sheet = new WorkSheet();
            workbook.addReport(sheet);

            // 标题行（不扩展）
            DefaultTemplateCellElement title = new DefaultTemplateCellElement(0, 0, "销售数据");
            CellExpandAttr titleExpand = new CellExpandAttr();
            titleExpand.setDirection(CellExpandAttr.None_EXTENDABLE);
            title.setCellExpandAttr(titleExpand);
            sheet.addCellElement(title);

            // 数据列（纵向扩展）
            String[] headers = {"地区", "产品", "销量", "利润"};
            for (int col = 0; col < headers.length; col++) {
                DefaultTemplateCellElement cell = new DefaultTemplateCellElement(col, 1, headers[col]);
                CellExpandAttr expand = new CellExpandAttr();
                expand.setDirection(CellExpandAttr.Vertical_EXTENDABLE);
                cell.setCellExpandAttr(expand);
                sheet.addCellElement(cell);
            }

            // 数据行（引用内置数据集 ds1）
            String[] dsNames = {"ds1.select(地区)", "ds1.select(产品)", "ds1.select(销量)", "ds1.select(利润)"};
            for (int col = 0; col < dsNames.length; col++) {
                DefaultTemplateCellElement data = new DefaultTemplateCellElement(col, 2, "=" + dsNames[col]);
                CellExpandAttr expand = new CellExpandAttr();
                expand.setDirection(CellExpandAttr.Vertical_EXTENDABLE);
                data.setCellExpandAttr(expand);
                sheet.addCellElement(data);
            }

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_单元格扩展.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
