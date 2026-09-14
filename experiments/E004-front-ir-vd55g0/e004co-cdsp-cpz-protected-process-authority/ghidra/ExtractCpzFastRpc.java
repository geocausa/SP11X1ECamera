//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractCpzFastRpc extends GhidraScript {
  private boolean match(String s) {
    String x=s.toLowerCase(Locale.ROOT);
    String[] ns={"cpz","secure_process","secure process","qurtos_secure_proc_v2","fastrpc_invoke_mmap_get_cpz_phys","fastrpc_invoke_process_create","fastrpc_invoke_process_destroy","signed","secure_root"};
    for(String n:ns) if(x.contains(n)) return true;
    return false;
  }
  public void run() throws Exception {
    String[] a=getScriptArgs(); if(a.length<1) throw new IllegalArgumentException("output path required");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager();
    LinkedHashSet<Function> roots=new LinkedHashSet<>();
    DataIterator it=l.getDefinedData(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)) continue; String s=(String)v; if(!match(s)) continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()) { Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); pw.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null) roots.add(f); }
    }
    LinkedHashSet<Function> all=new LinkedHashSet<>(roots);
    for(Function f:new ArrayList<>(roots)) {
      Set<Function> c=f.getCalledFunctions(monitor); all.addAll(c);
    }
    pw.println("\n=== ROOTS ==="); for(Function f:roots) pw.println(f.getName()+" @"+f.getEntryPoint());
    pw.println("\n=== ROOT + 1-HOP DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:all){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,90,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC()); else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close(); println("wrote "+a[0]+" roots="+roots.size()+" total="+all.size());
  }
}
