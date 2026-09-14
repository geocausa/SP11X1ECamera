// ExtractIoDomain.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.app.decompiler.*; import ghidra.program.model.listing.*; import ghidra.program.model.symbol.*; import java.io.*; import java.util.*;
public class ExtractIoDomain extends GhidraScript {
 public void run() throws Exception {String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); SymbolTable st=currentProgram.getSymbolTable(); FunctionManager fm=currentProgram.getFunctionManager(); DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
  SymbolIterator it=st.getAllSymbols(true); ArrayList<Function> fs=new ArrayList<>(); while(it.hasNext()){Symbol s=it.next(); String n=s.getName(); String l=n.toLowerCase(Locale.ROOT); if(l.contains("iodomain")||l.contains("io_domain")||l.contains("devicegpa")){Function f=fm.getFunctionAt(s.getAddress()); if(f!=null&&!fs.contains(f)){fs.add(f); p.println("SYMBOL "+n+" @"+s.getAddress()+" sig="+f.getSignature());}}}
  p.println("\n=== DECOMP ==="); for(Function f:fs){p.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////"); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC());} di.dispose(); p.close(); }
}
