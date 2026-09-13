// ExtractSecureUSBVideo.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSecureUSBVideo extends GhidraScript {
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing listing=currentProgram.getListing();
    ReferenceManager rm=currentProgram.getReferenceManager();
    FunctionManager fm=currentProgram.getFunctionManager();
    SymbolTable st=currentProgram.getSymbolTable();
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    Set<Function> funcs=new LinkedHashSet<>();

    String[] symbols={"CreateSecureSection","OpenSecureSection","CloseHandle","UuidCreate","MapViewOfFile","UnmapViewOfFile"};
    for(String n:symbols){
      pw.println("=== SYMBOL "+n+" ===");
      SymbolIterator si=st.getSymbols(n);
      while(si.hasNext()){
        Symbol s=si.next();
        pw.println("SYMBOL "+s.getAddress()+" "+s.getName()+" type="+s.getSymbolType());
        ReferenceIterator ri=rm.getReferencesTo(s.getAddress());
        while(ri.hasNext()){
          Reference ref=ri.next();
          Function f=fm.getFunctionContaining(ref.getFromAddress());
          pw.println("  REF "+ref.getFromAddress()+" "+ref.getReferenceType()+" caller="+
            (f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
          if(f!=null) funcs.add(f);
        }
      }
    }

    String[] needles={
      "Invalid secure capture buffer description passed",
      "Failed to create secure section",
      "Failed to map secure section",
      "Secure buffers allocated",
      "GetSecureFrameBuffer",
      "ReplaceSecureFrameBuffer",
      "SetSecureBufferAttribute",
      "FreeSecureBuffer",
      "AllocateUvcBuffers",
      "CopySecureUvcPayloadToSecureFrameBuffer"
    };
    DataIterator it=listing.getDefinedData(true);
    while(it.hasNext()){
      Data data=it.next(); Object v=data.getValue();
      if(!(v instanceof String)) continue;
      String s=(String)v; boolean hit=false;
      for(String n:needles) if(s.contains(n)){hit=true;break;}
      if(!hit) continue;
      pw.println("STRING "+data.getAddress()+" = "+s.replace("\n","\\n"));
      ReferenceIterator ri=rm.getReferencesTo(data.getAddress());
      while(ri.hasNext()){
        Reference ref=ri.next(); Function f=fm.getFunctionContaining(ref.getFromAddress());
        pw.println("  REF "+ref.getFromAddress()+" "+ref.getReferenceType()+" caller="+
          (f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
        if(f!=null) funcs.add(f);
      }
    }

    Set<Function> all=new LinkedHashSet<>(funcs);
    for(Function f:funcs){
      ReferenceIterator ri=rm.getReferencesTo(f.getEntryPoint());
      while(ri.hasNext()){
        Reference ref=ri.next(); Function cf=fm.getFunctionContaining(ref.getFromAddress());
        if(cf!=null) all.add(cf);
      }
    }
    pw.println("=== DECOMPILATIONS ===");
    for(Function f:all){
      pw.println("//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,180,monitor);
      if(dr!=null && dr.decompileCompleted() && dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      pw.println();
    }
    di.dispose(); pw.close();
  }
}
