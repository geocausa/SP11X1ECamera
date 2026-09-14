//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractDeviceMftSwab extends GhidraScript {
 static final String[] N={"CamX::IQInterface::GetSWABF101Data","CamX::IQInterface::GetSWASF101Data","CamX::IFENode::UpdateSWABFData","CamX::IFENode::UpdateSWASFData","No change in SWABF data","No change in SWASF data","swasf10_sw_v2","swabf10_sw_v2"};
 boolean w(String s){for(String n:N)if(s.contains(n))return true;return false;}
 void dec(PrintWriter pw,DecompInterface di,Function f,String tag){if(f==null)return;pw.println("\n===== "+tag+" "+f.getName()+" @"+f.getEntryPoint()+" =====");DecompileResults r=di.decompileFunction(f,240,monitor);if(r!=null&&r.decompileCompleted()&&r.getDecompiledFunction()!=null)pw.println(r.getDecompiledFunction().getC());}
 public void run()throws Exception{String[]a=getScriptArgs();PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));Listing l=currentProgram.getListing();ReferenceManager rm=currentProgram.getReferenceManager();FunctionManager fm=currentProgram.getFunctionManager();LinkedHashSet<Function> roots=new LinkedHashSet<>();DataIterator it=l.getDefinedData(true);while(it.hasNext()){Data d=it.next();Object v=d.getValue();if(!(v instanceof String))continue;String s=(String)v;if(!w(s))continue;pw.println("STRING @"+d.getAddress()+" = "+s);ReferenceIterator ri=rm.getReferencesTo(d.getAddress());while(ri.hasNext()){Reference rr=ri.next();Function f=fm.getFunctionContaining(rr.getFromAddress());pw.println("  XREF "+rr.getFromAddress()+(f==null?"":" "+f.getName()+" @"+f.getEntryPoint()));if(f!=null)roots.add(f);}}DecompInterface di=new DecompInterface();di.openProgram(currentProgram);LinkedHashSet<Function> all=new LinkedHashSet<>(roots);for(Function f:roots){all.addAll(f.getCallingFunctions(monitor));all.addAll(f.getCalledFunctions(monitor));}for(Function f:all)dec(pw,di,f,roots.contains(f)?"ROOT":"NEIGHBOR");di.dispose();pw.close();println("roots="+roots.size()+" funcs="+all.size());}
}
