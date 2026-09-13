// DumpQcTrEEConstants.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import java.io.*;

public class DumpQcTrEEConstants extends GhidraScript {
  public void run() throws Exception {
    String[] args=getScriptArgs(); if(args.length<1) throw new IllegalArgumentException("output path");
    PrintWriter pw=new PrintWriter(new FileOutputStream(args[0]));
    Memory m=currentProgram.getMemory();
    String[] as={"140030990","140030994","140030998","140030c60","140030c64","140030c68",
                 "140036340","140036344","140036348","14003634c","140036350","140036354","140036358"};
    for(String x:as){ Address a=toAddr(x); int v=m.getInt(a); long u=Integer.toUnsignedLong(v); pw.printf("%s u32=0x%08x unsigned=%d%n",x,v,u); }
    pw.close();
  }
}
