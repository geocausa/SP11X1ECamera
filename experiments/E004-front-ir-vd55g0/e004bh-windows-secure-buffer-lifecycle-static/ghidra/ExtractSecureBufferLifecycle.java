// ExtractSecureBufferLifecycle.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureBufferLifecycle extends GhidraScript {
  private Address A(long v) {
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);
  }
  private String F(Function f) {
    return f == null ? "<none>" : f.getName()+"@"+f.getEntryPoint();
  }
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    long[] targets={0x180004828L,0x180004c58L,0x180005430L};
    FunctionManager fm=currentProgram.getFunctionManager();
    ReferenceManager rm=currentProgram.getReferenceManager();
    DecompInterface di=new DecompInterface();
    di.openProgram(currentProgram);
    Set<Address> callers=new LinkedHashSet<>();
    for(long x:targets) {
      Address a=A(x);
      Function f=fm.getFunctionAt(a);
      pw.println("TARGET "+a+" "+F(f));
      ReferenceIterator ri=rm.getReferencesTo(a);
      while(ri.hasNext()) {
        Reference ref=ri.next();
        Function cf=fm.getFunctionContaining(ref.getFromAddress());
        pw.println("  REF "+ref.getFromAddress()+" "+ref.getReferenceType()+" caller="+F(cf));
        if(cf!=null) callers.add(cf.getEntryPoint());
      }
      pw.println();
    }
    for(Address ca:callers) {
      Function f=fm.getFunctionAt(ca);
      pw.println("//// CALLER "+F(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,180,monitor);
      if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null)
        pw.println(dr.getDecompiledFunction().getC());
      pw.println();
    }
    di.dispose();
    pw.close();
  }
}
