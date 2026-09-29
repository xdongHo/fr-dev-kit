package fr.agent;

import java.awt.Component;
import java.awt.Window;

import java.awt.Container;
import javax.swing.*;

/**
 * FR 组件解析器 — 将 Swing 组件映射到 FR Java API 类名
 * 基于 ckzl/gf/FR_HEADLESS_GUIDE.md 的已验证 API 列表
 */
public class ComponentResolver {
    
    /**
     * 将 AWT 组件映射到对应的 FR API 类
     * 通过检查组件类名、层级中是否包含 FR 包名来判断
     */
    public static String mapToFrApi(Component c) {
        if (c == null) return "null";
        
        String clsName = c.getClass().getName();
        
        // 直接 FR 类
        if (clsName.startsWith("com.fr.")) {
            return clsName;
        }
        
        // 遍历父级查找 FR 容器
        Component cur = c.getParent();
        while (cur != null) {
            if (cur.getClass().getName().startsWith("com.fr.")) {
                return cur.getClass().getName() + "::child";
            }
            cur = cur.getParent();
        }
        
        // 根据 Swing 组件类型和上下文推测
        String simple = c.getClass().getSimpleName();
        switch (simple) {
            case "DesignerFrame":
                return "com.fr.design.mainframe.DesignerFrame";
            case "JWorkBook":
                return "com.fr.design.mainframe.JWorkBook";
            case "CellElement":
                return "com.fr.report.cell.DefaultTemplateCellElement";
            // 通用映射 — 仅作参考
            default:
                if (c instanceof JTree) return "javax.swing.JTree (FR: ReportTree)";
                if (c instanceof JTable) return "javax.swing.JTable (FR: CellTable)";
                if (c instanceof JTabbedPane) return "javax.swing.JTabbedPane (FR: TabPane)";
                if (c instanceof JToolBar) return "javax.swing.JToolBar (FR: ToolBar)";
                if (c instanceof JMenuBar) return "javax.swing.JMenuBar (FR: MenuBar)";
                if (c instanceof JPopupMenu) return "javax.swing.JPopupMenu (FR: PopupMenu)";
                if (c instanceof JComboBox) return "javax.swing.JComboBox (FR: ComboBox)";
                if (c instanceof JTextField) return "javax.swing.JTextField (FR: TextField)";
                return "swing:" + clsName;
        }
    }
    
    /** dump 整个 Swing 组件树 */
    public static String dumpComponentTree() {
        StringBuilder sb = new StringBuilder();
        for (java.awt.Window w : Window.getWindows()) {
            if (w.isShowing()) dumpTree(w, 0, sb);
        }
        return sb.toString();
    }
    
    private static void dumpTree(Component c, int depth, StringBuilder sb) {
        if (depth > 15) return;
        for (int i = 0; i < depth; i++) sb.append("  ");
        sb.append(c.getClass().getSimpleName());
        
        String label = "";
        if (c instanceof JButton) label = ((JButton)c).getText();
        else if (c instanceof JLabel) label = ((JLabel)c).getText();
        else if (c instanceof JFrame) label = ((JFrame)c).getTitle();
        else if (c.getName() != null && !c.getName().isEmpty()) label = c.getName();
        
        if (!label.isEmpty()) sb.append(" [").append(label).append("]");
        sb.append(" -> ").append(mapToFrApi(c)).append("\n");
        
        if (c instanceof Container) {
            for (Component child : ((Container)c).getComponents()) {
                dumpTree(child, depth + 1, sb);
            }
        }
    }
}
