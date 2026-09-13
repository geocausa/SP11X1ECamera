// FindIfeHalOffsets.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.*;
import java.io.*;
import java.util.*;
public class FindIfeHalOffsets extends GhidraScript {
  private String F(Function f){return f==null?"<none>":f.getName()+"@"+f.getEntryPoint();}
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Listing l=currentProgram.getListing(); FunctionManager fm=currentProgram.getFunctionManager();
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    long[] vals={0x6b568L,0x6b570L,0x6b578L,0x6b580L,0xe8L,0xf0L,0xf8L};
    InstructionIterator it=l.getInstructions(true);
    while(it.hasNext()&&!monitor.isCancelled()){
      Instruction ins=it.next(); long off=ins.getAddress().getOffset();
      if(off<0x180000000L || off>=0x180030000L) continue;
      for(long val:vals){
        boolean hit=false;
        for(int op=0;op<ins.getNumOperands();op++) for(Object o:ins.getOpObjects(op))
          if(o instanceof Scalar && ((Scalar)o).getUnsignedValue()==val) hit=true;
        if(hit){
          Function f=fm.getFunctionContaining(ins.getAddress());
          pw.println(String.format("SCALAR 0x%x @%s %s function=%s",val,ins.getAddress(),ins,F(f)));
          if(f!=null) funcs.add(f);
          break;
        }
      }
    }
    pw.println(); pw.println("=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println(); pw.println("//// "+F(f)+" ////");
      DecompileResults dr=di.decompileFunction(f,120,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null) pw.println(dr.getDecompiledFunction().getC());
    }
    di.dispose(); pw.close();
  }
}
