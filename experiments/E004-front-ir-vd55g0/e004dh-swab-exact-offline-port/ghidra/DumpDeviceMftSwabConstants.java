//@category SP11.Camera
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.io.*;
public class DumpDeviceMftSwabConstants extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs(); PrintWriter pw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(a[0]),"UTF-8"));
    Memory m=currentProgram.getMemory();
    long[] addrs={0x180a6ab98L,0x180a6aba0L}; int[] lens={8,4};
    for(int k=0;k<addrs.length;k++){
      Address ad=currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addrs[k]);
      byte[] b=new byte[lens[k]]; m.getBytes(ad,b);
      pw.printf("%s",ad); for(byte x:b)pw.printf(" %02x",x&0xff); pw.println();
      if(lens[k]==4){int v=(b[0]&255)|((b[1]&255)<<8)|((b[2]&255)<<16)|((b[3]&255)<<24);pw.println("float="+Float.intBitsToFloat(v)+" raw=0x"+Integer.toHexString(v));}
      else {long v=0;for(int i=0;i<8;i++)v|=((long)b[i]&255)<<(8*i);pw.println("double="+Double.longBitsToDouble(v)+" raw=0x"+Long.toHexString(v));}
    }
    pw.close();
  }
}
