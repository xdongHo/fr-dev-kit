import com.sun.tools.attach.VirtualMachine;

/**
 * Dynamic JVM agent attacher — used by designer.bat to inject fr-agent.jar
 * into a running FR Designer JVM at startup.
 *
 * Compile: javac -cp %FR_HOME%\lib\tools.jar AttachAgent.java
 * Run:     java -cp .;%FR_HOME%\lib\tools.jar AttachAgent <PID> <agent.jar>
 */
public class AttachAgent {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: AttachAgent <PID> <agent.jar>");
            System.exit(1);
        }
        String pid = args[0];
        String jar = args[1];
        String extraArgs = args.length > 2 ? args[2] : "";

        System.out.println("Attaching to PID=" + pid + " ...");
        VirtualMachine vm = VirtualMachine.attach(pid);
        vm.loadAgent(jar, extraArgs);
        vm.detach();
        System.out.println("OK");
    }
}
