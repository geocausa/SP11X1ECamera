//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractStaticHashAuthority extends GhidraScript {
  static final String[] NEEDLES={"/statichashes/%s","module: Static hash found","num_segments","error: dynamic module is unsigned","oemconfig.so","SigVerify_get_lib_hash","/statichashes/example_image.so","/statichashes/example_image_runner.so","/statichashes/libloadalgo_skel.so"};
  boolean wanted(String s){ for(String n:NEEDLES) if(s.contains(n)) return true; return false; }
  void decomp(PrintWriter pw,DecompInterface di,Function f,String tag){
    if(f==null)return; pw.println("\n//// "+tag+" "+f.getName()+" @"+f.getEntryPoint()+" ////");
    DecompileResults dr=di.decompileFunction(f,120,monitor);
    if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
    else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
  }
  public void run() throws Exception{
    String[] a=getScriptArgs(); if(a.length<1)throw new IllegalArgumentException("output");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager();
    LinkedHashSet<Function> roots=new LinkedHashSet<>();
    DataIterator it=l.getDefinedData(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Data d=it.next(); Object v=d.getValue(); if(!(v instanceof String))continue; String s=(String)v; if(!wanted(s))continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()){ Reference r=ri.next(); Function f=fm.getFunctionContaining(r.getFromAddress()); pw.println("  XREF "+r.getFromAddress()+(f==null?"":" function="+f.getName()+" entry="+f.getEntryPoint())); if(f!=null)roots.add(f); }
    }
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    LinkedHashSet<Function> all=new LinkedHashSet<>(roots);
    for(Function f:roots){ all.addAll(f.getCallingFunctions(monitor)); all.addAll(f.getCalledFunctions(monitor)); }
    for(Function f:all) decomp(pw,di,f,roots.contains(f)?"ROOT":"NEIGHBOR");
    di.dispose(); pw.close(); println("wrote "+a[0]+" roots="+roots.size()+" funcs="+all.size());
  }
}
