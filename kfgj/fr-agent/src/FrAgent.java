package fr.agent;

import java.awt.*;
import java.lang.instrument.Instrumentation;

public class FrAgent {
    // 端口可通过系统属性覆盖: -Dfr.agent.http.port=19100 -Dfr.agent.exec.port=19101
    // 默认 18999/19000 保持向后兼容
    public static final int HTTP_PORT = Integer.parseInt(System.getProperty("fr.agent.http.port", "18999"));
    public static final int EXEC_PORT = Integer.parseInt(System.getProperty("fr.agent.exec.port", "19000"));
    public static EventRecorder recorder;
    private static volatile boolean listenerReady = false;

    public static void shutdown() {
        ExecServer.stop();
        CommandServer.shutdown();
    }

    public static void premain(String args, Instrumentation inst) {
        recorder = new EventRecorder();
        System.out.println("[FrAgent] Loaded, PID=" +
            java.lang.management.ManagementFactory.getRuntimeMXBean().getName().split("@")[0]);

        EventQueue.invokeLater(() -> {
            try {
                long mask = AWTEvent.MOUSE_EVENT_MASK | AWTEvent.KEY_EVENT_MASK |
                    AWTEvent.FOCUS_EVENT_MASK | AWTEvent.WINDOW_EVENT_MASK |
                    AWTEvent.COMPONENT_EVENT_MASK;
                Toolkit.getDefaultToolkit().addAWTEventListener(recorder, mask);
                listenerReady = true;
                System.out.println("[FrAgent] Listener registered on EDT");
            } catch (Exception e) {
                System.err.println("[FrAgent] Listener FAILED: " + e.getMessage());
            }
        });

        new Thread(() -> {
            try { Thread.sleep(2000);
                new CommandServer(HTTP_PORT).start();
                System.out.println("[FrAgent] API: http://localhost:" + HTTP_PORT);
            } catch (Exception e) {
                System.err.println("[FrAgent] Server: " + e.getMessage());
            }
        }, "srv").start();

        new Thread(() -> {
            try { Thread.sleep(2500);
                ExecServer.start(EXEC_PORT);
                System.out.println("[FrAgent] Exec API: http://localhost:" + EXEC_PORT + "/exec");
            } catch (Exception e) {
                System.err.println("[FrAgent] ExecServer: " + e.getMessage());
            }
        }, "exec").start();
    }

    public static void agentmain(String args, Instrumentation inst) { premain(args, inst); }

    public static void ensureListener() {
        if (listenerReady) return;
        EventQueue.invokeLater(() -> {
            long mask = AWTEvent.MOUSE_EVENT_MASK | AWTEvent.KEY_EVENT_MASK |
                AWTEvent.FOCUS_EVENT_MASK | AWTEvent.WINDOW_EVENT_MASK |
                AWTEvent.COMPONENT_EVENT_MASK;
            Toolkit.getDefaultToolkit().addAWTEventListener(recorder, mask);
            listenerReady = true;
        });
    }
}
