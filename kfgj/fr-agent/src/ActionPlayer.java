package fr.agent;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.List;

/**
 * 动作回放器 — 使用 java.awt.Robot 精确回放录制的操作序列
 * 支持: 点击、打字、快捷键、菜单导航、剪贴板操作
 */
public class ActionPlayer {
    private final Robot robot;
    private volatile boolean playing = false;
    private volatile boolean stopped = false;

    public ActionPlayer() throws AWTException {
        this.robot = new Robot();
        robot.setAutoDelay(5);
    }

    public void stop() { stopped = true; playing = false; }

    /** 回放事件序列 */
    public String replay(List<EventRecorder.RecordedEvent> events, double speed) {
        playing = true; stopped = false;
        int delayMs = (int)(10 / speed); // speed=1.0 -> 10ms delay
        int count = 0, errors = 0;
        long lastTs = 0;

        for (EventRecorder.RecordedEvent evt : events) {
            if (stopped) break;
            
            // 模拟原有时序间隔
            if (lastTs > 0) {
                long gap = (evt.timestamp - lastTs);
                if (gap > 0 && gap < 5000) {
                    robot.delay((int)(gap / speed));
                }
            }
            lastTs = evt.timestamp;

            try {
                executeEvent(evt);
                count++;
            } catch (Exception e) {
                errors++;
                System.err.println("Replay error: " + e.getMessage());
            }
        }
        playing = false;
        return String.format("Replayed %d events, %d errors", count, errors);
    }

    /** 执行单个事件 */
    private void executeEvent(EventRecorder.RecordedEvent evt) {
        switch (evt.type) {
            case "MOUSE_PRESSED":
            case "MOUSE_CLICKED":
                robot.mouseMove(evt.screenX, evt.screenY);
                robot.mousePress(getButtonMask(evt.button));
                robot.mouseRelease(getButtonMask(evt.button));
                break;
                
            case "MOUSE_RELEASED":
                robot.mouseMove(evt.screenX, evt.screenY);
                robot.mouseRelease(getButtonMask(evt.button));
                break;
                
            case "MOUSE_DRAGGED":
                robot.mouseMove(evt.screenX, evt.screenY);
                break;
                
            case "MOUSE_WHEEL":
                robot.mouseWheel(evt.detail.contains("DOWN") ? -3 : 3);
                break;
                
            case "KEY_PRESSED":
                if (evt.detail.contains("ks=")) {
                    // KeyStroke 格式: "ctrl pressed C"
                    String ks = evt.detail.split("ks=")[1].trim();
                    executeKeyStroke(ks);
                } else if (evt.detail.contains("code=")) {
                    try {
                        String codeStr = evt.detail.split("code=")[1].split(" ")[0];
                        int code = Integer.parseInt(codeStr);
                        if (evt.detail.contains("+Ctrl")) robot.keyPress(KeyEvent.VK_CONTROL);
                        if (evt.detail.contains("+Shift")) robot.keyPress(KeyEvent.VK_SHIFT);
                        if (evt.detail.contains("+Alt")) robot.keyPress(KeyEvent.VK_ALT);
                        robot.keyPress(code);
                        robot.keyRelease(code);
                        if (evt.detail.contains("+Alt")) robot.keyRelease(KeyEvent.VK_ALT);
                        if (evt.detail.contains("+Shift")) robot.keyRelease(KeyEvent.VK_SHIFT);
                        if (evt.detail.contains("+Ctrl")) robot.keyRelease(KeyEvent.VK_CONTROL);
                    } catch (NumberFormatException ignored) {}
                }
                break;
                
            case "CLIPBOARD":
                // 剪贴板: 将内容放入系统剪贴板
                Toolkit.getDefaultToolkit().getSystemClipboard()
                    .setContents(new java.awt.datatransfer.StringSelection(evt.detail), null);
                break;
                
            case "ACTION_PERFORMED":
                // Action 事件回放 — 尝试通过菜单/按钮路径找到并点击
                String path = evt.component.path;
                if (path.contains("[")) {
                    String label = path.substring(path.lastIndexOf("[") + 1, path.lastIndexOf("]"));
                    clickComponentByLabel(label);
                }
                break;
        }
    }

    private int getButtonMask(int btn) {
        switch (btn) {
            case MouseEvent.BUTTON2: return InputEvent.BUTTON2_DOWN_MASK;
            case MouseEvent.BUTTON3: return InputEvent.BUTTON3_DOWN_MASK;
            default: return InputEvent.BUTTON1_DOWN_MASK;
        }
    }

