// ExtractDeviceGpa.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.app.decompiler.*; import ghidra.program.model.listing.*; import ghidra.program.model.symbol.*; import java.io.*; import java.util.*;
public class ExtractDeviceGpa extends GhidraScript {
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); SymbolTable st=currentProgram.getSymbolTable(); FunctionManager fm=currentProgram.getFunctionManager(); DecompInterface di=new DecompInterface(); di.openProgram(currentProgram); String[] names={"IumAssignMemoryToSocDomain","ShvlMapSparseDeviceGpaPages","ShvlUnmapSparseDeviceGpaPages","SkmmProbeSecureSectionPages","SkmmReferenceSecureSection"}; for(String n:names){p.println("\n=== "+n+" ==="); for(Symbol s:st.getGlobalSymbols(n)){Function f=fm.getFunctionAt(s.getAddress()); p.println("addr="+s.getAddress()+" sig="+(f==null?"null":f.getSignature())); if(f!=null){DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());}}} di.dispose(); p.close();}
}
