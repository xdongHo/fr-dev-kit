package com.fr.kb.format;

import java.awt.Dimension;
import java.awt.Rectangle;
import java.io.File;

import com.fr.form.main.parameter.FormParameterUI;
import com.fr.form.ui.Widget;
import com.fr.form.ui.container.WAbsoluteLayout.BoundsWidget;
import com.fr.form.ui.container.WParameterLayout;
import com.fr.io.TemplateWorkBookIO;
import com.fr.main.TemplateWorkBook;
import com.fr.report.parameter.ReportParameterAttr;

/**
 * ParamPanelFormatter — 参数面板格式化器（FR Java API 版, 2026-08-05）
 *
 * 设计：完全通过 FR Java API 操作模板对象（读模板 → 重排控件 bounds →
 * 写面板尺寸 → 保存），不触碰 XML 文本，从根上避免 Python 正则脚本
 * 损坏模板完整性的问题。
 *
 * 两种方案（LAYOUT_SPEC Ver0.5）：
 *   watermark (默认): 无 Label，输入控件均布 180px 网格，按钮右对齐
 *   label      (分支): Label+控件配对（Label 左对齐、Label→5px）
 *
 * ⚠ 运行环境限制（2026-08-05 实测）：
 *   TemplateWorkBookIO 磁盘读写依赖 FR web 会话（ConfigurationActivator
 *   需 extra session）。在 fr-agent /exec（Nashorn，Designer JVM）中直接
 *   调用会抛 Fine-Engine_NS_Exception_ReadError / cannot find extra session。
 *   可行运行方式：
 *     a) 在 FR 报表服务器(webroot)的 web 环境下，经 servlet/自定义类加载运行；
 *     b) 通过 fr-agent 扩展：先让 Designer 打开目标模板（GUI），再经
 *        Designer API 取内存工作簿对象格式化后由 Designer 保存（待实现）；
 *     c) 纯离线校验请用 fmt_panel_safe.py（坐标级 XML 替换，安全）。
 *
 * 编译（需要 FR lib: fine-core/fine-report-engine 等）:
 *   javac -encoding UTF-8 -cp "<FR_HOME>/webapps/webroot/WEB-INF/lib/*" ParamPanelFormatter.java
 */
public class ParamPanelFormatter {

    static final int CTRL_W = 180, CTRL_H = 26;
    static final int LABEL_GAP = 5, CTRL_GAP = 20, BTN_GAP = 40;
    static final int MARGIN = 12, ROW_GAP = 8;
    static final int BTN_W = 80, IMPORT_W = 120;

    static boolean isInput(Widget w) {
        String n = w.getClass().getName();
        return n.contains("ComboCheckBox") || n.contains("ComboBox")
                || n.contains("YearControl") || n.contains("DateEditor")
                || n.contains("TextEditor") || n.contains("NumberEditor")
                || n.contains("CheckBox") || n.contains("RadioGroup")
                || n.contains("TreeEditor");
    }

    static boolean isButton(Widget w) {
        String n = w.getClass().getName();
        return n.contains("FreeButton") || n.contains("FormSubmitButton")
                || n.contains("Button") || n.contains("ToggleButton");
    }

    static boolean isLabel(Widget w) {
        return w.getClass().getName().contains("Label");
    }

    static int buttonWidth(Widget w) {
        return w.getWidgetName() != null
                && (w.getWidgetName().contains("Import") || w.getWidgetName().contains("import"))
                ? IMPORT_W : BTN_W;
    }

    static int labelWidth(String text) {
        if (text == null || text.isEmpty()) return 40;
        int w = 0;
        for (int i = 0; i < text.length(); i++) {
            w += text.charAt(i) > 127 ? 14 : 8;
        }
        return Math.max(40, w + 16);
    }

    static String fmt(Rectangle r) {
        return "x=" + r.x + " y=" + r.y + " w=" + r.width + " h=" + r.height;
    }

