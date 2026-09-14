//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractFastRpcMmapAuthority extends GhidraScript {
  static final String[] NEEDLES = {
    "fastrpc_invoke_fd_mmap_create",
    "fastrpc_invoke_fd_mmap_get",
    "fastrpc_invoke_mmap_create",
    "fastrpc_invoke_mmap_get_cpz_phys",
    "apps_mem_dma_handle_map failed for fd",
    "map fd %d",
    "unmap fd %d"
  };
  boolean wanted(String s) {
    for (String n: NEEDLES) if (s.contains(n)) return true;
    return false;
  }
  void decomp(PrintWriter pw, DecompInterface di, Function f, String tag) {
    if (f == null) return;
    pw.println("\n//// " + tag + " " + f.getName() + " @" + f.getEntryPoint() + " ////");
    DecompileResults dr = di.decompileFunction(f, 120, monitor);
    if (dr != null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null)
      pw.println(dr.getDecompiledFunction().getC());
    else pw.println("[decompile failed] " + (dr==null?"null":dr.getErrorMessage()));
  }
  public void run() throws Exception {
    String[] a=getScriptArgs(); if(a.length<1) throw new IllegalArgumentException("output path");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager();
    LinkedHashSet<Function> roots=new LinkedHashSet<>();
    DataIterator it=l.getDefinedData(true);
    while(it.hasNext() && !monitor.isCancelled()) {
      Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)) continue;
      String s=(String)v; if(!wanted(s)) continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()) {
        Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint()));
        if(f!=null) roots.add(f);
      }
    }
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f: roots) {
      decomp(pw,di,f,"ROOT");
      for(Function c: f.getCallingFunctions(monitor)) decomp(pw,di,c,"CALLER");
      for(Function c: f.getCalledFunctions(monitor)) decomp(pw,di,c,"CALLEE");
    }
    di.dispose(); pw.close(); println("wrote "+a[0]+" roots="+roots.size());
  }
}
