import os
BASE = r"C:\Users\<你的用户名>\Desktop\fr_dev_kit\fr-agent\src"

# === FrAgent.java ===
open(os.path.join(BASE, "FrAgent.java"), "w", encoding="utf-8").write(
"""package fr.agent;

import java.awt.*;
import java.lang.instrument.Instrumentation;

public class FrAgent {
    public static final int HTTP_PORT = 18999;

    public static void premain(String args, Instrumentation inst) {
        System.out.println("[FrAgent] Agent loaded, PID=" + ProcessHandle.current().pid());

        EventQueue.invokeLater(() -> {
            try {
                EventRecorder recorder = new EventRecorder();
                long mask = AWTEvent.MOUSE_EVENT_MASK | AWTEvent.MOUSE_MOTION_EVENT_MASK
                    | AWTEvent.KEY_EVENT_MASK | AWTEvent.FOCUS_EVENT_MASK
                    | AWTEvent.ACTION_EVENT_MASK | AWTEvent.WINDOW_EVENT_MASK;
                Toolkit.getDefaultToolkit().addAWTEventListener(recorder, mask);
                Toolkit.getDefaultToolkit().getSystemClipboard()
                    .addFlavorListener(e -> recorder.onClipboardChange());
                System.out.println("[FrAgent] Listeners registered");
            } catch (Exception e) {
                System.err.println("[FrAgent] Error: " + e.getMessage());
            }
        });

        new Thread(() -> {
            try {
                new CommandServer(HTTP_PORT).start();
                System.out.println("[FrAgent] API: http://localhost:" + HTTP_PORT);
            } catch (Exception e) {
                System.err.println("[FrAgent] Server error: " + e.getMessage());
            }
        }, "agent-server").start();
    }
}
""")
print("FrAgent.java OK")