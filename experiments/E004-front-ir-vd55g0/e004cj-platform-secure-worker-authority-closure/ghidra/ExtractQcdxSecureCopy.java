// ExtractQcdxSecureCopy.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*; import java.util.*;
public class ExtractQcdxSecureCopy extends GhidraScript {
 boolean hit(String s){String x=s.toLowerCase(Locale.ROOT); String[] q={"cryptosendcopycmdsecureapp","cryptocopydata","cryptononsecurecopydata","playrdy","playready","securecopy","treememshare","treepassthrough","treewinsecapp","cryptostartsecureapp"}; for(String n:q) if(x.contains(n))return true; return false;}
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> roots=new LinkedHashSet<>();
  DataIterator it=l.getDefinedData(true); while(it.hasNext()){Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String)||!hit((String)v))continue; p.println("STRING @"+d.getAddress()+" = "+((String)v).replace("\n","\\n")); ReferenceIterator ri=rm.getReferencesTo(d.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); p.println(" XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f);}}
  LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCalledFunctions(monitor)); all.addAll(f.getCallingFunctions(monitor));}
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); p.println("\n=== DECOMP ==="); for(Function f:all){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("FAIL");} di.dispose(); p.close(); println("roots="+roots.size()+" all="+all.size()); }
}
