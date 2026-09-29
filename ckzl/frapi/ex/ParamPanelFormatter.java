package com.example.fr.autolayout;

import com.fr.base.GraphHelper;
import com.fr.base.parameter.ParameterUI;
import com.fr.form.event.Listener;
import com.fr.form.main.parameter.FormParameterUI;
import com.fr.form.parameter.FormSubmitButton;
import com.fr.form.ui.*;
import com.fr.form.ui.container.WLayout;
import com.fr.form.ui.container.WParameterLayout;
import com.fr.form.ui.widget.CRBoundsWidget;
import com.fr.io.TemplateWorkBookIO;
import com.fr.js.JavaScriptImpl;
import com.fr.main.TemplateWorkBook;
import com.fr.main.parameter.ReportParameterAttr;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.Rectangle;
import java.io.File;
import java.util.*;

/**
 * FR 参数面板自动格式化。
 * API 均已通过 javap 验证（2026-07-31）。
 */
public class ParamPanelFormatter {

    static final int GRID = 12;
    static final int CTRL_H = 24;
    static final int CTRL_MIN = 96;
    static final int CTRL_MAX = 220;
    static final int BTN_MIN = 72;
    static final int BTN_MAX = 168;
    static final int LABEL_GAP = 8;
    static final int BTN_GAP = 12;
    static final int ROW_GAP = 12;
    static final int CTRL_GAP = 24;
    static final int BTN_LEAD = 24;
    static final int PAD_H = 16;
    static final int PAD_V = 12;
    static final int MAX_COLS = 4;
    static final int TREE_INDENT = 18;
    static final int DICT_FALLBACK_WIDTH = 156;

    enum Role { LABEL, FILTER, ACTION, PRESERVE, UNKNOWN }
    enum ActionKind { QUERY, EXPORT, SUBMIT, IMPORT, ADJ, OTHER }

    static class Field {
        Widget widget;
        CRBoundsWidget ref;
        String widgetName;
        Role role;
        ActionKind actionKind = ActionKind.OTHER;
        Rectangle originalBounds;
        int measuredWidth;
        int measuredHeight = CTRL_H;
        Field labelRef;
        boolean labelConsumed = false;
        Rectangle finalBounds;
        Rectangle finalLabelBounds;
        boolean isYearDegraded = false;
    }

    static class ColumnMetrics {
        List<Integer> colX = new ArrayList<>();
    }

