//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.util.*;

public class DecompileNamed extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs(); if(a.length<2) throw new IllegalArgumentException("out fn...");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    FunctionManager fm=currentProgram.getFunctionManager();
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    pw.println("PROGRAM="+currentProgram.getName());
    for(int i=1;i<a.length;i++) {
      String n=a[i]; boolean found=false;
      FunctionIterator it=fm.getFunctions(true);
      while(it.hasNext()) {
        Function f=it.next();
        if(!f.getName().equals(n)) continue;
        found=true;
        pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
        DecompileResults dr=di.decompileFunction(f,120,monitor);
        if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
        else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
      }
      if(!found) pw.println("\n//// NOT_FOUND "+n+" ////");
    }
    di.dispose(); pw.close();
  }
}
