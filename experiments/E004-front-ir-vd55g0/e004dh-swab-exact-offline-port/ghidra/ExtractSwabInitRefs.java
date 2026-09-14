//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class ExtractSwabInitRefs extends GhidraScript {
 static final long[] ADDRS={0x18003d228L,0x18003d240L,0x18003da48L,0x18003da50L,0x18003da58L,0x18003da60L,0x18003da68L,0x18003da70L,0x18003da78L};
 public void run() throws Exception {
  String[] a=getScriptArgs(); PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
  ReferenceManager rm=currentProgram.getReferenceManager(); FunctionManager fm=currentProgram.getFunctionManager(); LinkedHashSet<Function> fs=new LinkedHashSet<>();
  for(long x:ADDRS){ Address ad=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(x); pw.println("ADDR "+ad); ReferenceIterator ri=rm.getReferencesTo(ad); while(ri.hasNext()){Reference r=ri.next();Function f=fm.getFunctionContaining(r.getFromAddress());pw.println("  XREF "+r.getFromAddress()+(f==null?"":" "+f.getName()+" @"+f.getEntryPoint())); if(f!=null)fs.add(f);} }
  DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
  for(Function f:fs){pw.println("\n===== "+f.getName()+" @"+f.getEntryPoint()+" ====="); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());}
  di.dispose();pw.close();println("functions="+fs.size());
 }
}
