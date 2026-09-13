// ExtractPinConfigurerFactory.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractPinConfigurerFactory extends GhidraScript {
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager();
    String[] needles={"CItemFactory::CreatePinConfigurer","CPinConfigurer::Construct","CPinConfigurer::CPinConfigurer","CPinConfigurer_QC::CPinConfigurer_QC"};
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    for(Data d: iterable(l.getDefinedData(true))){
      if(!d.hasStringValue())continue; Object v=d.getValue(); if(v==null)continue;
      String s=v.toString(); boolean hit=false; for(String n:needles)if(s.contains(n)){hit=true;break;}
      if(!hit)continue;
      pw.println("STRING "+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=l.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+(f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
        if(f!=null)funcs.add(f);
      }
    }
    pw.println("\n=== FUNCTION REFS ===");
    for(Function f:new ArrayList<Function>(funcs)){
      pw.println("TARGET "+f.getEntryPoint()+" "+f.getName());
      ReferenceIterator ri=rm.getReferencesTo(f.getEntryPoint());
      while(ri.hasNext()){
        Reference r=ri.next(); Function c=l.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" caller="+(c==null?"<none>":c.getName()+"@"+c.getEntryPoint()));
        if(c!=null)funcs.add(c);
      }
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed]");
    }
    di.dispose();pw.close();println("wrote "+out+" funcs="+funcs.size());
  }
  private static <T> Iterable<T> iterable(final Iterator<T> it){return new Iterable<T>(){public Iterator<T> iterator(){return it;}};}
}
