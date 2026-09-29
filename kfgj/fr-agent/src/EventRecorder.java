package fr.agent;

import java.awt.*;
import java.awt.event.*;
import java.awt.datatransfer.*;
import javax.swing.*;
import java.util.*;
import java.util.concurrent.*;
import java.time.Instant;

/**
 * 全局 AWT 事件录制器 — 捕获所有鼠标/键盘/剪贴板事件
 * 同时识别事件的 FR 组件路径
 */
public class EventRecorder implements AWTEventListener {
    // 环形缓冲区，保留最近 10000 条事件
    public static final ConcurrentLinkedDeque<RecordedEvent> events = new ConcurrentLinkedDeque<>();
    public static final int MAX_EVENTS = 10000;
    
    private volatile boolean recording = false;
    private long recordingStart = 0;
    private final java.util.List<RecordedEvent> currentSession = new ArrayList<>();

    public void startRecording() {
        currentSession.clear();
        recordingStart = System.currentTimeMillis();
        recording = true;
        System.out.println("[EventRecorder] Recording started");
    }

    public java.util.List<RecordedEvent> stopRecording() {
        recording = false;
        System.out.println("[EventRecorder] Recording stopped. Events: " + currentSession.size());
        return new ArrayList<>(currentSession);
    }

    public boolean isRecording() { return recording; }

    @Override
    public void eventDispatched(AWTEvent event) {
        RecordedEvent evt = null;

        if (event instanceof MouseEvent) {
            evt = handleMouse((MouseEvent) event);
        } else if (event instanceof KeyEvent) {
            evt = handleKey((KeyEvent) event);
        } else if (event instanceof FocusEvent) {
            evt = handleFocus((FocusEvent) event);
        } else if (event instanceof ActionEvent) {
            evt = handleAction((ActionEvent) event);
        } else if (event instanceof WindowEvent) {
            evt = handleWindow((WindowEvent) event);
        }

        if (evt != null) {
            events.addLast(evt);
            while (events.size() > MAX_EVENTS) events.removeFirst();
            if (recording) currentSession.add(evt);
        }
    }

    private RecordedEvent handleMouse(MouseEvent me) {
        String type;
        switch (me.getID()) {
            case MouseEvent.MOUSE_PRESSED:  type = "MOUSE_PRESSED"; break;
            case MouseEvent.MOUSE_RELEASED: type = "MOUSE_RELEASED"; break;
            case MouseEvent.MOUSE_CLICKED:  type = "MOUSE_CLICKED"; break;
            case MouseEvent.MOUSE_MOVED:    return null; // 太频繁，跳过
            case MouseEvent.MOUSE_DRAGGED:  type = "MOUSE_DRAGGED"; break;
            case MouseEvent.MOUSE_WHEEL:    type = "MOUSE_WHEEL"; break;
            default: return null;
        }

        Component c = me.getComponent();
        return new RecordedEvent(
            type,
            System.currentTimeMillis(),
            resolveComponent(c),
            me.getX(), me.getY(),
            me.getXOnScreen(), me.getYOnScreen(),
            me.getButton(), me.getModifiersEx(),
            me.isPopupTrigger() ? "POPUP" : ""
        );
    }

    private RecordedEvent handleKey(KeyEvent ke) {
        if (ke.getID() != KeyEvent.KEY_PRESSED && ke.getID() != KeyEvent.KEY_RELEASED)
            return null;

        String type = ke.getID() == KeyEvent.KEY_PRESSED ? "KEY_PRESSED" : "KEY_RELEASED";
        Component c = ke.getComponent();
        StringBuilder detail = new StringBuilder();
        
        detail.append("key=").append(KeyEvent.getKeyText(ke.getKeyCode()));
        detail.append(" code=").append(ke.getKeyCode());
        if (ke.isControlDown()) detail.append(" +Ctrl");
        if (ke.isShiftDown()) detail.append(" +Shift");
        if (ke.isAltDown()) detail.append(" +Alt");
        if ((int)ke.getKeyChar() >= 32) detail.append(" char=").append(ke.getKeyChar());

        KeyStroke ks = KeyStroke.getKeyStrokeForEvent(ke);
        if (ks != null) detail.append(" ks=").append(ks.toString());

        return new RecordedEvent(
            type, System.currentTimeMillis(),
            resolveComponent(c), 0, 0, 0, 0, 0,
            ke.getModifiersEx(), detail.toString()
        );
    }

    private RecordedEvent handleFocus(FocusEvent fe) {
        String type = fe.getID() == FocusEvent.FOCUS_GAINED ? "FOCUS_GAINED" : "FOCUS_LOST";
        Component c = fe.getComponent();
        return new RecordedEvent(
            type, System.currentTimeMillis(),
            resolveComponent(c), 0, 0, 0, 0, 0, 0, ""
        );
    }

