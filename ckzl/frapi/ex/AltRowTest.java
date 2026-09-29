import com.fr.main.impl.WorkBook;
import com.fr.report.worksheet.WorkSheet;
import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.base.Style;
import com.fr.general.FRFont;
import com.fr.base.background.ColorBackground;
import com.fr.data.impl.EmbeddedTableData;
import com.fr.data.condition.CommonCondition;
import com.fr.report.cell.cellattr.ConditionAttr;
import com.fr.report.cell.cellattr.ConditionCollection;
import com.fr.report.cell.cellattr.ConditionAttrRowColumn;
import com.fr.base.Formula;
import com.fr.stable.unit.FU;

import java.awt.Color;
import java.io.FileOutputStream;
import java.util.*;

/**
 * 用 FR Java API 生成含隔行换色的测试模板，抓 XML 格式
 */
public class AltRowTest {
    public static void main(String[] args) throws Exception {
        WorkBook wb = new WorkBook();

        // 数据集
        EmbeddedTableData ds = new EmbeddedTableData();
        ds.setName("ds1");
        ds.addColumn("Name", String.class);
        ds.addColumn("Value", Integer.class);
        List rows = new ArrayList();
        rows.add(Arrays.asList("A", 100));
        rows.add(Arrays.asList("B", 200));
        rows.add(Arrays.asList("C", 300));
        rows.add(Arrays.asList("D", 400));
        ds.getRowDataConf().get().setRowData(rows);
        wb.putTableData("ds1", ds);

        // 样式
        Style headerStyle = Style.DEFAULT_STYLE
            .deriveFRFont(FRFont.getInstance("微软雅黑", 1, 9))
            .deriveBackground(ColorBackground.getInstance(Color.BLUE))
            .deriveBorder(1, Color.GRAY, 1, Color.GRAY, 1, Color.GRAY, 1, Color.GRAY);

        Style dataStyle = Style.DEFAULT_STYLE
            .deriveFRFont(FRFont.getInstance("微软雅黑", 0, 9))
            .deriveBorder(1, Color.GRAY, 1, Color.GRAY, 1, Color.GRAY, 1, Color.GRAY);

        WorkSheet sheet = new WorkSheet();

        // 表头
        DefaultTemplateCellElement h1 = new DefaultTemplateCellElement(0, 0, "Name");
        h1.setStyle(headerStyle);
        sheet.addCellElement(h1);

        DefaultTemplateCellElement h2 = new DefaultTemplateCellElement(1, 0, "Value");
        h2.setStyle(headerStyle);
        sheet.addCellElement(h2);

        // 数据行 — 给第一行第一列加条件属性
        DefaultTemplateCellElement c1 = new DefaultTemplateCellElement(0, 1,
            new com.fr.report.cell.cellattr.core.group.DSColumn("ds1", "Name"));
        c1.setStyle(dataStyle);

        // 添加条件属性：row()%2==0 → 红色背景
        ConditionAttr attr = new ConditionAttr();
        ConditionCollection cc = new ConditionCollection();
        CommonCondition cond = new CommonCondition();
        cond.setConditionAttrData(new ConditionAttrRowColumn(0)); // 0 = current row
        cond.setFormulaExpr(new Formula("row()%2==0"));
        cc.addCondition(cond);
        attr.setConditionCollection(cc);
        attr.setStyle(Style.DEFAULT_STYLE.deriveBackground(
            ColorBackground.getInstance(Color.RED)));
        c1.setConditionAttr(attr);

        sheet.addCellElement(c1);

        DefaultTemplateCellElement c2 = new DefaultTemplateCellElement(1, 1,
            new com.fr.report.cell.cellattr.core.group.DSColumn("ds1", "Value"));
        c2.setStyle(dataStyle);
        // 也加条件属性
        c2.setConditionAttr(attr);
        sheet.addCellElement(c2);

        wb.addReport("sheet1", sheet);
        wb.export(new FileOutputStream("C:/Users/<你的用户名>/Desktop/fr_dev_kit - 副本/alt_row_test.cpt"));
        System.out.println("Generated alt_row_test.cpt");
    }
}
