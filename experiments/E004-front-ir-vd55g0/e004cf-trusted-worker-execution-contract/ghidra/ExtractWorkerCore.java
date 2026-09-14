// ExtractWorkerCore.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.io.*; import java.util.*;
public class ExtractWorkerCore extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
  FunctionManager fm=currentProgram.getFunctionManager(); DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
  Function start=fm.getFunctionAt(toAddr("18001a138"));
  LinkedHashMap<Function,Integer> seen=new LinkedHashMap<>(); ArrayDeque<Function> q=new ArrayDeque<>(); ArrayDeque<Integer> dq=new ArrayDeque<>(); q.add(start);dq.add(0);
  while(!q.isEmpty()){Function f=q.remove();int d=dq.remove();if(seen.containsKey(f))continue;seen.put(f,d);p.println("\n//// DEPTH "+d+" "+f.getName()+" @"+f.getEntryPoint()+" external="+f.isExternal()+" ////");
   if(f.isExternal()){ExternalLocation el=currentProgram.getExternalManager().getExternalLocation(f.getSymbol()); if(el!=null)p.println("EXTERNAL library="+el.getLibraryName()+" label="+el.getLabel()); continue;}
   DecompileResults dr=di.decompileFunction(f,120,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("[decompile failed]");
   ArrayList<Function> cs=new ArrayList<>(f.getCalledFunctions(monitor)); cs.sort(Comparator.comparing(x->x.getEntryPoint().toString()));
   p.println("DIRECT_CALLEES_BEGIN"); for(Function c:cs){p.println("CALLEE "+c.getName()+" @"+c.getEntryPoint()+" external="+c.isExternal()); if(d<5){q.add(c);dq.add(d+1);}} p.println("DIRECT_CALLEES_END");
  }
  p.println("\n=== EXTERNALS ==="); for(Map.Entry<Function,Integer> e:seen.entrySet()) if(e.getKey().isExternal()){ExternalLocation el=currentProgram.getExternalManager().getExternalLocation(e.getKey().getSymbol());p.print("DEPTH "+e.getValue()+" "+e.getKey().getName());if(el!=null)p.print(" library="+el.getLibraryName()+" label="+el.getLabel());p.println();}
  di.dispose();p.close();println("wrote "+a[0]+" reachable="+seen.size());
 }
}
