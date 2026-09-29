import com.fr.file.ConnectionConfig;
import com.fr.data.impl.JDBCDatabaseConnection;
import java.sql.*;

public class SQLRunner {
    public static void main(String[] args) throws Exception {
        String connName = args[0];
        String sql = args[1];
        System.out.println("Conn: " + connName);
        System.out.println("SQL: " + sql);
        
        ConnectionConfig cfg = ConnectionConfig.getInstance();
        JDBCDatabaseConnection jdbc = (JDBCDatabaseConnection) cfg.getConnection(connName);
        if (jdbc == null) {
            System.out.println("ERROR: Connection not found: " + connName);
            System.exit(1);
        }
        
        Connection conn = jdbc.createConnection();
        Statement stmt = conn.createStatement();
        boolean isResult = stmt.execute(sql);
        
        if (isResult) {
            ResultSet rs = stmt.getResultSet();
            int cols = rs.getMetaData().getColumnCount();
            int cnt = 0;
            while (rs.next()) {
                for (int i = 1; i <= cols; i++) {
                    if (i > 1) System.out.print("\t");
                    System.out.print(rs.getString(i));
                }
                System.out.println();
                cnt++;
            }
            System.out.println("Rows: " + cnt);
        } else {
            System.out.println("Updated: " + stmt.getUpdateCount());
        }
        
        stmt.close();
        conn.close();
        System.out.println("DONE");
    }
}