// ExtractQcSkHypPolicy.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*; import java.util.*;
public class ExtractQcSkHypPolicy extends GhidraScript {
 boolean hit(String s){String x=s.toLowerCase(Locale.ROOT); return x.contains("assignment to hyp domain cannot be shared") || x.contains("assignment to ac_vm_hyp successful") || x.contains("unsupported assign to hyp vm") || x.contains("hyp assignment cannot be made") || x.contains("failure closing handle for memory mapped to hyp vm") || x.contains("hyp_assign is being performed");}
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>();
  DataIterator it=l.getDefinedData(true); while(it.hasNext()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)||!hit((String)v))continue; p.println("STRING @"+d.getAddress()+" = "+((String)v).replace("\n","\\n")); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); p.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f);}}
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); for(Function f:roots){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////"); DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted())p.println(dr.getDecompiledFunction().getC()); else p.println("FAIL");} di.dispose(); p.close(); println("roots="+roots.size()); }
}
