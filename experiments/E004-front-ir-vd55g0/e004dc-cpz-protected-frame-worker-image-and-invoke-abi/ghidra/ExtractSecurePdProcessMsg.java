//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractSecurePdProcessMsg extends GhidraScript {
 static final String[] N={"process_msg","ALGO buffer","HEAP buffer","POOL buffer","DATA_LOADED","Starting static execution","sec_algo.elf","symbol %s not found","launching in new thread","secure channel is in an invalid state"};
 boolean hit(String s){for(String n:N)if(s.contains(n))return true;return false;}
 void dc(PrintWriter p,DecompInterface d,Function f,String t){if(f==null)return;p.println("\n//// "+t+" "+f.getName()+" @"+f.getEntryPoint()+" ////");DecompileResults r=d.decompileFunction(f,180,monitor);if(r!=null&&r.decompileCompleted()&&r.getDecompiledFunction()!=null)p.println(r.getDecompiledFunction().getC());}
 public void run() throws Exception {String[] a=getScriptArgs();PrintWriter p=new PrintWriter(new FileOutputStream(a[0]));Listing l=currentProgram.getListing();ReferenceManager rm=currentProgram.getReferenceManager();FunctionManager fm=currentProgram.getFunctionManager();LinkedHashSet<Function> fs=new LinkedHashSet<>();DataIterator it=l.getDefinedData(true);while(it.hasNext()){Data x=it.next();Object v=x.getValue();if(!(v instanceof String)||!hit((String)v))continue;p.println("STRING @"+x.getAddress()+" = "+v);ReferenceIterator ri=rm.getReferencesTo(x.getAddress());while(ri.hasNext()){Reference r=ri.next();Function f=fm.getFunctionContaining(r.getFromAddress());p.println("  XREF "+r.getFromAddress()+" "+(f==null?"":f.getName()+"@"+f.getEntryPoint()));if(f!=null)fs.add(f);}}DecompInterface d=new DecompInterface();d.openProgram(currentProgram);for(Function f:fs){dc(p,d,f,"ROOT");for(Function c:f.getCallingFunctions(monitor))dc(p,d,c,"CALLER");for(Function c:f.getCalledFunctions(monitor))dc(p,d,c,"CALLEE");}d.dispose();p.close();}
}
