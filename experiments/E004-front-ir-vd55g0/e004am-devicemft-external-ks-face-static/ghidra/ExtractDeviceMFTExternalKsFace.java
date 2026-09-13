// ExtractDeviceMFTExternalKsFace.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractDeviceMFTExternalKsFace extends GhidraScript {
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    String[] needles={
      "CDeviceMFT::QueryInterface",
      "CDeviceMFT::KsProperty",
      "CDeviceMFT::KsMethod",
      "CDeviceMFT::KsEvent",
      "CDeviceMFT::GetService",
      "CDeviceMFT::InitializeTransform"
    };
    Listing l=currentProgram.getListing(); ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> fs=new LinkedHashSet<>();
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    pw.println("program="+currentProgram.getName());
    for(Data d: iterable(l.getDefinedData(true))){
      if(!d.hasStringValue()||d.getValue()==null)continue;
      String s=d.getValue().toString(); boolean hit=false;
      for(String n:needles)if(s.contains(n)){hit=true;break;}
      if(!hit)continue;
      pw.println("STRING "+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()){
        Reference r=ri.next(); Function f=l.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+(f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
        if(f!=null)fs.add(f);
      }
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    for(Function f:fs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed]");
    }
    di.dispose();pw.close();println("wrote "+out+" funcs="+fs.size());
  }
  private static <T> Iterable<T> iterable(final Iterator<T> it){return new Iterable<T>(){public Iterator<T> iterator(){return it;}};}
}
