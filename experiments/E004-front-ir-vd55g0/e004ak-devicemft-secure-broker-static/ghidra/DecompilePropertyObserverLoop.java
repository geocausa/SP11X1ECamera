// DecompilePropertyObserverLoop.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;

public class DecompilePropertyObserverLoop extends GhidraScript {
    private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
    public void run() throws Exception {
        String out=getScriptArgs()[0];
        PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
        long[] addrs={0x180047cd0L,0x180047d40L,0x180309760L,0x180309880L,0x180302d20L,0x180302f40L};
        DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
        Listing l=currentProgram.getListing();
        for(long a:addrs){
            Function f=l.getFunctionAt(A(a));
            pw.println("\n//// "+(f==null?"<none>":f.getName())+" @"+A(a)+" ////");
            if(f!=null){
                DecompileResults dr=di.decompileFunction(f,90,monitor);
                if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
                else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
            }
        }
        di.dispose(); pw.close(); println("wrote "+out);
    }
}
