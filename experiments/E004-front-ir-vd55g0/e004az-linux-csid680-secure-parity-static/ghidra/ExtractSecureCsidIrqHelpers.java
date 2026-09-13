// ExtractSecureCsidIrqHelpers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class ExtractSecureCsidIrqHelpers extends GhidraScript {
 private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
 public void run() throws Exception {
  PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
  DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
  long[] xs={0x180011a58L,0x180011b60L,0x180013408L};
  for(long x:xs){Function f=currentProgram.getFunctionManager().getFunctionAt(A(x)); pw.println("//// "+(f==null?"NONE":f.getName()+"@"+f.getEntryPoint())+" ////"); if(f!=null){DecompileResults dr=di.decompileFunction(f,120,monitor);if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());} pw.println();}
  di.dispose();pw.close();
 }
}
