// ExtractQheeSmmuCamera.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*; import java.util.*;
public class ExtractQheeSmmuCamera extends GhidraScript {
 boolean match(String s){String x=s.toLowerCase(Locale.ROOT); String[] q={"acsmmumapandupdatelistext","acsmmuunmapandupdatelistext","acsmmutzassignext","smmusecuremodeswitch","cpz_camera_validate","camera preview","iommu programming","smmu_paravirtualization_syscall"}; for(String n:q)if(x.contains(n))return true; return false;}
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>(); DataIterator it=l.getDefinedData(true); while(it.hasNext()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String))continue; String s=(String)v; if(!match(s))continue; p.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n")); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); p.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f);}}
 LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCalledFunctions(monitor)); all.addAll(f.getCallingFunctions(monitor));}
 DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); p.println("\n=== ROOTS ==="); for(Function f:roots)p.println(f.getName()+" @"+f.getEntryPoint()); for(Function f:all){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());} di.dispose(); p.close(); println("roots="+roots.size()+" all="+all.size());}
}
