package fr.agent;

/**
 * 简单 JSON 序列化（不依赖第三方库）
 */
class EventSerializer {
    static String toJson(EventRecorder.RecordedEvent evt) {
        EventRecorder.ComponentInfo ci = evt.component;
        return String.format(
            "{\"type\":\"%s\",\"ts\":%d,\"comp\":{\"cls\":\"%s\",\"path\":\"%s\",\"fr\":\"%s\"}," +
            "\"lx\":%d,\"ly\":%d,\"sx\":%d,\"sy\":%d,\"btn\":%d,\"mod\":%d,\"detail\":\"%s\"}",
            esc(evt.type), evt.timestamp, esc(ci.className), esc(ci.path), esc(ci.frApiClass),
            evt.localX, evt.localY, evt.screenX, evt.screenY,
            evt.button, evt.modifiers, esc(evt.detail)
        );
    }
    
    static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
    }
}
