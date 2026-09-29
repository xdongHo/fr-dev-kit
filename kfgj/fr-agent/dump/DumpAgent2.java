import java.lang.instrument.*;
import java.io.*;

public class DumpAgent2 {
    public static void agentmain(String args, Instrumentation inst) {
        try {
            FileWriter fw = new FileWriter("C:/tmp/dump/agent2_loaded.txt");
            fw.write("DumpAgent2 loaded at " + new java.util.Date());
            fw.close();
        } catch (Exception e) {}
    }
}
