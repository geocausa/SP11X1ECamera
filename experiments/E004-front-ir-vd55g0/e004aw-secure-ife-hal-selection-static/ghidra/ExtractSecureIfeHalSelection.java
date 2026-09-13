// ExtractSecureIfeHalSelection.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.scalar.*;
import java.io.*;
import java.util.*;

public class ExtractSecureIfeHalSelection extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  private boolean smatch(String s){
    String x=s.toLowerCase(Locale.ROOT);
    return x.contains("hal_ife_get_hw_version") ||
           x.contains("hal_ife_lite_get_hw_version") ||
           x.contains("hw version") || x.contains("hw_version") ||
           x.contains("hardware version") ||
           x.contains("register_secure_ife") ||
           x.contains("register_secure_csid") ||
           x.contains("ife_cmd_id_config_csid_top");
  }
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing l=currentProgram.getListing();
    FunctionManager fm=currentProgram.getFunctionManager();
    ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName());
    pw.println("image_base="+currentProgram.getImageBase());
    pw.println();
    pw.println("=== MATCHED STRINGS / XREFS ===");
    DataIterator it=l.getDefinedData(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Data d=it.next(); Object v=d.getValue();
      if(!(v instanceof String)) continue;
      String s=(String)v; if(!smatch(s)) continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\r","\\r").replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); int n=0;
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+F(f));
        if(f!=null) funcs.add(f); n++;
      }
      pw.println("  REFCOUNT "+n);
    }

    pw.println(); pw.println("=== GLOBAL REFERENCES ===");
    long[] globals={0x18003d1f0L,0x18003d230L,0x18003de20L};
    for(long g:globals){
      Address a=A(g); pw.println("GLOBAL "+a);
      ReferenceIterator ri=rm.getReferencesTo(a);
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+F(f));
        if(f!=null) funcs.add(f);
      }
    }

    pw.println(); pw.println("=== IFE/CSID FUNCTION NAME INDEX ===");
    FunctionIterator fi=fm.getFunctions(true);
    while(fi.hasNext()){
      Function f=fi.next();
      String n=f.getName().toLowerCase(Locale.ROOT);
      if(n.contains("ife")||n.contains("csid")||n.contains("hal")){
        pw.println(F(f));
      }
    }

    pw.println(); pw.println("=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println(); pw.println("//// "+F(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null)
        pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close();
    println("wrote "+out+" functions="+funcs.size());
  }
}
