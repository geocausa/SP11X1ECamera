// ExtractSecureModeCallers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureModeCallers extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[0]),"UTF-8"));
        long[] vas={0x14001ebb0L,0x140083120L,0x140083040L,0x140009b18L};
        FunctionManager fm=currentProgram.getFunctionManager();
        ReferenceManager rm=currentProgram.getReferenceManager();
        LinkedHashSet<Function> funcs=new LinkedHashSet<>();
        for(long va:vas){
            Address a=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(va);
            Function target=fm.getFunctionAt(a);
            pw.println("TARGET "+a+" "+(target==null?"<none>":target.getName()));
            ReferenceIterator it=rm.getReferencesTo(a);
            while(it.hasNext()){
                Reference ref=it.next();
                Function caller=fm.getFunctionContaining(ref.getFromAddress());
                pw.println("  REF "+ref.getFromAddress()+" type="+ref.getReferenceType()+
                    (caller==null?"":" caller="+caller.getName()+" entry="+caller.getEntryPoint()));
                if(caller!=null) funcs.add(caller);
            }
            if(target!=null) funcs.add(target);
        }
        pw.println("\n=== DECOMPILATIONS ===");
        DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
        for(Function f:funcs){
            pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
            DecompileResults dr=di.decompileFunction(f,60,monitor);
            if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
            else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
        }
        di.dispose(); pw.close();
        println("wrote "+args[0]+" funcs="+funcs.size());
    }
}