    private void executeKeyStroke(String ks) {
        // 解析 "ctrl pressed C" 格式
        try {
            String[] parts = ks.split(" ");
            int mask = 0;
            int key = 0;
            for (String p : parts) {
                if (p.equalsIgnoreCase("ctrl") || p.equalsIgnoreCase("control"))
                    mask |= InputEvent.CTRL_DOWN_MASK;
                else if (p.equalsIgnoreCase("shift")) mask |= InputEvent.SHIFT_DOWN_MASK;
                else if (p.equalsIgnoreCase("alt")) mask |= InputEvent.ALT_DOWN_MASK;
                else if (p.equalsIgnoreCase("meta")) mask |= InputEvent.META_DOWN_MASK;
                else if (p.equalsIgnoreCase("pressed") || p.equalsIgnoreCase("released")) ;
                else {
                    // 单个字符
                    if (p.length() == 1) {
                        key = KeyEvent.getExtendedKeyCodeForChar(p.charAt(0));
                    }
                }
            }
            if (key > 0) {
                if (mask != 0) {
                    robot.keyPress(maskToVK(mask));
                }
                robot.keyPress(key);
                robot.keyRelease(key);
                if (mask != 0) {
                    robot.keyRelease(maskToVK(mask));
                }
            }
        } catch (Exception ignored) {}
    }

    private int maskToVK(int mask) {
        if ((mask & InputEvent.CTRL_DOWN_MASK) != 0) return KeyEvent.VK_CONTROL;
        if ((mask & InputEvent.SHIFT_DOWN_MASK) != 0) return KeyEvent.VK_SHIFT;
        if ((mask & InputEvent.ALT_DOWN_MASK) != 0) return KeyEvent.VK_ALT;
        return 0;
    }

    /** 通过 label 点击组件（遍历组件树） */
    private void clickComponentByLabel(String label) {
        for (java.awt.Window w : Window.getWindows()) {
            if (w.isShowing()) {
                Component found = findByLabel(w, label);
                if (found != null) {
                    Point p = found.getLocationOnScreen();
                    Dimension d = found.getSize();
                    robot.mouseMove(p.x + d.width/2, p.y + d.height/2);
                    robot.mousePress(InputEvent.BUTTON1_DOWN_MASK);
                    robot.mouseRelease(InputEvent.BUTTON1_DOWN_MASK);
                    return;
                }
            }
        }
    }

    private Component findByLabel(Component c, String label) {
        if (label == null || label.isEmpty()) return null;
        if (c instanceof JButton && label.equals(((JButton)c).getText())) return c;
        if (c instanceof JMenuItem && label.equals(((JMenuItem)c).getText())) return c;
        if (c instanceof javax.swing.AbstractButton && 
            label.equals(((javax.swing.AbstractButton)c).getText())) return c;
        if (c instanceof Container) {
            for (Component child : ((Container)c).getComponents()) {
                Component found = findByLabel(child, label);
                if (found != null) return found;
            }
        }
        return null;
    }

    /** 直接点击坐标 */
    public void clickAt(int x, int y) {
        robot.mouseMove(x, y);
        robot.mousePress(InputEvent.BUTTON1_DOWN_MASK);
        robot.mouseRelease(InputEvent.BUTTON1_DOWN_MASK);
    }

    /** 直接键盘输入 */
    public void typeText(String text) {
        for (char ch : text.toCharArray()) {
            int code = KeyEvent.getExtendedKeyCodeForChar(ch);
            if (code != KeyEvent.VK_UNDEFINED) {
                robot.keyPress(code);
                robot.keyRelease(code);
            }
        }
    }

    /** 快捷键 */
    public void shortcut(String keys) {
        // keys: "ctrl+s", "ctrl+shift+f" 等
        String[] parts = keys.toLowerCase().split("\\+");
        int mask = 0;
        int lastKey = 0;
        for (String p : parts) {
            switch (p.trim()) {
                case "ctrl": case "control":
                    robot.keyPress(KeyEvent.VK_CONTROL);
                    mask |= InputEvent.CTRL_DOWN_MASK; break;
                case "shift":
                    robot.keyPress(KeyEvent.VK_SHIFT);
                    mask |= InputEvent.SHIFT_DOWN_MASK; break;
                case "alt":
                    robot.keyPress(KeyEvent.VK_ALT);
                    mask |= InputEvent.ALT_DOWN_MASK; break;
                default:
                    if (p.length() == 1) {
                        lastKey = KeyEvent.getExtendedKeyCodeForChar(p.charAt(0));
                    } else {
                        try {
                            lastKey = KeyEvent.class.getField("VK_" + p.toUpperCase()).getInt(null);
                        } catch (Exception ignored) {}
                    }
            }
        }
        if (lastKey > 0) robot.keyPress(lastKey);
        robot.keyRelease(lastKey);
        if ((mask & InputEvent.ALT_DOWN_MASK) != 0) robot.keyRelease(KeyEvent.VK_ALT);
        if ((mask & InputEvent.SHIFT_DOWN_MASK) != 0) robot.keyRelease(KeyEvent.VK_SHIFT);
        if ((mask & InputEvent.CTRL_DOWN_MASK) != 0) robot.keyRelease(KeyEvent.VK_CONTROL);
    }

    public boolean isPlaying() { return playing; }
}
