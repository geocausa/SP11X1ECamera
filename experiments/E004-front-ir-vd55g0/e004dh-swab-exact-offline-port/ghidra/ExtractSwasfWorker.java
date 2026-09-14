//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.util.*;
public class ExtractSwasfWorker extends GhidraScript {
  void dec(PrintWriter pw, DecompInterface di, Function f, String tag) throws Exception {
    if (f==null) return;
    pw.println("\n===== "+tag+" "+f.getEntryPoint()+" "+f.getName()+" =====");
    DecompileResults dr=di.decompileFunction(f,240,monitor);
    if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
    else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
  }
  public void run() throws Exception {
    String[] a=getScriptArgs(); PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    Address seed=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x18001e238L);
    Function root=getFunctionAt(seed); if(root==null) root=getFunctionContaining(seed);
    LinkedHashSet<Function> lvl1=new LinkedHashSet<>(), lvl2=new LinkedHashSet<>();
    if(root!=null) lvl1.addAll(root.getCalledFunctions(monitor));
    for(Function f:lvl1) lvl2.addAll(f.getCalledFunctions(monitor));
    dec(pw,di,root,"ROOT");
    for(Function f:lvl1) dec(pw,di,f,"CALLEE1");
    for(Function f:lvl2) if(f!=root&&!lvl1.contains(f)) dec(pw,di,f,"CALLEE2");
    pw.println("\nROOT_CALLERS"); if(root!=null) for(Function f:root.getCallingFunctions(monitor)) pw.println(f.getEntryPoint()+" "+f.getName());
    di.dispose(); pw.close(); println("root="+(root==null?"null":root.getName())+" l1="+lvl1.size()+" l2="+lvl2.size());
  }
}
