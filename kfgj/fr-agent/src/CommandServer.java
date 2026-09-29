package fr.agent;


import com.sun.net.httpserver.*;

import java.io.*;

import java.net.*;

import java.nio.charset.StandardCharsets;

import java.util.*;

import java.util.stream.Collectors;



public class CommandServer {

    private final HttpServer server;

    private final EventRecorder recorder;

    private ActionPlayer player;

    private static HttpServer activeServer;



    public static void shutdown() {

        if (activeServer != null) { activeServer.stop(0); activeServer = null; }

    }



    public CommandServer(int port) throws IOException {

        this.server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);

        this.recorder = FrAgent.recorder;

        try { this.player = new ActionPlayer(); }

        catch (Exception e) { System.err.println("Player init: " + e.getMessage()); }


        server.createContext("/ping", this::handlePing);
        server.createContext("/status", this::handleStatus);
        server.createContext("/events", this::handleEvents);
        server.createContext("/record/start", this::handleRecordStart);
        server.createContext("/record/stop", this::handleRecordStop);
        server.createContext("/record/status", this::handleRecordStatus);
        server.createContext("/replay", this::handleReplay);
        server.createContext("/click", this::handleClick);
        server.createContext("/type", this::handleType);
        server.createContext("/shortcut", this::handleShortcut);
        server.createContext("/tree", this::handleTree);
        server.createContext("/eval", this::handleEval);
        server.createContext("/exec", this::handleExec);
        server.createContext("/shutdown", this::handleShutdown);
        server.createContext("/import", this::handleImport);

