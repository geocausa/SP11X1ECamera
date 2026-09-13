// DumpQcTrEESmcInvokeConstants.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.program.model.address.Address; import ghidra.program.model.mem.Memory; import java.io.*;
public class DumpQcTrEESmcInvokeConstants extends GhidraScript {
 public void run() throws Exception { String[] args=getScriptArgs(); PrintWriter pw=new PrintWriter(new FileOutputStream(args[0])); Memory m=currentProgram.getMemory();
 String[] as={"1400359f8","1400359fc","140035a00","140035a04","140036350","140036354","140036358","14003635c","140034a90","140034a94","140034a98","140034a9c","140035184","140035188","14003518c","140035190"};
 for(String x:as){Address a=toAddr(x); int v=m.getInt(a); pw.printf("%s u32=0x%08x unsigned=%d%n",x,v,Integer.toUnsignedLong(v));} pw.close(); }
}
