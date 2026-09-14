//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import ghidra.program.model.address.*;
import java.io.*; import java.util.*;
public class ExtractProtectedCdspCallers extends GhidraScript {
 public void run() throws Exception { String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>();
  DataIterator it=l.getDefinedData(true); while(it.hasNext()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String))continue; String s=(String)v; String x=s.toLowerCase(Locale.ROOT); if(!(x.contains("mfmediatype_protected")||x.contains("protected=%s")||x.contains("remote_register_dma_handle")||x.contains("remote_register_buf_attr")||x.contains("libbitml_nsp")||x.contains("libdsp_streamer")))continue; p.println("STRING @"+d.getAddress()+" = "+s); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference rr=ri.next(); Function f=fm.getFunctionContaining(rr.getFromAddress()); p.println(" XREF "+rr.getFromAddress()+" function="+(f==null?"":f.getName())+" entry="+(f==null?"":f.getEntryPoint())); if(f!=null)roots.add(f);}}
  String[] imports={"remote_register_dma_handle","remote_register_dma_handle_attr","remote_register_buf_attr","remote_register_buf_attr2","remote_handle64_invoke","remote_handle64_open"}; for(String n:imports){ List<Function> fs=getGlobalFunctions(n); for(Function f:fs){p.println("IMPORT "+n+" @"+f.getEntryPoint()); ReferenceIterator ri=rm.getReferencesTo(f.getEntryPoint()); while(ri.hasNext()){Reference rr=ri.next(); Function c=fm.getFunctionContaining(rr.getFromAddress()); p.println(" CALLXREF "+rr.getFromAddress()+" caller="+(c==null?"":c.getName())+" entry="+(c==null?"":c.getEntryPoint())); if(c!=null)roots.add(c);}}}
  LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCallingFunctions(monitor)); all.addAll(f.getCalledFunctions(monitor));}
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); p.println("\n=== ROOTS ==="); for(Function f:roots)p.println(f.getName()+" @"+f.getEntryPoint()); for(Function f:all){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());} di.dispose(); p.close(); }
}
