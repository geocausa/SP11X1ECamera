//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*; import java.util.*;
public class ExtractDeviceMftStreamer extends GhidraScript {
 boolean match(String s){String x=s.toLowerCase(Locale.ROOT); return x.contains("libdsp_streamer_skel.so")||x.contains("s_hfastrpchandle")||x.contains("remote_handle64_open")||x.contains("remote_handle64_invoke");}
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>(); DataIterator it=l.getDefinedData(true); while(it.hasNext()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)||!match((String)v))continue; p.println("STRING @"+d.getAddress()+" = "+v); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference rr=ri.next(); Function f=fm.getFunctionContaining(rr.getFromAddress()); p.println(" XREF "+rr.getFromAddress()+" function="+(f==null?"":f.getName())+" entry="+(f==null?"":f.getEntryPoint())); if(f!=null)roots.add(f);}}
 LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCalledFunctions(monitor)); all.addAll(f.getCallingFunctions(monitor)); for(Function c:f.getCallingFunctions(monitor))all.addAll(c.getCallingFunctions(monitor));}
 DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); p.println("\n=== ROOTS ==="); for(Function f:roots)p.println(f.getName()+" @"+f.getEntryPoint()); for(Function f:all){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("[decompile failed]");} di.dispose(); p.close(); }
}
