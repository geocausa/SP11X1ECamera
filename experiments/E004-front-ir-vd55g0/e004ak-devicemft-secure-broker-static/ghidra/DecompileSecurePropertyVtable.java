// DecompileSecurePropertyVtable.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;

public class DecompileSecurePropertyVtable extends GhidraScript {
    private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
    public void run() throws Exception {
        String out=getScriptArgs()[0];
        PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
        long[] addrs={
            0x180046fd0L, // vtable +0x30
            0x180047690L, // vtable +0x50
            0x180047b60L, // vtable +0x58
            0x180047c60L, // vtable +0x60
            0x180043f60L, // SecureMode SetProperty
            0x180043ce0L  // SecureMode GetProperty
        };
        DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
        Listing l=currentProgram.getListing();
        for(long a:addrs){
            Function f=l.getFunctionAt(A(a));
            pw.println("\n//// "+(f==null?"<none>":f.getName())+" @"+A(a)+" ////");
            if(f!=null){
                DecompileResults dr=di.decompileFunction(f,90,monitor);
                if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
                else pw.println("[decompile failed]");
            }
        }
        di.dispose();pw.close();
        println("wrote "+out);
    }
}
