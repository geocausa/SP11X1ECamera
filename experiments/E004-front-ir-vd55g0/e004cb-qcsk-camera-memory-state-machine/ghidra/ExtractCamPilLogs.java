// ExtractCamPilLogs.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.app.decompiler.*; import ghidra.program.model.listing.*; import ghidra.program.model.symbol.*; import ghidra.program.model.data.*; import java.io.*; import java.util.*;
public class ExtractCamPilLogs extends GhidraScript {
 public void run() throws Exception { String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> fs=new LinkedHashSet<>();
 DataIterator it=l.getDefinedData(true); while(it.hasNext()&&!monitor.isCancelled()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String))continue; String s=(String)v; String x=s.toLowerCase(Locale.ROOT); if(!(x.contains("cam-pil")||x.contains("pil_camera_mem_assign")||x.contains("camera_set_state")))continue; p.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n")); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); p.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)fs.add(f);}}
 DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); for(Function f:fs){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////"); DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());}
 di.dispose(); p.close(); }
}