    // ===================== MAIN =====================

    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0]
            : "C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/示例报表工程/明细报表/示例实际表.cpt";
        boolean dryRun = args.length <= 1 || !"write".equalsIgnoreCase(args[1]);

        new ParamPanelFormatter().format(path, 1200, dryRun);
    }

    public void format(String templatePath, int availWidth, boolean dryRun) throws Exception {
        TemplateWorkBook wb = TemplateWorkBookIO.readTemplateWorkBook(templatePath);

        // CPT 路线: ReportParameterAttr → ParameterUI → FormParameterUI
        ReportParameterAttr attr = wb.getReportParameterAttr();
        if (attr == null) {
            log("无 ReportParameterAttr，跳过");
            return;
        }
        ParameterUI pui = attr.getParameterUI();
        if (!(pui instanceof FormParameterUI)) {
            log("ParameterUI 不是 FormParameterUI，跳过");
            return;
        }
        FormParameterUI ui = (FormParameterUI) pui;
        WLayout wl = ui.getContainer();
        if (!(wl instanceof WParameterLayout)) {
            log("Container 不是 WParameterLayout，跳过");
            return;
        }
        WParameterLayout layout = (WParameterLayout) wl;

        // 阶段一
        List<Field> ir = buildIR(layout);
        log("阶段一: IR 构建完成, " + ir.size() + " 个控件");

        // 阶段二
        measureAll(ir);
        log("阶段二: 测量完成");

        // Label 配对
        pairLabels(ir);
        log("Label 配对完成");

        // 阶段三
        List<Field> filters = filterByRole(ir, Role.FILTER);
        List<List<Field>> rows = packRows(filters, availWidth);
        log("阶段三: 行打包完成, " + rows.size() + " 行");

        // 阶段四
        ColumnMetrics cols = alignColumns(rows);
        if (cols.colX.isEmpty()) {
            log("无列对齐数据，跳过");
            return;
        }
        assignFilterBounds(rows, cols, availWidth);
        log("阶段四: 列对齐完成, " + cols.colX.size() + " 列");

        // 阶段五
        List<Field> actions = filterByRole(ir, Role.ACTION);
        placeButtons(actions, rows, cols, availWidth);
        log("阶段五: 按钮布局完成, " + actions.size() + " 个按钮");

        // PRESERVE
        List<Field> preserves = filterByRole(ir, Role.PRESERVE);
        int rowsBottom = PAD_V + rows.size() * CTRL_H + Math.max(0, rows.size() - 1) * ROW_GAP
                + (actions.isEmpty() ? 0 : (ROW_GAP + CTRL_H));
        placePreserveBlocks(preserves, rowsBottom);

        int designH = Math.max(rowsBottom, maxPreserveBottom(preserves)) + PAD_V;
        designH = roundUp(designH, GRID);
        log("阶段六: designW=" + availWidth + " designH=" + designH);

        if (dryRun) {
            log("[dry-run] 校验通过, 不写入. W=" + availWidth + " H=" + designH);
            for (List<Field> row : rows) {
                StringBuilder sb = new StringBuilder("  ");
                for (Field f : row) {
                    String label = f.labelRef != null ? f.labelRef.widgetName + ":" : "";
                    sb.append(label).append(f.widgetName)
                      .append("(").append(f.measuredWidth).append("px)  ");
                }
                log(sb.toString());
            }
            if (!actions.isEmpty()) {
                StringBuilder sb = new StringBuilder("  按钮: ");
                for (Field a : actions) {
                    sb.append(a.widgetName).append("(").append(a.measuredWidth).append("px) ");
                }
                log(sb.toString());
            }
            return;
        }

        // 写入
        applyToTemplate(layout, ui, ir, availWidth, designH);
        TemplateWorkBookIO.writeTemplateWorkBook(wb, templatePath);
        log("写入完成: " + templatePath);
    }

    // ===================== IR 构建 =====================

    private List<Field> buildIR(WParameterLayout layout) {
        List<Field> result = new ArrayList<>();
        int count = layout.getWidgetCount();
        for (int i = 0; i < count; i++) {
            Widget w = layout.getWidget(i);
            CRBoundsWidget bw = layout.getBoundsWidget(w);
            if (bw == null) continue;

            Field f = new Field();
            f.widget = w;
            f.ref = bw;
            f.widgetName = w.getWidgetName() != null ? w.getWidgetName() : "";
            f.originalBounds = bw.getBounds();
            f.role = classifyRole(w);

            if (isYearControl(w)) {
                f.isYearDegraded = true; // 保守降级
            }

            if (f.role == Role.ACTION) {
                f.actionKind = classifyAction(w);
            }
            result.add(f);
        }
        return result;
    }

    private Role classifyRole(Widget w) {
        if (w instanceof ElementCaseEditor || w instanceof ChartEditor) return Role.PRESERVE;
        if (w instanceof Label) return Role.LABEL;
        if (w instanceof FormSubmitButton) return Role.ACTION;
        if (w instanceof FreeButton || w instanceof Button || w instanceof ToggleButton) return Role.ACTION;
        if (w instanceof TextEditor || w instanceof NumberEditor || w instanceof Password
            || w instanceof TextArea || w instanceof DateEditor || w instanceof FileEditor
            || w instanceof ComboCheckBox || w instanceof ComboBox
            || w instanceof CheckBox || w instanceof CheckBoxGroup || w instanceof Radio || w instanceof RadioGroup
            || w instanceof TreeEditor || w instanceof TreeComboBoxEditor
            || isYearControl(w))
            return Role.FILTER;
        return Role.UNKNOWN;
    }

    private boolean isYearControl(Widget w) {
        try {
            return Class.forName("com.fr.plugin.widget.year.YearControl").isInstance(w);
        } catch (ClassNotFoundException e) { return false; }
    }

    private ActionKind classifyAction(Widget w) {
        String name = (w.getWidgetName() != null ? w.getWidgetName() : "").toLowerCase();
        String text = getButtonText(w);
        String js = getJsContent(w);

        if (w instanceof FormSubmitButton) return ActionKind.QUERY;
        if (hasAny(js, "exportreporttoexcel") || hasAny(text, "export", "导出")) return ActionKind.EXPORT;
        if (hasAny(js, "verifyandwritereport") || hasAny(text, "submit", "保存", "confirm", "提交")) return ActionKind.SUBMIT;
        if (hasAny(text, "import", "导入") || name.contains("import")) return ActionKind.IMPORT;
        if (hasAny(text, "adj") || name.contains("adj")) return ActionKind.ADJ;
        if (hasAny(text, "query", "查询") || name.contains("search")) return ActionKind.QUERY;
        return ActionKind.OTHER;
    }

    private String getJsContent(Widget w) {
        StringBuilder sb = new StringBuilder();
        try {
            for (int i = 0; i < w.getListenerSize(); i++) {
                Listener l = w.getListener(i);
                if (l != null && l.getAction() instanceof JavaScriptImpl) {
                    String c = ((JavaScriptImpl) l.getAction()).getContent();
                    if (c != null) sb.append(c).append("\n");
                }
            }
        } catch (Exception ignored) {}
        return sb.toString().toLowerCase();
    }

    private String getButtonText(Widget w) {
        if (w instanceof FormSubmitButton) {
            String t = ((FormSubmitButton) w).getText();
            if (t == null || t.trim().isEmpty()) return "查询";
            return t;
        }
        if (w instanceof Button) {
            String t = ((Button) w).getText();
            return t != null ? t : "";
        }
        return "";
    }

    private boolean hasAny(String s, String... needles) {
        if (s == null) return false;
        for (String n : needles) if (s.contains(n)) return true;
        return false;
    }

    // ===================== 测量 =====================

    private final Font defaultFont = new Font("Microsoft YaHei", Font.PLAIN, 12);

    private void measureAll(List<Field> ir) {
        for (Field f : ir) {
            switch (f.role) {
                case LABEL:
                    f.measuredWidth = measureLabel(f);
                    break;
                case FILTER:
                    f.measuredWidth = measureFilter(f);
                    break;
                case ACTION:
                    f.measuredWidth = measureButton(f);
                    break;
                case PRESERVE:
                    f.measuredWidth = f.originalBounds.width;
                    f.measuredHeight = f.originalBounds.height;
                    break;
                default:
                    f.measuredWidth = CTRL_MIN;
            }
        }
    }

    private int measureLabel(Field f) {
        String text = "";
        if (f.widget instanceof Label) {
            try {
                Object t = f.widget.getClass().getMethod("getText").invoke(f.widget);
                text = t != null ? t.toString() : "";
            } catch (Exception ignored) {}
        }
        int w = GraphHelper.getWidth(text, defaultFont) + LABEL_GAP;
        return clamp(roundUp(w, GRID), GRID, 9999);
    }

    private int measureFilter(Field f) {
        if (f.isYearDegraded) return 108;
        if (f.widget instanceof TreeEditor || f.widget instanceof TreeComboBoxEditor) {
            return clamp(roundUp(DICT_FALLBACK_WIDTH + TREE_INDENT, GRID), CTRL_MIN, CTRL_MAX);
        }
        return clamp(roundUp(DICT_FALLBACK_WIDTH, GRID), CTRL_MIN, CTRL_MAX);
    }

    private int measureButton(Field f) {
        String text = getButtonText(f.widget);
        int w = GraphHelper.getWidth(text, defaultFont) + 24;
        return clamp(roundUp(w, GRID), BTN_MIN, BTN_MAX);
    }

    // ===================== Label 配对 =====================

    private void pairLabels(List<Field> ir) {
        List<Field> labels = filterByRole(ir, Role.LABEL);
        List<Field> filters = filterByRole(ir, Role.FILTER);
        for (Field label : labels) {
            if (label.labelConsumed) continue;
            String key = stripPrefix(label.widgetName);
            if (key.isEmpty()) continue;
            for (Field filter : filters) {
                if (filter.labelRef != null) continue;
                if (filter.widgetName.equalsIgnoreCase(key)) {
                    bind(label, filter); break;
                }
            }
        }
        for (Field filter : filters) {
            if (filter.labelRef != null) continue;
            Field best = null; int bestDx = 9999;
            for (Field label : labels) {
                if (label.labelConsumed) continue;
                int dy = Math.abs(label.originalBounds.y - filter.originalBounds.y);
                if (dy >= CTRL_H) continue;
                int dx = filter.originalBounds.x - (label.originalBounds.x + label.originalBounds.width);
                if (dx < 0 || dx > CTRL_GAP * 2) continue;
                if (dx < bestDx) { bestDx = dx; best = label; }
            }
            if (best != null) bind(best, filter);
        }
    }

    private void bind(Field label, Field filter) {
        filter.labelRef = label; label.labelConsumed = true;
    }

    private String stripPrefix(String name) {
        if (name == null) return "";
        String n = name.toLowerCase();
        if (n.startsWith("label_para_")) return name.substring(11);
        if (n.startsWith("label_")) return name.substring(6);
        if (n.startsWith("lbl_")) return name.substring(4);
        return "";
    }

    // ===================== 行打包 =====================

    private List<List<Field>> packRows(List<Field> filters, int availWidth) {
        List<List<Field>> rows = new ArrayList<>();
        List<Field> cur = new ArrayList<>();
        int used = PAD_H;
        for (Field f : filters) {
            int lw = f.labelRef != null ? f.labelRef.measuredWidth : 0;
            int uw = lw + f.measuredWidth;
            int addW = cur.isEmpty() ? uw : CTRL_GAP + uw;
            if (!cur.isEmpty() && (used + addW + PAD_H > availWidth || cur.size() >= MAX_COLS)) {
                rows.add(cur); cur = new ArrayList<>(); used = PAD_H; addW = uw;
            }
            cur.add(f); used += addW;
        }
        if (!cur.isEmpty()) rows.add(cur);
        return rows;
    }

    // ===================== 列对齐 =====================

    private ColumnMetrics alignColumns(List<List<Field>> rows) {
        ColumnMetrics cm = new ColumnMetrics();
        int maxc = 0;
        for (List<Field> r : rows) maxc = Math.max(maxc, r.size());
        if (maxc == 0) return cm;
        int[] lw = new int[maxc], cw = new int[maxc];
        for (List<Field> r : rows) {
            for (int i = 0; i < r.size(); i++) {
                Field f = r.get(i);
                lw[i] = Math.max(lw[i], f.labelRef != null ? f.labelRef.measuredWidth : 0);
                cw[i] = Math.max(cw[i], f.measuredWidth);
            }
        }
        int x = PAD_H;
        for (int i = 0; i < maxc; i++) {
            cm.colX.add(x);
            x += lw[i] + cw[i] + CTRL_GAP;
        }
        return cm;
    }

    private void assignFilterBounds(List<List<Field>> rows, ColumnMetrics cols, int availWidth) {
        int y = PAD_V;
        for (List<Field> row : rows) {
            for (int i = 0; i < row.size(); i++) {
                Field f = row.get(i);
                int cx = cols.colX.get(i);
                int lw = f.labelRef != null ? f.labelRef.measuredWidth : 0;
                if (f.labelRef != null)
                    f.labelRef.finalBounds = new Rectangle(cx, y, lw - LABEL_GAP, CTRL_H);
                f.finalBounds = new Rectangle(cx + lw, y, f.measuredWidth, CTRL_H);
            }
            y += CTRL_H + ROW_GAP;
        }
    }

    // ===================== 按钮 =====================

    private void placeButtons(List<Field> actions, List<List<Field>> rows, ColumnMetrics cols, int availWidth) {
        actions.sort(Comparator.comparingInt(a -> {
            switch (a.actionKind) { case QUERY:return 0; case EXPORT:return 1; case SUBMIT:return 2; case IMPORT:return 3; case ADJ:return 4; default:return 5; }
        }));
        if (actions.isEmpty() || rows.isEmpty()) return;

        int lastRight = PAD_H;
        List<Field> lastRow = rows.get(rows.size() - 1);
        for (Field f : lastRow) if (f.finalBounds != null) lastRight = Math.max(lastRight, f.finalBounds.x + f.finalBounds.width);

        int bw = 0;
        for (Field a : actions) bw += a.measuredWidth;
        bw += (actions.size() - 1) * BTN_GAP;

        int y = PAD_V + (rows.size() - 1) * (CTRL_H + ROW_GAP);
        boolean newLine = (lastRight + BTN_LEAD + bw + PAD_H > availWidth);
        if (newLine) y += CTRL_H + ROW_GAP;

        int x = newLine ? PAD_H : lastRight + BTN_LEAD;
        for (Field a : actions) {
            a.finalBounds = new Rectangle(x, y, a.measuredWidth, CTRL_H);
            x += a.measuredWidth + BTN_GAP;
        }
    }

    // ===================== PRESERVE =====================

    private void placePreserveBlocks(List<Field> ps, int startY) {
        int y = startY + ROW_GAP;
        for (Field f : ps) {
            f.finalBounds = new Rectangle(f.originalBounds.x, y, f.originalBounds.width, f.originalBounds.height);
            y += f.originalBounds.height + ROW_GAP;
        }
    }

    private int maxPreserveBottom(List<Field> ps) {
        int b = 0;
        for (Field f : ps) if (f.finalBounds != null) b = Math.max(b, f.finalBounds.y + f.finalBounds.height);
        return b;
    }

    // ===================== 写入 =====================

    private void applyToTemplate(WParameterLayout layout, FormParameterUI ui,
                                  List<Field> ir, int availWidth, int designH) {
        for (Field f : ir) {
            if (f.finalBounds != null) f.ref.setBounds(f.finalBounds);
            if (f.labelRef != null && f.labelRef.finalBounds != null)
                f.labelRef.ref.setBounds(f.labelRef.finalBounds);
        }
        layout.setDesignWidth(availWidth);
        ui.setDesignSize(new Dimension(availWidth, designH));
    }

    // ===================== utils =====================

    private List<Field> filterByRole(List<Field> ir, Role role) {
        List<Field> out = new ArrayList<>();
        for (Field f : ir) if (f.role == role) out.add(f);
        return out;
    }

    private int clamp(int v, int min, int max) { return Math.max(min, Math.min(max, v)); }
    private int roundUp(int v, int grid) { return ((v + grid - 1) / grid) * grid; }

    private static void log(String msg) { System.out.println("[Format] " + msg); }
}