    public static void format(String templatePath, boolean labelMode) throws Exception {
        TemplateWorkBook wb = TemplateWorkBookIO.readTemplateWorkBook(templatePath);
        ReportParameterAttr attr = wb.getReportParameterAttr();
        if (attr == null) {
            System.out.println("no parameter panel");
            return;
        }
        FormParameterUI ui = (FormParameterUI) attr.getParameterUI();
        WParameterLayout layout = (WParameterLayout) ui.getContainer();
        if (layout == null) return;

        int n = layout.getWidgetCount();
        java.util.List<Widget> inputs = new java.util.ArrayList<>();
        java.util.List<Widget> labels = new java.util.ArrayList<>();
        java.util.List<Widget> btns = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) {
            Widget w = layout.getWidget(i);
            if (isButton(w)) btns.add(w);
            else if (isLabel(w)) labels.add(w);
            else if (isInput(w)) inputs.add(w);
        }

        int panelW, panelH;
        if (labelMode && !labels.isEmpty()) {
            panelW = layoutLabel(layout, labels, inputs, btns);
        } else {
            panelW = layoutWatermark(layout, inputs, btns);
        }
        panelH = designHeight(inputs.size(), btns.size(), labelMode && !labels.isEmpty());
        // 宽度：Layout；高度：ParameterUI（唯一写入口，两步缺一不可）
        layout.setDesignWidth(panelW);
        ui.setDesignSize(new Dimension(panelW, panelH));
        System.out.println("panel " + panelW + "x" + panelH);

