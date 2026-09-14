// ExtractXhciSecureSection.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.io.*; import java.util.*;
public class ExtractXhciSecureSection extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0]));
  SymbolTable st=currentProgram.getSymbolTable(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager();
  String[] names={"CreateSecureSection","OpenSecureSection","GetExposedSecureSection","MapSecureIo","ProtectSecureIo","MapViewOfFile","UnmapSecureIo","UnmapViewOfFile"};
  LinkedHashSet<Function> roots=new LinkedHashSet<>();
  for(String n:names){p.println("=== IMPORT "+n+" ==="); SymbolIterator si=st.getSymbols(n); while(si.hasNext()){Symbol s=si.next(); p.println("SYMBOL "+s.getName()+" @"+s.getAddress()); ReferenceIterator ri=rm.getReferencesTo(s.getAddress()); while(ri.hasNext()){Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); p.println(" XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f);}}}
  LinkedHashSet<Function> all=new LinkedHashSet<>(roots); for(Function f:roots){all.addAll(f.getCalledFunctions(monitor));}
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
  p.println("\n=== DECOMPILATIONS ===");
  for(Function f:all){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" root="+roots.contains(f)+" ////"); DecompileResults dr=di.decompileFunction(f,90,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("[decompile failed]");}
  di.dispose(); p.close(); println("roots="+roots.size()+" all="+all.size());
 }
}
