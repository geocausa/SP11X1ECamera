//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractCpzCallers extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs(); if(a.length<1) throw new IllegalArgumentException("output path required");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    String[] addrs={"f000fb94","f000fc64","f0121af0","f01123e4","f010a6a0","f004b950"};
    FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    for(String s:addrs){
      Address ad=toAddr(s); Function target=fm.getFunctionAt(ad); if(target==null) target=fm.getFunctionContaining(ad);
      pw.println("TARGET "+s+" function="+(target==null?"<none>":target.getName()+" @"+target.getEntryPoint()));
      if(target!=null) funcs.add(target);
      ReferenceIterator it=rm.getReferencesTo(ad);
      while(it.hasNext()){
        Reference ref=it.next(); Function f=fm.getFunctionContaining(ref.getFromAddress());
        pw.println("  XREF "+ref.getFromAddress()+" type="+ref.getReferenceType()+" caller="+(f==null?"<none>":f.getName()+" @"+f.getEntryPoint()));
        if(f!=null) funcs.add(f);
      }
      if(target!=null){
        for(Function f:target.getCallingFunctions(monitor)){ pw.println("  CALLER "+f.getName()+" @"+f.getEntryPoint()); funcs.add(f); }
      }
      pw.println();
    }
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    pw.println("=== DECOMPILATIONS ===");
    for(Function f:funcs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,90,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC()); else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close(); println("wrote "+a[0]+" functions="+funcs.size());
  }
}
