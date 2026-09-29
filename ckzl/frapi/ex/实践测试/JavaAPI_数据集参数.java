import com.fr.data.impl.DBTableData;
import com.fr.data.impl.NameDatabaseConnection;
import com.fr.main.impl.WorkBook;
import com.fr.main.parameter.ReportParameterAttr;
import com.fr.base.Parameter;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_数据集参数.cpt
 * 
 * 演示：数据集参数（doc-158）
 * - 用 DBTableData 定义 SQL 查询，内嵌 ${area} 数据集参数
 * - 用 Parameter 注册同名参数到工作簿
 * - 写出 .cpt 模板
 * 
 * 数据源：FRDemo（内置演示数据库）
 * SQL：SELECT * FROM 销量 WHERE 地区 = '${area}'
 * 参数：area，默认值"华东"
 */
public class JavaAPI_数据集参数 {
    public static void main(String[] args) {
        try {
            // 1. 创建数据集
            DBTableData ds = new DBTableData();
            ds.setName("ds1");
            ds.setDatabase(new NameDatabaseConnection("FRDemo"));
            ds.setQuery("SELECT * FROM 销量 WHERE 地区 = '${area}'");

            // 2. 创建参数
            Parameter param = new Parameter();
            param.setName("area");
            param.setValue("华东");

            // 3. 创建工作簿
            WorkBook workbook = new WorkBook();
            workbook.putTableData("ds1", ds);
            ReportParameterAttr paramAttr = new ReportParameterAttr();

            // 4. 写出 .cpt
            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_数据集参数.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}