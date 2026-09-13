// ExtractFaceProcessorSecureControls.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractFaceProcessorSecureControls extends GhidraScript {
  private boolean match(String s){
    String x=s.toLowerCase(Locale.ROOT);
    String[] n={
      "setfaceauthmodepropertystring","setsecuremodepropertystring",
      "togglefacemode","togglesecuresensor","enable secure","enablesecuremode",
      "setproperty.","setpropertystring","getpropertybuffer",
      "faceauthcapability","securemodecapability",
      "setfaceauthprofile","faceauthenticationmode",
      "infraredsourcecontroller->setpropertyasync"
    };
    for(String q:n) if(x.contains(q)) return true;
    return false;
  }
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception{
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); FunctionManager fm=currentProgram.getFunctionManager(); ReferenceManager rm=currentProgram.getReferenceManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    pw.println("program="+currentProgram.getName()); pw.println("image_base="+currentProgram.getImageBase());
    pw.println("=== MATCHED STRINGS ===");
    DataIterator di0=l.getDefinedData(true);
    while(di0.hasNext()&&!monitor.isCancelled()){
      Data d=di0.next(); Object v=d.getValue(); if(!(v instanceof String)) continue;
      String s=(String)v; if(!match(s)) continue;
      pw.println("STRING @"+d.getAddress()+" = "+s.replace("\r","\\r").replace("\n","\\n"));
      ReferenceIterator it=rm.getReferencesTo(d.getAddress()); int n=0;
      while(it.hasNext()){
        Reference r=it.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+F(f));
        if(f!=null) funcs.add(f); n++;
      }
      pw.println("  REFCOUNT "+n);
    }
    byte[] guid=new byte[]{(byte)0x12,(byte)0x91,(byte)0xb7,(byte)0x1c,(byte)0xd2,(byte)0xc0,(byte)0x13,(byte)0x42,(byte)0x9c,(byte)0xa6,(byte)0xcd,(byte)0x4f,(byte)0xdb,(byte)0x92,(byte)0x79,(byte)0x72};
    pw.println(); pw.println("=== EXTENDED CAMERA GUID BYTE MATCHES ===");
    Memory mem=currentProgram.getMemory();
    Address cur=currentProgram.getMinAddress();
    while(cur!=null){
      Address hit=mem.findBytes(cur,guid,null,true,monitor);
      if(hit==null) break;
      pw.println("GUID @"+hit);
      ReferenceIterator it=rm.getReferencesTo(hit);
      while(it.hasNext()){
        Reference r=it.next(); Function f=fm.getFunctionContaining(r.getFromAddress());
        pw.println("  XREF "+r.getFromAddress()+" type="+r.getReferenceType()+" function="+F(f));
        if(f!=null) funcs.add(f);
      }
      cur=hit.add(1);
      if(cur.compareTo(currentProgram.getMaxAddress())>0) break;
    }
    pw.println(); pw.println("=== DECOMPILATIONS ===");
    DecompInterface dec=new DecompInterface(); dec.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println(); pw.println("//// "+F(f)+" ////");
      DecompileResults dr=dec.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    dec.dispose(); pw.close(); println("wrote "+getScriptArgs()[0]+" funcs="+funcs.size());
  }
}
