// DecompileSecureSectionNamed.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;
public class DecompileSecureSectionNamed extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0]));
    String[] names={"IumCreateSecureSection","IumOpenSecureSection","IumGetExposedSecureSection","SkmmCreateSecureSection","SkmmCreateExposedSecureSection","SkmmReferenceSecureSection","SkmmProbeSecureSectionPages","SkmmCreateSecureAllocation"};
    FunctionManager fm=currentProgram.getFunctionManager(); SymbolTable st=currentProgram.getSymbolTable(); DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(String n:names){
      List<Symbol> syms=st.getGlobalSymbols(n); p.println("=== SYMBOL "+n+" count="+syms.size()+" ===");
      for(Symbol s:syms){ p.println("symbol="+s.getName()+" addr="+s.getAddress()+" type="+s.getSymbolType()); Function f=fm.getFunctionAt(s.getAddress()); if(f==null) f=fm.getFunctionContaining(s.getAddress()); if(f!=null){p.println("function="+f.getName()+" entry="+f.getEntryPoint()+" sig="+f.getSignature()); DecompileResults dr=di.decompileFunction(f,180,monitor); if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)p.println(dr.getDecompiledFunction().getC()); else p.println("[decompile failed]");}}
    }
    di.dispose(); p.close();
  }
}
