// DumpQcSkDomainMap.java
//@category SP11.Camera
import ghidra.app.script.GhidraScript; import ghidra.program.model.address.Address; import ghidra.program.model.mem.Memory; import java.io.*;
public class DumpQcSkDomainMap extends GhidraScript {
 public void run() throws Exception { String[] a=getScriptArgs(); PrintWriter p=new PrintWriter(new FileOutputStream(a[0])); Memory m=currentProgram.getMemory(); long base=0x1400042c0L; for(int i=0;i<5;i++){Address x=toAddr(Long.toHexString(base+i*8)); int domain=m.getInt(x); int mapped=m.getInt(x.add(4)); p.printf("entry[%d] addr=%s input_domain=0x%x mapped_vmid=0x%x%n",i,x,domain,mapped);} p.close(); }
}
