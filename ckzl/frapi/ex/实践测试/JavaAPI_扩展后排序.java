import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.report.cell.cellattr.CellExpandAttr;
import com.fr.main.impl.WorkBook;
import com.fr.report.worksheet.WorkSheet;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_扩展后排序.cpt (doc-897)
 * 
 * 已验证 API:
 * - CellExpandAttr.setOrder(int) 排序类型
 * - CellExpandAttr.setSortFormula(String) 排序公式
 * - CellExpandAttr.setDirection(byte) 扩展方向
 * - 注意: 扩展后排序必须设在最父格 (doc-897 注1)
 * 
 * XML 对应: <Expand dir="0" sortAfterExpand="1"><SortExpression>...</SortExpression>
 */
public class JavaAPI_扩展后排序 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();
            WorkSheet sheet = new WorkSheet();
            workbook.addReport(sheet);

            // 排序字段（最父格，A2）
            DefaultTemplateCellElement sortCell = new DefaultTemplateCellElement(0, 1, "=ds1.select(销量)");
            CellExpandAttr expand = new CellExpandAttr();
            expand.setDirection(CellExpandAttr.Vertical_EXTENDABLE);
            expand.setOrder(1);  // 升序
            expand.setSortFormula("=ds1.select(销量)");  // 排序公式
            sortCell.setCellExpandAttr(expand);
            sheet.addCellElement(sortCell);

            // 其他列（产品名）
            DefaultTemplateCellElement prodCell = new DefaultTemplateCellElement(1, 1, "=ds1.select(产品)");
            CellExpandAttr expand2 = new CellExpandAttr();
            expand2.setDirection(CellExpandAttr.Vertical_EXTENDABLE);
            prodCell.setCellExpandAttr(expand2);
            sheet.addCellElement(prodCell);

            // 标题行
            DefaultTemplateCellElement title1 = new DefaultTemplateCellElement(0, 0, "销量(排序)");
            DefaultTemplateCellElement title2 = new DefaultTemplateCellElement(1, 0, "产品");
            sheet.addCellElement(title1);
            sheet.addCellElement(title2);

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_扩展后排序.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
