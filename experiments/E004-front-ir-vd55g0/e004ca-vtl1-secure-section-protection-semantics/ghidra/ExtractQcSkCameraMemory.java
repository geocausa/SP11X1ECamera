// ExtractQcSkCameraMemory.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import ghidra.program.model.address.*;
import java.io.*; import java.util.*;
public class ExtractQcSkCameraMemory extends GhidraScript {
  boolean match(String s){String x=s.toLowerCase(Locale.ROOT); String[] q={"qcskassignmemorytosocdomain","pil_camera_mem_assign","camera_set_state","mapping vmid","assignmemorytosocdomain","create securesectionspecifypages","createsecuresectionspecifypages","hlos_unmapped","cp_camera","assignment to domains","assignmem"}; for(String n:q) if(x.contains(n)) return true; return false;}
  public void run() throws Exception {
    String[] a=getScriptArgs(); PrintWriter pw=new PrintWriter(new FileOutputStream(a[0]));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName()); pw.println("image_base="+currentProgram.getImageBase());
    DataIterator it=l.getDefinedData(true); while(it.hasNext()&&!monitor.isCancelled()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String))continue; String s=(String)v; if(!match(s))continue; pw.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n")); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); pw.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f);}}
    LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCalledFunctions(monitor)); all.addAll(f.getCallingFunctions(monitor));}
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); pw.println("\n=== ROOTS ==="); for(Function f:roots)pw.println(f.getName()+" @"+f.getEntryPoint());
    for(Function f:all){pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC()); else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));}
    di.dispose(); pw.close(); println("wrote "+a[0]+" roots="+roots.size()+" total="+all.size());
  }
}
