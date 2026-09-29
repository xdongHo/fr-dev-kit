package fr.agent;

import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.Executors;

/** Standalone /exec server — binds to port 19000, provides Nashorn script execution. */
public class ExecServer {
    private static HttpServer server;

    public static void start(int port) throws IOException {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        server.createContext("/exec", ExecServer::handleExec);
        server.createContext("/ping", Ex -> {
            byte[] b = "{\"status\":\"ok\"}".getBytes(StandardCharsets.UTF_8);
            Ex.sendResponseHeaders(200, b.length);
            Ex.getResponseBody().write(b);
        });
        server.setExecutor(Executors.newSingleThreadExecutor());
        server.start();
    }

    public static void stop() { if (server != null) { server.stop(0); server = null; } }

    private static void handleExec(HttpExchange ex) throws IOException {
        String body = new String(readAll(ex.getRequestBody()), StandardCharsets.UTF_8);
        String script = extract(body, "script");
        if (script.isEmpty()) { json(ex, "{\"error\":\"script required\"}"); return; }
        try {
            javax.script.ScriptEngineManager mgr = new javax.script.ScriptEngineManager();
            javax.script.ScriptEngine engine = mgr.getEngineByName("nashorn");
            if (engine == null) { json(ex, "{\"error\":\"Nashorn not available\"}"); return; }
            Object result = engine.eval(script);
            String s = serialize(result);
            json(ex, "{\"status\":\"ok\",\"type\":\"" + esc(result != null ? result.getClass().getName() : "null") + "\",\"result\":\"" + esc(s) + "\"}");
        } catch (Exception e) {
            StringWriter sw = new StringWriter();
            e.printStackTrace(new PrintWriter(sw));
            json(ex, "{\"error\":\"" + esc(sw.toString()) + "\"}");
        }
    }

    private static String serialize(Object o) {
        if (o == null) return "null";
        if (o instanceof String || o instanceof Number || o instanceof Boolean) return String.valueOf(o);
        if (o instanceof Collection) {
            Collection<?> c = (Collection<?>) o;
            StringBuilder sb = new StringBuilder("Collection[" + c.size() + "]: [");
            int i = 0;
            for (Object item : c) {
                if (i++ > 0) sb.append(", ");
                if (sb.length() < 8000) sb.append(String.valueOf(item));
            }
            sb.append("]"); return sb.toString();
        }
        if (o.getClass().isArray()) {
            int len = java.lang.reflect.Array.getLength(o);
            StringBuilder sb = new StringBuilder("[" + len + "]: [");
            for (int i = 0; i < len && i < 200; i++) {
                if (i > 0) sb.append(", ");
                Object e = java.lang.reflect.Array.get(o, i);
                sb.append(e != null ? String.valueOf(e) : "null");
            }
            sb.append("]"); return sb.toString();
        }
        return String.valueOf(o);
    }

    private static void json(HttpExchange ex, String s) throws IOException {
        byte[] b = s.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(200, b.length);
        ex.getResponseBody().write(b);
    }

    private static byte[] readAll(InputStream is) throws IOException {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        byte[] d = new byte[4096]; int n;
        while ((n = is.read(d)) != -1) buf.write(d, 0, n);
        return buf.toByteArray();
    }

    private static String extract(String json, String key) {
        int ki = json.indexOf("\"" + key + "\"");
        if (ki < 0) return "";
        int vs = json.indexOf(":", ki); if (vs < 0) return "";
        vs++; while (vs < json.length() && json.charAt(vs) == ' ') vs++;
        if (vs < json.length() && json.charAt(vs) == '"') {
            vs++;
            StringBuilder sb = new StringBuilder();
            while (vs < json.length()) {
                char ch = json.charAt(vs);
                if (ch == '\\' && vs + 1 < json.length()) {
                    char next = json.charAt(vs + 1);
                    if (next == '"' || next == '\\' || next == '/' || next == 'n' || next == 'r' || next == 't') {
                        if (next == '"' || next == '\\' || next == '/') sb.append(next);
                        else if (next == 'n') sb.append('\n');
                        else if (next == 'r') sb.append('\r');
                        else if (next == 't') sb.append('\t');
                        vs += 2; continue;
                    }
                }
                if (ch == '"') break;
                sb.append(ch); vs++;
            }
            return sb.toString();
        }
        int end = vs;
        while (end < json.length() && json.charAt(end) != ',' && json.charAt(end) != '}') end++;
        return json.substring(vs, end).trim();
    }

    private static String esc(String s) {
        if (s == null) return "";
        StringBuilder sb = new StringBuilder(s.length());
        for (char ch : s.toCharArray()) {
            if (ch == '\\') sb.append("\\\\");
            else if (ch == '"') sb.append("\\\"");
            else if (ch == '\n') sb.append("\\n");
            else if (ch == '\r') sb.append("\\r");
            else if (ch == '\t') sb.append("\\t");
            else sb.append(ch);
        }
        return sb.toString();
    }
}
