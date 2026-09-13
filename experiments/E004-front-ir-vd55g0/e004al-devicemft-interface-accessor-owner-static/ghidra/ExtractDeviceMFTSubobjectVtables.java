// ExtractDeviceMFTSubobjectVtables.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractDeviceMFTSubobjectVtables extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  private String fn(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager();
    long[] targets={0x181330900L,0x181330940L,0x181330980L,0x1813309c0L,0x181330a00L};
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    for(long t:targets){
      Address a=A(t); pw.println("TARGET "+a);
      ReferenceIterator ri=rm.getReferencesTo(a);
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=l.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" caller="+fn(f));
        if(f!=null)funcs.add(f);
      }
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println("\n//// "+fn(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed]");
    }
    di.dispose(); pw.close(); println("wrote "+out+" funcs="+funcs.size());
  }
}
