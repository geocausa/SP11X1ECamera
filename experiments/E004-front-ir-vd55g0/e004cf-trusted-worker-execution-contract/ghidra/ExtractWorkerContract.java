// ExtractWorkerContract.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.io.*; import java.util.*;

public class ExtractWorkerContract extends GhidraScript {
  private PrintWriter pw;
  private FunctionManager fm;
  private DecompInterface di;
  private final String[] seeds = {
    "1800033d8","180003478","180003718","1800037c8","180019828",
    "180028600","1800290a0","180008540","180008600"
  };
  private void printCallees(Function f) {
    Set<Function> cs=f.getCalledFunctions(monitor);
    ArrayList<Function> list=new ArrayList<>(cs);
    list.sort(Comparator.comparing(x -> x.getEntryPoint().toString()));
    for(Function c:list) {
      pw.print("  CALLEE "+c.getName()+" @"+c.getEntryPoint());
      if(c.isExternal()) {
        ExternalLocation el=currentProgram.getExternalManager().getExternalLocation(c.getSymbol());
        pw.print(" external=true");
        if(el!=null) pw.print(" library="+el.getLibraryName()+" label="+el.getLabel());
      }
      pw.println();
    }
  }
  private void dump(Function f) {
    pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" external="+f.isExternal()+" ////");
    printCallees(f);
    if(!f.isExternal()) {
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
  }
  public void run() throws Exception {
    String[] args=getScriptArgs(); if(args.length<1) throw new IllegalArgumentException("output path");
    pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[0]),"UTF-8")); fm=currentProgram.getFunctionManager(); di=new DecompInterface(); di.openProgram(currentProgram);
    pw.println("program="+currentProgram.getName()); pw.println("image_base="+currentProgram.getImageBase());
    LinkedHashSet<Function> roots=new LinkedHashSet<>();
    for(String s:seeds){Address a=toAddr(s); Function f=fm.getFunctionAt(a); if(f==null)f=fm.getFunctionContaining(a); pw.println("SEED "+s+" -> "+(f==null?"NOT_FOUND":f.getName()+" @"+f.getEntryPoint())); if(f!=null)roots.add(f);}
    pw.println("\n=== SEED DECOMPILATIONS / DIRECT CALLEES ==="); for(Function f:roots)dump(f);
    pw.println("\n=== DEPTH-3 REACHABLE FROM TRANSFER DISPATCHER ===");
    Function start=fm.getFunctionAt(toAddr("1800037c8"));
    LinkedHashMap<Function,Integer> seen=new LinkedHashMap<>(); ArrayDeque<Function> q=new ArrayDeque<>(); ArrayDeque<Integer> d=new ArrayDeque<>(); q.add(start); d.add(0);
    while(!q.isEmpty()){Function f=q.remove(); int dep=d.remove(); if(seen.containsKey(f))continue; seen.put(f,dep); pw.println("DEPTH "+dep+" "+f.getName()+" @"+f.getEntryPoint()+" external="+f.isExternal()); if(dep>=3||f.isExternal())continue; for(Function c:f.getCalledFunctions(monitor)){q.add(c);d.add(dep+1);}}
    pw.println("\n=== REACHABLE EXTERNAL IMPORTS DEPTH<=3 ===");
    for(Map.Entry<Function,Integer> e:seen.entrySet()){Function f=e.getKey(); if(!f.isExternal())continue; ExternalLocation el=currentProgram.getExternalManager().getExternalLocation(f.getSymbol()); pw.print("DEPTH "+e.getValue()+" "+f.getName()); if(el!=null)pw.print(" library="+el.getLibraryName()+" label="+el.getLabel()); pw.println();}
    di.dispose(); pw.close(); println("wrote "+args[0]+" roots="+roots.size()+" reachable="+seen.size());
  }
}
