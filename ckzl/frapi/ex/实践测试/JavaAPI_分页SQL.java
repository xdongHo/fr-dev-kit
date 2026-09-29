import com.fr.data.impl.DBTableData;
import com.fr.data.impl.NameDatabaseConnection;
import com.fr.main.impl.WorkBook;
import com.fr.io.TemplateWorkBookIO;

/**
 * JavaAPI_分页SQL行式引擎.cpt (doc-996)
 * 
 * 已验证 API (javap 实测):
 * - DBTableData.setQuery(String) 普通 SQL (注意: 非 setSql)
 * - DBTableData.setPageQuerySql(String) 分页 SQL (注意: 非 setPaginationQuery)
 * - DBTableData.setDatabase(Connection) + NameDatabaseConnection(String)
 * - ${fr_pagenumber}/${fr_pagesize}/${fr_rowcount} 行式引擎内置变量
 * 
 * XML 对应: <TableData class="com.fr.data.impl.DBTableData">
 *           <Database name="FRDemo"><Query>...</Query><PageQuerySql>...</PageQuerySql>
 */
public class JavaAPI_分页SQL {
    public static void main(String[] args) {
        try {
            WorkBook workbook = new WorkBook();

            // 数据集 + 分页 SQL
            DBTableData ds = new DBTableData();
            ds.setName("ds1");
            ds.setDatabase(new NameDatabaseConnection("FRDemo"));
            ds.setQuery("SELECT 地区, 产品, 销量 FROM 销量");
            ds.setPageQuerySql("SELECT 地区, 产品, 销量 FROM 销量 LIMIT ${fr_pagenumber}, ${fr_pagesize}");
            workbook.putTableData("ds1", ds);

            String outputPath = "D:/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/实践测试/JavaAPI_分页SQL.cpt";
            TemplateWorkBookIO.writeTemplateWorkBook(workbook, outputPath);
            System.out.println("SUCCESS: " + outputPath);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}
