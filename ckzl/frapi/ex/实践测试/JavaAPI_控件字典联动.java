import com.fr.form.ui.ComboBox;
import com.fr.data.impl.TableDataDictionary;
import com.fr.data.impl.DBTableData;
import com.fr.data.impl.NameDatabaseConnection;
import com.fr.base.Parameter;
import com.fr.main.impl.WorkBook;
import com.fr.report.cell.DefaultTemplateCellElement;
import com.fr.report.worksheet.WorkSheet;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_控件字典联动.cpt (doc-608)
 * 
 * 已验证 API:
 * - com.fr.form.ui.ComboBox (下拉框) + setWidgetName/setDictionary
 * - com.fr.data.impl.TableDataDictionary (数据字典) setTableData(TableData)
 * - com.fr.data.impl.DBTableData (SQL 数据集, 无 SQLTableData 类)
 * - com.fr.base.Parameter (模板参数)
 * - DefaultTemplateCellElement.setWidget(Widget)
 * 
 * 联动机制: 后级 SQL 引用前级参数 ${area}, 由同名 Parameter 运行时替换
 */
public class JavaAPI_控件字典联动 {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();

            // 下拉框控件（地区）
            ComboBox areaCombo = new ComboBox();
            areaCombo.setWidgetName("area");

            // 数据字典（地区列表）
            TableDataDictionary dict = new TableDataDictionary();
            DBTableData areaData = new DBTableData();
            areaData.setDatabase(new NameDatabaseConnection("FRDemo"));
            areaData.setQuery("SELECT DISTINCT 地区 FROM 销量");
            dict.setTableData(areaData);
            areaCombo.setDictionary(dict);

            // 模板参数（经 ReportParameterAttr 承载；Java 侧直接构造 Parameter 对象）
            Parameter param = new Parameter("area", "华东");

            // 工作表 + 单元格挂控件
            WorkSheet sheet = new WorkSheet();
            workbook.addReport(sheet);
            DefaultTemplateCellElement cell = new DefaultTemplateCellElement(0, 0, "地区");
            cell.setWidget(areaCombo);
            sheet.addCellElement(cell);

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_控件字典联动.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
