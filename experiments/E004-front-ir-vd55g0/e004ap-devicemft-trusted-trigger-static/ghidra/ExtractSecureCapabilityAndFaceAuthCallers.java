// ExtractSecureCapabilityAndFaceAuthCallers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureCapabilityAndFaceAuthCallers extends GhidraScript {
  private Address A(long v){ return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v); }
  private String F(Function f){ return f==null?"<none>":f.getName()+"@"+f.getEntryPoint(); }
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    long[] ts={
      0x18018c890L,0x1800c5ba0L,0x1800f7858L,
      0x180291c00L,0x180295050L,
      0x18029a900L,0x180301f80L,
      0x1800407d0L,0x180040aa0L,
      0x180309460L,0x1802f7458L,
      0x180293ad8L
    };
    pw.println("program="+currentProgram.getName());
    pw.println("image_base="+currentProgram.getImageBase());
    pw.println("=== TARGET REFERENCES ===");
    for(long t:ts){
      Address a=A(t); Function f=l.getFunctionAt(a); pw.println("TARGET "+a+" "+F(f)); if(f!=null) funcs.add(f);
      ReferenceIterator it=rm.getReferencesTo(a); int n=0;
      while(it.hasNext()){
        Reference r=it.next(); Function c=l.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" caller="+F(c));
        if(c!=null) funcs.add(c); n++;
      }
      pw.println("  REFCOUNT "+n);
    }
    pw.println(); pw.println("=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println(); pw.println("//// "+F(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close(); println("wrote "+out+" funcs="+funcs.size());
  }
}
