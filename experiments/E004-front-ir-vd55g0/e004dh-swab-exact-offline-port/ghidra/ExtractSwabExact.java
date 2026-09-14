//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class ExtractSwabExact extends GhidraScript {
  static final long[] FUNCS={0x180019828L,0x18001a138L,0x18001f170L,0x18001f420L};
  static final long[][] DUMPS={{0x18003d240L,0x804L},{0x18003da40L,0x50L},{0x18001f400L,0x20L},{0x1800201e0L,0x30L}};
  void decomp(PrintWriter pw,DecompInterface di,long a)throws Exception{
    Address ad=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(a);
    Function f=getFunctionAt(ad); if(f==null)f=getFunctionContaining(ad);
    pw.println("\n===== FUNCTION "+Long.toHexString(a)+" "+(f==null?"<none>":f.getName())+" =====");
    if(f==null)return;
    DecompileResults dr=di.decompileFunction(f,180,monitor);
    if(dr!=null&&dr.decompileCompleted()&&dr.getDecompiledFunction()!=null)pw.println(dr.getDecompiledFunction().getC());
    else pw.println("[decompile failed] "+(dr==null?"null":dr.getErrorMessage()));
  }
  void dump(PrintWriter pw,long a,long n)throws Exception{
    Address ad=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(a);
    Memory m=currentProgram.getMemory(); byte[] b=new byte[(int)n]; int got=m.getBytes(ad,b);
    pw.println("\n===== DUMP "+Long.toHexString(a)+" len="+n+" got="+got+" =====");
    for(int i=0;i<got;i+=16){
      pw.printf("%08x:",a+i);
      for(int j=0;j<16&&i+j<got;j++)pw.printf(" %02x",b[i+j]&0xff);
      pw.println();
    }
  }
  public void run()throws Exception{
    String[] args=getScriptArgs(); if(args.length<1)throw new IllegalArgumentException("out");
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[0]),"UTF-8"));
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    for(long a:FUNCS)decomp(pw,di,a);
    for(long[] d:DUMPS)dump(pw,d[0],d[1]);
    di.dispose(); pw.close(); println("wrote "+args[0]);
  }
}
