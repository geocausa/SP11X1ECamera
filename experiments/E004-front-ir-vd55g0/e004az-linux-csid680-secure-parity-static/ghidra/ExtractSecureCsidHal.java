// ExtractSecureCsidHal.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;

public class ExtractSecureCsidHal extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
    long[] t={
      0x1800119e0L,0x180011a10L,0x180011cf0L,0x180011d40L,
      0x180012a80L,0x180012ce0L,0x180012ea0L,0x180012f00L,0x180012f20L,
      0x1800133c0L,0x1800134f0L,0x180013bf0L,0x180013dc0L,0x180013f40L,0x180013f90L
    };
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(long x:t){
      Address a=A(x); Function f=fm.getFunctionAt(a);
      pw.println("TARGET "+a+" "+F(f));
      ReferenceIterator it=rm.getReferencesTo(a);
      while(it.hasNext()){Reference r=it.next();pw.println("  REF "+r.getFromAddress()+" "+r.getReferenceType()+" caller="+F(fm.getFunctionContaining(r.getFromAddress())));}
      if(f!=null){
        pw.println("//// "+F(f)+" ////");
        DecompileResults dr=di.decompileFunction(f,120,monitor);
        if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
        else pw.println("[decompile failed]");
      }
      pw.println();
    }
    di.dispose(); pw.close();
  }
}
