// FindIfeHwVersionFieldUsers.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.*;
import java.io.*;
import java.util.*;
public class FindIfeHwVersionFieldUsers extends GhidraScript {
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); FunctionManager fm=currentProgram.getFunctionManager();
    LinkedHashSet<Function> fs=new LinkedHashSet<>();
    InstructionIterator it=l.getInstructions(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Instruction ins=it.next(); long a=ins.getAddress().getOffset();
      if(a<0x180014000L||a>=0x180019000L) continue;
      boolean hit=false;
      for(int op=0;op<ins.getNumOperands();op++) for(Object o:ins.getOpObjects(op))
        if(o instanceof Scalar && ((Scalar)o).getUnsignedValue()==0x100L) hit=true;
      if(hit){Function f=fm.getFunctionContaining(ins.getAddress()); pw.println("HIT "+ins.getAddress()+" "+ins+" function="+F(f)); if(f!=null) fs.add(f);}
    }
    pw.println();pw.println("=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    for(Function f:fs){pw.println();pw.println("//// "+F(f)+" ////");DecompileResults dr=di.decompileFunction(f,120,monitor);if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());}
    di.dispose();pw.close();
  }
}