    private RecordedEvent handleAction(ActionEvent ae) {
        return new RecordedEvent(
            "ACTION_PERFORMED", System.currentTimeMillis(),
            resolveComponent((Component)ae.getSource()), 0, 0, 0, 0, 0, 0,
            ae.getActionCommand()
        );
    }

    private RecordedEvent handleWindow(WindowEvent we) {
        String type;
        switch (we.getID()) {
            case WindowEvent.WINDOW_OPENED:   type = "WINDOW_OPENED"; break;
            case WindowEvent.WINDOW_CLOSING:  type = "WINDOW_CLOSING"; break;
            case WindowEvent.WINDOW_ACTIVATED: type = "WINDOW_ACTIVATED"; break;
            default: return null;
        }
        return new RecordedEvent(
            type, System.currentTimeMillis(),
            resolveComponent(we.getWindow()), 0, 0, 0, 0, 0, 0, ""
        );
    }

    public void onClipboardChange() {
        try {
            Transferable t = Toolkit.getDefaultToolkit().getSystemClipboard().getContents(null);
            if (t != null && t.isDataFlavorSupported(DataFlavor.stringFlavor)) {
                String text = (String) t.getTransferData(DataFlavor.stringFlavor);
                RecordedEvent evt = new RecordedEvent(
                    "CLIPBOARD", System.currentTimeMillis(),
                    new ComponentInfo("java.awt.datatransfer.Clipboard", "system_clipboard", "clipboard", ""), 0, 0, 0, 0, 0, 0,
                    text.length() > 200 ? text.substring(0, 200) + "..." : text
                );
                events.addLast(evt);
                if (recording) currentSession.add(evt);
            }
        } catch (Exception ignored) {}
    }

    /** 解析组件路径 — 从叶子到根的完整路径 */
    public static ComponentInfo resolveComponent(Component c) {
        if (c == null) return new ComponentInfo("null", "null", "null", "");
        
        StringBuilder path = new StringBuilder();
        Component cur = c;
        while (cur != null) {
            String name = cur.getClass().getSimpleName();
            // 尝试获取有意义的名称
            String label = "";
            if (cur instanceof JButton) label = ((JButton)cur).getText();
            else if (cur instanceof JLabel) label = ((JLabel)cur).getText();
            else if (cur instanceof JMenuItem) label = ((JMenuItem)cur).getText();
            else if (cur instanceof javax.swing.AbstractButton) 
                label = ((javax.swing.AbstractButton)cur).getText();
            else if (cur instanceof JFrame) label = ((JFrame)cur).getTitle();
            else if (cur instanceof JDialog) label = ((JDialog)cur).getTitle();
            else if (cur instanceof JTabbedPane) {
                int idx = ((JTabbedPane)cur).getSelectedIndex();
                if (idx >= 0) label = ((JTabbedPane)cur).getTitleAt(idx);
            }
            if (cur.getName() != null && !cur.getName().isEmpty()) 
                label = cur.getName();

            String segment = name;
            if (!label.isEmpty()) segment += "[" + label + "]";
            if (path.length() > 0) segment += "/";
            path.insert(0, segment);
            
            cur = cur.getParent();
            if (path.length() > 500) break;
        }
        
        // 尝试映射到 FR API
        String frApi = ComponentResolver.mapToFrApi(c);
        
        return new ComponentInfo(
            c.getClass().getName(),
            path.toString(),
            frApi,
            c instanceof JComponent ? 
                ((JComponent)c).getToolTipText() : ""
        );
    }

    /** 事件数据结构 */
    public static class RecordedEvent {
        public final String type;
        public final long timestamp;
        public final ComponentInfo component;
        public final int localX, localY, screenX, screenY;
        public final int button, modifiers;
        public final String detail;

        RecordedEvent(String type, long ts, ComponentInfo comp,
                      int lx, int ly, int sx, int sy, int btn, int mods, String detail) {
            this.type = type;
            this.timestamp = ts;
            this.component = comp;
            this.localX = lx; this.localY = ly;
            this.screenX = sx; this.screenY = sy;
            this.button = btn; this.modifiers = mods;
            this.detail = detail;
        }

        public String toJson() { return EventSerializer.toJson(this); }
        @Override public String toString() { return toJson(); }
    }

    /** 组件信息 */
    public static class ComponentInfo {
        public final String className;
        public final String path;
        public final String frApiClass;
        public final String tooltip;

        ComponentInfo(String cn, String p, String fr, String tt) {
            this.className = cn; this.path = p; this.frApiClass = fr; this.tooltip = tt;
        }
    }

    /** Called from custom EventQueue.dispatchEvent */
    public void dispatchFromQueue(AWTEvent event) {
        eventDispatched(event);
    }

}
