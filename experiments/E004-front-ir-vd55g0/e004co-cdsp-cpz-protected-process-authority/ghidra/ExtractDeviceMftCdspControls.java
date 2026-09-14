//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractDeviceMftCdspControls extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); if(a.length<1) throw new IllegalArgumentException("output path required");
  PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
  String[] names={"remote_session_control","remote_handle64_open","remote_handle64_invoke","remote_handle64_close"};
  SymbolTable st=currentProgram.getSymbolTable(); FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
  LinkedHashSet<Function> fs=new LinkedHashSet<>();
  for(String n:names){
   pw.println("=== SYMBOL "+n+" ===");
   SymbolIterator si=st.getSymbols(n);
   while(si.hasNext()){
    Symbol sym=si.next(); Address ad=sym.getAddress(); pw.println("SYMBOL "+sym.getName(true)+" @"+ad+" type="+sym.getSymbolType());
    ReferenceIterator ri=rm.getReferencesTo(ad);
    while(ri.hasNext()){
     Reference ref=ri.next(); Function f=fm.getFunctionContaining(ref.getFromAddress());
     pw.println(" XREF "+ref.getFromAddress()+" type="+ref.getReferenceType()+" caller="+(f==null?"<none>":f.getName()+" @"+f.getEntryPoint()));
     if(f!=null) fs.add(f);
    }
   }
  }
  DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
  pw.println("\n=== DECOMPILATIONS ===");
  for(Function f:fs){
    pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
    DecompileResults dr=di.decompileFunction(f,90,monitor);
    if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC()); else pw.println("[decompile failed]");
  }
  di.dispose();pw.close();println("wrote "+a[0]+" functions="+fs.size());
 }
}
