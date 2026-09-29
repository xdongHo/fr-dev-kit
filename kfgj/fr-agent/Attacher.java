import com.sun.tools.attach.VirtualMachine;
public class Attacher {
    public static void main(String[] args) throws Exception {
        VirtualMachine vm = VirtualMachine.attach(args[0]);
        vm.loadAgent(args[1]);
        vm.detach();
        System.out.println("Agent attached to PID " + args[0]);
    }
}