        TemplateWorkBookIO.writeTemplateWorkBook(new File(templatePath), wb);
        System.out.println("written: " + templatePath);
    }

    /** 水印式：输入控件按原 y 分组，均布 180px 网格；按钮右对齐。 */
    static int layoutWatermark(WParameterLayout layout,
                               java.util.List<Widget> inputs,
                               java.util.List<Widget> btns) {
        java.util.List<java.util.List<Widget>> rows = new java.util.ArrayList<>();
        for (Widget w : inputs) {
            Rectangle r = layout.getBoundsWidget(w).getBounds();
            boolean placed = false;
            for (java.util.List<Widget> row : rows) {
                Rectangle rr = layout.getBoundsWidget(row.get(0)).getBounds();
                if (Math.abs(r.y - rr.y) <= 5) { row.add(w); placed = true; break; }
            }
            if (!placed) { java.util.List<Widget> nr = new java.util.ArrayList<>(); nr.add(w); rows.add(nr); }
        }
        int right = MARGIN;
        for (int ri = 0; ri < rows.size(); ri++) {
            java.util.List<Widget> row = rows.get(ri);
            row.sort((a, b) -> layout.getBoundsWidget(a).getBounds().x
                    - layout.getBoundsWidget(b).getBounds().x);
            int y = MARGIN + ri * (CTRL_H + ROW_GAP);
            for (int ci = 0; ci < row.size(); ci++) {
                int x = MARGIN + ci * (CTRL_W + CTRL_GAP);
                layout.getBoundsWidget(row.get(ci)).setBounds(new Rectangle(x, y, CTRL_W, CTRL_H));
                right = Math.max(right, x + CTRL_W);
            }
        }
        placeButtons(layout, btns, right, MARGIN + rows.size() * (CTRL_H + ROW_GAP));
        return Math.max(right, panelRight(layout, btns, right)) + MARGIN;
    }

    /** Label 式：Label+控件配对，Label 左对齐，Label→5px，跨行 Label 列对齐。 */
    static int layoutLabel(WParameterLayout layout,
                           java.util.List<Widget> labels,
                           java.util.List<Widget> inputs,
                           java.util.List<Widget> btns) {
        java.util.List<java.util.List<Widget[]>> rows = new java.util.ArrayList<>();
        java.util.List<Widget[]> all = new java.util.ArrayList<>();
        for (Widget l : labels) {
            Rectangle lr = layout.getBoundsWidget(l).getBounds();
            Widget partner = null;
            for (Widget c : inputs) {
                Rectangle cr = layout.getBoundsWidget(c).getBounds();
                if (Math.abs(cr.y - lr.y) <= 5 && cr.x >= lr.x + lr.width
                        && cr.x - (lr.x + lr.width) <= CTRL_GAP * 2) { partner = c; break; }
            }
            if (partner != null) all.add(new Widget[]{l, partner});
        }
        if (all.isEmpty()) {
            java.util.List<Widget> combined = new java.util.ArrayList<>(inputs);
            combined.addAll(labels);
            return layoutWatermark(layout, combined, btns);
        }
        for (Widget[] p : all) {
            Rectangle lr = layout.getBoundsWidget(p[0]).getBounds();
            boolean placed = false;
            for (java.util.List<Widget[]> row : rows) {
                Rectangle rr = layout.getBoundsWidget(row.get(0)[0]).getBounds();
                if (Math.abs(lr.y - rr.y) <= 5) { row.add(p); placed = true; break; }
            }
            if (!placed) { java.util.List<Widget[]> nr = new java.util.ArrayList<>(); nr.add(p); rows.add(nr); }
        }
        int nCols = 0;
        for (java.util.List<Widget[]> r : rows) nCols = Math.max(nCols, r.size());
        int[] colLw = new int[nCols];
        for (java.util.List<Widget[]> r : rows) {
            r.sort((a, b) -> layout.getBoundsWidget(a[0]).getBounds().x
                    - layout.getBoundsWidget(b[0]).getBounds().x);
            for (int ci = 0; ci < r.size(); ci++) {
                String t = r.get(ci)[0].getWidgetName();
                colLw[ci] = Math.max(colLw[ci], labelWidth(t));
            }
        }
        int right = MARGIN;
        for (int ri = 0; ri < rows.size(); ri++) {
            java.util.List<Widget[]> row = rows.get(ri);
            int y = MARGIN + ri * (CTRL_H + ROW_GAP);
            int x = MARGIN;
            for (int ci = 0; ci < row.size(); ci++) {
                Widget l = row.get(ci)[0], c = row.get(ci)[1];
                layout.getBoundsWidget(l).setBounds(new Rectangle(x, y, colLw[ci], CTRL_H));
                layout.getBoundsWidget(c).setBounds(new Rectangle(x + colLw[ci] + LABEL_GAP, y, CTRL_W, CTRL_H));
                x = x + colLw[ci] + LABEL_GAP + CTRL_W + CTRL_GAP;
            }
            right = Math.max(right, x - CTRL_GAP);
        }
        placeButtons(layout, btns, right, MARGIN + rows.size() * (CTRL_H + ROW_GAP));
        return Math.max(right, panelRight(layout, btns, right)) + MARGIN;
    }

    static void placeButtons(WParameterLayout layout, java.util.List<Widget> btns,
                             int right, int y) {
        btns.sort((a, b) -> layout.getBoundsWidget(a).getBounds().x
                - layout.getBoundsWidget(b).getBounds().x);
        int x = right;
        for (int i = btns.size() - 1; i >= 0; i--) {
            Widget w = btns.get(i);
            int bw = buttonWidth(w);
            layout.getBoundsWidget(w).setBounds(new Rectangle(x - bw, y, bw, CTRL_H));
            x = x - bw - BTN_GAP;
        }
    }

    static int panelRight(WParameterLayout layout, java.util.List<Widget> btns, int fallback) {
        int r = fallback;
        for (Widget w : btns) {
            r = Math.max(r, layout.getBoundsWidget(w).getBounds().x
                    + layout.getBoundsWidget(w).getBounds().width);
        }
        return r;
    }

    static int designHeight(int inputCount, int btnCount, boolean labelMode) {
        // 行数估算：输入控件按 5/行（Label 式按 4 组/行），按钮独立一行
        int perRow = labelMode ? 4 : 5;
        int rows = Math.max(1, (inputCount + perRow - 1) / perRow);
        return MARGIN + rows * (CTRL_H + ROW_GAP) + (btnCount > 0 ? CTRL_H + ROW_GAP : 0) + 13;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("usage: java ParamPanelFormatter <cpt路径> [watermark|label]");
            return;
        }
        boolean labelMode = args.length > 1 && "label".equalsIgnoreCase(args[1]);
        format(args[0], labelMode);
    }
}
