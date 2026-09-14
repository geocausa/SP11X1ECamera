// ExtractSocDomain.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*; import java.util.*;
public class ExtractSocDomain extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0]));
  SymbolTable st=currentProgram.getSymbolTable(); FunctionManager fm=currentProgram.getFunctionManager();
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
  ArrayList<Function> funcs=new ArrayList<>();
  SymbolIterator it=st.getAllSymbols(true);
  while(it.hasNext()){Symbol s=it.next(); String n=s.getName(); String l=n.toLowerCase(Locale.ROOT); if(l.contains("socdomain")||l.contains("assignmemoryto")||l.contains("soc_domain")){Function f=fm.getFunctionAt(s.getAddress()); if(f!=null && !funcs.contains(f)){funcs.add(f); p.println("SYMBOL "+n+" @"+s.getAddress()+" sig="+f.getSignature());}}}
  p.println("\n=== DECOMPILATIONS ===");
  for(Function f:funcs){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////"); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("[FAIL] "+(dr==null?"null":dr.getErrorMessage()));}
  di.dispose(); p.close(); println("wrote "+a[0]+" funcs="+funcs.size());
 }
}
