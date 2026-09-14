//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecurePdRoot extends GhidraScript {
 static final String[] N={"algo_main","sec_gaussian","securepd_main_thread","securepd_init","/statichashes/example_image.so","/statichashes/example_image_runner.so","/statichashes/libloadalgo_skel.so","dynamic module is unsigned","Static hash found"};
 boolean hit(String s){for(String n:N)if(s.contains(n))return true;return false;}
 void dc(PrintWriter pw,DecompInterface di,Function f,String tag){if(f==null)return;pw.println("\n//// "+tag+" "+f.getName()+" @"+f.getEntryPoint()+" ////");DecompileResults r=di.decompileFunction(f,120,monitor);if(r!=null&&r.decompileCompleted()&&r.getDecompiledFunction()!=null)pw.println(r.getDecompiledFunction().getC());else pw.println("[fail]");}
 public void run() throws Exception{
  String[] a=getScriptArgs();PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
  Listing l=currentProgram.getListing();ReferenceManager rm=currentProgram.getReferenceManager();FunctionManager fm=currentProgram.getFunctionManager();LinkedHashSet<Function> fs=new LinkedHashSet<>();
  DataIterator it=l.getDefinedData(true);while(it.hasNext()){Data d=it.next();Object v=d.getValue();if(!(v instanceof String))continue;String s=(String)v;if(!hit(s))continue;pw.println("STRING @"+d.getAddress()+" = "+s);ReferenceIterator ri=rm.getReferencesTo(d.getAddress());while(ri.hasNext()){Reference r=ri.next();Function f=fm.getFunctionContaining(r.getFromAddress());pw.println("  XREF "+r.getFromAddress()+" "+(f==null?"":f.getName()+"@"+f.getEntryPoint()));if(f!=null)fs.add(f);}}
  DecompInterface di=new DecompInterface();di.openProgram(currentProgram);for(Function f:fs){dc(pw,di,f,"ROOT");for(Function c:f.getCallingFunctions(monitor))dc(pw,di,c,"CALLER");for(Function c:f.getCalledFunctions(monitor))dc(pw,di,c,"CALLEE");}di.dispose();pw.close();
 }
}
