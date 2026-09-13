// DumpSurfaceSecureConstants.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.io.*;
public class DumpSurfaceSecureConstants extends GhidraScript {
  private Address A(long v){return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);}
  public void run() throws Exception {
    PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(getScriptArgs()[0]),"UTF-8"));
    Memory m=currentProgram.getMemory();
    long[] addrs={0x14008d378L,0x140018ea0L,0x14008e2a4L,0x14008d370L,0x14008d374L};
    for(long x:addrs){
      Address a=A(x);
      int v=m.getInt(a);
      pw.printf("%s u32=0x%08x%n",a,v);
    }
    pw.close();
  }
}
