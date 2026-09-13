// ExtractSurfaceAvsLiteConfig.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSurfaceAvsLiteConfig extends GhidraScript {
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  private boolean match(String s){
    String x=s.toLowerCase(Locale.ROOT);
    String[] n={
      "ife_lite_secure_mode","ife_lite_mode",
      "setdeviceconfiguration","deviceconfiginfo",
      "feature mask","featuremask","feature flag",
      "acquire ife","secureispdriver_deviceconfig",
      "secure ife","monocamera"
    };
    for(String q:n) if(x.contains(q)) return true;
    return false;
  }
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName()); pw.println("image_base="+currentProgram.getImageBase());
    pw.println("=== MATCHED STRINGS / XREFS ===");
    DataIterator it=l.getDefinedData(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)) continue;
      String s=(String)v; if(!match(s)) continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\r","\\r").replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); int n=0;
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+F(f));
        if(f!=null) funcs.add(f); n++;
      }
      pw.println("  REFCOUNT "+n);
    }
    pw.println(); pw.println("=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println(); pw.println("//// "+F(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,180,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close();
  }
}
