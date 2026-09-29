import com.fr.main.impl.WorkBook;
import com.fr.report.worksheet.WorkSheet;
import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.base.Style;
import com.fr.base.background.ColorBackground;
import com.fr.general.FRFont;
import com.fr.io.TemplateWorkBookIO;
import java.awt.Color;
import java.awt.Font;

/**
 * JavaAPI_单元格样式.cpt (doc-217)
 * 
 * 已验证 API (javap 实测 fine-core-10.0.jar):
 * - com.fr.base.Style (注意: 在 com.fr.base 包, 非 com.fr.report.style)
 *   - Style.getInstance() 工厂方法 (无 new Style())
 *   - deriveFRFont(FRFont) / deriveBackground(Background) / deriveFormat(Format)
 * - com.fr.base.CellBorderStyle (边框: setTopColor/setTopStyle/setBottomColor...)
 * - com.fr.base.background.ColorBackground.createBackground(Color)
 * - com.fr.general.FRFont (字体, 继承 java.awt.Font)
 * - DefaultTemplateCellElement.setStyle(Style)
 */
public class JavaAPI_单元格样式 {
    public static void main(String[] args) {
        try {
            // 0. 创建工作簿与工作表
            WorkBook workbook = new WorkBook();
            WorkSheet sheet = new WorkSheet();
            workbook.addReport(sheet);

            // ===== 单元格1: A1 标题 =====
            DefaultTemplateCellElement titleCell = new DefaultTemplateCellElement(0, 0, "销售报表演示");
            Style titleStyle = Style.getInstance();
            titleStyle = titleStyle.deriveFRFont(FRFont.getInstance("微软雅黑", Font.BOLD, 18));
            titleStyle = titleStyle.deriveBackground(ColorBackground.getInstance(new Color(0, 102, 153)));
            titleCell.setStyle(titleStyle);
            titleCell.setColumnSpan(2);
            sheet.addCellElement(titleCell);

            // ===== 单元格2: A3 表头"产品" =====
            DefaultTemplateCellElement header1 = new DefaultTemplateCellElement(0, 2, "产品");
            Style headerStyle = Style.getInstance();
            headerStyle = headerStyle.deriveFRFont(FRFont.getInstance("微软雅黑", Font.BOLD, 12));
            headerStyle = headerStyle.deriveBackground(ColorBackground.getInstance(new Color(204, 204, 204)));
            headerStyle = headerStyle.deriveBorder(1, Color.BLACK, 1, Color.BLACK, 1, Color.BLACK, 1, Color.BLACK);
            header1.setStyle(headerStyle);
            sheet.addCellElement(header1);

            // ===== 单元格3: B3 表头"销量" =====
            DefaultTemplateCellElement header2 = new DefaultTemplateCellElement(1, 2, "销量");
            header2.setStyle(headerStyle);
            sheet.addCellElement(header2);

            // ===== 单元格4: A4 数据（日期格式） =====
            DefaultTemplateCellElement data1 = new DefaultTemplateCellElement(0, 3, "2024-01-15");
            Style dataStyle1 = Style.getInstance();
            dataStyle1 = dataStyle1.deriveFRFont(FRFont.getInstance("微软雅黑", Font.PLAIN, 11));
            dataStyle1 = dataStyle1.deriveBorder(1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY);
            data1.setStyle(dataStyle1);
            sheet.addCellElement(data1);

            // ===== 单元格5: B4 数据（数字格式，红色前景） =====
            DefaultTemplateCellElement data2 = new DefaultTemplateCellElement(1, 3, 12800.50);
            Style dataStyle2 = Style.getInstance();
            dataStyle2 = dataStyle2.deriveFRFont(FRFont.getInstance("微软雅黑", Font.PLAIN, 11));
            dataStyle2 = dataStyle2.deriveBackground(ColorBackground.getInstance(new Color(255, 240, 240)));
            dataStyle2 = dataStyle2.deriveBorder(1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY, 1, Color.LIGHT_GRAY);
            data2.setStyle(dataStyle2);
            sheet.addCellElement(data2);

            // 5. 写出 .cpt
            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_单元格样式.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
