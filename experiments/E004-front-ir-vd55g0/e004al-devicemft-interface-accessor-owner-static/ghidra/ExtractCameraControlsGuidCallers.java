// ExtractCameraControlsGuidCallers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractCameraControlsGuidCallers extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  private String fn(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing listing=currentProgram.getListing();
    ReferenceManager rm=currentProgram.getReferenceManager();
    long[] targets={
      0x1813552e0L, // private CameraControls interface GUID
      0x180051860L, // CInterfaceAccessor::GetInterface
      0x180050d40L, // SetCameraControls
      0x180051830L, // CameraControls getter (+0xb8)
      0x180021cf0L, // CreateCameraControls
      0x18002d0d0L  // CCameraControls::KsProperty
    };
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName());
    pw.println("=== REFERENCES ===");
    for(long t:targets){
      Address a=A(t); Function f=listing.getFunctionAt(a);
      pw.println("TARGET "+a+" "+fn(f));
      ReferenceIterator ri=rm.getReferencesTo(a);
      int n=0;
      while(ri.hasNext()){
        Reference r=ri.next();
        Function c=listing.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" caller="+fn(c));
        if(c!=null)funcs.add(c); n++;
      }
      pw.println("  REFCOUNT "+n);
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,90,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed]");
    }
    di.dispose();pw.close();println("wrote "+out+" funcs="+funcs.size());
  }
}