        server.setExecutor(java.util.concurrent.Executors.newFixedThreadPool(4));
    }


    public void start() { shutdown(); server.start(); activeServer = server; }


    private void json(HttpExchange ex, String s) throws IOException {
        byte[] b = s.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.sendResponseHeaders(200, b.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(b); }
    }


    private void handlePing(HttpExchange ex) throws IOException {
        json(ex, "{\"status\":\"ok\",\"pid\":" + java.lang.management.ManagementFactory.getRuntimeMXBean().getName().split("@")[0] + "}");
    }


    private void handleStatus(HttpExchange ex) throws IOException {
        String wb = "unknown";
        try {
            for (java.awt.Frame f : java.awt.Frame.getFrames()) {
                if (f.getClass().getName().contains("DesignerFrame")) {
                    wb = f.getTitle(); break;
                }
            }
        } catch (Exception e) { wb = "Err: " + e.getMessage(); }
        json(ex, "{\"status\":\"ok\",\"pid\":" + java.lang.management.ManagementFactory.getRuntimeMXBean().getName().split("@")[0] +
            ",\"events\":" + EventRecorder.events.size() +
            ",\"recording\":" + recorder.isRecording() +
            ",\"player\":" + (player != null) +
            ",\"workbook\":\"" + esc(wb) + "\"}");
    }


    private void handleEvents(HttpExchange ex) throws IOException {
        int n = 50;
        try {
            String q = ex.getRequestURI().getQuery();
            if (q != null) for (String p : q.split("&"))
                if (p.startsWith("n=")) n = Integer.parseInt(p.substring(2));
        } catch (Exception ignored) {}
        n = Math.min(n, 10000);
        StringBuilder sb = new StringBuilder("[");
        int i = 0;
        for (EventRecorder.RecordedEvent evt : EventRecorder.events) {
            if (i >= n) break;
            if (i > 0) sb.append(",");
            sb.append(evt.toJson()); i++;
        }
        sb.append("]");
        json(ex, sb.toString());
    }


    // === RECORDING WITH LAZY LISTENER ===

    private void handleRecordStart(HttpExchange ex) throws IOException {
        FrAgent.ensureListener();
        recorder.startRecording();
        json(ex, "{\"status\":\"recording\"}");
    }


    private void handleRecordStop(HttpExchange ex) throws IOException {
        java.util.List<EventRecorder.RecordedEvent> evts = recorder.stopRecording();
        java.util.List<EventRecorder.RecordedEvent> filtered = evts.stream()
            .filter(e -> !e.type.equals("MOUSE_MOVED")).collect(Collectors.toList());
        StringBuilder sb = new StringBuilder(
            "{\"status\":\"ok\",\"count\":" + filtered.size() + ",\"events\":[");
        for (int j = 0; j < filtered.size(); j++) {
            if (j > 0) sb.append(","); sb.append(filtered.get(j).toJson());
        }
        sb.append("]}");
        json(ex, sb.toString());
    }


    private void handleRecordStatus(HttpExchange ex) throws IOException {
        json(ex, "{\"recording\":" + recorder.isRecording() + "}");
    }


    private void handleReplay(HttpExchange ex) throws IOException {
        if (player == null) { json(ex, "{\"error\":\"no player\"}"); return; }
        double speed = 1.0;
        try {
            String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
            java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("\"speed\"\\s*:\\s*(\\d+\\.?\\d*)").matcher(body);
            if (m.find()) speed = Double.parseDouble(m.group(1));
        } catch (Exception ignored) {}
        java.util.List<EventRecorder.RecordedEvent> evts = recorder.stopRecording();
        String result = player.replay(evts, speed);
        json(ex, "{\"status\":\"ok\",\"result\":\"" + esc(result) +
            "\",\"count\":" + evts.size() + "}");
    }


    private void handleClick(HttpExchange ex) throws IOException {
        if (player == null) { json(ex, "{\"error\":\"no player\"}"); return; }
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        try {
            player.clickAt(Integer.parseInt(extract(body, "x")),
                          Integer.parseInt(extract(body, "y")));
            json(ex, "{\"status\":\"ok\"}");
        } catch (Exception e) { json(ex, "{\"error\":\"" + esc(e.getMessage()) + "\"}"); }
    }


    private void handleType(HttpExchange ex) throws IOException {
        if (player == null) { json(ex, "{\"error\":\"no player\"}"); return; }
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        player.typeText(extract(body, "text"));
        json(ex, "{\"status\":\"ok\"}");
    }


    private void handleShortcut(HttpExchange ex) throws IOException {
        if (player == null) { json(ex, "{\"error\":\"no player\"}"); return; }
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        player.shortcut(extract(body, "keys"));
        json(ex, "{\"status\":\"ok\"}");
    }


    private void handleTree(HttpExchange ex) throws IOException {
        final StringBuilder tree = new StringBuilder();
        try {
            java.awt.EventQueue.invokeAndWait(() ->
                tree.append(ComponentResolver.dumpComponentTree()));
            json(ex, "{\"tree\":\"" + esc(tree.toString()) + "\"}");
        } catch (Exception e) {
            json(ex, "{\"error\":\"" + esc(e.getMessage()) + "\"}");
        }
    }


    private void handleEval(HttpExchange ex) throws IOException {
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        String clsName = extract(body, "class");
        try {
            Class<?> cls = Class.forName(clsName);
            StringBuilder sb = new StringBuilder("Class: " + cls.getName() + "\nMethods:");
            for (java.lang.reflect.Method m : cls.getMethods()) {
                if (sb.length() < 5000) sb.append("\n  ").append(m.getName());
            }
            json(ex, "{\"status\":\"ok\",\"result\":\"" + esc(sb.toString()) + "\"}");
        } catch (Exception e) {
            json(ex, "{\"error\":\"" + esc(e.getMessage()) + "\"}");
        }
    }


    private void handleExec(HttpExchange ex) throws IOException {
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        String script = extract(body, "script");
        if (script.isEmpty()) {
            json(ex, "{\"error\":\"script required\"}");
            return;
        }
        try {
            javax.script.ScriptEngineManager mgr = new javax.script.ScriptEngineManager();
            javax.script.ScriptEngine engine = mgr.getEngineByName("nashorn");
            if (engine == null) {
                json(ex, "{\"error\":\"Nashorn engine not available\"}");
                return;
            }
            Object result = engine.eval(script);
            String resultStr;
            if (result == null) {
                resultStr = "null";
            } else if (result instanceof java.util.Collection) {
                java.util.Collection<?> col = (java.util.Collection<?>) result;
                StringBuilder sb = new StringBuilder("[");
                int i = 0;
                for (Object item : col) {
                    if (i++ > 0) sb.append(", ");
                    if (sb.length() < 8000) sb.append(String.valueOf(item));
                }
                sb.append("]");
                resultStr = "Collection[" + col.size() + "]: " + sb.toString();
            } else if (result instanceof String || result instanceof Number || result instanceof Boolean) {
                resultStr = String.valueOf(result);
            } else if (result.getClass().isArray()) {
                int len = java.lang.reflect.Array.getLength(result);
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < len && i < 200; i++) {
                    if (i > 0) sb.append(", ");
                    Object elem = java.lang.reflect.Array.get(result, i);
                    sb.append(elem != null ? String.valueOf(elem) : "null");
                }
                sb.append("]");
                resultStr = "Array[" + len + "]: " + sb.toString();
            } else {
                resultStr = String.valueOf(result);
            }
            json(ex, "{\"status\":\"ok\",\"type\":\"" + esc(result != null ? result.getClass().getName() : "null") + "\",\"result\":\"" + esc(resultStr) + "\"}");
        } catch (Exception e) {
            java.io.StringWriter sw = new java.io.StringWriter();
            e.printStackTrace(new java.io.PrintWriter(sw));
            json(ex, "{\"error\":\"" + esc(sw.toString()) + "\"}");
        }
    }


    private void handleShutdown(HttpExchange ex) throws IOException {
        json(ex, "{\"status\":\"shutting_down\"}");
        new Thread(() -> {
            try { Thread.sleep(200); } catch (InterruptedException ignored) {}
            shutdown();
        }).start();
    }


    private static byte[] readAllBytes(InputStream is) throws IOException {
        java.io.ByteArrayOutputStream buf = new java.io.ByteArrayOutputStream();
        byte[] data = new byte[4096];
        int n;
        while ((n = is.read(data)) != -1) buf.write(data, 0, n);
        return buf.toByteArray();
    }


    private String extract(String json, String key) {
        int ki = json.indexOf("\"" + key + "\"");
        if (ki < 0) return "";
        int vs = json.indexOf(":", ki);
        if (vs < 0) return "";
        vs++; while (vs < json.length() && json.charAt(vs) == ' ') vs++;
        if (vs < json.length() && json.charAt(vs) == '"') {
            vs++;
            int end = json.indexOf('"', vs);
            return end > vs ? json.substring(vs, end) : "";
        }
        int end = vs;
        while (end < json.length() && json.charAt(end) != ',' && json.charAt(end) != '}') end++;
        return json.substring(vs, end).trim();
    }


    private String esc(String s) {
        if (s == null) return "";
        StringBuilder sb = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == '\\') sb.append("\\\\");
            else if (ch == '"') sb.append("\\\"");
            else if (ch == '\n') sb.append("\\n");
            else if (ch == '\r') sb.append("\\r");
            else if (ch == '\t') sb.append("\\t");
            else sb.append(ch);
        }
        return sb.toString();
    }

    private void handleImport(HttpExchange ex) throws IOException {
        String body = new String(readAllBytes(ex.getRequestBody()), StandardCharsets.UTF_8);
        String xlsxPath = extract(body, "xlsx");
        String cptPath = extract(body, "cpt");
        if (xlsxPath.isEmpty() || cptPath.isEmpty()) {
            json(ex, "{\"error\":\"xlsx and cpt required\"}");
            return;
        }
        try {
            java.io.File xlsxFile = new java.io.File(xlsxPath);
            if (!xlsxFile.exists()) {
                json(ex, "{\"error\":\"file not found: \"" + esc(xlsxPath) + "\"\"");
                return;
            }
            Class<?> factoryCls = Class.forName("com.fr.io.importer.ExcelReportImporterFactory");
            java.lang.reflect.Method createMethod = factoryCls.getMethod(
                "createExcelImporter", String.class);
            Object importer = createMethod.invoke(null, xlsxPath);
            java.io.FileInputStream fis = new java.io.FileInputStream(xlsxFile);
            java.lang.reflect.Method genMethod = importer.getClass().getMethod(
                "generateWorkBookByStream", java.io.InputStream.class);
            Object wb = genMethod.invoke(importer, fis);
            fis.close();
            java.io.File cptFile = new java.io.File(cptPath);
            cptFile.getParentFile().mkdirs();
            Class<?> ioCls = Class.forName("com.fr.io.TemplateWorkBookIO");
            Class<?> wbCls = Class.forName("com.fr.main.TemplateWorkBook");
            java.lang.reflect.Method writeMethod = ioCls.getMethod(
                "writeTemplateWorkBook", wbCls, String.class);
            writeMethod.invoke(null, wb, cptPath);
            json(ex, "{\"status\":\"ok\",\"cpt\":\"" + esc(cptPath) + "\"}");
        } catch (Exception e) {
            java.io.StringWriter sw = new java.io.StringWriter();
            e.printStackTrace(new java.io.PrintWriter(sw));
            json(ex, "{\"error\":\"" + esc(sw.toString()) + "\"}");
        }
    }

}
