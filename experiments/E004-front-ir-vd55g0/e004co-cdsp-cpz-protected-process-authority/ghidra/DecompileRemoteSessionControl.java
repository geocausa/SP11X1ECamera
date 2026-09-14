//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
public class DecompileRemoteSessionControl extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); if(a.length<1) throw new IllegalArgumentException("output path required");
  PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
  Function f=null; SymbolIterator it=currentProgram.getSymbolTable().getSymbols("remote_session_control");
  while(it.hasNext()){ Symbol s=it.next(); Function x=currentProgram.getFunctionManager().getFunctionAt(s.getAddress()); if(x!=null){ f=x; break; } }
  if(f==null){ for(Function x: currentProgram.getFunctionManager().getFunctions(true)){ if(x.getName().equals("remote_session_control")){f=x;break;} } }
  if(f==null) throw new RuntimeException("remote_session_control not found");
  pw.println("program="+currentProgram.getName()); pw.println("function="+f.getName()+" @"+f.getEntryPoint());
  DecompInterface di=new DecompInterface();di.openProgram(currentProgram);DecompileResults dr=di.decompileFunction(f,120,monitor);
  if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC()); else pw.println("[decompile failed]");
  di.dispose();pw.close();println("wrote "+a[0]);
 }
}
