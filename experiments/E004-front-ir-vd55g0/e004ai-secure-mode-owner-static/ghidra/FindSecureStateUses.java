// FindSecureStateUses.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
import java.util.*;

public class FindSecureStateUses extends GhidraScript {
  public void run() throws Exception {
    String[] args=getScriptArgs();
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[0]),"UTF-8"));
    long[] wanted={0x2adL,0x2b4L,0x2b6L,0x2b8L,0x2b9L,0x2baL};
    Set<Long> ws=new HashSet<>(); for(long v:wanted)ws.add(v);
    LinkedHashSet<Function> funcs=new LinkedHashSet<>();
    Listing listing=currentProgram.getListing();
    InstructionIterator ii=listing.getInstructions(true);
    while(ii.hasNext()&&!monitor.isCancelled()){
      Instruction ins=ii.next();
      boolean hit=false;
      for(int op=0;op<ins.getNumOperands();op++){
        for(Object o:ins.getOpObjects(op)){
          if(o instanceof Scalar && ws.contains(((Scalar)o).getUnsignedValue())) hit=true;
        }
      }
      if(hit){
        Function f=listing.getFunctionContaining(ins.getAddress());
        pw.println("INS "+ins.getAddress()+" "+ins+" function="+(f==null?"<none>":f.getName()+"@"+f.getEntryPoint()));
        if(f!=null)funcs.add(f);
      }
    }
    pw.println("\n=== DECOMPILATIONS ===");
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(Function f:funcs){
      pw.println("\n//// "+f.getName()+" @"+f.getEntryPoint()+" ////");
      DecompileResults dr=di.decompileFunction(f,60,monitor);
      if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
      else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
    }
    di.dispose(); pw.close();
    println("wrote "+args[0]+" funcs="+funcs.size());
  }
}