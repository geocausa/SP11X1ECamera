// DecompileIfeDispatch.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
public class DecompileIfeDispatch extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    long[] t={0x180016470L,0x1800170c0L,0x180016430L,0x18000f610L,0x18000d000L,0x18000bbf0L};
    FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(long x:t){
      Address a=A(x); Function f=fm.getFunctionAt(a);
      pw.println("TARGET "+a+" "+F(f));
      ReferenceIterator ri=rm.getReferencesTo(a);
      while(ri.hasNext()){
        Reference r=ri.next(); pw.println("  REF "+r.getFromAddress()+" "+r.getReferenceType()+" caller="+F(fm.getFunctionContaining(r.getFromAddress())));
      }
      if(f!=null){
        DecompileResults dr=di.decompileFunction(f,120,monitor);
        pw.println("//// "+F(f)+" ////");
        if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      }
      pw.println();
    }
    di.dispose(); pw.close();
  }
}
