// ExtractInterfaceAccessor.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractInterfaceAccessor extends GhidraScript {
  public void run() throws Exception {
    String out=getScriptArgs()[0];
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out),"UTF-8"));
    Listing listing=currentProgram.getListing();
    ReferenceManager rm=currentProgram.getReferenceManager();
    String[] needles={
      "CInterfaceAccessor::GetInterface",
      "CInterfaceAccessor::SetProcessorMediator",
      "CInterfaceAccessor::SetCaptureDevice",
      "CInterfaceAccessor::SetGlobalSettings",
      "CInterfaceAccessor::SetD3dDeviceManager",
      "CInterfaceAccessor::SetSensorDataProvider",
      "CInterfaceAccessor::SetPhotoConfirmation",
      "CInterfaceAccessor::SetSourceTransformQcPDMFT",
      "CInterfaceAccessor::SetSourceTransform",
      "CInterfaceAccessor::SetThreadPool",
      "CInterfaceAccessor::SetMediaEventGenerator",
      "CInterfaceAccessor::QueryInterface",
      "CInterfaceAccessor::CInterfaceAccessor",
      "CInterfaceAccessor::~CInterfaceAccessor",
      "SetCameraControls"
    };
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName());
    for(Data d: iterable(listing.getDefinedData(true))){
      if(!d.hasStringValue()) continue;
      Object v=d.getValue(); if(v==null) continue;
      String s=v.toString();
      boolean hit=false; for(String n:needles) if(s.contains(n)){hit=true;break;}
      if(!hit) continue;
      pw.println("STRING "+d.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(d.getAddress());
      while(ri.hasNext()){
        Reference r=ri.next();
        Function f=listing.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+(f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
        if(f!=null) funcs.add(f);
      }
    }
    pw.println("\n=== FUNCTION REFS ===");
    ArrayList<Function> seed=new ArrayList<>(funcs);
    for(Function f:seed){
      pw.println("TARGET "+f.getEntryPoint()+" "+f.getName());
      ReferenceIterator ri=rm.getReferencesTo(f.getEntryPoint());
      while(ri.hasNext()){
        Reference r=ri.next();
        Function c=listing.getFunctionContaining(r.getFromAddress());
        pw.println("  REF "+r.getFromAddress()+" type="+r.getReferenceType()+" caller="+(c==null?"<none>":c.getName()+"@"+c.getEntryPoint()));
        if(c!=null) funcs.add(c);
      }
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,90,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close(); println("wrote "+out+" funcs="+funcs.size());
  }
  private static <T> Iterable<T> iterable(final Iterator<T> it){return new Iterable<T>(){public Iterator<T> iterator(){return it;}};}
}
