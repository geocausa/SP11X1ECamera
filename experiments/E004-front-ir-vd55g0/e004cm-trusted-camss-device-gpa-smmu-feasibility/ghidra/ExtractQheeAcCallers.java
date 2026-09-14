// ExtractQheeAcCallers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.app.decompiler.*; import ghidra.program.model.listing.*; import java.io.*; import java.util.*;
public class ExtractQheeAcCallers extends GhidraScript {
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); FunctionManager fm=currentProgram.getFunctionManager(); Function t=fm.getFunctionAt(toAddr("001b8c58")); p.println("TARGET "+t.getName()+" @"+t.getEntryPoint()+" sig="+t.getSignature()); LinkedHashSet<Function> fs=new LinkedHashSet<>(); for(Function c:t.getCallingFunctions(monitor)){p.println("CALLER "+c.getName()+" @"+c.getEntryPoint()+" sig="+c.getSignature());fs.add(c);} DecompInterface di=new DecompInterface();di.openProgram(currentProgram);for(Function f:fs){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");DecompileResults dr=di.decompileFunction(f,120,monitor);if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());}di.dispose();p.close();}
}
